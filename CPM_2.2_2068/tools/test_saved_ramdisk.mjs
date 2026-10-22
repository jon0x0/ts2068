// Save on the TS2068, remove power, and reload the exact disk without a PC repack.
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
for(const [name,options,split] of [['legacy',{},false],['modern',{modern:true},false],['modern-split',{modern:true},true],['modern-service',{modern:true,service:disk},false]]){
 const t=machine(options);t.boot();t.type('PIP COPY.COM=HELLO.COM\r');t.frames(500);t.type('COPY\r');t.frames(200);
 assert.equal((t.log().match(/HELLO from a \.COM/g)||[]).length,2);
 const updated=t.pico.image().subarray(0,disk.length);
 t.type(split?'TPSAVE SPLIT\r':'TPSAVE\r');t.frames(200);t.type('Y');
 const one=options.modern&&!split;
 t.until(one?'Saved one disk TAP':'Saved disk chunks');
 if(one){
  assert.equal(t.pico.saved.size,1);const blocks=tapBlocks(t.pico.saved.get('CPMRAM.TAP'));
  assert.equal(blocks.length,2+count*2);
  for(const block of blocks)assert.equal(block.reduce((a,b)=>a^b,0),0);
  assert.deepEqual(Buffer.concat(Array.from({length:count},(_,i)=>blocks[3+i*2].subarray(1,-1))),updated);
 }else{
  assert.equal(t.pico.saved.size,count+1);assert(t.pico.saved.has('CPMSTATE.TAP'));
 }
 const reloaded=machine(options,t.pico.volumes);reloaded.boot('L');
 assert.deepEqual(reloaded.pico.image().subarray(0,disk.length),updated);
 assert.equal(reloaded.m.bus.read(0xeff6),one?2:1);
 reloaded.type('COPY\r');reloaded.frames(200);assert.equal((reloaded.log().match(/HELLO from a \.COM/g)||[]).length,2);
 console.log(`${name} ${disk.length/1024}KB: save -> fresh-machine reload -> execute changed disk, no repack PASS`);
 if(!one&&name==='legacy'){
  // Old exports remain loadable, with an on-machine size choice.
  const old={...t.pico.volumes};delete old['/CPM/SAVE/CPMSTATE.TAP'];
  const untyped=machine({},old);untyped.until('Saved chunks found (old format)');untyped.type(single?'1':'2');untyped.until('HELLO from a .COM');
  assert.deepEqual(untyped.pico.image().subarray(0,disk.length),updated);
  // Missing pages, incomplete saves and valid-TAP but mixed page data must stop.
  for(const fault of ['missing','incomplete','mixed']){
   const broken={...t.pico.volumes};const page=`/CPM/SAVE/CPM${String(count-1).padStart(2,'0')}.TAP`;
   if(fault==='missing')delete broken[page];
   else if(fault==='mixed'){const data=Buffer.from(broken[page]);data[24]^=1;data[data.length-1]^=1;broken[page]=data;}
   else{const key='/CPM/SAVE/CPMSTATE.TAP',data=Buffer.from(broken[key]);data[32]=0;data[data.length-1]^=1;broken[key]=data;}
   const bad=machine({},broken);bad.until('failed. Do not boot.');assert(!bad.log().includes('HELLO from a .COM'),fault);
  }
  console.log('Old export direct load; missing, incomplete and mixed save refusal PASS');
 }
 const output=`build/saved-roundtrip-${disk.length/1024}-${name}`;fs.mkdirSync(output,{recursive:true});
 for(const [filename,data] of t.pico.saved)fs.writeFileSync(path.join(output,filename),data);
 fs.writeFileSync(path.join(output,'expected.img'),updated);
}
