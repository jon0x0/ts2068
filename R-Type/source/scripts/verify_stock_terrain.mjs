import fs from 'node:fs';import assert from 'node:assert/strict';
import {stockFixture}from './stock_fixture.mjs';import{root,off,rev}from './r22_test_machine.mjs';
const n=Number(process.argv[2]||1),f=stockFixture(n),{m,call,out}=f;
const j=JSON.parse(fs.readFileSync(out+`/../L${n}_native_terrain.json`)),palette=fs.readFileSync(out+'/terrain/palette.bin'),home=Buffer.from(m.ram);
assert(Buffer.from(m.ram.slice(0xfbd0,0xfc50)).equals(palette),'Live palette must match current source');let cases=0,visible=0;const l2Source=n===2?fs.readFileSync(root+'/build/fullgame/visible_hits_r145/level02_region.bin'):null;
for(const retained of[false,true])for(const t of j.rawTiles)for(let flip=0;flip<4;flip++){
 m.ram.set(home);m.ram.fill(0,0x4000,0x5800);m.ram.fill(0,0x6000,0x7800);m.ram.fill(0,0x7800,0x7a80);m.ram.fill(0,0x8100,0x8380);
 for(let y=0;y<32;y++)for(let x=0;x<4;x++)m.ram[0xa600+off(y)+1+x]=0;
 m.ram[0x7a9c]=0;m.ram[0x7a84]=8;m.ram[0x8eb1]=0;m.ram[0x8ebf]=retained?0xa6:0x40;m.ram[0xbe00]=2;
 call(0x882d,{a:t.tile});const ptr=m.cpu.h*256+m.cpu.l;
 assert(Buffer.from(m.ram.slice(ptr,ptr+144)).equals(Buffer.from(t.bytes)),'Native tile source '+t.tile);
 call([0x8cfd,0x8d65,0x8dd3,0x8e29][flip],{h:ptr>>8,l:ptr&255,b:0,c:1,d:4,e:4});
 if(retained)for(let cy=0;cy<4;cy++)for(let cx=0;cx<4;cx++){
  const p=off(cy*8)+1+cx;for(let y=0;y<8;y++)m.ram[0x4000+p+y*256]=m.ram[0xa600+p+y*256];call(0x160d,{a:1,h:(0x4000+p)>>8,l:p&255});
 }
 for(let y=0;y<32;y++)for(let x=0;x<4;x++){
  const sx=flip&1?3-x:x,sy=flip&2?31-y:y,cell=((sy>>3)*4+sx)*9,header=t.bytes[cell],p=off(y)+1+x;
  const expectedBits=flip&1?rev(t.bytes[cell+1+(sy&7)]):t.bytes[cell+1+(sy&7)],bits=m.ram[0x4000+p],attr=m.ram[0x6000+p];
  assert.equal(bits,expectedBits,JSON.stringify({retained,tile:t.tile,flip,x,y}));
  const tag=m.ram[0x7800+(y>>3)*32+1+x],style=tag&8;
  const expected=header&128?(l2Source?l2Source[0x8343+y]:palette[((header&0x77)|style)*8+(sy&7)]):header;
  for(let bit=0;bit<8;bit++){
   const actual=(bits&(128>>bit))?attr&7:attr>>3&7,want=(expectedBits&(128>>bit))?expected&7:expected>>3&7;
   assert.equal(actual,want,JSON.stringify({retained,tile:t.tile,flip,x,y,header,tag,attr,expected}));if(want)visible++;
  }
 }
 cases++;
}
const result={passed:true,level:n,cases,visiblePixelsCompared:visible,romWrites:f.romWrites,tileDimensionsUnchanged:true,scope:'All current ordinary native terrain tiles, four flips, direct and retained publication; composite L2 boss and moving scroll phases separate'};
fs.writeFileSync(out+'/terrain_validation.json',JSON.stringify(result,null,2));console.log(result);
