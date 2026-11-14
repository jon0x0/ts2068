import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';
import{api,z,root,off}from'./r22_test_machine.mjs';
const out=path.join(root,'build/fullgame/shot_sequence_r57'),engine=fs.readFileSync(path.join(out,'overlay.bin'));
const symbols=Object.fromEntries([...fs.readFileSync(path.join(out,'overlay.sym'),'utf8').matchAll(/(\w+): EQU 0x([0-9a-f]+)/ig)].map(v=>[v[1],parseInt(v[2],16)]));
let cases=0,owned=0,empty=0,outside=0;
for(const y of[0,1,7,32,33,34,35,36,37,38,39,80,145,152])for(const x of[8,40,81,224])for(const mode of['empty','mixed']){
 const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));api.insertDock(m,Buffer.concat([Buffer.from([0,...Array(8).fill(3)]),Buffer.alloc(65536)]));m.dock[7].set(engine,0x400);m.portF4=0x89;m.portFF=2;m.dock[7][0x1680]=x;m.dock[7][0x1681]=y;
 const pixels=Buffer.from(Array.from({length:6144},(_,i)=>(i*37+63)&255)),attrs=Buffer.from(Array.from({length:6144},(_,i)=>(i*13+3)&0x7f)),meta=Buffer.from(Array.from({length:640},(_,i)=>mode==='empty'?(i%2?3:0):[0,3,1,2,0x81,0xff][i%6]));m.dock[3].set(pixels);m.dock[2].set(attrs);m.dock[7].set(meta,0x1880);
 Object.assign(m.cpu,{pc:symbols.cache_backing,sp:0x5ce0,iff1:false,iff2:false});m.ram[0x5ce0]=0;m.ram[0x5ce1]=0x80;let steps=0;while(m.cpu.pc!==0x8000&&steps++<100000)z.runZ80(m.cpu,m.bus,1,m);assert(steps<100000);assert.equal(m.cpu.sp,0x5ce2);assert.equal(m.portF4,0x89);
 const left=m.dock[7][0x16b4],top=m.dock[7][0x16b5];assert.equal(top&7,0,'whole character rows');for(let r=0;r<192;r++)for(let c=0;c<32;c++){const i=off(r)+c,inPatch=r>=top&&r<top+64&&c>=left&&c<left+10;let ep=pixels[i],ea=attrs[i];if(inPatch){const owner=meta[(r>>3)*32+c];if(owner===0||owner===3){ep=ea=0;empty++;}else owned++;const at=(r-top)*10+c-left;assert.equal(m.dock[7][0x1100+at],ep,'backing bits');assert.equal(m.dock[2][0x1d00+at],ea,'backing attr');}else outside++;assert.equal(m.dock[3][i],ep,'retained bits');assert.equal(m.dock[2][i],ea,'retained attr');}
 cases++;
}
assert(owned>0&&empty>0);const result={passed:true,cases,owned_bytes_preserved:owned,unowned_bytes_cleaned:empty,outside_patch_bytes_preserved:outside,whole_character_rows:true,scope:'Whole 64x10 backing patch at edge/fine phases, empty/dirty3 and mixed occupied metadata; inactive retained garbage cleared while owned art and all bytes outside patch remain exact'};
fs.writeFileSync(path.join(out,'clean_cache_validation.json'),JSON.stringify(result,null,2));console.log(result);
