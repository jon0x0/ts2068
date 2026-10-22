// Modern 320KB image service: native Z80 CP/M with modeled TPI wire protocol.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {PicoModel} from './tspico_model.mjs';
const api=await import(pathToFileURL(path.resolve('../../TSRun/machine.js')));
const {runZ80}=await import(pathToFileURL(path.resolve('../../TSRun/z80.js')));
const dir='build/profiles/tspico-sd';
const disk=fs.readFileSync(dir+'/drive-a.img'),cart=fs.readFileSync(dir+'/ts2068-cpm.dck');
const symbols=Object.fromEntries([...fs.readFileSync(dir+'/bios.bin.sym','utf8').matchAll(/^(\w+): EQU 0x([\da-f]+)/gmi)].map(x=>[x[1],parseInt(x[2],16)]));
function machine(mode,image=disk){
 const keys=new Uint8Array(8).fill(255),m=api.createMachine(keys,new Uint8Array(2).fill(255));
 api.setHomeRom(m,fs.readFileSync('../../TSRun/roms/ts2068-0.rom'));api.setExRom(m,fs.readFileSync('../../TSRun/roms/ts2068-1.rom'));assert.equal(api.insertDock(m,cart),null);
 m.exCart.fill(null);m.exCartRam.fill(false);m.dockRam.fill(true);
 const pico=new PicoModel(image,{mode}),rd=m.bus.ioRead,wr=m.bus.ioWrite;
 m.bus.ioRead=p=>[14,15].includes(p&255)?pico.read(p):rd(p);
 m.bus.ioWrite=(p,v)=>[14,15].includes(p&255)?pico.write(p,v):wr(p,v);
 let text='';const write=m.bus.write;m.bus.write=(a,v)=>{if(a>=0xf800&&a<0xfe00)text+=String.fromCharCode(v);write(a,v);};
 const frames=n=>{for(let i=0;i<n;i++)api.runFrame(m);};
 const map=['\0ZXCV','ASDFG','QWERT','12345','09876','POIUY','\rLKJH',' \0MNB'];
 function type(s){for(const c of s){let done=false;for(let r=0;r<8;r++){const b=map[r].indexOf(c);if(b>=0){keys[r]&=~(1<<b);frames(4);keys.fill(255);frames(4);done=true;break;}}assert(done,c);}}
 function call(name,lba,drive=0){m.cpu.pc=symbols[name];m.cpu.h=lba>>8;m.cpu.l=lba&255;m.cpu.c=drive;m.cpu.sp=0xfefe;m.bus.write(0xfefe,0);m.bus.write(0xfeff,0xf7);const clock={tstates:0};let n=0;while(m.cpu.pc!==0xf700&&n++<100000)runZ80(m.cpu,m.bus,1,clock);assert(n<100000);return m.cpu.a;}
 return {m,pico,frames,type,call,log:()=>text};
}
for(const mode of ['absent','legacy','busy','stale','stock','badcrc']){
 const t=machine(mode);t.frames(500);assert.match(t.log(),/No usable disk/);assert.doesNotMatch(t.log(),/HELLO from/);
 if(['legacy','busy'].includes(mode)){assert.equal(t.pico.syncs,0);assert.equal(t.pico.writes.length,0);}
}
if(fs.existsSync('build/dual-fixtures/stock160/drive-a.img')){
 const small=machine('service',fs.readFileSync('build/dual-fixtures/stock160/drive-a.img'));
 small.frames(500);assert.match(small.log(),/HELLO from a \.COM/);
 assert.equal(small.m.bus.read(symbols.disk_tracks),80);
 console.log('Modern cartridge cold boot with 160KB service geometry PASS');
}
const live=machine('service');live.frames(500);assert.match(live.log(),/HELLO from a \.COM/);assert.equal(live.m.bus.read(symbols.storage_kind),1);
for(let lba=0;lba<2560;lba++){
 assert.equal(live.call('block_read',lba),0);
 assert.deepEqual(Buffer.from(Array.from({length:128},(_,i)=>live.m.bus.read(symbols.bounce+i))),disk.subarray(lba*128,lba*128+128));
}
for(const lba of [0,1,511,512,2047,2048,2559]){
 const pattern=Buffer.from(Array.from({length:128},(_,i)=>(lba+i*17)&255));
 pattern.forEach((v,i)=>live.m.bus.write(symbols.bounce+i,v));assert.equal(live.call('block_write',lba),0);assert.equal(live.call('block_read',lba),0);
 assert.deepEqual(live.pico.image.subarray(lba*128,lba*128+128),pattern);
 disk.subarray(lba*128,lba*128+128).forEach((v,i)=>live.m.bus.write(symbols.bounce+i,v));assert.equal(live.call('block_write',lba),0);
}
const count=live.pico.commands.length;assert.notEqual(live.call('block_read',2560),0);assert.notEqual(live.call('block_write',0,1),0);assert.equal(live.pico.commands.length,count);
live.m.cpu.pc=symbols.warm;live.frames(200);live.type('SUBMIT DEMO\r');live.frames(3500);assert.match(live.log(),/Assembled on the TS2068!/);
fs.writeFileSync('build/tspico-sd320-transcript.txt',live.log());
if(JSON.parse(fs.readFileSync(dir+'/manifest.json')).with_infocom){
 for(const [command,title]of [['PLANET','PLANETFALL'],['ZORK1','ZORK I']]){
  live.type(command+'\r');live.frames(1800);assert(live.log().slice(-5000).includes(title),command+' boot');
  live.type('LOOK\r');live.frames(700);assert(live.log().slice(-2500).includes('>LOOK'),command+' LOOK');
  for(const action of ['SAVE','RESTORE']){
   const before=live.log().length;live.type(action+'\r');live.frames(300);live.type('\r');live.frames(900);live.type('\r');live.frames(900);
   assert(live.log().slice(before).includes('Ok.'),command+' '+action);
  }
  live.type('QUIT\r');live.frames(300);live.type('Y\r');live.frames(800);
 }
 console.log('Modern SD: Planetfall and Zork I boot, LOOK, SAVE/RESTORE and exit PASS');
}
console.log('Modern 320KB: capability checks, absent/legacy/stock rejection, all 2560 sectors, binary writes, SUBMIT/ASM/LOAD PASS');
