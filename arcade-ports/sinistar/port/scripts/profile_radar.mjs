import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
let mapping=0x50,attributes=[];
const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0,'no ROM writes');ram[a]=v;if(a>=0x6000&&a<0x7800)attributes.push([a,v]);},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;}};
function call(label,map=0x50){mapping=map;cpu.pc=sym[label];assert.ok(cpu.pc,label);cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;const t=clock.tstates;for(let n=0;cpu.pc!==0x100;n++){assert.ok(n<100000,label);runZ80(cpu,bus,1,clock);}return clock.tstates-t;}
const word=(a,v)=>{ram[a]=v&255;ram[a+1]=v>>8;};const set=(n,v)=>ram[sym[n]]=v;
const records=[...Array.from({length:8},(_,i)=>0x79b0+i*10),...Array.from({length:8},(_,i)=>0x7db0+i*10),0x58b4];
set('game_mode',1);set('rock_alive',1);set('rock_x',180);set('rock_y',120);set('worker_alive',1);set('worker_x',150);set('worker_y',140);set('assembly_count',12);word(sym.face_x,200*256);word(sym.face_y,80*256);
for(let i=0;i<17;i++){word(records[i],(i*37+15)&511);word(records[i]+2,(i*53+70)&511);ram[records[i]+7]=1;}
function update(){ram[0x7802]=(ram[0x5867]+24)&255;const prepare=call('radar_step',0x10),bytes=ram[0x5868],publish=call('radar_publish',0x10);return {prepare,publish,total:prepare+publish,bytes};}
const initial=update();update();const still=update(),moving=[];
for(let i=1;i<=128;i++){const x=(i*7)&511,y=(i*3)&511;word(sym.px,(x&255)*256);word(sym.py,(y&255)*256);ram[0x7c96]=x>>8;ram[0x7c97]=y>>8;word(0x5884,(x-100)&511);word(0x5886,(y-110)&511);moving.push(update());}
const mean=k=>moving.reduce((n,v)=>n+v[k],0)/moving.length;
const meanT=mean('total');
const rates=[24,12,8,6].map(ticks=>({ticks,hz:60.1145/ticks,cpuPercent:meanT*(60.1145/ticks)/3528000*100,extraCpuPoints:meanT*(60.1145/ticks-60.1145/24)/3528000*100}));
// Actual end-screen drawing must use normal white on normal black throughout.
set('game_status',2);ram[0x5897]=0;attributes=[];call('wb_end_screen');assert.equal(attributes.length,168);assert.ok(attributes.every(([,v])=>v===7));
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),conditions:'Native Z80 instruction cycles; 18 planetoids, worker, partial Sinistar, 128 camera/player positions. Includes radar_step bank calls and queued publication. Excludes contention/interrupts and any extra main-render scheduling delay.',initial,still,moving:{meanPrepareT:mean('prepare'),meanPublishT:mean('publish'),meanTotalT:meanT,meanMs:meanT/3528,minT:Math.min(...moving.map(v=>v.total)),maxT:Math.max(...moving.map(v=>v.total)),meanChangedBytes:mean('bytes')},rates,gameOver:{attributeWrites:attributes.length,allNormalBlack:true}};
fs.writeFileSync(path.join(root,'build/radar-cost-verification.json'),JSON.stringify(report,null,2));console.log(report);
