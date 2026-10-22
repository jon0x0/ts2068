import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {SramPicoModel} from './tspico_sram_model.mjs';
const api=await import(pathToFileURL(path.resolve('../../TSRun/machine.js')));
const {runZ80}=await import(pathToFileURL(path.resolve('../../TSRun/z80.js')));
const dir=process.argv[2]||'build';
const single=process.argv.includes('--single');
const symbols=Object.fromEntries([...fs.readFileSync(dir+'/bios.bin.sym','utf8').matchAll(/^(\w+): EQU 0x([\da-f]+)/gmi)].map(x=>[x[1],parseInt(x[2],16)]));
const disk=fs.readFileSync(dir+'/drive-a.img'),cart=fs.readFileSync(dir+'/ts2068-cpm.dck'),tap=fs.readFileSync(dir+'/CPM320.TAP');
function machine(options={}){
 const keys=new Uint8Array(8).fill(255),m=api.createMachine(keys,new Uint8Array(2).fill(255));
 api.setHomeRom(m,fs.readFileSync('../../TSRun/roms/ts2068-0.rom'));api.setExRom(m,fs.readFileSync('../../TSRun/roms/ts2068-1.rom'));
 const volumes=Object.fromEntries(Array.from({length:single?4:8},(_,i)=>[`/CPM/CPM3200${i}.TAP`,fs.readFileSync(dir+`/CPM3200${i}.TAP`)]));
 assert.equal(api.insertDock(m,cart),null);const pico=new SramPicoModel(m,cart,tap,{...options,volumes});
 const rd=m.bus.ioRead,wr=m.bus.ioWrite;
 m.bus.ioRead=p=>[14,15].includes(p&255)?pico.read(p):rd(p);
 m.bus.ioWrite=(p,v)=>[14,15].includes(p&255)?pico.write(p,v):wr(p,v);
 let text='';const write=m.bus.write;m.bus.write=(a,v)=>{if(a>=0xf800&&a<0xfe00)text+=String.fromCharCode(v);write(a,v);};
 const frames=n=>{for(let i=0;i<n;i++)api.runFrame(m);};
 function boot(){for(let n=0;n<150;n++){frames(200);if(text.includes('HELLO from a .COM')||text.includes('failed. Do not boot.'))return;}throw Error('boot timeout '+text.slice(-500)+' PC='+m.cpu.pc.toString(16));}
 function call(name,lba=0,drive=0){m.cpu.pc=symbols[name];m.cpu.h=lba>>8;m.cpu.l=lba&255;m.cpu.c=drive;m.cpu.sp=0xfefe;m.bus.write(0xfefe,0);m.bus.write(0xfeff,0xf7);const clock={tstates:0};let n=0;while(m.cpu.pc!==0xf700&&n++<1000000)runZ80(m.cpu,m.bus,1,clock);assert(n<1000000,name);return m.cpu.a;}
 const map=['\0ZXCV','ASDFG','QWERT','12345','09876','POIUY','\rLKJH',' \0MNB'],sym={'.':'M','=':'L'};
 function type(s){for(let c of s){if(sym[c]){keys[7]&=~2;c=sym[c];}let done=false;for(let r=0;r<8;r++){const bit=map[r].indexOf(c);if(bit>=0){keys[r]&=~(1<<bit);frames(4);keys.fill(255);frames(4);done=true;break;}}assert(done,c);}}
 return {m,pico,frames,boot,call,type,log:()=>text};
}
const t=machine();t.boot();assert.match(t.log(),/HELLO from a \.COM/);
const screen=Buffer.from(Array.from({length:0x4000},(_,i)=>(i*13+7)&255));
t.m.ram.set(screen,0x4000);
// Separate write-snooping framebuffer, following PicoVideo 4.2 HSR gates.
const shadow=Buffer.from(screen),memoryWrite=t.m.bus.write;
t.m.bus.write=(address,value)=>{if(address>=0x4000&&address<0x8000&&!(t.m.portF4&(1<<(address>>13))))shadow[address-0x4000]=value;memoryWrite(address,value);};
for(const page of [0,2,3,5,12,19,26,33]){
 const data=Buffer.from(Array.from({length:8192},(_,i)=>(page*7+i*19)&255));
 for(let i=0;i<data.length;i++)t.m.bus.write(0xa000+i,data[i]);
 t.m.cpu.a=page;assert.equal(t.call('sram_install_page'),0,'install '+page);
 assert.deepEqual(Buffer.from(t.m.ram.subarray(0x4000,0x8000)),screen,'install changed video RAM '+page);
 for(let i=0;i<data.length;i++)t.m.bus.write(0xa000+i,0);
 t.m.cpu.a=page;assert.equal(t.call('sram_fetch_page'),0,'fetch '+page);
 assert.deepEqual(Buffer.from(Array.from({length:8192},(_,i)=>t.m.bus.read(0xa000+i))),data,'fetch data '+page);
 assert.deepEqual(Buffer.from(t.m.ram.subarray(0x4000,0x8000)),screen,'fetch changed video RAM '+page);
 assert.deepEqual(shadow,screen,'PicoVideo shadow changed during bank transfer '+page);
 assert.equal(t.pico.slot,4);assert.equal(t.m.portF4,15);
}
assert(t.log().includes('Loading block 40 of 40'),'missing final page progress');
console.log('Install/fetch across all A000 pairs preserves both HOME screen planes and verifies disk data; progress reaches 40/40 PASS');

for(const window of [0,5]){
 const bad=machine({readOnlyPage:window});bad.boot();
 assert(bad.log().includes('failed. Do not boot.'),'verification failed to reject unwritable bank '+window);
 assert(!bad.log().includes('HELLO from a .COM'));
}
console.log('Optimized verification still rejects failed readback in direct and bounce-buffer windows PASS');
