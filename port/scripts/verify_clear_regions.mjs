import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
function machine(build){
 const cart=fs.readFileSync(path.join(build,'sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
 const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
 let mapping=0x50;const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;}};
 return {ram,sym,cart,cpu,clock,call(label,map=0x50){mapping=map;cpu.pc=sym[label];cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;for(let i=0;cpu.pc!==0x100;i++){assert.ok(i<100000);runZ80(cpu,bus,1,clock);}}};
}
const old=machine(path.join(root,'revisions/playable-shared-preparation-v52/build')),now=machine(path.join(root,'build'));
const off=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;
let seed=53,oldT=0,newT=0;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed>>>24;};
for(let test=0;test<512;test++){
 const w=1+test%7,h=1+rand()%52,x=rand()%(33-w),y=64+rand()%(113-h),initial=new Uint8Array(65536);
 for(const start of [0xa000,0xc000])for(let i=0;i<6144;i++)initial[start+i]=rand();
 for(let r=64;r<176;r++){initial[0x7900+r]=rand()%33;initial[0x7d00+r]=rand()%33;}
 const expected=initial.slice();
 for(let r=y;r<y+h;r++){expected[0x7900+r]=Math.min(expected[0x7900+r],x);expected[0x7d00+r]=Math.max(expected[0x7d00+r],x+w);for(let c=x;c<x+w;c++){expected[0xa000+off(c,r)]=0;expected[0xc000+off(c,r)]=7;}}
 for(const m of [old,now]){
  m.ram.set(initial);m.ram.set([x,y,w,h],0x5800);m.ram[0x7be0]=0xc3;m.cpu.yh=0x58;m.cpu.yl=0;m.cpu.xh=0x12;m.cpu.xl=0x34;
  const t=m.clock.tstates;m.call('clear_plain',0x10);if(m===old)oldT+=m.clock.tstates-t;else newT+=m.clock.tstates-t;
  for(const [a,b] of [[0xa000,0xb800],[0xc000,0xd800],[0x7940,0x79b0],[0x7d40,0x7db0]])assert.deepEqual(m.ram.slice(a,b),expected.slice(a,b),`clear ${test}`);
  assert.equal((m.cpu.xh<<8)|m.cpu.xl,0x1234);assert.equal((m.cpu.yh<<8)|m.cpu.yl,0x5800);
 }
}
const report={dck_sha256:createHash('sha256').update(now.cart).digest('hex'),cases:512,exact:true,averageTstates:{before:oldT/512,after:newT/512},reductionPercent:(1-newT/oldT)*100};fs.writeFileSync(path.join(root,'build/clear-regions-verification.json'),JSON.stringify(report,null,2));console.log(report);
