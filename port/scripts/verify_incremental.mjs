import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536);
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const cpu=createZ80(),clock={tstates:0,stepAdded:0};let mapping=16,writes=new Map(),seed=1982;
const random=n=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed%n;};
const off=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;
const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0,'ROM write');if((a>=0xa800&&a<0xb800)||(a>=0xc800&&a<0xd800))writes.set(a,(writes.get(a)||0)+1);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){assert.equal(p&255,0xf4);mapping=v;}};
let restored=0,preserved=0;
for(let n=0;n<600;n++){
 ram.fill(0);ram.fill(0xa5,0xa800,0xb800);ram.fill(0x47,0xc800,0xd800);ram.fill(32,0x7940,0x79b0);ram[0x78df]=16;ram[0x7be0]=0xc3;ram[0x7ba0]=1;writes=new Map();
 const ox=random(32),oy=64+random(112),ow=Math.min(1+random(7),32-ox),oh=Math.min(1+random(52),176-oy);
 const nx=Math.max(0,Math.min(31,ox+random(17)-8)),ny=Math.max(64,Math.min(175,oy+random(61)-30)),nw=Math.min(random(8),32-nx),nh=Math.min(random(53),176-ny);
 ram.set([ox,oy,ow,oh],sym.oldrects);ram.set([nx,ny,nw,nh],sym.rects+20);
 cpu.yh=sym.oldrects>>8;cpu.yl=sym.oldrects&255;cpu.pc=sym.clear_object;cpu.sp=0x7ffd;cpu.halted=false;ram[0x7ffd]=0;ram[0x7ffe]=1;
 let steps=0;while(cpu.pc!==0x100){assert.ok(++steps<20000,'bounded restoration');runZ80(cpu,bus,1,clock);}
 assert.equal(cpu.sp,0x7fff);assert.equal(mapping,16);assert.equal(ram[0x78df],16);
 for(let y=64;y<176;y++)for(let x=0;x<32;x++){
  const old=x>=ox&&x<ox+ow&&y>=oy&&y<oy+oh,face=x>=nx&&x<nx+nw&&y>=ny&&y<ny+nh,erase=old&&!face,o=off(x,y);
  assert.equal(ram[0xa000+o],erase?0:0xa5,`bitmap ${n} ${x},${y}`);assert.equal(ram[0xc000+o],erase?7:0x47,`attribute ${n} ${x},${y}`);
  assert.equal(writes.get(0xa000+o)||0,erase?1:0,'each exposed bitmap cell restored once');assert.equal(writes.get(0xc000+o)||0,erase?1:0,'each exposed attribute restored once');
  if(erase)restored++;if(old&&face)preserved++;
 }
}
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),rectangleCases:600,restoredCells:restored,preservedOverlapCells:preserved,duplicateRestorationWrites:0,romWrites:0,bankAndStackRestored:true};
fs.writeFileSync(path.join(root,'build/incremental-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(report);
