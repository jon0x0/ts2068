import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
function machine(build){
 const cart=fs.readFileSync(path.join(build,'sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
 const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
 let mapping=0x50;const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;}};
 return {ram,sym,cart,cpu,clock,call(label,map=0x50,end=0x100){mapping=map;cpu.pc=sym[label];cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;for(let i=0;cpu.pc!==end;i++){assert.ok(i<100000);runZ80(cpu,bus,1,clock);}}};
}
const old=machine(path.join(root,'revisions/playable-lean-rock-loops-v53/build')),now=machine(path.join(root,'build'));
let cases=0,rows=[];
for(let mouth=0;mouth<3;mouth++)for(let phase=0;phase<8;phase++)for(let eye=0;eye<3;eye++){
 const timing=[];
 for(const m of [old,now]){
  m.ram.fill(0);m.ram[m.sym.game_mode]=1;m.ram[m.sym.sinistar_built]=1;m.ram[m.sym.awake_done]=1;m.ram[m.sym.awake_mouth]=mouth;m.ram[m.sym.eye_phase]=eye;m.ram[m.sym.face_x+1]=phase;m.ram[m.sym.rects+22]=0;m.ram[m.sym.rects+23]=52;m.ram[0x78df]=0x10;
  const t=m.clock.tstates;m.call('mr_awake_image',0x10,m.sym.mr_after_piece);timing.push(m.clock.tstates-t);
  assert.ok(m.ram.slice(0x4000,0x5800).every(x=>!x));assert.ok(m.ram.slice(0x6000,0x7800).every(x=>!x));
  assert.equal(m.ram[m.sym.awake_mouth],mouth);assert.equal(m.ram[m.sym.eye_phase],eye);assert.equal(m.ram[0x78df],0x10);
 }
 rows.push({mouth,phase,eye,before:timing[0],after:timing[1]});cases++;
}
const report={dck_sha256:createHash('sha256').update(now.cart).digest('hex'),cases,noScreenWrites:true,animationStatePreserved:true,rows};fs.writeFileSync(path.join(root,'build/hidden-face-verification.json'),JSON.stringify(report,null,2));console.log({cases,shiftedSpeechBefore:rows.filter(x=>x.mouth&&x.phase).reduce((s,x)=>s+x.before,0)/42,after:rows[0].after});
