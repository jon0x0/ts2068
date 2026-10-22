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
 let metrics={};
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
 function call(name,lba=0,drive=0){m.cpu.pc=symbols[name];m.cpu.h=lba>>8;m.cpu.l=lba&255;m.cpu.c=drive;m.cpu.sp=0xfefe;m.bus.write(0xfefe,0);m.bus.write(0xfeff,0xf7);const clock={tstates:0};let started=null,verify=0;let n=0;while(m.cpu.pc!==0xf700&&n++<100000){if(m.cpu.pc===symbols.sram_verify&&started===null)started=clock.tstates;if(m.cpu.pc===symbols.sram_restore&&started!==null){verify+=clock.tstates-started;started=null;}runZ80(m.cpu,m.bus,1,clock);}metrics={total:clock.tstates,verify};assert(n<100000,name);return m.cpu.a;}
 const map=['\0ZXCV','ASDFG','QWERT','12345','09876','POIUY','\rLKJH',' \0MNB'],sym={'.':'M','=':'L'};
 function type(s){for(let c of s){if(sym[c]){keys[7]&=~2;c=sym[c];}let done=false;for(let r=0;r<8;r++){const bit=map[r].indexOf(c);if(bit>=0){keys[r]&=~(1<<bit);frames(4);keys.fill(255);frames(4);done=true;break;}}assert(done,c);}}
 return {m,pico,frames,boot,call,type,metrics:()=>metrics,log:()=>text};
}

const t=machine();t.boot();assert(t.log().includes('HELLO from a .COM'));
t.m.cpu.a=0;assert.equal(t.call('sram_install_page'),0);
const measured=t.metrics(),hz=3528000;
assert(measured.verify>0&&measured.verify<8192*59);
const result={clock_hz:hz,bytes_per_page:8192,verify_tstates:measured.verify,verify_ms_per_page:1000*measured.verify/hz,normal_40_page_verify_seconds:40*measured.verify/hz,previous_40_page_verify_seconds:40*8192*59/hz};
fs.writeFileSync('build/ramdisk-verification-timing.json',JSON.stringify(result,null,2)+'\n');
console.log(result);
