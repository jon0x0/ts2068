import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
function machine(build){
 const cart=fs.readFileSync(path.join(build,'sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
 const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
 let mapping=0x50;const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;}};
 return {ram,sym,cart,cpu,clock,call(label,map=0x50){mapping=map;cpu.pc=sym[label];cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;for(let i=0;cpu.pc!==0x100;i++){assert.ok(i<100000);runZ80(cpu,bus,1,clock);}}};
}
const baseline=path.join(root,'revisions/playable-register-render-v51/build'),current=path.join(root,'build'),old=machine(baseline),now=machine(current);
old.helper=fs.readFileSync(path.join(baseline,'home-render.bin'));now.helper=fs.readFileSync(path.join(current,'home-render.bin'));old.sym.hp_prepare=now.sym.hp_prepare=0xa690;
const records=[...Array.from({length:8},(_,i)=>0x79b0+i*10),...Array.from({length:8},(_,i)=>0x7db0+i*10),0x58b4];
let seed=52,oldT=0,newT=0;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed>>>24;};
for(let test=0;test<256;test++){
 const initial=new Uint8Array(65536),word=(a,v)=>{initial[a]=v&255;initial[a+1]=v>>8;};
 const cx=rand()*2,cy=rand()*2;word(0x5884,cx);word(0x5886,cy);
 for(const p of records){word(p,rand()*2);word(p+2,rand()*2);initial[p+7]=rand()<40?0:96;}
 for(const [start,length] of [[0xbc80,153],[0x5b00,153],[0x7d00,64],[0x7f40,4]])for(let i=0;i<length;i++)initial[start+i]=rand();
 initial[0x5bcd]=test&1;initial[old.sym.game_mode]=1;initial.set([7,80,5,28],old.sym.rects);initial.set([0,0,5,0],0x7cd0);
 const results=[];
 for(const m of [old,now]){
  m.ram.set(initial);m.ram.set(m.helper,0xa690);const t=m.clock.tstates;m.call('hp_prepare',0x50);if(m===old)oldT+=m.clock.tstates-t;else newT+=m.clock.tstates-t;
  results.push([...m.ram.slice(0xbc80,0xbd19),...m.ram.slice(0x5b00,0x5bb1),...m.ram.slice(0x5bca,0x5bcf),...m.ram.slice(m.sym.rects,m.sym.rects+4),...m.ram.slice(0x7cd0,0x7cd4)]);
 }
 assert.deepEqual(results[1],results[0],`population cache ${test}`);
}
const report={dck_sha256:createHash('sha256').update(now.cart).digest('hex'),baseline:'playable-register-render-v51',cases:256,exact:true,averageTstates:{before:oldT/256,after:newT/256},reductionPercent:(1-newT/oldT)*100};
fs.writeFileSync(path.join(root,'build/population-cache-verification.json'),JSON.stringify(report,null,2));console.log(report);
