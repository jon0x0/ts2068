import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
function machine(build){
 const cart=fs.readFileSync(path.join(build,'sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
 const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
 let mapping=0x50;const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;}};
 return {ram,sym,cart,cpu,clock,call(label,map=0x50){mapping=map;cpu.pc=sym[label];cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;for(let i=0;cpu.pc!==0x100;i++){assert.ok(i<100000);runZ80(cpu,bus,1,clock);}}};
}
const old=machine(path.join(root,'revisions/playable-collision-gate-v50/build')),now=machine(path.join(root,'build'));
let seed=48;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed>>>24;};
const off=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;
let oldT=0,newT=0,records=0;
for(let test=0;test<128;test++){
 const mem=new Uint8Array(65536),expected=new Map();
 mem[0x78f6]=test&1;mem.set([8,15,80,132],0x5800);
 for(let y=64;y<176;y++){
  let left=rand()%32,right=Math.min(32,left+1+rand()%32);
  if(y%5===0){left=32;right=0;} // empty rows
  if(y%7===0){left=0;right=32;} // low-byte underflow / full width
  mem[0x7900+y]=left;mem[0x7d00+y]=right;
  for(let x=0;x<32;x++)for(const base of [0x4000,0x6000]){
   const a=base+off(x,y),shadow=a+0x6000,v=rand();mem[a]=v;mem[shadow]=rand()<12?rand():v;
   const excluded=mem[0x78f6]&&y>=80&&y<132&&x>=8&&x<15;
   if(x>=left&&x<right&&!excluded&&v!==mem[shadow])expected.set(a,mem[shadow]);
  }
 }
 for(const m of [old,now]){
  m.ram.set(mem);const before=m.clock.tstates;m.call('compile_stream',0x10);
  if(m===old)oldT+=m.clock.tstates-before;else newT+=m.clock.tstates-before;
  const start=m.ram[0x7bb2]|m.ram[0x7bb3]<<8,got=new Map();
  for(let p=start;p<0xfffe;p+=4){const a=m.ram[p+2]|m.ram[p+3]<<8;assert.ok(!got.has(a));got.set(a,m.ram[p+1]);}
  assert.deepEqual(got,expected,`changed-byte records case ${test}`);
 }
 records+=expected.size;
}
const report={dck_sha256:createHash('sha256').update(now.cart).digest('hex'),baseline:"playable-collision-gate-v50",cases:128,records,exact:true,oldTstates:oldT/128,newTstates:newT/128,reductionPercent:(1-newT/oldT)*100};
fs.writeFileSync(path.join(root,'build/dirty-stream-verification.json'),JSON.stringify(report,null,2));console.log(report);
