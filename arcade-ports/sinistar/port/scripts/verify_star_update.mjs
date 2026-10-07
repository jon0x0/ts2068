import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
function machine(build){
 const cart=fs.readFileSync(path.join(build,'sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
 const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
 let mapping=0x50;const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;}};
 return {ram,sym,cart,cpu,clock,call(label,map=0x50){mapping=map;cpu.pc=sym[label];cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;for(let i=0;cpu.pc!==0x100;i++){assert.ok(i<100000);runZ80(cpu,bus,1,clock);}}};
}
const old=machine(path.join(root,'revisions/playable-register-render-v51/build')),now=machine(path.join(root,'build'));
let cases=0,oldT=0,newT=0,smallOld=0,smallNew=0,smallCases=0;
for(let dy=0;dy<512;dy++)for(let sample=0;sample<12;sample++){
 const priorX=(sample*47)&511,nextX=(priorX+dy*13)&511,priorY=(sample*97)&511,nextY=(priorY-dy)&511;
 const results=[];
 for(const m of [old,now]){
  m.ram.fill(0);m.ram[m.sym.game_mode]=1;m.ram[0x5892]=sample!==11?1:0;
  for(const [a,v] of [[0x5884,nextX],[0x5886,nextY],[0x5888,priorX],[0x588a,priorY]]){m.ram[a]=v&255;m.ram[a+1]=v>>8;}
  for(let i=0;i<10;i++){m.ram[0x58c0+2*i]=(sample*29+i*23)&255;m.ram[0x58c1+2*i]=(sample*10+i)%112;}
  const start=m.clock.tstates;m.call('wb_stars_update',0x50);const t=m.clock.tstates-start;
  if(m===old)oldT+=t;else newT+=t;
  if(dy<5||dy>507){if(m===old)smallOld+=t;else{smallNew+=t;smallCases++;}}
  results.push([...m.ram.slice(0x58c0,0x58e8),...m.ram.slice(0x5888,0x588c),m.ram[0x5892]]);
 }
 assert.deepEqual(results[1],results[0],`stars dy=${dy} sample=${sample}`);cases++;
}
const report={dck_sha256:createHash('sha256').update(now.cart).digest('hex'),baseline:'playable-register-render-v51',cases,exact:true,all512WrappedYDisplacements:true,all112StarRows:true,initialization:true,averageTstates:{before:oldT/cases,after:newT/cases},smallScrollTstates:{before:smallOld/smallCases,after:smallNew/smallCases}};
fs.writeFileSync(path.join(root,'build/star-update-verification.json'),JSON.stringify(report,null,2));console.log(report);
