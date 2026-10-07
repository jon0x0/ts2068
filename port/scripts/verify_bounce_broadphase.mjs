import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
function machine(build){
 const cart=fs.readFileSync(path.join(build,'sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
 const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
 let mapping=0x50;const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;}};
 return {ram,sym,cart,cpu,clock,call(label,map=0x50){mapping=map;cpu.pc=sym[label];cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;for(let i=0;cpu.pc!==0x100;i++){assert.ok(i<100000);runZ80(cpu,bus,1,clock);}}};
}
const old=machine(path.join(root,'revisions/playable-clipped-rocks-v49/build')),now=machine(path.join(root,'build'));
let seed=50,cases=0,oldT=0,newT=0,farOld=0,farNew=0,farCount=0;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed>>>16;};
for(let dx=0;dx<512;dx++)for(let sample=0;sample<16;sample++){
 const rx=sample&1?508:100,ry=sample&2?510:100,px=(rx+dx)&511,dy=[0,7,17,25,26,511,500,256][sample&7],py=(ry+dy)&511,vx=(rand()%1201)-600,vy=(rand()%1201)-600;
 const result=[];
 for(const m of [old,now]){
  m.ram.fill(0);m.ram[0x78df]=0x50;m.ram[m.sym.px+1]=px&255;m.ram[0x7c96]=px>>8;m.ram[m.sym.py+1]=py&255;m.ram[0x7c97]=py>>8;
  m.ram[m.sym.pvx]=vx&255;m.ram[m.sym.pvx+1]=(vx>>8)&255;m.ram[m.sym.pvy]=vy&255;m.ram[m.sym.pvy+1]=(vy>>8)&255;
  m.ram[0x5c25]=sample===14?4:0;m.ram[0x5c2b]=sample===15?1:0;
  m.cpu.h=rx>>8;m.cpu.l=rx&255;m.cpu.d=ry>>8;m.cpu.e=ry&255;m.cpu.a=2*(sample%9);m.cpu.ix=0x79b0;
  const t=m.clock.tstates;m.call('wb_bounce_call',0x50);const elapsed=m.clock.tstates-t;
  if(m===old)oldT+=elapsed;else newT+=elapsed;
  if(((dx+10)&255)>=34){if(m===old)farOld+=elapsed;else{farNew+=elapsed;farCount++;}}
  result.push([m.ram[m.sym.pvx],m.ram[m.sym.pvx+1],m.ram[m.sym.pvy],m.ram[m.sym.pvy+1],m.ram[0x5c25],m.ram[0x78df],m.cpu.ix]);
 }
 assert.deepEqual(result[1],result[0],`collision state dx=${dx},sample=${sample}`);cases++;
}
const report={dck_sha256:createHash('sha256').update(now.cart).digest('hex'),cases,exact:true,wrappedCoordinates:true,bounceDisabledAndRecovery:true,averageTstates:{before:oldT/cases,after:newT/cases},farRejectionTstates:{before:farOld/farCount,after:farNew/farCount},reductionPercent:(1-newT/oldT)*100};
fs.writeFileSync(path.join(root,'build/bounce-broadphase-verification.json'),JSON.stringify(report,null,2));console.log(report);
