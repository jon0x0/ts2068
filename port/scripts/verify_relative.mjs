// Execute relocated Z80 drawing streams against independently composed sprite planes.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const upstream=path.resolve(root,'../../../TSRun');
const {createZ80,runZ80}=await import(pathToFileURL(path.join(upstream,'z80.js')));
const api=await import(pathToFileURL(path.join(upstream,'machine.js')));
const read=n=>fs.readFileSync(path.join(root,n));
const symbols=Object.fromEntries([...read('build/scene-symbols.txt').toString().matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const memory=new Uint8Array(65536); const rom=read('build/sinistar-pursuit.bin');let hsr=16;
const cpu=createZ80(), clock={tstates:0,stepAdded:0};
let writes=0,cases=0;
const bus={read:a=>hsr&(1<<(a>>13))?rom[a]:memory[a],write:(a,v)=>{assert.ok(!(hsr&(1<<(a>>13))),`ROM write ${a.toString(16)}`);memory[a]=v;writes++;},ioRead:()=>255,ioWrite:(port,value)=>{assert.equal(port&255,0xf4);hsr=value;}};
const signed=x=>(x<<16)>>16;
const put=(hi,lo,n)=>{cpu[hi]=(n>>8)&255;cpu[lo]=n&255;};
const hl=()=>signed(cpu.h*256+cpu.l);
const timing={};
function invoke(name){
 cpu.pc=symbols[name];cpu.sp=0x7ffd;cpu.halted=false;
 memory[0x7ffd]=0;memory[0x7ffe]=1; // sentinel return address $0100
 const start=clock.tstates;
 let steps=0;
 while(cpu.pc!==0x100){assert.ok(++steps<30000,`Nontermination ${name}`);runZ80(cpu,bus,1,clock);}
 assert.equal(cpu.sp,0x7fff);
 timing[name]=Math.max(timing[name]||0,clock.tstates-start);cases++;
}
memory.set(rom.subarray(0x6000,0x8000),0xe000);
memory.set(rom.subarray(0x6b00,0x71c0),0xb940);
memory.set(rom.subarray(0x71c0,0x79c0),0xd800);
memory[0x7b80]=0xc3;
const faces=Array.from({length:8},(_,p)=>fs.readFileSync(path.join(root,`../assets/face-00-${p}.bin`)));
const off=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;
const w=(a,v)=>{memory[a]=v&255;memory[a+1]=v>>8;};
function picture(x,y){
 const bitmap=new Uint8Array(6144),attr=new Uint8Array(6144).fill(7),data=faces[x&7];
 for(let r=0;r<52;r++)for(let c=0;c<7;c++){
  const i=(r*7+c)*3,o=off((x>>3)+c,y+r);
  if(data[i]!==255){bitmap[o]=data[i+1];attr[o]=data[i+2];}
 }
 return {bitmap,attr};
}
function runAt(address,stack=0x7ffd){
 cpu.pc=address;cpu.sp=stack;cpu.halted=false;memory[0x7ffd]=0;memory[0x7ffe]=1;
 let steps=0;while(cpu.pc!==0x100){assert.ok(++steps<30000);runZ80(cpu,bus,1,clock);}
 assert.equal(cpu.sp,0x7fff);
}
let transitions=0,fastTotal=0,baselineTotal=0,fastMax=0,baselineMax=0;
const covered=new Set();
for(const xb of [1,7,16,24])for(const y of [40,55,63,64,120,131])for(let phase=0;phase<8;phase++)for(const dy of [-1,0,1])for(const dx of [-1,0,1]){
 const x=xb*8+phase,nx=x+dx,ny=y+dy;if(nx<0||nx>=200||ny<40||ny>=133)continue;
 const old=picture(x,y),next=picture(nx,ny);
 memory.set(next.bitmap,0xa000);memory.set(next.attr,0xc000);
 memory.set([xb,y,7],symbols.oldface);memory.set([nx>>3,ny,7],symbols.newface);
 memory[symbols.sx+1]=nx+24;memory[0x78ee]=phase;
 memory.set([Math.min(xb,nx>>3),Math.max(xb,nx>>3)+7,Math.min(y,ny),Math.max(y,ny)+52],0x78e0);
 invoke('select_relative_transition');assert.equal(cpu.a,1);assert.equal(memory[0x78ed],1);
 for(const fast of [false,true]){
  invoke('select_relative_transition');
  memory.set(old.bitmap,0x4000);memory.set(old.attr,0x6000);
  const begin=clock.tstates;
  put('h2','l2',0xf000);put('yh','yl',0x78e0);
  invoke(fast?'relative_face_attributes':'separated_color_box');
  const colorEnd=cpu.h2*256+cpu.l2;memory[colorEnd]=0xc9;runAt(0xf000);
  assert.deepEqual(memory.subarray(0x6000,0x7800),next.attr,`color ${x},${y},${dx},${dy}`);
  // Re-select restores the bitmap row origin consumed by the previous execution.
  invoke('select_relative_transition');memory[0x78ed]=fast?1:0;
  put('h2','l2',0xeb00);put('yh','yl',0x78e0);
  invoke(fast?'relative_bitmap_list':'separated_box');
  const end=cpu.h2*256+cpu.l2;w(end,0x7c80);
  memory.set([0x31,0xfd,0x7f,0xc9],0x7c80);memory[0x7c90]=0xc9;
  runAt(0x7c90,0xeb00);
  assert.deepEqual(memory.subarray(0x4000,0x5800),next.bitmap,`bitmap ${x},${y},${dx},${dy}`);
  const duration=clock.tstates-begin;
  if(fast){fastTotal+=duration;fastMax=Math.max(fastMax,duration);}else{baselineTotal+=duration;baselineMax=Math.max(baselineMax,duration);}
 }
 covered.add(`${phase},${dx},${dy}`);transitions++;
}
assert.equal(covered.size,72);assert.ok(fastTotal<baselineTotal);
const report={dck_sha256:createHash('sha256').update(read('build/sinistar-pursuit.dck')).digest('hex'),relocation_cases:transitions,transitions:covered.size,average_fast_tstates:fastTotal/transitions,average_previous_tstates:baselineTotal/transitions,average_reduction_percent:100*(1-fastTotal/baselineTotal),max_fast_tstates:fastMax,max_previous_tstates:baselineMax};
fs.writeFileSync(path.join(root,'build/relative-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(report);
