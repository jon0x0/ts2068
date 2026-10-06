import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),{createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const cpu=createZ80(),clock={tstates:0,stepAdded:0};let mapping=16,key=255;const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0);ram[a]=v;},ioRead:()=>key,ioWrite(p,v){assert.equal(p&255,0xf4);mapping=v;}};
function invoke(n,map=16){mapping=map;ram[0x78df]=map;cpu.pc=sym[n];cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;cpu.halted=false;for(let i=0;cpu.pc!==0x100;i++){assert.ok(i<30000,n);runZ80(cpu,bus,1,clock);}assert.equal(mapping,map);assert.equal(cpu.sp,0x7fff);}
const records=[...Array.from({length:8},(_,i)=>0x79b0+i*10),...Array.from({length:8},(_,i)=>0x7db0+i*10),0x58b4];
ram[sym.game_mode]=1;ram[0x5893]=1;ram[sym.awake_done]=1;ram[sym.rock_alive]=1;ram[sym.mass]=91;ram[sym.rects+2]=5;
records.forEach((p,i)=>{ram[p+7]=80+i;ram[0xbc82+9*i]=i<2?5:0;});
invoke('mode_filter',0x94);assert.equal(ram[0x5bb2],0);assert.equal(records.filter(p=>ram[p+7]).length,17);
key=247;invoke('mode_filter',0x94);assert.equal(ram[0x5bb1],1);assert.equal(ram[0x5bb2],1);assert.equal(records.filter(p=>ram[p+7]).length,1);assert.equal(ram[sym.rock_alive],1);
invoke('mode_filter',0x94);assert.equal(ram[0x5bb1],1,'held F toggles only once');
ram[sym.rects+2]=0;ram[0xbc82]=0;invoke('mode_filter',0x94);assert.equal(ram[sym.rock_alive],0);assert.equal(ram[records[0]+7],0);assert.equal(ram[records[1]+7],0);
// Simulated projections returning to view cannot resurrect retired masses.
ram[sym.rects+2]=5;records.forEach((p,i)=>ram[0xbc82+9*i]=5);invoke('mode_filter',0x94);assert.equal(ram[sym.rock_alive],0);assert.equal(records.filter(p=>ram[p+7]).length,0);
// Actual population physics must not replenish any hidden slot.
for(let t=0;t<384;t++)invoke('world_step');assert.equal(records.filter(p=>ram[p+7]).length,0);
ram[sym.rock_alive]=1;invoke('rock_next_velocity');assert.equal(ram[sym.rock_alive],0,'primary regeneration suppressed');
key=255;invoke('mode_filter',0x94);key=247;invoke('mode_filter',0x94);assert.equal(ram[0x5bb1],0);assert.equal(ram[0x5bb2],0);assert.equal(ram[sym.mass],91);assert.equal(ram[sym.rock_alive],1);records.forEach((p,i)=>assert.equal(ram[p+7],80+i));
// Chase ending restores retired rocks without requiring another key press.
key=255;invoke('mode_filter',0x94);key=247;ram[sym.rects+2]=0;records.forEach((p,i)=>ram[0xbc82+9*i]=0);invoke('mode_filter',0x94);assert.equal(records.filter(p=>ram[p+7]).length,0);ram[sym.game_status]=1;invoke('mode_filter',0x94);assert.equal(records.filter(p=>ram[p+7]).length,17);assert.equal(ram[0x5bb2],0);
// Before the chase, cap visible population but retain hidden world objects.
ram[sym.game_status]=0;ram[sym.awake_done]=0;ram[sym.rects+2]=5;records.forEach((p,i)=>ram[0xbc82+9*i]=i<5?5:0);invoke('mode_filter',0x94);
assert.equal(ram[0x5bc9],2);assert.equal(records.filter((p,i)=>ram[0xbc82+9*i]).length,1);assert.equal(records.filter(p=>ram[p+7]).length,13);
// Native notice is drawn, survives briefly, then clears on the refresh timer.
const off=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;
const band=()=>Array.from({length:7},(_,y)=>Array.from(ram.slice(0x4000+off(9,52+y),0x4000+off(9,52+y)+13))).flat();
assert.ok(band().some(v=>v));ram[0x7802]=89;invoke('mode_filter',0x94);assert.ok(band().some(v=>v));ram[0x7802]=90;invoke('mode_filter',0x94);assert.ok(band().every(v=>v===0));for(let y=52;y<59;y++)for(let x=9;x<22;x++)assert.equal(ram[0x6000+off(x,y)],7,'notice restores black background');
// Repeated pre-awakening culls must refill, not exhaust the construction supply.
assert.equal(ram[0x5bb2],0,'no refill suppression before awake');
for(let cycle=0;cycle<6;cycle++){
 for(let t=0;t<384;t++)invoke('world_step');
 assert.ok(records.every(p=>ram[p+7]>0),'all culled/depleted secondary slots refill');
 records.forEach((p,i)=>ram[0xbc82+9*i]=5);ram[sym.rects+2]=5;invoke('mode_filter',0x94);
 assert.equal(records.filter(p=>ram[p+7]>0).length,1,'two visible slots including primary');
 assert.ok(Array.from(ram.slice(0x5bb5,0x5bc6)).every(x=>x===0),'recycled slots are not chase-retired');
}
ram[sym.rock_alive]=1;invoke('rock_next_velocity');assert.equal(ram[sym.rock_alive],1,'primary mine replacement is allowed before awakening');
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),preChaseRefillCycles:6,primaryMineReplenishes:true,defaultOff:true,keyEdgeToggle:true,visibleLimit:2,nativeNoticeExpiresAt90Ticks:true,preChaseHiddenRocksRetained:true,offscreenRocksRetired:true,noReentry:true,refillSuppressedTicks:384,primaryRegenerationSuppressed:true,toggleAndChaseEndRestore:true};fs.writeFileSync(path.join(root,'build/fast-mode-verification.json'),JSON.stringify(report,null,2));console.log(report);
