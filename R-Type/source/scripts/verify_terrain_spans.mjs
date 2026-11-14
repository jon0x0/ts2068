import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../TSRun'),api=await import(pathToFileURL(path.join(up,'machine.js'))),z=await import(pathToFileURL(path.join(up,'z80.js')));
const off=y=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2),results=[];
for(const target of ['r15','rom']){
 const folder=target==='rom'?'build/readonly_ecm':'build/ecm_native',symtext=fs.readFileSync(path.join(root,folder,'renderer.sym'),'utf8'),entry=parseInt(symtext.match(/terrain_colour_core: EQU 0x([0-9a-f]+)/i)[1],16);
 const cart=fs.readFileSync(path.join(root,folder,target==='rom'?'RType_ECM_ROM_candidate.dck':'RType_level1_ECM_TSPico_RAM_r15.dck'));
 for(let row=0;row<20;row++)for(const [left,right] of [[1,1],[5,10],[1,30]])for(const iff of [false,true])for(let phase=0;phase<8;phase++)for(const cached of [false,true]){
  const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));api.insertDock(m,cart);m.ram.set(fs.readFileSync(path.join(root,"build/art_assets/terrain_palette.bin")).subarray(0,128),0xfbd0);m.portF4=target==='rom'?3:9;m.portFF=2;m.ram.fill(0x2f,0x6000,0x7800);if(target==='rom')m.ram[0xbe00]=2;else m.dock[1][0x1ff0]=2;
  m.bus.write(0x7a82,phase);const expected=new Uint8Array(6144).fill(0x2f),id=0x7e00+row*32;
  for(let x=0;x<32;x++){
   m.bus.write(id+x,x>=left&&x<=right?255:x===left-1?3:0);
   m.ram[0x5800+row*32+x]=cached?0x80|(Math.floor(x/2)%16):0x40|((Math.floor(x/2)%7)+1);
   for(let dy=0;dy<8;dy++)m.ram[0x4000+off(row*8+dy)+x]=[0,1,128,255,0x55,0xaa,15,240][(dy+x)%8];
  }
  m.bus.write(0x7800+row*32+31,cached?0x89:0x45);const legacy=Uint8Array.from(m.ram.slice(0x5800,0x5b00));
  for(let x=Math.max(1,left-1);x<=right;x++)for(let dy=0;dy<8;dy++){
   const at=m.ram[0x5800+row*32+x],nt=(x===30?m.bus.read(0x7800+row*32+31):m.ram[0x5800+row*32+x+1]),decode=(a,y)=>(a&128)?cart[9+0x9c00+(a&127)*8+y]:a,a=decode(at,dy),n=decode(nt,dy);
   if(x===left-1&&left>1){expected[off(row*8+dy)+x]=n;continue;}if(at===nt&&phase!==0&&phase!==7)continue;
   const pixels=m.ram[0x4000+off(row*8+dy)+x],mask=(255<<(phase+1))&255;
   expected[off(row*8+dy)+x]=(pixels&mask)?a:n;
  }
  const de=id+left-1,hl=0x4000+off(row*8)+right;Object.assign(m.cpu,{a:0x12,f:0x54,b:0x23,c:0x45,d:de>>8,e:de&255,h:hl>>8,l:hl&255,xh:0x45,xl:0x67,yh:0x67,yl:0x89,sp:0xd000,pc:entry,i:0x84,iff1:iff,iff2:iff});m.ram[0xd000]=0;m.ram[0xd001]=0xf0;
  let steps=0;while(m.cpu.pc!==0xf000&&steps++<10000)z.runZ80(m.cpu,m.bus,1,m);assert(steps<10000);const c=m.cpu;assert.deepEqual(m.ram.slice(0x5800,0x5b00),legacy);
  assert.deepEqual([c.a,c.f,c.b,c.c,c.d,c.e,c.h,c.l,c.xh,c.xl,c.yh,c.yl,c.sp,c.iff1],[0x12,0x54,0x23,0x45,de>>8,de&255,hl>>8,hl&255,0x45,0x67,0x67,0x89,0xd002,iff]);assert.deepEqual(m.ram.slice(0x6000,0x7800),expected,`${target} row${row} span${left}-${right}`);assert.equal(m.portF4,target==='rom'?3:9);assert.equal(m.portFF,2);results.push({target,row,left,right,iff,phase,cached,cycles:m.tstates,passed:true});
 }
}
fs.mkdirSync(path.join(root,'build/diagnostics/terrain_motion'),{recursive:true});fs.writeFileSync(path.join(root,'build/diagnostics/terrain_motion/edge_cpu_validation_r15.json'),JSON.stringify(results,null,2));console.log(results.length,'terrain-span CPU cases pass exact entire6144-byte output, borders, left spill cells, all fine phases, registers, stack, IFF and mapping');
