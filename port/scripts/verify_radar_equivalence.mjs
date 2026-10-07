import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
function machine(build){
 const cart=fs.readFileSync(path.join(build,'sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
 const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
 let mapping=0x50;const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;}};
 return {ram,sym,cart,call(label,map=0x50){mapping=map;cpu.pc=sym[label];cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;for(let i=0;cpu.pc!==0x100;i++){assert.ok(i<100000);runZ80(cpu,bus,1,clock);}}};
}
const old=machine(path.join(root,'revisions/playable-gameover-black-v44/build')),now=machine(path.join(root,'build'));
const records=[...Array.from({length:8},(_,i)=>0x79b0+i*10),...Array.from({length:8},(_,i)=>0x7db0+i*10),0x58b4];
let seed=914;function rand(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed>>>16;}
for(let test=0;test<1024;test++){
 const values=Array.from({length:100},rand);
 for(const m of [old,now]){
  const put=(a,v)=>{m.ram[a]=v&255;m.ram[a+1]=v>>8;},set=(n,v)=>m.ram[m.sym[n]]=v;
  // Exhaust all 64 x 16 radar origins, with varying player low/high bits.
  const px=values[0]&511,py=values[1]&511;
  put(m.sym.px,(px&255)*256);put(m.sym.py,(py&255)*256);m.ram[0x7c96]=px>>8;m.ram[0x7c97]=py>>8;
  put(0x5884,(px+((test&63)-32)*8)&511);put(0x5886,(py+((test>>6)-8)*32-64)&511);
  set('rock_alive',test%2);set('rock_x',values[2]);set('rock_y',values[3]);m.ram[0x586e]=values[4]&1;m.ram[0x586f]=values[5]&1;
  set('worker_alive',test%3);set('worker_x',values[6]);set('worker_y',values[7]);m.ram[0x7c98]=values[8]&1;m.ram[0x7c99]=values[9]&1;
  set('assembly_count',test%21);set('bs_hits',test%14);put(m.sym.face_x,(values[10]&255)*256);put(m.sym.face_y,(values[11]&255)*256);m.ram[0x7c9a]=values[12]&1;m.ram[0x7c9b]=values[13]&1;
  for(let i=0;i<17;i++){put(records[i],values[14+i*3]&511);put(records[i]+2,values[15+i*3]&511);m.ram[records[i]+7]=values[16+i*3]&1;}
  m.call('radar_entry');
 }
 assert.deepEqual(now.ram.slice(0x7e00,0x7f00),old.ram.slice(0x7e00,0x7f00),`staging scene ${test}`);
 assert.equal(now.ram[0x5868],old.ram[0x5868]);
 assert.deepEqual(now.ram.slice(0xe000,0xe000+now.ram[0x5868]*3),old.ram.slice(0xe000,0xe000+old.ram[0x5868]*3),`queue scene ${test}`);
 for(const m of [old,now])m.call('radar_publish',0x10);
 assert.deepEqual(now.ram.slice(0x4000,0x5800),old.ram.slice(0x4000,0x5800));
 assert.deepEqual(now.ram.slice(0x6000,0x7800),old.ram.slice(0x6000,0x7800));
}
const report={dck_sha256:createHash('sha256').update(now.cart).digest('hex'),baseline:'v44',scenes:1024,allRadarOrigins:true,stagingQueueAndPublishedBytesIdentical:true,romWrites:0};
fs.writeFileSync(path.join(root,'build/radar-equivalence-verification.json'),JSON.stringify(report,null,2));console.log(report);
