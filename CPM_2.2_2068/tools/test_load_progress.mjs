// Native Z80 execution against both protocol families, using one DCK.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {SramPicoModel,tapBlocks} from './tspico_sram_model.mjs';
const api=await import(pathToFileURL(path.resolve('../../TSRun/machine.js')));
const dir='build/profiles/tspico-dual',ram='build/profiles/tspico-ram';
const single=process.argv.includes('--single'),media=single?'build/dual-fixtures/stock160':dir;
const cart=fs.readFileSync(dir+'/ts2068-cpm.dck'),tap=fs.readFileSync(media+'/CPM320.TAP');
const image=fs.readFileSync(media+'/drive-a.img'),pages=image.length/8192;
const volumes=Object.fromEntries(Array.from({length:single?4:8},(_,i)=>[`/CPM/CPM3200${i}.TAP`,fs.readFileSync(media+`/CPM3200${i}.TAP`)]));
const map=['\0ZXCV','ASDFG','QWERT','12345','09876','POIUY','\rLKJH',' \0MNB'];
function machine(options){
 const keys=new Uint8Array(8).fill(255),m=api.createMachine(keys,new Uint8Array(2).fill(255));
 api.setHomeRom(m,fs.readFileSync('../../TSRun/roms/ts2068-0.rom'));api.setExRom(m,fs.readFileSync('../../TSRun/roms/ts2068-1.rom'));
 assert.equal(api.insertDock(m,cart),null);const pico=new SramPicoModel(m,cart,tap,{volumes,...options});
 const rd=m.bus.ioRead,wr=m.bus.ioWrite;m.bus.ioRead=p=>[14,15].includes(p&255)?pico.read(p):rd(p);
 m.bus.ioWrite=(p,v)=>[14,15].includes(p&255)?pico.write(p,v):wr(p,v);
 if(process.argv.includes('--video80')){
  const video=new Uint8Array(256);video[127]=0x42;let index=0;
  m.picovideoRegs=video;
  const pr=m.bus.ioRead,pw=m.bus.ioWrite;
  m.bus.ioRead=p=>p===0xbf3b?index:p===0xff3b?video[index]:pr(p);
  m.bus.ioWrite=(p,v)=>{if(p===0xbf3b)index=v;else if(p===0xff3b)video[index]=v;else pw(p,v);};
 }
 if(options.unavailable){
  m.bus.ioRead=p=>[14,15].includes(p&255)?255:rd(p);
  m.bus.ioWrite=(p,v)=>{if([14,15].includes(p&255)){assert.equal(p&255,14,'unknown device must not receive SYNC');}else wr(p,v);};
 }
 let text='';const write=m.bus.write;m.bus.write=(a,v)=>{if(a>=0xf800&&a<0xfe00)text+=String.fromCharCode(v);write(a,v);};
 function frames(n){for(let i=0;i<n;i++)api.runFrame(m);}
 function until(needle,max=600,from=0){for(let i=0;i<max&&!text.slice(from).includes(needle);i++)frames(100);assert(text.slice(from).includes(needle),JSON.stringify({needle,pc:m.cpu.pc.toString(16),tail:text.replaceAll('\0','').slice(-1500),commands:pico.commands.slice(-4)}));}
 function type(s){for(let c of s){if(c==='.'||c==='='){keys[7]&=~2;c=c==='.'?'M':'L';}let found=false;for(let r=0;r<8;r++){const bit=map[r].indexOf(c);if(bit>=0){keys[r]&=~(1<<bit);frames(4);keys.fill(255);frames(4);found=true;break;}}assert(found,c);}}
 return {m,pico,frames,until,type,log:()=>text};
}

for(const [label,options,choice] of [['legacy',{},null],['modern TAP',{modern:true},null],['snapshot',{modern:true,service:image},'R']]){const t=machine(options);if(choice){t.until('ENTER: persistent SD');t.type(choice);}t.until('Loading block 01 of '+pages);assert(!t.log().includes('HELLO from a .COM'));t.until('HELLO from a .COM');assert(t.log().includes('Loading block '+pages+' of '+pages));assert.deepEqual(t.pico.image().subarray(0,image.length),image);if(process.argv.includes('--video80'))assert(t.log().includes('PicoVideo 80 column mode enabled'));console.log(label+': first/final counter, disk integrity, startup notice PASS');}
