// Exercise FORMAT through the native CCP/BDOS/BIOS, checking actual disk bytes.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {SramPicoModel,tapBlocks} from './tspico_sram_model.mjs';
const api=await import(pathToFileURL(path.resolve('../../TSRun/machine.js')));
const single=process.argv.includes('--single'),dir='build/profiles/tspico-dual';
const media=single?'build/dual-fixtures/stock160':dir;
const cart=fs.readFileSync(dir+'/ts2068-cpm.dck'),disk=fs.readFileSync(media+'/drive-a.img'),tap=fs.readFileSync(media+'/CPM320.TAP');
const count=disk.length/8192;
const seed=Object.fromEntries(Array.from({length:single?4:8},(_,i)=>[`/CPM/CPM3200${i}.TAP`,fs.readFileSync(media+`/CPM3200${i}.TAP`)]));
const map=['\0ZXCV','ASDFG','QWERT','12345','09876','POIUY','\rLKJH',' \0MNB'];
function machine(options={},volumes=seed){
 const keys=new Uint8Array(8).fill(255),m=api.createMachine(keys,new Uint8Array(2).fill(255));
 api.setHomeRom(m,fs.readFileSync('../../TSRun/roms/ts2068-0.rom'));api.setExRom(m,fs.readFileSync('../../TSRun/roms/ts2068-1.rom'));
 assert.equal(api.insertDock(m,cart),null);const pico=new SramPicoModel(m,cart,tap,{volumes,...options});
 const rd=m.bus.ioRead,wr=m.bus.ioWrite;m.bus.ioRead=p=>[14,15].includes(p&255)?pico.read(p):rd(p);
 m.bus.ioWrite=(p,v)=>[14,15].includes(p&255)?pico.write(p,v):wr(p,v);
 let text='';const write=m.bus.write;m.bus.write=(a,v)=>{if(a>=0xf800&&a<0xfe00)text+=String.fromCharCode(v);write(a,v);};
 function frames(n){for(let i=0;i<n;i++)api.runFrame(m);}
 function until(needle,max=800){for(let i=0;i<max&&!text.includes(needle);i++)frames(100);assert(text.includes(needle),JSON.stringify({needle,pc:m.cpu.pc.toString(16),tail:text.replaceAll('\0','').slice(-1200),cmd:pico.commands.slice(-6)}));}
 function type(s){for(let c of s){if(c==='.'||c==='='){keys[7]&=~2;c=c==='.'?'M':'L';}let found=false;for(let r=0;r<8;r++){const bit=map[r].indexOf(c);if(bit>=0){keys[r]&=~(1<<bit);frames(4);keys.fill(255);frames(4);found=true;break;}}assert(found,c);}}
 function boot(choice){if(options.service){until('L: reload saved RAMDisk');type(choice||'R');}until('HELLO from a .COM');}
 return {m,pico,frames,until,type,boot,log:()=>text};
}

for(const [name,options,choice] of [['legacy RAM',{},null],['modern RAM',{modern:true},null],['modern SD',{modern:true,service:disk},'\r']]){
 const t=machine(options);t.boot(choice);
 const bytes=()=>options.service?t.pico.service:t.pico.image().subarray(0,disk.length);
 const original=Buffer.from(bytes());
 t.type('FORMAT B\r');t.until('Drive unavailable. Nothing formatted.');assert.deepEqual(bytes(),original);
 t.type('FORMAT\r');t.until('FORMAT A: initializes');assert.deepEqual(bytes(),original);
 t.type('FORMAT A\r');t.until('Type Y to format:');t.type('N');t.until('Cancelled.');t.frames(300);assert.deepEqual(bytes(),original);
 t.type('FORMAT A\r');t.frames(100);t.type('Y');t.until('Disk initialized and directory verified.');
 t.frames(300);
 if(options.service){
  assert.deepEqual(bytes().subarray(0,4096),Buffer.alloc(4096,0xe5));
  assert.deepEqual(bytes().subarray(4096),original.subarray(4096),'format overwrote file payload/system area');
 }else{
  assert.equal(bytes().subarray(1,12).toString(),'TPSAVE  COM');
  assert.deepEqual(bytes().subarray(32,4096),Buffer.alloc(4096-32,0xe5));
  const saver=fs.readFileSync('build/profiles/tspico-ram/files/TPSAVE.COM');
  assert.deepEqual(bytes().subarray(4096,4096+saver.length),saver);
 }
 t.type('DIR\r');t.frames(100);assert(t.log().includes(options.service?'NO FILE':'TPSAVE'),t.log().slice(-1000));
 // BDOS must rebuild allocation state, then create and reload a new file.
 t.type('SAVE 1 NEW.COM\r');t.frames(200);t.type('DIR\r');t.frames(100);
 assert.match(t.log(),/NEW\s+COM/);
 assert(!bytes().subarray(0,32).every(v=>v===0xe5));
 console.log(`${name} ${disk.length/1024}KB: unavailable drive, usage, cancellation, format, readback and create PASS`);
}
