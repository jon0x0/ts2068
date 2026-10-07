import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
function machine(build){
 const cart=fs.readFileSync(path.join(build,'sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
 const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
 let mapping=0x50;const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;}};
 return {ram,sym,cart,cpu,clock,call(label,map=0x50){mapping=map;cpu.pc=sym[label];cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;for(let i=0;cpu.pc!==0x100;i++){assert.ok(i<100000);runZ80(cpu,bus,1,clock);}}};
}
const old=machine(path.join(root,'revisions/playable-longer-shots-v56/build')),now=machine(path.join(root,'build'));let seed=57;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed>>>24;};const timing=[];
for(let phase=0;phase<8;phase++){
 let before=0,after=0;
 for(let sample=0;sample<32;sample++){
  const data=Uint8Array.from({length:1092},rand);for(let i=2;i<data.length;i+=3)data[i]=[1,2,6,7][rand()&3];
  for(const m of [old,now]){m.ram.fill(0);m.ram.set(data,0xb800);m.ram[0x78df]=0x50;m.cpu.a=phase;const t=m.clock.tstates;m.call('wb_shift_assembly',0x50);if(m===old)before+=m.clock.tstates-t;else after+=m.clock.tstates-t;assert.equal(m.ram[0x78df],0x50);}
  assert.deepEqual(now.ram.slice(0xb800,0xbc44),old.ram.slice(0xb800,0xbc44),`mouth shift ${phase}/${sample}`);
 }
 timing.push({phase,before:before/32,after:after/32});
}
const poses=[];
for(let eye=0;eye<3;eye++)for(let mouth=0;mouth<3;mouth++)for(let phase=1;phase<8;phase++){
 const costs=[];
 for(const m of [old,now]){
  m.ram.fill(0);m.ram[0x78df]=0x50;m.ram[m.sym.eye_phase]=eye;
  const rom=m.cart.subarray(9),entry=m.sym.sprites+(308+eye*3+mouth)*3;
  m.cpu.e=rom[entry+1];m.cpu.d=rom[entry+2];m.cpu.a=phase;
  const t=m.clock.tstates;m.call('wb_awake_shift');costs.push(m.clock.tstates-t);
 }
 assert.deepEqual(now.ram.slice(0xb800,0xbc44),old.ram.slice(0xb800,0xbc44),`pose ${eye}/${mouth}/${phase}`);
 poses.push({eye,mouth,phase,before:costs[0],after:costs[1]});
}
const report={dck_sha256:createHash('sha256').update(now.cart).digest('hex'),cases:256,pose_cases:63,exact:true,timing,poses};fs.writeFileSync(path.join(root,'build/mouth-shift-verification.json'),JSON.stringify(report,null,2));console.log(report);
