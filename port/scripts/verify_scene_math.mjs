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
const read=n=>fs.readFileSync(path.join(root,n));
const symbols=Object.fromEntries([...read('build/scene-symbols.txt').toString().matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const memory=new Uint8Array(65536); const rom=read('build/sinistar-pursuit.bin');let hsr=16;
const cpu=createZ80(), clock={tstates:0,stepAdded:0};
let writes=0,cases=0;
const bus={read:a=>hsr&(1<<(a>>13))?rom[a]:memory[a],write:(a,v)=>{assert.ok(a>=0x7f00&&a<0x8000);memory[a]=v;writes++;},ioRead:()=>255,ioWrite:(port,value)=>{assert.equal(port&255,0xf4);hsr=value;}};
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
const table=[[32767,2047,5],[4000,4096,4],[1024,128,1],[600,320,5],[80,256,3],[64,192,4],[32,128,4],[16,96,3],[0,64,2]];
for(let distance=-512;distance<512;distance++){
 put('h','l',distance);invoke('scene_velocity');
 const magnitude=table.find(r=>Math.abs(distance)>=r[0])[1];
 assert.equal(hl(),distance<0?magnitude:-magnitude);
 assert.equal(cpu.a,table.find(r=>magnitude>=r[1])[2]);assert.equal(hsr,16);
}
for(let current=0;current<256;current++)for(let target=0;target<256;target++){
 cpu.a=current;cpu.b=target;cpu.c=127;invoke('scene_turn');
 const delta=((target-current)<<24)>>24;
 assert.equal(cpu.a,(current+Math.floor((delta*127+128)/256))&255);
}
for(let bits=0;bits<65536;bits++){
 const current=signed(bits*29),diff=signed(bits),desired=signed(current+diff);
 put('h','l',desired);put('d','e',current);cpu.c=127;invoke('player_accelerate');
 const product=signed(Math.floor(diff*127/256));
 assert.equal(hl(),signed(current+Math.floor((product+4)/8)));
}
const report={dck_sha256:createHash('sha256').update(read('build/sinistar-pursuit.dck')).digest('hex'),cases,max_tstates:timing};
fs.writeFileSync(path.join(root,'build/scene-math-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(report);
