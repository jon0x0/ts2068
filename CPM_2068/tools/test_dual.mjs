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
for(const [label,options,choice] of [
 ['legacy SRAM',{},null],['modern TAP SRAM',{modern:true},null],
 ['modern SD',{modern:true,service:image},'\r'],['modern SD snapshot SRAM',{modern:true,service:image},'R']]){
 if(process.argv.includes('--modern-only')&&!options.modern)continue;
 if(process.argv.includes('--service-only')&&!options.service)continue;
 if(process.argv.includes('--sd-only')&&label!=='modern SD')continue;
 const t=machine(options);
 if(choice){t.until('ENTER: persistent SD');t.type(choice);}
 t.until('HELLO from a .COM');
 if(process.argv.includes('--video80'))assert.equal(t.m.bus.read(0xeff5),1);
 if(process.argv.includes('--video80')){
  t.type('COLOR 1\r');t.frames(200);assert.equal(t.m.picovideoRegs[7],2);assert.equal(t.m.picovideoRegs[8],0x90);
  t.type('COLOR 7\r');t.frames(200);
 }
 if(label==='modern SD'){
  assert.match(t.log(),/Modern protocol; persistent SD/);assert.equal(t.m.bus.read(0xeff4),0);
 }else{
  assert.match(t.log(),/run TPSAVE before power off/);assert.equal(t.m.bus.read(0xeff4),1);
  assert.match(t.log(),label.startsWith('legacy')?/Legacy FIFO protocol/:/Modern protocol; RAMDisk/);
  assert.deepEqual(t.pico.image().subarray(0,image.length),image);
 }
 const before=Buffer.from(t.pico.service||[]);
 t.type('PIP COPY.COM=HELLO.COM\r');t.frames(600);t.type('COPY\r');t.frames(250);
 assert.equal((t.log().match(/HELLO from a \.COM/g)||[]).length,2,t.log().slice(-1000));
 if(label==='modern SD'){
  assert.notDeepEqual(t.pico.service,before);
  t.type('TPSAVE\r');t.frames(200);assert.match(t.log(),/TPSAVE is for RAMDisk mode/);assert.equal(t.pico.saved.size,0);
  // Programs own the TPA. A cartridge restart must still find its BIOS in ROM.
  for(let address=0x1000;address<0x4000;address++)t.m.bus.write(address,0xa7);
  const restart=t.log().length;t.m.bus.ioWrite(0xf4,0x10);t.m.cpu.pc=0x8008;
  t.until('ENTER: persistent SD',600,restart);t.type('\r');t.until('HELLO from a .COM',600,restart);
  if(process.argv.includes('--games')){
   for(const [command,title] of [['PLANET','PLANETFALL'],['ZORK1','ZORK I']]){
    const start=t.log().length;t.type(command+'\r');t.until(title,600,start);
    t.frames(1800);
    assert.equal(t.m.bus.read(0x103),process.argv.includes('--video80')?79:63);
    t.type('LOOK\r');t.frames(700);assert(t.log().slice(start).includes('>LOOK'),t.log().slice(-2000));
    t.type('QUIT\r');t.frames(300);t.type('Y\r');t.frames(800);
   }
   console.log('Infocom dynamic 64/80-column configuration and LOOK PASS');
  }
 }
 else{
  if(options.service)assert.deepEqual(t.pico.service,before,'RAM writes leaked into SD');
  t.type('TPSAVE\r');t.frames(200);t.type('Y');t.until(options.modern?'Saved one disk TAP':'Saved disk chunks');
  assert.equal(t.pico.saved.size,options.modern?1:pages+1);
  const parts=options.modern?tapBlocks(t.pico.saved.get('CPMRAM.TAP')):null;
  const exported=Buffer.concat(Array.from({length:pages},(_,i)=>options.modern?parts[3+i*2].subarray(1,-1):t.pico.saved.get(`CPM${String(i).padStart(2,'0')}.TAP`).subarray(24,-1)));
  assert.deepEqual(exported,t.pico.image().subarray(0,image.length));
 }
 assert.equal(t.m.bus.read(0xeff3),options.modern?2:1);
 assert.deepEqual(Buffer.from(t.pico.ram.subarray(4*32768+4*8192,4*32768+5*8192)),cart.subarray(9+4*8192,9+5*8192),'immutable startup/BIOS page changed');
 if(!options.modern)assert.equal(t.pico.syncs,0);
 fs.writeFileSync('build/dual-'+(single?'160-':'320-')+label.replaceAll(' ','-')+'.txt',t.log());
 console.log(label+': selection, notice, CP/M copy/execute, persistence/export PASS');
}
const absent=machine({unavailable:true});absent.until('failed. Do not boot.');
assert.match(absent.log(),/RAMDisk diagnostic \(hex\): protocol=00 stage=01/);
assert.equal(absent.m.bus.read(0xeff3),0);assert.equal(absent.pico.commands.length,0);
console.log('Unknown/floating response: bounded failure, no modern SYNC PASS');
