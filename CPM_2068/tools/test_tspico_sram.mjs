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
 function call(name,lba=0,drive=0){m.cpu.pc=symbols[name];m.cpu.h=lba>>8;m.cpu.l=lba&255;m.cpu.c=drive;m.cpu.sp=0xfefe;m.bus.write(0xfefe,0);m.bus.write(0xfeff,0xf7);const clock={tstates:0};let n=0;while(m.cpu.pc!==0xf700&&n++<100000)runZ80(m.cpu,m.bus,1,clock);assert(n<100000,name);return m.cpu.a;}
 const map=['\0ZXCV','ASDFG','QWERT','12345','09876','POIUY','\rLKJH',' \0MNB'],sym={'.':'M','=':'L'};
 function type(s){for(let c of s){if(sym[c]){keys[7]&=~2;c=sym[c];}let done=false;for(let r=0;r<8;r++){const bit=map[r].indexOf(c);if(bit>=0){keys[r]&=~(1<<bit);frames(4);keys.fill(255);frames(4);done=true;break;}}assert(done,c);}}
 return {m,pico,frames,boot,call,type,log:()=>text};
}
const t=machine();t.boot();assert.match(t.log(),/HELLO from a \.COM/);assert.deepEqual(t.pico.image().subarray(0,disk.length),disk);assert.equal(t.pico.slot,4);assert.equal(t.m.portF4,15);
if(single){
 assert.equal(t.m.bus.read(symbols.disk_tracks),80);
 for(let lba=0;lba<1280;lba++){
  assert.equal(t.call('block_read',lba),0);
  assert.deepEqual(Buffer.from(Array.from({length:128},(_,i)=>t.m.bus.read(symbols.bounce+i))),disk.subarray(lba*128,lba*128+128));
 }
 assert.notEqual(t.call('block_read',1280),0);
 t.m.cpu.pc=symbols.warm;t.frames(200);
 t.type('PIP COPY.COM=HELLO.COM\r');t.frames(500);t.type('COPY\r');t.frames(200);
 assert.equal((t.log().match(/HELLO from a \.COM/g)||[]).length,2,t.log().slice(-1000));
 t.type('TPSAVE\r');t.frames(200);t.type('Y');
 for(let i=0;i<150&&!t.log().includes('Saved disk chunks');i++)t.frames(200);
 assert(t.log().includes('Saved disk chunks'),t.log().slice(-1000));assert.equal(t.pico.saved.size,21);
 const exported=Buffer.concat(Array.from({length:20},(_,i)=>t.pico.saved.get(`CPM${String(i).padStart(2,'0')}.TAP`).subarray(24,-1)));
 assert.deepEqual(exported,t.pico.image().subarray(0,163840));
 fs.writeFileSync('build/tspico-sram160-transcript.txt',t.log());
 console.log('160KB stock TAP preload: 20 pages, all 1280 sectors, geometry, CP/M copy/execute, 20-chunk export PASS');
 process.exit(0);
}
console.log('TAP loader: all 40 pages read, checksum checked, installed and verified; CP/M boots');
// A non-destructive pattern check over every logical record and bank boundary.
for(let lba=0;lba<2560;lba++){
 assert.equal(t.call('block_read',lba),0);
 assert.deepEqual(Buffer.from(Array.from({length:128},(_,i)=>t.m.bus.read(symbols.bounce+i))),disk.subarray(lba*128,lba*128+128));
 assert.equal(t.pico.slot,4);assert.equal(t.m.portF4,15);
}
for(const lba of [0,63,64,447,448,895,896,1343,1344,1791,1792,2239,2240,2559]){
 const pattern=Buffer.from(Array.from({length:128},(_,i)=>(lba+i*19)&255));pattern.forEach((v,i)=>t.m.bus.write(symbols.bounce+i,v));
 assert.equal(t.call('block_write',lba),0);assert.equal(t.call('block_read',lba),0);
 assert.deepEqual(Buffer.from(Array.from({length:128},(_,i)=>t.m.bus.read(symbols.bounce+i))),pattern);
 disk.subarray(lba*128,lba*128+128).forEach((v,i)=>t.m.bus.write(symbols.bounce+i,v));assert.equal(t.call('block_write',lba),0);
}
const commands=t.pico.commands.length;assert.notEqual(t.call('block_read',2560),0);assert.notEqual(t.call('block_write',65535),0);assert.notEqual(t.call('block_read',0,1),0);assert.equal(t.pico.commands.length,commands);
// Restore CCP execution after direct backend calls, then use native keyboard.
t.m.cpu.pc=symbols.warm;t.frames(200);
t.type('SUBMIT DEMO\r');t.frames(4000);assert(t.log().includes('Assembled on the TS2068!'),JSON.stringify({pc:t.m.cpu.pc.toString(16),slot:t.pico.slot,f4:t.m.portF4,tail:t.log().slice(-700),head:t.m.bus.read(symbols.qhead),tailq:t.m.bus.read(symbols.qtail)}));
fs.writeFileSync('build/tspico-sram-transcript.txt',t.log());
console.log('All 2560 sectors, pair boundaries, writes, invalid requests and SUBMIT/ASM/LOAD PASS');
if(JSON.parse(fs.readFileSync(dir+'/manifest.json')).with_infocom){
 for(const [command,title]of [['PLANET','PLANETFALL'],['ZORK1','ZORK I']]){
  t.type(command+'\r');t.frames(1800);assert(t.log().slice(-5000).includes(title),command+' boot');
  t.type('LOOK\r');t.frames(700);assert(t.log().slice(-2500).includes('>LOOK'),command+' LOOK');
  const before=t.log().length;t.type('SAVE\r');t.frames(300);t.type('\r');t.frames(900);t.type('\r');t.frames(900);
  assert(t.log().slice(before).includes('Ok.'),command+' SAVE '+JSON.stringify(t.log().slice(before).slice(-1600)));
  const restoring=t.log().length;t.type('RESTORE\r');t.frames(300);t.type('\r');t.frames(900);t.type('\r');t.frames(900);
  assert(t.log().slice(restoring).includes('Ok.'),command+' RESTORE');
  t.type('QUIT\r');t.frames(300);t.type('Y\r');t.frames(800);
 }
 console.log('Planetfall and Zork I: boot, LOOK, SAVE/RESTORE and return to CP/M PASS');
}
// Export through the actual utility and validate every saved TAP chunk.
t.type('TPSAVE\r');t.frames(200);t.type('Y');
for(let i=0;i<150&&!t.log().includes('Saved disk chunks');i++)t.frames(200);
assert(t.log().includes('Saved disk chunks'),JSON.stringify({pc:t.m.cpu.pc.toString(16),saved:t.pico.saved.size,phase:t.pico.phase,queue:t.pico.queue.slice(0,10),cmd:t.pico.commands.slice(-3),tail:t.log().slice(-200)}));assert.equal(t.pico.saved.size,41);
const exported=Buffer.concat(Array.from({length:40},(_,i)=>t.pico.saved.get(`CPM${String(i).padStart(2,'0')}.TAP`).subarray(24,-1)));
assert.deepEqual(exported,t.pico.image());
fs.writeFileSync('build/tspico-sram-after.img',t.pico.image());
const output='build/tspico-saved-chunks';fs.mkdirSync(output,{recursive:true});for(const [name,bytes]of t.pico.saved)fs.writeFileSync(path.join(output,name),bytes);
console.log('TPSAVE: all 40 binary-safe TAP chunks match current SRAM disk PASS');
for(const options of [{badBlock:5},{readOnlyPage:5},{missing:true}]){
 const bad=machine(options);bad.boot();assert.match(bad.log(),/failed. Do not boot./);assert.doesNotMatch(bad.log(),/HELLO from a \.COM/);
}
console.log('Bad TAP checksum, failed SRAM readback and missing image fail closed PASS');
