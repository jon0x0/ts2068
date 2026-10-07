import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
function machine(build){
 const cart=fs.readFileSync(path.join(build,'sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
 const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
 let mapping=0x50;const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;}};
 return {ram,sym,cart,cpu,clock,call(label,map=0x50){mapping=map;cpu.pc=sym[label];cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;for(let i=0;cpu.pc!==0x100;i++){assert.ok(i<100000);runZ80(cpu,bus,1,clock);}}};
}
const old=machine(path.join(root,'revisions/playable-death-response-v46/build')),now=machine(path.join(root,'build'));
let seed=812;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed>>>24;};const timing=[];
for(let phase=0;phase<8;phase++){
 let oldT=0,newT=0;
 for(let test=0;test<32;test++){
  const indices=Uint8Array.from({length:78},()=>rand()&31),dict=Uint8Array.from({length:96},rand);
  for(let i=2;i<96;i+=3)dict[i]=[1,2,6,7][rand()&3];
  for(const m of [old,now]){m.ram.set(indices,0xa800);m.ram.set(dict,0xa900);m.cpu.h=0xa8;m.cpu.l=0;m.cpu.d=0xa9;m.cpu.e=0;m.cpu.c=phase;const t=m.clock.tstates;m.call('explosion_unpack',0x10);if(m===old)oldT+=m.clock.tstates-t;else newT+=m.clock.tstates-t;}
  assert.deepEqual(now.ram.slice(0xb800,0xb938),old.ram.slice(0xb800,0xb938),`phase ${phase}, sample ${test}`);
 }
 timing.push({phase,oldT:oldT/32,newT:newT/32,reductionPercent:(1-newT/oldT)*100});
}
const report={dck_sha256:createHash('sha256').update(now.cart).digest('hex'),cases:256,byteExact:true,romWrites:0,timing};fs.writeFileSync(path.join(root,'build/explosion-speed-verification.json'),JSON.stringify(report,null,2));console.log(report);
