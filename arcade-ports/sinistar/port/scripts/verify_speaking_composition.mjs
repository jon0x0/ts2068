import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
function machine(build){
 const cart=fs.readFileSync(path.join(build,'sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
 const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
 let mapping=0x50;const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;}};
 return {ram,sym,cart,cpu,clock,call(label,map=0x50){mapping=map;cpu.pc=sym[label];cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;for(let i=0;cpu.pc!==0x100;i++){assert.ok(i<100000);runZ80(cpu,bus,1,clock);}}};
}
const old=machine(path.join(root,'revisions/playable-fast-speaking-v57/build')),now=machine(path.join(root,'build'));
let seed=58;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed>>>24;};
let cases=0,before=0,after=0;
for(let eye=0;eye<3;eye++)for(let mouth=0;mouth<3;mouth++)for(let phase=1;phase<8;phase++){
 now.ram.fill(0);now.ram[0x78df]=0x50;now.ram[now.sym.eye_phase]=eye;
 const rom=now.cart.subarray(9),entry=now.sym.sprites+(308+eye*3+mouth)*3;
 now.cpu.e=rom[entry+1];now.cpu.d=rom[entry+2];now.cpu.a=phase;now.call('wb_awake_shift');
 const pose=now.ram.slice(0xb800,0xbc44);
 for(let row=0;row<52;row++)for(let col=0;col<7;col++)assert.equal(pose[row*21+col*3],col===0?(255<<(8-phase))&255:0,`mask ${eye}/${mouth}/${phase}/${row}/${col}`);
 for(let left=0;left<7;left++)for(const top of [0,17,51]){
  const width=7-left,height=52-top,data=[];
  for(let row=top;row<52;row++)data.push(...pose.slice(row*21+left*3,row*21+21));
  const bg=Uint8Array.from({length:6144},rand),attrs=Uint8Array.from({length:6144},rand);
  for(const m of [old,now]){
   m.ram.fill(0);m.ram.set(bg,0xa000);m.ram.set(attrs,0xc000);m.ram.set(pose,0xb800);
   m.ram.set([8+left,80+top,width,height],m.sym.rects+20);
   m.ram.set([top,left,7,52],0x7ce4);m.ram[m.sym.game_mode]=1;
   m.ram[m.sym.rects+23]=height;m.cpu.l=5;m.cpu.a=height;m.cpu.e=width;m.cpu.b=80+top;m.cpu.c=8+left;
   const t=m.clock.tstates;m.call(m===old?'scene_sprite':'scene_sinistar',0x10);
   if(m===old)before+=m.clock.tstates-t;else after+=m.clock.tstates-t;
  }
  assert.deepEqual(now.ram.slice(0xa000,0xb800),old.ram.slice(0xa000,0xb800));
  assert.deepEqual(now.ram.slice(0xc000,0xd800),old.ram.slice(0xc000,0xd800));cases++;
 }
}
const report={dck_sha256:createHash('sha256').update(now.cart).digest('hex'),cases,exact:true,before_tstates:before,after_tstates:after,saving_percent:100*(1-after/before)};
fs.writeFileSync(path.join(root,'build/speaking-composition-verification.json'),JSON.stringify(report,null,2));console.log(report);
