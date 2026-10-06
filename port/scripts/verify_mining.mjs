// Execute assembled Z80 against independent integer models of the cited 6809.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const upstream=path.resolve(root,'../../../TSRun');
const {createZ80,runZ80}=await import(pathToFileURL(path.join(upstream,'z80.js')));
const api=await import(pathToFileURL(path.join(upstream,'machine.js')));
const integrated=process.argv.includes('--integrated');
const read=n=>fs.readFileSync(path.join(root,integrated?({'build/symbols.txt':'build/mining-symbols.txt','build/bank4.bin':'build/mining-bank4.bin','build/sinistar-port-kernel.dck':'build/sinistar-mining.dck'}[n]||n):n));
const symbols=Object.fromEntries([...read('build/symbols.txt').toString().matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const memory=new Uint8Array(65536); memory.set(read('build/bank4.bin'),0x8000);
const cpu=createZ80(), clock={tstates:0,stepAdded:0};
let writes=0,cases=0;
const bus={read:a=>memory[a],write:(a,v)=>{assert.ok((a>=0x7f00&&a<0x8000)||(a>=0x7900&&a<0x7908),`Unexpected routine write ${a.toString(16)}`);memory[a]=v;writes++;},ioRead:()=>255,ioWrite:()=>{throw Error('Kernel routine performed I/O');}};
const signed=x=>(x<<16)>>16;
const put=(hi,lo,n)=>{cpu[hi]=(n>>8)&255;cpu[lo]=n&255;};
const hl=()=>signed(cpu.h*256+cpu.l);
const timing={};
function invoke(name){
 cpu.pc=symbols[name];cpu.sp=0x7ffd;cpu.halted=false;
 memory[0x7ffd]=0;memory[0x7ffe]=1; // sentinel return address $0100
 const start=clock.tstates;
 let steps=0;
 while(cpu.pc!==0x100){assert.ok(++steps<1000,`Nontermination ${name}`);runZ80(cpu,bus,1,clock);}
 assert.equal(cpu.sp,0x7fff);
 timing[name]=Math.max(timing[name]||0,clock.tstates-start);cases++;
}
for(let mass=0;mass<256;mass++)for(let richter=0;richter<256;richter++){
 cpu.a=richter;cpu.b=mass;invoke('rock_add_vibration');
 const inverse=[255,128,85,64,51,43,37,32,28,26,23,21,20,18,17][Math.max(1,mass>>4)-1];
 assert.equal(cpu.a,(richter>=96&&richter<128)?richter:(richter+(inverse>>2))&255);
}
for(let richter=0;richter<256;richter++)for(let random=0;random<256;random++)for(const sini of [0,1]){
 const mass=(richter*17+random)&255;
 cpu.a=richter;cpu.b=mass;cpu.c=random;cpu.d=sini;invoke('rock_try_crystal');
 const released=!sini&&richter>16&&random<=richter-16;
 assert.equal(cpu.f&1,Number(released));assert.equal(cpu.a,released?richter>>1:richter);
 assert.equal(cpu.b,released?Math.max(0,mass-8):mass);
}
for(let richter=0;richter<256;richter++)for(const screen of [0,1]){
 cpu.a=richter;cpu.c=screen;invoke('rock_damp');
 const damped=(richter-2)&255;const event=damped>=128?1:screen&&damped>=96?2:0;
 assert.equal(cpu.b,event);assert.equal(cpu.a,event?0:damped);
}
const report={dck_sha256:createHash('sha256').update(read('build/sinistar-port-kernel.dck')).digest('hex'),cases,max_tstates:timing};
fs.writeFileSync(path.join(root,integrated?'build/mining-integrated-rules.json':'build/mining-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(report);
