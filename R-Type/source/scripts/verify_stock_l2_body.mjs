import fs from 'node:fs';import assert from 'node:assert/strict';import{stockFixture}from './stock_fixture.mjs';import{off,z}from './r22_test_machine.mjs';
const f=stockFixture(2),{m,call,out}=f,j=JSON.parse(fs.readFileSync(out+'/combined_frames.json')),moving=fs.readFileSync(out+'/../L2_boss_moving.bin');
let repairIrqs=0;
const copyRaster=parseInt(fs.readFileSync(out+'/stock_l2_body.sym','utf8').match(/copy_raster: EQU 0x([0-9a-f]+)/i)[1],16);
const playerFlags=JSON.parse(fs.readFileSync(out+'/player_ram_layout.json')).clock_flags[0];
function repairCall(){
 const oldGuard=m.ram[playerFlags+13],old=m.ram[playerFlags+2];m.ram[playerFlags+2]=1;m.portF4=3;m.portFF=2;
 Object.assign(m.cpu,{pc:0xc09,sp:0xffe0,iff1:false,iff2:false,halted:false,eiDelay:false});m.ram.set([0,0xf0],0xffe0);
 let steps=0,injected=false;
 while(m.cpu.pc!==0xf000&&steps++<1000000){
  if(!injected&&m.cpu.pc===copyRaster+1&&m.cpu.iff1){
   assert.equal(m.ram[playerFlags+13],1,'Repair did not guard shared cache');
   const before=Buffer.from(m.ram.slice(0xc4ce,0xc98f)),pc=m.cpu.pc,sp=m.cpu.sp;
   assert(z.irqZ80(m.cpu,m.bus)>0);let q=0;
   while((m.cpu.pc!==pc||m.cpu.sp!==sp)&&q++<30000)z.runZ80(m.cpu,m.bus,1,m);
   assert(q<30000,'IRQ during body repair failed to return');assert(before.equals(Buffer.from(m.ram.slice(0xc4ce,0xc98f))),'IRQ replaced in-use body cache');repairIrqs++;injected=true;
  }
  z.runZ80(m.cpu,m.bus,1,m);
 }
 assert(steps<1000000,'Body repair hang');assert.equal(m.ram[playerFlags+13],oldGuard,'Body repair leaked guard');m.ram[playerFlags+2]=old;return steps;
}
let movingCases=0;for(let id=34;id<52;id++){call(0x882d,{a:id});const p=m.cpu.h*256+m.cpu.l;assert(Buffer.from(m.ram.slice(p,p+144)).equals(moving.subarray((id-34)*144,(id-33)*144)),'Moving body tile '+id);movingCases++;}
m.ram.fill(0,0x4000,0x5800);m.ram.fill(0,0x6000,0x7800);m.ram.fill(0,0x7800,0x7a80);m.ram.fill(0,0x7e00,0x8080);m.ram.fill(1,0x8100,0x8380);for(let y=0;y<160;y++)for(let x=0;x<32;x++)m.ram[0xa600+off(y)+x]=0;
// Real entrance leaves terrain ownershipFF and flip/state64 at the body cells.
for(const tile of j.boss_tiles){const cx=(tile.coord&7)*4,cy=(tile.coord>>3)*4;for(let c=0;c<16;c++){const cell=(cy+(c>>2))*32+cx+(c&3);m.ram[0x7e00+cell]=255;m.ram[0x8100+cell]=64;}}
const originalPredicate=m.ram[0xfba9]|m.ram[0xfbaa]<<8;
m.ram[0xbe00]=2;m.ram[0x7aa4]=3;m.ram[0x7a8e]=1;m.ram[0x8eb1]=0;m.ram[0x8ebf]=0xa6;repairCall();call(0x8842);call(0xc12);let pixels=0,material=0;
for(const tile of j.boss_tiles){const f=j.frames[tile.frame],cx=(tile.coord&7)*4,cy=(tile.coord>>3)*4;
 for(let c=0;c<16;c++){const col=cx+(c&3),row=cy+(c>>2);if(col===31)continue;const at=off(row*8)+col,bits=f.bits.slice(c*9+1,c*9+9),attrs=j.palette[f.rows[c]],has=bits.some((b,y)=>((attrs[y]&7)&&b)||((attrs[y]&56)&&b!==255));assert.equal(m.ram[0x7e00+row*32+col],0,'Stopped background must not be classified as scrolling terrain');if(has)material++;
  for(let y=0;y<8;y++){const p=at+y*256;assert.equal(m.ram[0x4000+p],bits[y],'Boss bitmap '+JSON.stringify({c,col,row,y,working:m.ram[0xa600+p],flag:m.ram[0x8100+row*32+col],owner:m.ram[0x7e00+row*32+col],tag:m.ram[0x7800+row*32+col]}));const a=m.ram[0x6000+p];for(let k=0;k<8;k++){const now=(bits[y]&(128>>k))?a&7:a>>3&7,want=(bits[y]&(128>>k))?attrs[y]&7:attrs[y]>>3&7;assert.equal(now,want,'Boss colour '+JSON.stringify({c,col,row,y,a,want,now}));pixels++;}}
 }
}
const expectedPixels=Buffer.from(m.ram.slice(0x4000,0x5800)),expectedAttrs=Buffer.from(m.ram.slice(0x6000,0x7800));
for(const tile of j.boss_tiles){const cx=(tile.coord&7)*4,cy=(tile.coord>>3)*4;for(let c=0;c<16;c++){const cell=(cy+(c>>2))*32+cx+(c&3);m.ram[0x8100+cell]|=1;const p=off((cy+(c>>2))*8)+cx+(c&3);for(let y=0;y<8;y++){m.ram[0x4000+p+y*256]=0;m.ram[0x6000+p+y*256]=0;m.ram[0xa600+p+y*256]=0;}}}
repairCall();call(0x8842);call(0xc12);for(let p=0;p<0x1800;p++)assert.equal(m.ram[0x4000+p],expectedPixels[p],'Body repair offset '+p.toString(16));assert(Buffer.from(m.ram.slice(0x6000,0x7800)).equals(expectedAttrs));
call(0xc12);
let cleanedCells=0;
for(const tile of j.boss_tiles){const cx=(tile.coord&7)*4,cy=(tile.coord>>3)*4;for(let c=0;c<16;c++){const col=cx+(c&3),row=cy+(c>>2);if(col===31)continue;const cell=row*32+col,p=off(row*8)+col,flag=m.ram[0x8100+cell];assert.equal(flag&3,0,'Cleanup retained foreground flags');assert(flag&32,'Cleanup lost ECM dictionary marker');call(0xe40,{a:m.ram[0x7800+cell],d:(0x4000+p)>>8,e:p&255});for(let y=0;y<8;y++){const a=m.ram[0x6000+p+y*256],e=expectedAttrs[p+y*256],b=expectedPixels[p+y*256];for(let bit=0;bit<8;bit++)assert.equal(b&(128>>bit)?a&7:a>>3&7,b&(128>>bit)?e&7:e>>3&7,'Post-cleanup palette restore changed boss art');}cleanedCells++;}}
const idle=repairCall();assert(idle<25000,'Idle boss repair must skip decoding/painting');
const tile=j.boss_tiles[0],cx=(tile.coord&7)*4,cy=(tile.coord>>3)*4,ci=cy*32+cx,p=off(cy*8)+cx;
m.ram[0x7e00+ci]=0x81;m.ram[0xa600+p]=0x5a;m.ram[0x8100+ci]=1;
repairCall();assert.equal(m.ram[0xa600+p],0x5a,'Boss repair must preserve foreground actor pixels');call(0xc12);assert.equal(m.ram[0x8100+ci],1,'Cleanup must preserve actor erase footprints');
assert(repairIrqs>0);assert.equal(m.ram[0xfba9]|m.ram[0xfbaa]<<8,originalPredicate,'Repair leaked forced draw predicate');
const r={passed:true,repairIrqs,cleanedCells,movingCases,stoppedTiles:j.boss_tiles.length,pixelsCompared:pixels,materialCells:material,repairAfterErase:true,preservesForegroundActors:true,idleRepairInstructions:idle,romWrites:f.romWrites,scope:'Actual native moving getter, stopped body painter, native copy, non-scrolling background ownership and erase/repair; gameplay and stars separately tested'};fs.writeFileSync(out+'/l2_body_validation.json',JSON.stringify(r,null,2));console.log(r);
