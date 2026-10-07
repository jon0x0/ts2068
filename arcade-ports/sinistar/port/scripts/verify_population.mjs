import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),{createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const cpu=createZ80(),clock={tstates:0,stepAdded:0};let mapping=16;const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){assert.equal(p&255,0xf4);mapping=v;}};
function invoke(n){cpu.pc=sym[n];cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;cpu.halted=false;for(let i=0;cpu.pc!==0x100;i++){assert.ok(i<30000,n);runZ80(cpu,bus,1,clock);}assert.equal(mapping,16);assert.equal(cpu.sp,0x7fff);}
const records=[...Array.from({length:8},(_,i)=>0x79b0+i*10),...Array.from({length:8},(_,i)=>0x7db0+i*10),0x58b4];const put=(a,v)=>{ram[a]=v;ram[a+1]=v>>8;},word=a=>ram[a]|ram[a+1]<<8;
const source=fs.readFileSync(path.join(root,'reference/original/SAM/SAMTABLE.SRC'),'utf8').split('SCIVELT\tFCB')[1].split('ESCIVEL')[0],directions=[[-1,0],...[...source.matchAll(/FCB\s+(-?\d+),(-?\d+)/g)].map(x=>[+x[1],+x[2]])];
let checks=0;
for(let v=0;v<9;v++)for(const pos of [0,255,256,511])for(const frac of [0,250]){
 ram.fill(0);ram[sym.game_mode]=1;ram[0x5893]=1;
 for(const a of records){put(a,pos);put(a+2,pos);ram[a+4]=ram[a+5]=frac;ram[a+6]=2*v;ram[a+7]=96;}
 for(let t=0;t<4;t++)invoke('world_step');
 const [vl,vs]=directions[v],dx=Math.round(vs*128*256/304),dy=Math.round(-vl*64*112/256);
 for(const a of records){assert.equal(word(a)*256+ram[a+4],(pos*256+frac+4*dx)&131071);assert.equal(word(a+2)*256+ram[a+5],(pos*256+frac+4*dy)&131071);checks+=2;}
}
ram.fill(0);ram[sym.game_mode]=1;ram[0x5893]=1;put(sym.px,200*256);put(sym.py,100*256);
for(let t=0;t<384;t++)invoke('world_step');assert.ok(records.every(a=>ram[a+7]===96),'all depleted slots refill');
// A secondary planetoid across the 511/0 seam can be hit and mined.
for(const a of records)ram[a+7]=0;const a=records[0];put(a,508);put(a+2,90);ram[a+7]=96;ram[a+8]=0;ram[a+6]=2;
put(sym.bx,2*256);put(sym.by,100*256);ram[0x7c94]=ram[0x7c95]=0;ram[sym.bullet_alive]=1;ram[0x5865]=0;invoke('world_step');assert.equal(ram[sym.bullet_alive],0);assert.equal(ram[sym.hits],1);assert.ok(ram[a+8]>0);
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),positionChecks:checks,sourceVelocityDirections:9,refillSlots:17,secondarySeamHit:true};fs.writeFileSync(path.join(root,'build/population-verification.json'),JSON.stringify(report,null,2));console.log(report);
