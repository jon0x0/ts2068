import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const upstream=path.resolve(root,'../../../TSRun');
const api=await import(pathToFileURL(path.join(upstream,'machine.js')));
const read=n=>fs.readFileSync(path.join(root,n));
const symbols=Object.fromEntries([...read('build/flight-symbols.txt').toString().matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));
m.homeRom.set(fs.readFileSync(path.join(upstream,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(upstream,'roms/ts2068-1.rom')));
const cartridge=read('build/sinistar-flight.dck');assert.equal(api.insertDock(m,cartridge),null);api.resetMachine(m);
const signed=x=>(x<<16)>>16,signed8=x=>(x<<24)>>24;
const off=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;
const word=a=>m.ram[a]+256*m.ram[a+1];
const table=JSON.parse(read('build/player-tables.json')).SINETBL;
const sprites=Array.from({length:32},(_,h)=>Array.from({length:8},(_,p)=>fs.readFileSync(path.join(root,`../assets/ship-${String(h).padStart(2,'0')}-${p}.bin`))));
let model={x:0x7b00,y:0x3800,vx:0,vy:0,sx:0,sy:0,cx:0,cy:0,px:0,py:0,angle:0,frame:0};
const stars=JSON.parse(read('build/star-seeds.json'));
let starWraps=0,overlaps=0; const ranges={x:[256,0],y:[192,0],cameraX:[0,0],cameraY:[0,0]};
let expected=null,done=0,start=0,prepared=0,publishTime=0,lastEnd=null,maxWork=0,maxPublish=0,wrongWrites=0,unchanged=0,romWrites=0,rasterBad=0,rasterPixels=0;
const cadence={},headings=new Set(),phases=new Set();
function update(){
 const target=(model.frame>>1)&255,delta=signed8(target-model.angle);
 model.angle=(model.angle+Math.floor((delta*127+128)/256))&255;
 const a=model.angle,q=a>>6,p=a&63;
 let sine=q&1?table[63-p]:table[p],cos=q&1?table[p]:table[63-p];
 if(q>=2)sine=sine^255;if(q===1||q===2)cos=cos^255;
 if(((delta+32)&255)<64){
  const accel=(want,v)=>signed(v+Math.floor((signed(Math.floor(signed(want-v)*127/256))+4)/8));
  model.vx=accel(signed8(sine)*8,model.vx);model.vy=accel(signed8(cos)*4,model.vy);
 }
 const camera=(pos,v,scroll,unit,short)=>{
  const next=((pos+v+scroll)&65535)>>8;
  if(next<(short?16:8)||next>=(short?240:108))scroll=signed(-v);
  let error=signed8((short?123:56)-(pos>>8));if(short)error>>=1;
  error=signed8(error-(unit>>3));const step=signed(error*8-v-scroll)>>5;
  return signed(scroll+step+(step>>1));
 };
 model.sx=camera(model.x,model.vx,model.sx,signed8(sine),true);
 model.sy=camera(model.y,model.vy,model.sy,signed8(cos),false);
 model.cx=(model.cx+model.sx)&0xffffff;model.cy=(model.cy+model.sy)&0xffffff;
 model.x=(model.x+model.vx+model.sx)&65535;model.y=(model.y+model.vy+model.sy)&65535;
 const px=((model.cx+128)>>8)&255,py=((model.cy+128)>>8)&255;
 const dx=signed8(px-model.px),dy=-signed8(py-model.py);model.px=px;model.py=py;
 for(const star of stars){
  if(star[0]+dx<0||star[0]+dx>255||star[1]+dy<0||star[1]+dy>=192)starWraps++;
  star[0]=(star[0]+dx+256)%256;star[1]=(star[1]+dy+192)%192;
 }

}
function compose(){
 assert.equal(word(0x7870),model.x);assert.equal(word(0x7860),model.y);
 assert.equal(signed(word(0x7872)),model.vx);assert.equal(signed(word(0x7862)),model.vy);assert.equal(m.ram[0x7828],model.angle);
 assert.equal(signed(word(0x7874)),model.sx);assert.equal(signed(word(0x7864)),model.sy);
 assert.equal(word(0x7883)+m.ram[0x7885]*65536,model.cx);assert.equal(word(0x7880)+m.ram[0x7882]*65536,model.cy);
 const pix=new Uint8Array(6144),attr=new Uint8Array(6144).fill(7);
 for(let i=0;i<stars.length;i++){const [x,y]=stars[i];assert.equal(m.ram[0x7d00+i*5],x);assert.equal(m.ram[0x7d01+i*5],y);pix[off(x>>3,y)]|=128>>(x&7);}
 const x=model.x>>8,y=152-(model.y>>8),heading=((model.angle+4)&255)>>3,phase=x&7;
 headings.add(heading);phases.add(phase);
 for(const [key,value] of [['x',x],['y',y],['cameraX',model.sx],['cameraY',model.sy]]){ranges[key][0]=Math.min(ranges[key][0],value);ranges[key][1]=Math.max(ranges[key][1],value);}
 for(const [sx,sy] of stars)if(sx>=(x>>3)*8&&sx<(x>>3)*8+24&&sy>=y&&sy<y+12)overlaps++;
 assert.ok(x>=0&&x+24<256&&y>=0&&y+12<192);
 const data=sprites[heading][phase];let p=0;
 for(let dy=0;dy<12;dy++)for(let dx=0;dx<3;dx++){
  const mask=data[p++],bits=data[p++],color=data[p++],o=off((x>>3)+dx,y+dy);
  if(mask!==255){pix[o]=(pix[o]&mask)|bits;attr[o]=color;}
 }
 return {pix,attr};
}
const writer=m.bus.write;m.bus.write=(a,v)=>{
 if(m.cpu.pc>=0x8000&&m.cpu.pc<0xa000){
  if(m.portF4&(1<<(a>>13)))romWrites++;
  if(expected&&((a>=0x4000&&a<0x5800)||(a>=0x6000&&a<0x7800))){
   if(v===m.ram[a])unchanged++;
   if(v!==(a<0x6000?expected.pix:expected.attr)[a&8191])wrongWrites++;
  }
 }
 writer(a,v);
};
const reader=m.bus.read;m.bus.read=a=>{
 if(a===m.cpu.pc){
  if(a===symbols.frame_start){start=m.tstates;update();}
  if(a===symbols.ready)prepared=m.tstates-start;
  if(a===symbols.publish){expected=compose();publishTime=m.tstates;}
  if(a===symbols.frame_done){
   assert.deepEqual(m.ram.slice(0x4000,0x5800),expected.pix,`bitmap frame ${done}`);
   assert.deepEqual(m.ram.slice(0x6000,0x7800),expected.attr,`attributes frame ${done}`);
   assert.equal(m.portF4,16);assert.equal(m.portFF,2);assert.equal(m.cpu.sp,0x7fff);
   const frame=Math.floor(m.tstates/58688);
   if(lastEnd!==null)cadence[frame-lastEnd]=(cadence[frame-lastEnd]||0)+1;
   lastEnd=frame;maxPublish=Math.max(maxPublish,m.tstates-publishTime);maxWork=Math.max(maxWork,prepared+m.tstates-publishTime);done++;model.frame++;
  }
 }
 return reader(a);
};
for(let f=0;f<2400;f++){
 api.runFrame(m);
 if(done>1){
  let bad=0;
  for(let y=0;y<192;y++)for(let x=0;x<256;x++){
   const o=off(x>>3,y),a=expected.attr[o],v=expected.pix[o]&(128>>(x&7))?a&7:(a>>3)&7;
   if(m.pixels[(y+24)*640+64+x*2]!==v||m.pixels[(y+24)*640+65+x*2]!==v)bad++;
  }
  if(bad){rasterBad++;rasterPixels+=bad;}
 }
 if(f===700)fs.writeFileSync(path.join(root,'build/flight-screen.ram'),m.ram);
}
const report={dck_sha256:createHash('sha256').update(cartridge).digest('hex'),frames:done,cadence,max_work_tstates:maxWork,max_publish_tstates:maxPublish,wrong_display_writes:wrongWrites,unchanged_display_writes:unchanged,rom_writes:romWrites,raster_mismatch_frames:rasterBad,raster_mismatch_pixels:rasterPixels,headings:headings.size,pixel_phases:phases.size,star_wraps:starWraps,star_ship_overlaps:overlaps,ranges};
fs.writeFileSync(path.join(root,'build/flight-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(report);
assert.ok(done>2000);assert.deepEqual(Object.keys(cadence),['1']);assert.equal(wrongWrites+unchanged+romWrites+rasterBad,0);
assert.equal(headings.size,32);assert.equal(phases.size,8);
