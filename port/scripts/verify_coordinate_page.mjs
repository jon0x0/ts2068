import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
function machine(build){
 const cart=fs.readFileSync(path.join(build,'sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
 const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
 let mapping=0x50;const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;}};
 return {ram,sym,cart,cpu,clock,call(label,map=0x50){mapping=map;cpu.pc=sym[label];cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;for(let i=0;cpu.pc!==0x100;i++){assert.ok(i<100000);runZ80(cpu,bus,1,clock);}}};
}
const old=machine(path.join(root,'revisions/playable-black-text-v55/build')),now=machine(path.join(root,'build'));
const names=['rock_x','rock_y','cx','cy','bx','by','px','py','worker_x','worker_y','face_x','face_y','bs_x','bs_y'];
const coord=names.map((n,i)=>old.sym[n]+([2,3,4,5,6,7,10,11].includes(i)?1:0)).concat([0x783c,0x783d]);
let seed=56,oldT=0,newT=0;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed>>>24;};
for(let test=0;test<512;test++){
 const state=new Uint8Array(65536);state[old.sym.game_mode]=1;
 for(let i=0;i<16;i++){state[coord[i]]=rand();state[0x7c90+i]=rand()&1;}
 state[0x586e]=rand()&1;state[0x586f]=rand()&1;
 for(const a of [0x5884,0x5886]){state[a]=rand();state[a+1]=rand()&1;}
 const outputs=[];
 for(const m of [old,now]){
  m.ram.set(state);let t=m.clock.tstates;m.call('wb_project',0x50);const projected=[...coord.map(a=>m.ram[a]),...m.ram.slice(0x7c90,0x7cc0),m.ram[0x586e],m.ram[0x586f]];
  m.call('wb_restore',0x50);if(m===old)oldT+=m.clock.tstates-t;else newT+=m.clock.tstates-t;
  for(const a of coord)assert.equal(m.ram[a],state[a]);assert.equal(m.ram[0x586e],state[0x586e]);assert.equal(m.ram[0x586f],state[0x586f]);
  const gets=[];for(let axis=0;axis<16;axis++){m.cpu.a=axis;m.call('wb_get',0x50);gets.push(m.cpu.h,m.cpu.l,m.cpu.d,m.cpu.e);}outputs.push([...projected,...gets]);
 }
 assert.deepEqual(outputs[1],outputs[0]);
}
const report={dck_sha256:createHash('sha256').update(now.cart).digest('hex'),cases:512,getCases:8192,exact:true,projectionRestoreTstates:{before:oldT/512,after:newT/512}};
fs.writeFileSync(path.join(root,'build/coordinate-page-verification.json'),JSON.stringify(report,null,2));console.log(report);
