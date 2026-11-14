import crypto from 'node:crypto';
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../TSRun'),api=await import(pathToFileURL(path.join(up,'machine.js'))),z=await import(pathToFileURL(path.join(up,'z80.js')));
const out=path.join(root,'build/ecm_native'),cart=fs.readFileSync(path.join(out,'RType_level1_ECM_TSPico_RAM_r24.dck')),initial=fs.readFileSync(path.join(root,'build/native/snapshot.bin')),original=fs.readFileSync(path.join(root,'build/native/snapshot.bin')),reference=fs.readFileSync(path.join(root,'build/ecm_native/authoring_palette.bin')),meta={};
const logical=Buffer.concat([Buffer.alloc(0x4000),original]),off=y=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2),rev=v=>parseInt(v.toString(2).padStart(8,'0').split('').reverse().join(''),2),modes=[0x8cfd,0x8dd3,0x8d65,0x8e29],results=[];
const boss=JSON.parse(fs.readFileSync(path.join(root,'build/ecm_native/boss_manifest.json'),'utf8'));
const orbFrame0=fs.readFileSync(path.join(root,'build/art_assets/fireball_frames.bin')).subarray(0,36);logical.set(orbFrame0,0xd550);
let cases=0,writes=0;
for(let id=1;id<=181;id++){
 const d=id>=112?0xd7f9+(id-112)*4:0xbc67+(id-1)*4,w=logical[d],h=logical[d+1];if(!w||!h)continue;let p=logical.readUInt16LE(d+2);const cells=[];
 for(let cy=0;cy<h;cy++)for(let cx=0;cx<w;cx++){const attr=logical[p],old=p;cells.push({cx,cy,attr,p,source:logical.subarray(p+1,p+9)});p+=attr===0x36?1:9;}
 for(let flip=0;flip<4;flip++)for(const [x,y] of (id===119?[[4,1],[0,0],[29,18]]:[[4,4],[0,0],[29,18]]))for(const iff of [false,true]){
  const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));api.insertDock(m,cart);m.ram.set(initial,0x4000);m.ram.set(orbFrame0,0xd550);m.ram.set(cart.subarray(9+0x4000,9+0x6000),0x8000);m.ram.set(cart.subarray(9+0x6000,9+0x8000),0xa000);m.dock[3].set(original.subarray(0x2000,0x4000));m.dock[3].fill(0,0x1e00);m.portF4=9;for(const [bank,address]of [[5,0xc000],[6,0xe000]])m.ram.set(cart.subarray(9+bank*8192,9+(bank+1)*8192),address);
  const cache=fs.readFileSync(path.join(out,'cache_ids.bin'));let ci=0;
  for(let j=1;j<=111;j++){const q=0xbc67+(j-1)*4;let p=logical.readUInt16LE(q+2);for(let cy=0;cy<logical[q+1];cy++)for(let cx=0;cx<logical[q];cx++){const a=logical[p];m.dock[1][p&8191]=cache[ci++];if(a===0x36){p++;continue;}for(let sy=0;sy<8;sy++)if(!(a&0x38)&&m.ram[p+1+sy]===255){m.ram[p+1+sy]=(sy&1)?0xaa:0x55;m.dock[1][(p+1+sy)&8191]=1;}p+=9;}}assert.equal(ci,cache.length);
  m.dock[1][0x1ff0]=2;m.dock[1][0x1ff1]=0;m.portFF=2;m.ram.fill(0xa5,0x4000,0x5800);m.ram.fill(0x47,0x6000,0x7800);m.ram.fill(0,0x7e00,0x8380);m.ram[0xbe00]=2;m.bus.write(0x7a9c,id);m.ram[0x8eb1]=0;m.ram[0x8ebf]=0x40;m.ram[0x8f10]=0xd8;
  for(let i=0;i<256;i++)m.ram[0x5d00+i]=rev(i);
  const src=logical.readUInt16LE(d+2);Object.assign(m.cpu,{b:y,c:x,d:h,e:w,h:src>>8,l:src&255,pc:modes[flip],sp:0xffe0,i:0x84,iff1:iff,iff2:iff});m.ram[0xffe0]=0;m.ram[0xffe1]=0xf0;
  const wr=m.bus.write;m.bus.write=(a,v)=>{if((m.portF4&(1<<(a>>>13)))&&!m.dockRam[a>>>13]){writes++;throw Error('ROM write '+a.toString(16));}wr(a,v);};
  let steps=0;while(m.cpu.pc!==0xf000&&steps++<150000)z.runZ80(m.cpu,m.bus,1,m);assert(steps<150000,`loop id${id} flip${flip} ${x},${y}`);assert.equal(m.cpu.sp,0xffe2);assert.equal(m.cpu.iff1,iff);assert.equal(m.portF4,9);
  const pix=new Uint8Array(6144).fill(0xa5),atr=new Uint8Array(6144).fill(0x47);
  for(const cell of cells){if(cell.attr===0x36)continue;const xx=x+((flip&2)?w-1-cell.cx:cell.cx),yy=y+((flip&1)?h-1-cell.cy:cell.cy);if(xx<1||xx>=31||yy>=20)continue;
   const page=reference[id]+(cell.cx%2),base=page*256+cell.cy*8;
   for(let sy=0;sy<8;sy++){
    const dy=(flip&1)?7-sy:sy,at=off(yy*8+dy)+xx;let pixel=cell.source[sy],color=reference[base+sy];
    if(id<112&&!(cell.attr&0x38)&&cell.source[sy]===255){pixel=sy%2===0?0x55:0xaa;color=reference[((page&254)===4?0x108:0x180)+color];}
    if(cell.attr&0x38||!(cell.attr&7))color=cell.attr&127;if(id>=112)color=boss.cells.find(v=>v.pointer===cell.p).colours[sy];
    pix[at]=(flip&2)?rev(pixel):pixel;atr[at]=color;
   }
  }
  try{assert.deepEqual(m.ram.slice(0x4000,0x5800),pix);assert.deepEqual(m.ram.slice(0x6000,0x7800),atr);}catch(e){const diff=[];for(let i=0;i<6144;i++)if(m.ram[0x4000+i]!==pix[i]||m.ram[0x6000+i]!==atr[i]){diff.push({offset:i,pixel:m.ram[0x4000+i],expectedPixel:pix[i],attr:m.ram[0x6000+i],expectedAttr:atr[i]});if(diff.length===12)break;}fs.writeFileSync(path.join(out,'boss_sram_failure.json'),JSON.stringify({id,flip,x,y,iff,pc:m.cpu.pc,diff},null,2));throw Error('Sprite mismatch id'+id+' flip'+flip+' at'+x+','+y);}
  if(id===119&&flip===0&&x===4&&y===1&&iff)fs.writeFileSync(path.join(out,'boss_cpu_home.bin'),m.ram);if(id>=112&&w===2&&h===2&&flip===0&&x===4&&y===4&&iff)fs.writeFileSync(path.join(out,'level_sprite'+(id-111)+'_cpu.bin'),m.ram);cases++;results.push({id,flip,x,y,iff,steps});
 }
 if(id%20===0)console.log('Verified ROM sprites through ID',id,'cases',cases);
}
fs.writeFileSync(path.join(out,'all_sram_validation.json'),JSON.stringify({bin_sha256:crypto.createHash("sha256").update(fs.readFileSync(path.join(out,"RType_level1_ECM_TSPico_RAM_r24.bin"))).digest("hex"),cases,romWrites:writes,passed:true,results},null,2));console.log('All',cases,'complete-sprite/clip/IFF cases match independent original bitmap and colour reference; no ROM writes');
