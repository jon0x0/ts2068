import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {root,fixture,call,off,rev} from './r22_test_machine.mjs';
const frames=fs.readFileSync(path.join(root,'build/art_assets/fireball_frames.bin')),colours=fs.readFileSync(path.join(root,'build/art_assets/fireball_colours.bin')),results=[];let copies=0,draws=0;
for(const target of ['sram','rom']){
 for(let counter=0;counter<8;counter++)for(const iff of [false,true]){const {m}=fixture(target);m.bus.write(0x7a89,counter);call(m,0x0d00,{iff1:iff,iff2:iff});const frame=[0,1,2,1][counter&3];assert.deepEqual(m.ram.slice(0xd550,0xd574),Uint8Array.from(frames.subarray(frame*36,(frame+1)*36)));assert.equal(target==='rom'?m.ram[0xbe01]:m.dock[1][0x1ff1],frame);assert.equal(m.cpu.iff1,iff);copies++;}
 for(let frame=0;frame<3;frame++)for(let flip=0;flip<4;flip++)for(const [x,y]of [[4,4],[0,0],[29,18]])for(const iff of [false,true]){
  const {m}=fixture(target);m.ram.fill(0xa5,0x4000,0x5800);m.ram.fill(0x47,0x6000,0x7800);m.ram.set(frames.subarray(frame*36,(frame+1)*36),0xd550);if(target==='rom')m.ram[0xbe01]=frame;else m.dock[1][0x1ff1]=frame;m.bus.write(0x7a9c,57);m.ram[0x8eb1]=0;m.ram[0x8ebf]=0x40;m.ram[0x8f10]=0xd8;call(m,[0x8cfd,0x8dd3,0x8d65,0x8e29][flip],{b:y,c:x,d:2,e:2,h:0xd5,l:0x50,iff1:iff,iff2:iff});const pix=new Uint8Array(6144).fill(0xa5),atr=new Uint8Array(6144).fill(0x47);
  for(let cy=0;cy<2;cy++)for(let cx=0;cx<2;cx++){const xx=x+((flip&2)?1-cx:cx),yy=y+((flip&1)?1-cy:cy);if(xx<1||xx>=31||yy>=20)continue;for(let sy=0;sy<8;sy++){const o=off(yy*8+((flip&1)?7-sy:sy))+xx,v=frames[frame*36+(cy*2+cx)*9+1+sy];pix[o]=(flip&2)?rev(v):v;atr[o]=colours[frame*32+(cy*2+cx)*8+sy];}}
  assert.deepEqual(m.ram.slice(0x4000,0x5800),pix);assert.deepEqual(m.ram.slice(0x6000,0x7800),atr);assert.equal(m.cpu.iff1,iff);draws++;
 }
 const {cart}=fixture(target);results.push({target,bin_sha256:crypto.createHash('sha256').update(cart.subarray(9)).digest('hex'),passed:true});
}
fs.writeFileSync(path.join(root,'build/art_assets/orb_validation.json'),JSON.stringify({copies,draws,results},null,2));console.log('Arcade orb',copies,'frame-copy/IFF cases and',draws,'complete frame/mirror/clip cases pass');
