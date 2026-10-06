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
const bus={read:a=>hsr&(1<<(a>>13))?rom[a]:memory[a],write:(a,v)=>{assert.ok((a>=0x7f00&&a<0x8000)||(a>=0x7894&&a<0x7898)||(a>=0x78a0&&a<=0x78a3));memory[a]=v;writes++;},ioRead:()=>255,ioWrite:(port,value)=>{assert.equal(port&255,0xf4);hsr=value;}};
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
const word=(a,v)=>{memory[a]=v&255;memory[a+1]=v>>8;};
const get=a=>memory[a]+256*memory[a+1];
for(const entry of ['sini_stop_check','sini_stop_step'])
for(let timer=0;timer<256;timer++)for(const grave of [0,1,255])for(const attract of [0,1,255])for(const screen of [0,1]){
 memory.set([timer,grave,attract,screen],0x78a0);
 word(symbols.svx,0x8123);word(symbols.svy,0x7ffe);
 invoke(entry);
 const remaining=entry==='sini_stop_step'?Math.max(0,timer-1):timer;
 const stop=remaining!==0||((grave!==0||attract!==0)&&screen!==0);
 assert.equal(memory[0x78a0],remaining);assert.equal(cpu.f&1,Number(stop));
 assert.equal(get(symbols.svx),stop?0:0x8123);assert.equal(get(symbols.svy),stop?0:0x7ffe);
 assert.deepEqual([...memory.subarray(0x78a1,0x78a4)],[grave,attract,screen]);
}
const report={dck_sha256:createHash('sha256').update(read('build/sinistar-pursuit.dck')).digest('hex'),cases,max_tstates:timing};
fs.writeFileSync(path.join(root,'build/scene-stop-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(report);
