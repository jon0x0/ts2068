import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{root,api,call,off,rev}from'./r22_test_machine.mjs';
const folder=path.join(root,'build/fullgame/cached_levels_r34'),raw=fs.readFileSync(path.join(folder,'level02_region.bin')),boot=fs.readFileSync(path.join(folder,'boot_region.bin')),layout=JSON.parse(fs.readFileSync(path.join(root,'build/fullgame/foundation/manifest.json'))).levels[1],m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));api.insertDock(m,Buffer.concat([Buffer.from([0,...Array(8).fill(3)]),raw]));
for(const[s,d]of[[7,2],[1,3],[2,4],[3,5],[5,6],[6,7]])m.ram.set((s===2||s===3?boot:raw).subarray(s*8192,(s+1)*8192),d*8192);for(const b of[1,2,3])m.dock[b].set(raw.subarray(b*8192,(b+1)*8192));for(let i=0;i<256;i++)m.ram[0x5d00+i]=rev(i);const source=Buffer.from(m.ram),dictionary=raw.subarray(0xe000,0xe400),results=[];
for(const id of[32,33,34,35,36,37,38,41,42,43,44]){
 const d=layout.enemy_descriptors_start+(id-1)*4,w=source[d],h=source[d+1],ptr=source.readUInt16LE(d+2),cells=[];let p=ptr;for(let cy=0;cy<h;cy++)for(let cx=0;cx<w;cx++){const a=source[p];cells.push({cx,cy,a,p});p+=a===54?1:9;}
 for(let flip=0;flip<4;flip++)for(const x of[1,8,29])for(const sy of[-3,-2,-1,0,16,18,19]){
  m.ram.set(source);m.portF4=9;m.portFF=2;m.ram.fill(0xa5,0x4000,0x5800);m.ram.fill(7,0x6000,0x7800);m.dock[3].fill(0,0x1e00);m.bus.write(0x7a9c,130);m.ram[0x8eb1]=0;m.ram[0x8ebf]=0x60;m.ram[0x8f10]=0xd0;m.dock[3].fill(0xa5,0,6144);m.dock[2].fill(7,0,6144);
  call(m,[0x8cfd,0x8dd3,0x8d65,0x8e29][flip],{b:sy&255,c:x,d:h,e:w,h:ptr>>8,l:ptr&255});
  const pix=Buffer.alloc(6144,0xa5),atr=Buffer.alloc(6144,7);for(const c of cells){if(c.a===54)continue;const xx=x+((flip&2)?w-1-c.cx:c.cx),yy=sy+((flip&1)?h-1-c.cy:c.cy);if(xx<1||xx>=31||yy<0||yy>=20)continue;for(let y=0;y<8;y++){const at=off(yy*8+((flip&1)?7-y:y))+xx;pix[at]=(flip&2)?rev(source[c.p+1+y]):source[c.p+1+y];atr[at]=dictionary[(c.a&127)*8+y];}}
  const actual=Buffer.from(m.dock[3].slice(0,6144));if(!actual.equals(pix)){results.push({id,flip,x,y:sy,bitmap:false});console.log(results.at(-1));}else if(!Buffer.from(m.dock[2].slice(0,6144)).equals(atr)){results.push({id,flip,x,y:sy,bitmap:true,colours:false});console.log(results.at(-1));}
 }
}
fs.writeFileSync(path.join(root,'build/diagnostics/l2_emergence/background_clipping_failures.json'),JSON.stringify(results,null,2));console.log('Failures',results.length);
