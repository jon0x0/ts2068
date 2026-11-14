import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {root,api,z,fixture,call,off,rev} from './r22_test_machine.mjs';
const patches=fs.readFileSync(path.join(root,'build/art_assets/terrain_patches.bin')),out=path.join(root,'build/diagnostics/terrain_art');fs.mkdirSync(out,{recursive:true});const results=[];let decoded=0,drawn=0,restored=0;
for(const target of ['sram','rom']){
 for(let tile=0;tile<22;tile++)for(let flip=0;flip<4;flip++)for(let column=0;column<4;column++)for(const iff of [false,true]){
  const {m}=fixture(target);m.bus.write(0x7a83,column);m.bus.write(0x7a80,0);m.bus.write(0x7a81,0x5e);call(m,[0x8741,0x8778,0x87b8,0x87f2][flip],{a:tile,iff1:iff,iff2:iff});const expected=[];
  for(let y=0;y<4;y++){const sx=(flip&1)?3-column:column,sy=(flip&2)?3-y:y,p=tile*144+(sy*4+sx)*9,a=patches[p],pix=Array.from(patches.subarray(p+1,p+9));if(flip&2)pix.reverse();expected.push(...pix.map(v=>(flip&1)?rev(v):v),(flip&2)&&(a&128)?a|4:a);}
  assert.deepEqual(Array.from(m.ram.slice(0x5e00,0x5e24)),expected,`${target} tile${tile} mirror${flip} col${column}`);assert.equal(m.cpu.iff1,iff);assert.equal(m.cpu.sp,0xffe2);decoded++;
 }
 for(let tile=0;tile<22;tile++)for(let flip=0;flip<4;flip++)for(const [x,y]of [[4,4],[0,0],[29,18]])for(const iff of [false,true])for(const background of [false,true]){
  const {m,cart}=fixture(target),pixels=new Uint8Array(6144).fill(0xa5),colours=new Uint8Array(6144).fill(0x47),visible=[];m.ram.fill(0xa5,0x4000,0x5800);m.ram.fill(0x47,0x6000,0x7800);if(target==='rom')m.ram.fill(0xa5,0xa600,0xbe00);else {m.dock[3].fill(0xa5,0,6144);m.dock[2].fill(0x47,0,6144);}m.ram.fill(0,0x8100,0x8380);for(let a=0x7e00;a<0x8080;a++)m.bus.write(a,0);m.bus.write(0x7a9c,1);m.ram[0x8eb1]=0;m.ram[0x8ebf]=background?(target==='rom'?0xa6:0x60):0x40;m.ram[0x8f10]=background?0xd0:0xd8;
  const end=m.ram[0xc4bc]|m.ram[0xc4bd]<<8,src=end-(tile+1)*144;call(m,[0x8cfd,0x8dd3,0x8d65,0x8e29][flip],{b:y,c:x,d:4,e:4,h:src>>8,l:src&255,iff1:iff,iff2:iff});
  for(let cy=0;cy<4;cy++)for(let cx=0;cx<4;cx++){const xx=x+((flip&2)?3-cx:cx),yy=y+((flip&1)?3-cy:cy);if(xx<1||xx>=31||yy>=20)continue;const p=tile*144+(cy*4+cx)*9,a=patches[p];visible.push({xx,yy});for(let sy=0;sy<8;sy++){const dy=(flip&1)?7-sy:sy,o=off(yy*8+dy)+xx;pixels[o]=(flip&2)?rev(patches[p+1+sy]):patches[p+1+sy];colours[o]=(a&128)?fs.readFileSync(path.join(root,'build/art_assets/terrain_palette.bin'))[(a&127)*8+sy]:a;}}
  if(background){assert.deepEqual(target==='rom'?m.ram.slice(0xa600,0xbe00):m.dock[3].slice(0,6144),pixels,`${target} BG pixels tile${tile}`);if(target==='sram')assert.deepEqual(m.dock[2].slice(0,6144),colours,`SRAM BG colours tile${tile}`);
   for(const {xx,yy}of visible){const hl=0x4000+off(yy*8)+xx,de=0x7e00+yy*32+xx;call(m,0x8881,{a:1,h:hl>>8,l:hl&255,d:de>>8,e:de&255,iff1:iff,iff2:iff},0x88cd);assert.equal(m.cpu.sp,0xffde);restored++;}
  }
  assert.deepEqual(m.ram.slice(0x4000,0x5800),pixels,`${target} tile${tile} mirror${flip} BG${background}`);assert.deepEqual(m.ram.slice(0x6000,0x7800),colours,`${target} colours tile${tile} mirror${flip} BG${background}`);assert.equal(m.cpu.iff1,iff);assert.equal(m.portF4,target==='rom'?3:9);drawn++;
 }
 const {cart}=fixture(target);results.push({target,bin_sha256:crypto.createHash('sha256').update(cart.subarray(9)).digest('hex'),passed:true});
}
fs.writeFileSync(path.join(out,'validation.json'),JSON.stringify({decoded,drawn,restored,results},null,2));console.log('Terrain art passes',decoded,'oriented source-column decodes,',drawn,'draw/clip cases and',restored,'cell restores');
