import crypto from 'node:crypto';
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../TSRun'),api=await import(pathToFileURL(path.join(up,'machine.js'))),z=await import(pathToFileURL(path.join(up,'z80.js'))),out=path.join(root,'build/readonly_ecm');
const cart=fs.readFileSync(path.join(out,'RType_ECM_ROM_candidate.dck')),initial=fs.readFileSync(path.join(out,'initial_home.bin')),logical=Buffer.concat([Buffer.alloc(0x4000),fs.readFileSync(path.join(root,'build/native/snapshot.bin'))]),ref=fs.readFileSync(path.join(root,'build/ecm_native/authoring_palette.bin')),meta=JSON.parse(fs.readFileSync(path.join(out,'manifest.json'),'utf8'));
const boss=JSON.parse(fs.readFileSync(path.join(root,'build/ecm_native/boss_manifest.json'),'utf8'));
const orbFrame0=fs.readFileSync(path.join(root,'build/art_assets/fireball_frames.bin')).subarray(0,36);logical.set(orbFrame0,0xd550);
const off=y=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2),rev=v=>parseInt(v.toString(2).padStart(8,'0').split('').reverse().join(''),2),modes=[0x8cfd,0x8dd3,0x8d65,0x8e29];let cases=0,restored=0,erased=0;
function until(m,pc){let n=0;while(m.cpu.pc!==pc&&n++<150000)z.runZ80(m.cpu,m.bus,1,m);assert(n<150000,'CPU loop at'+m.cpu.pc.toString(16));}
function at(m,pc,hl,de,a=1){Object.assign(m.cpu,{pc,sp:0xffe0,a,f:0,b:0x12,c:0x34,h:hl>>8,l:hl&255,d:de>>8,e:de&255});m.ram[0xffe0]=0;m.ram[0xffe1]=0xf0;}
for(let id=1;id<=181;id++){
 const d=id>=112?0xd7f9+(id-112)*4:0xbc67+(id-1)*4,w=logical[d],h=logical[d+1];if(!w||!h)continue;let p=logical.readUInt16LE(d+2);const cells=[];
 for(let cy=0;cy<h;cy++)for(let cx=0;cx<w;cx++){const attr=logical[p];cells.push({cx,cy,attr,p,source:logical.subarray(p+1,p+9)});p+=attr===0x36?1:9;}
 for(let flip=0;flip<4;flip++)for(const iff of [false,true]){
  const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));api.insertDock(m,cart);m.ram.set(initial,0x4000);m.ram.set(orbFrame0,0xd550);m.portF4=3;m.portFF=2;m.ram.fill(0xa5,0x4000,0x5800);m.ram.fill(0xa5,0xa600,0xbe00);m.ram.fill(0x47,0x6000,0x7800);m.ram.fill(0x47,0x7800,0x7a80);m.ram.fill(0,0x7e00,0x8380);for(let i=0;i<640;i++)m.ram[0x8100+i]=i&1;
  m.ram[0xbe00]=2;m.ram[0x7a9c]=id;m.ram[0x8eb1]=0;m.ram[0x8ebf]=0xa6;m.ram[0x8f10]=0xd0;m.ram[0x7a82]=0;for(let i=0;i<256;i++)m.ram[0x5d00+i]=rev(i);
  const wr=m.bus.write;m.bus.write=(a,v)=>{assert(!(m.portF4&(1<<(a>>>13))),'ROM write');wr(a,v);};
  const src=id>=112?logical.readUInt16LE(d+2):meta.address_map[logical.readUInt16LE(d+2).toString()];Object.assign(m.cpu,{b:4,c:4,d:h,e:w,h:src>>8,l:src&255,pc:modes[flip],sp:0xffe0,i:0x84,iff1:iff,iff2:iff});m.ram[0xffe0]=0;m.ram[0xffe1]=0xf0;until(m,0xf000);
  const bg=new Uint8Array(6144).fill(0xa5),pix=new Uint8Array(6144).fill(0xa5),atr=new Uint8Array(6144).fill(0x47),visible=[];
  for(const cell of cells){if(cell.attr===0x36)continue;const xx=4+((flip&2)?w-1-cell.cx:cell.cx),yy=4+((flip&1)?h-1-cell.cy:cell.cy);if(xx<1||xx>=31||yy>=20)continue;visible.push({xx,yy});const page=ref[id]+cell.cx%2,base=page*256+cell.cy*8;
   for(let sy=0;sy<8;sy++){const dy=(flip&1)?7-sy:sy,o=off(yy*8+dy)+xx;let pixel=cell.source[sy],color=ref[base+sy];if(id<112&&!(cell.attr&0x38)&&pixel===255){pixel=sy%2===0?0x55:0xaa;color=ref[((page&254)===4?0x108:0x180)+color];}if(cell.attr&0x38||!(cell.attr&7))color=cell.attr&127;if(id>=112)color=boss.cells.find(v=>v.pointer===cell.p).colours[sy];bg[o]=(flip&2)?rev(pixel):pixel;pix[o]=bg[o];atr[o]=color;}
  }
  assert.deepEqual(m.ram.slice(0xa600,0xbe00),bg,`background pixels ${id}/${flip}`);assert.deepEqual(m.ram.slice(0x6000,0x7800),new Uint8Array(6144).fill(0x47),'background painting touched live colours');
  for(const {xx,yy} of visible){const hl=0x4000+off(yy*8)+xx,de=0x7e00+yy*32+xx,flag=0x8100+yy*32+xx,before=m.ram[flag];assert.equal(before&1,(yy*32+xx)&1);at(m,0x8881,hl,de,id);until(m,0x88cd);assert.equal(m.cpu.sp,0xffde);assert.equal(m.ram[flag],(before&128)|1);restored++;}
  try{assert.deepEqual(m.ram.slice(0x4000,0x5800),pix);assert.deepEqual(m.ram.slice(0x6000,0x7800),atr);}catch(e){const diff=[];for(let i=0;i<6144;i++)if(m.ram[0x6000+i]!==atr[i]){diff.push({offset:i,actual:m.ram[0x6000+i],expected:atr[i]});if(diff.length===8)break;}fs.writeFileSync(path.join(out,'background_failure.json'),JSON.stringify({id,flip,iff,diff},null,2));throw e;}
  for(const {xx,yy} of visible){const hl=0x4000+off(yy*8)+xx,de=0x7e00+yy*32+xx,flag=0x8100+yy*32+xx,before=m.ram[flag];m.ram[de]=0;m.ram[0x5800+yy*32+xx]=0x47;at(m,0x88b3,hl,de,0);m.cpu.sp=0xffde;m.ram[0xffde]=hl&255;m.ram[0xffdf]=hl>>8;until(m,0x88cd);assert.equal(m.ram[flag],before&128);for(let dy=0;dy<8;dy++){const o=off(yy*8+dy)+xx;assert.equal(m.ram[0x4000+o],0);assert.equal(m.ram[0x6000+o],0x47);}erased++;}
  assert.equal(m.cpu.iff1,iff);cases++;
 }
}
fs.writeFileSync(path.join(out,'background_validation.json'),JSON.stringify({bin_sha256:crypto.createHash("sha256").update(fs.readFileSync(path.join(out,"RType_ECM_ROM_candidate.bin"))).digest("hex"),cases,restored_cells:restored,erased_cells:erased,passed:true,format:'Existing7800 palette tokens plus dirty-grid bit7; no extra cartridge RAM'},null,2));console.log(cases,'background sprites,',restored,'restores and',erased,'empty erasures match independent pixels/colours; dirty flags and IFF preserved');
