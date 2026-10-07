import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
function machine(build){
 const cart=fs.readFileSync(path.join(build,'sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
 const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
 let mapping=0x50;const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;}};
 return {ram,sym,cart,cpu,clock,call(label,map=0x50){mapping=map;cpu.pc=sym[label];cpu.sp=0xbffd;ram[0xbffd]=0;ram[0xbffe]=1;for(let i=0;cpu.pc!==0x100;i++){assert.ok(i<100000);runZ80(cpu,bus,1,clock);}}};
}
const old=machine(path.join(root,'revisions/playable-hidden-face-v54/build')),now=machine(path.join(root,'build'));let oldT=0,newT=0,cases=0;
for(let glyph=0;glyph<37;glyph++)for(let phase=0;phase<8;phase++)for(const color of [2,6,7]){
 const result=[];
 for(const m of [old,now]){
  m.ram.fill(0);m.ram.fill(7,0x6000,0x7800);m.ram[0x5e7e]=color;m.cpu.a=glyph;m.cpu.b=72;m.cpu.c=80+phase;
  const t=m.clock.tstates;m.call('front_char',0x98);if(m===old)oldT+=m.clock.tstates-t;else newT+=m.clock.tstates-t;
  result.push([...m.ram.slice(0x4000,0x5800),...m.ram.slice(0x6000,0x7800)]);
 }
 assert.deepEqual(result[1],result[0],`glyph ${glyph} phase ${phase} color ${color}`);cases++;
}
const report={dck_sha256:createHash('sha256').update(now.cart).digest('hex'),cases,exact:true,averageTstates:{before:oldT/cases,after:newT/cases},reductionPercent:(1-newT/oldT)*100};fs.writeFileSync(path.join(root,'build/text-cell-verification.json'),JSON.stringify(report,null,2));console.log(report);
