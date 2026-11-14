import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{root,api,call}from'./r22_test_machine.mjs';
const out=path.join(root,'build/fullgame/rocket_fix_r41'),diag=path.join(root,'build/diagnostics/rocket_fix_r41');fs.mkdirSync(diag,{recursive:true});const boot=fs.readFileSync(path.join(out,'boot_region.bin'));let count=0;
for(const rev of['debug_ram_r38','rocket_fix_r41'])for(const level of[1,2,3,4,5,6,7,8]){
 const raw=fs.readFileSync(path.join(root,`build/fullgame/${rev}/level${String(level).padStart(2,'0')}_region.bin`)),m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));api.insertDock(m,Buffer.concat([Buffer.from([0,...Array(8).fill(3)]),raw]));for(const[s,d]of[[7,2],[1,3],[2,4],[3,5],[5,6],[6,7]])m.ram.set(boot.subarray(s*8192,(s+1)*8192),d*8192);m.portF4=9;m.portFF=2;
 // Snapshot fully initialized native state, then poison only retained playfield.
 const keep=Buffer.from(m.dock[3]);for(let y=0;y<160;y++)for(let x=0;x<32;x++){const at=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;m.dock[3][at]=(x*13+y+17)&255;}
 if(rev==='debug_ram_r38')m.ram[0xfcc8]=0xc9;
 const before=Buffer.from(m.dock[3]);call(m,0x1485);let remaining=0;for(let y=0;y<160;y++)for(let x=0;x<32;x++){const at=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;if(m.dock[3][at])remaining++;}
 if(rev==='debug_ram_r38')assert(remaining>4000,'Old init must leave retained poison');else assert.equal(remaining,0,'Retained bitmap clear');
 // Focused helper contract: no workspace, front plane, register or bank changes.
 if(rev==='rocket_fix_r41'){
  m.dock[3].set(before);const front=Buffer.from(m.ram.slice(0x4000,0x7800));call(m,0xfcc8,{a:0x42,f:0x81,b:0x12,c:0x34,d:0x56,e:0x78,h:0x9a,l:0xbc});assert.equal(m.cpu.a,0x42);assert.equal(m.cpu.f,0x81);assert.equal(m.cpu.b*256+m.cpu.c,0x1234);assert.equal(m.cpu.d*256+m.cpu.e,0x5678);assert.equal(m.cpu.h*256+m.cpu.l,0x9abc);assert.equal(m.portF4,9);assert(front.equals(Buffer.from(m.ram.slice(0x4000,0x7800))));for(let i=0;i<8192;i++){const gamePixel=i<4096||(i<6144&&(i&255)<128);assert.equal(m.dock[3][i],gamePixel?0:before[i],'Interleaved workspace '+i.toString(16));}count++;
 }
 console.log(rev,level,'stale bytes',remaining);
}
console.log('All8 initialization and exact interleaved workspace guards pass',count);
