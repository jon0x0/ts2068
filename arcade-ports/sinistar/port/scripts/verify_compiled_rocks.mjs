import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
function fixture(dir){
 const cart=fs.readFileSync(path.join(dir,'sinistar-mining.dck')),rom=cart.subarray(9);
 const symbols=Object.fromEntries([...fs.readFileSync(path.join(dir,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)]));
 const word=a=>rom[a]|rom[a+1]<<8;
 return {cart,run(phase,row,seed){
  const ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
  const bus={read:a=>(a>>13)===2?rom[a]:ram[a],write:(a,v)=>{assert.ok((a>>13)!==2);ram[a]=v;},ioRead:()=>255,ioWrite:()=>assert.fail('no ports in compiled row')};
  for(let n=0;n<5;n++){ram[0xa020+n]=(seed*37+n*61)&255;ram[0xc020+n]=(seed*13+n*17)&127;}
  cpu.pc=word(word(symbols.rock_programs+phase*2)+row*2);cpu.h=0xa0;cpu.l=0x20;cpu.d=0xc0;cpu.e=0x20;cpu.sp=0x7ffd;ram[0x7ffe]=1;
  for(let n=0;cpu.pc!==0x100;n++){assert.ok(n<300);runZ80(cpu,bus,1,clock);}
  assert.equal(cpu.sp,0x7fff);
  return {pixels:[...ram.slice(0xa020,0xa025),...ram.slice(0xc020,0xc025)],t:clock.tstates};
 }};
}
const old=fixture(path.join(root,'revisions/playable-attract-scores-v30/build')),current=fixture(path.join(root,'build'));
let cases=0,oldT=0,newT=0,maxExtra=0;
for(let phase=0;phase<8;phase++)for(let row=0;row<28;row++)for(let seed=0;seed<4;seed++){
 const a=old.run(phase,row,seed),b=current.run(phase,row,seed);
 assert.deepEqual(b.pixels,a.pixels,`phase ${phase}, row ${row}, background ${seed}`);
 oldT+=a.t;newT+=b.t;maxExtra=Math.max(maxExtra,b.t-a.t);cases++;
}
const result={dck_sha256:createHash('sha256').update(current.cart).digest('hex'),cases,exactPixels:true,oldT,newT,maxExtraTstatesPerRow:maxExtra,averageExtraTstatesPerRock:(newT-oldT)/cases*28};
fs.writeFileSync(path.join(root,'build/frontend-compiled-rocks-verification.json'),JSON.stringify(result,null,2));console.log(result);
