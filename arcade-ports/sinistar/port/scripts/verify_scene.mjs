import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const upstream=path.resolve(root,'../../../TSRun');
const api=await import(pathToFileURL(path.join(upstream,'machine.js')));
const read=n=>fs.readFileSync(path.join(root,n));
const symbols=Object.fromEntries([...read('build/scene-symbols.txt').toString().matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const inputKeys=new Uint8Array(8).fill(31);
const inputJoy=new Uint8Array(2).fill(255);
const m=api.createMachine(inputKeys,inputJoy);
const controls=process.argv.includes('--controls');let manual=false;
m.homeRom.set(fs.readFileSync(path.join(upstream,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(upstream,'roms/ts2068-1.rom')));
const cartridge=read('build/sinistar-pursuit.dck');assert.equal(api.insertDock(m,cartridge),null);api.resetMachine(m);
const signed=x=>(x<<16)>>16,signed8=x=>(x<<24)>>24;
const off=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;
const word=a=>m.ram[a]+256*m.ram[a+1];
const table=JSON.parse(read('build/player-tables.json')).SINETBL;
const sprites=Array.from({length:32},(_,h)=>Array.from({length:8},(_,p)=>fs.readFileSync(path.join(root,`../assets/ship-${String(h).padStart(2,'0')}-${p}.bin`))));
let model={x:0x7b00,y:0x3800,vx:0,vy:0,sx:0,sy:0,cx:0,cy:0,px:0,py:0,angle:0,frame:0};
const stars=JSON.parse(read('build/star-seeds.json'));
let starWraps=0,overlaps=0,faceFrames=0,faceOverlaps=0,physicsSteps=0;
model.stun=0;let stoppedTicks=0;
model.siniX=0x4000;model.siniY=0x4800;model.siniVX=0;model.siniVY=0;
const faces=Array.from({length:8},(_,p)=>fs.readFileSync(path.join(root,`../assets/face-00-${p}.bin`))); const ranges={x:[256,0],y:[192,0],cameraX:[0,0],cameraY:[0,0]};
let expected=null,done=0,start=0,prepared=0,publishTime=0,lastEnd=null,maxWork=0,maxPublish=0,wrongWrites=0,unchanged=0,romWrites=0,rasterBad=0,rasterPixels=0;
const stress=process.argv.includes('--stress');let probes=0,pathTransitions=0,lastPath=null;
let relativeHits=0;
const renderPaths={};
const cadence={},headings=new Set(),phases=new Set();
const detail={};let detailAt=0,detailName='';
const preparation={background_and_face:0,player:0,compile:0};let stageAt=0,phaseName='';
function update(){
 let target=(model.frame>>1)&255,power=true;
 if(controls&&model.frame>=1024){
  inputKeys.fill(31);inputJoy.fill(255);
  const step=Math.floor((model.frame-1024)/128)%10;
  if(step<8){
   manual=true;target=step*32;
   if([0,1,7].includes(step))inputKeys[2]&=~1;
   if([3,4,5].includes(step))inputKeys[1]&=~1;
   if([5,6,7].includes(step))inputKeys[5]&=~2;
   if([1,2,3].includes(step))inputKeys[5]&=~1;
   if(Math.floor((model.frame-1024)/1280)%2){
    let mask=0;if(!(inputKeys[2]&1))mask|=1;if(!(inputKeys[1]&1))mask|=2;
    if(!(inputKeys[5]&2))mask|=4;if(!(inputKeys[5]&1))mask|=8;
    inputJoy[0]=255^mask;inputKeys.fill(31);
   }
  }else if(step===8){target=model.angle;power=false;}
  else{inputKeys[1]&=~4;manual=false;}
 }
 const delta=signed8(target-model.angle);
 model.angle=(model.angle+Math.floor((delta*127+128)/256))&255;
 const a=model.angle,q=a>>6,p=a&63;
 let sine=q&1?table[63-p]:table[p],cos=q&1?table[p]:table[63-p];
 if(q>=2)sine=sine^255;if(q===1||q===2)cos=cos^255;
 if(power&&((delta+32)&255)<64){
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

 const speedTable=[[32767,2047,5],[4000,4096,4],[1024,128,1],[600,320,5],[80,256,3],[64,192,4],[32,128,4],[16,96,3],[0,64,2]];
 const chase=(desired,target)=>{
  if((desired<0)!==(target<0))return desired;
  let sum=signed(desired+target);
  if(desired>=0)return sum>2047?2047:sum;
  return signed(Math.abs(sum))>2047?-2047:sum;
 };
 model.siniX=(model.siniX+model.sx)&65535;model.siniY=(model.siniY+model.sy)&65535;
 if((model.frame&1023)===512)model.stun=61;
 if(model.stun)model.stun--;
 if(model.stun){model.siniVX=0;model.siniVY=0;stoppedTicks++;}
 else for(const [pos,v,target,targetV,multiple] of [['siniY','siniVY','y','vy',2],['siniX','siniVX','x','vx',1]]){
  const distance=((model[pos]>>8)-(model[target]>>8))*multiple;
  const mag=speedTable.find(r=>Math.abs(distance)>=r[0])[1];
  const shift=speedTable.find(r=>mag>=r[1])[2];
  const desired=chase((distance<0?mag:-mag)*(multiple===1?2:1),model[targetV]);
  const diff=signed(desired-model[v]);
  if(diff)model[v]=signed(model[v]+((diff>>shift)|1));
  model[pos]=(model[pos]+model[v])&65535;
 }
 model.frame++;physicsSteps++;

}
function compose(){
 assert.equal(word(0x7870),model.x);assert.equal(word(0x7860),model.y);
 assert.equal(signed(word(0x7872)),model.vx);assert.equal(signed(word(0x7862)),model.vy);assert.equal(m.ram[0x7828],model.angle);
 assert.equal(signed(word(0x7874)),model.sx);assert.equal(signed(word(0x7864)),model.sy);
 assert.equal(word(0x7883)+m.ram[0x7885]*65536,model.cx);assert.equal(word(0x7880)+m.ram[0x7882]*65536,model.cy);
 const pix=new Uint8Array(6144),attr=new Uint8Array(6144).fill(7);
 for(let i=0;i<stars.length;i++){const [x,y]=stars[i];assert.equal(m.ram[0x7e00+i*5],x);assert.equal(m.ram[0x7e01+i*5],y);pix[off(x>>3,y)]|=128>>(x&7);}

 assert.equal(word(0x7890),model.siniX);assert.equal(word(0x7892),model.siniY);
 assert.equal(signed(word(0x7894)),model.siniVX);assert.equal(signed(word(0x7896)),model.siniVY);
 const fx=(model.siniX>>8)-24,fy=126-(model.siniY>>8);
 if(fx>=0&&fx<200&&fy>=40&&fy<133){
  faceFrames++;
  const face=faces[fx&7];let p=0;
  for(let dy=0;dy<52;dy++)for(let dx=0;dx<7;dx++){
   const mask=face[p++],bits=face[p++],color=face[p++],o=off((fx>>3)+dx,fy+dy);
   if(mask!==255){pix[o]=(pix[o]&mask)|bits;attr[o]=color;}
  }
  if((model.x>>8)<fx+49&&(model.x>>8)+12>fx&&152-(model.y>>8)<fy+52&&164-(model.y>>8)>fy)faceOverlaps++;
 }
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
let fallbackFrames=0,maxFallbackBytes=0,maxListBytes=0;let appActive=false;
const writer=m.bus.write;m.bus.write=(a,v)=>{
 if(appActive){
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
  if(a===symbols.start)appActive=true;
  if(a===symbols.flight_step)update();
  if(a===symbols.frame_start){
   if(stress&&done>0&&done%120===0){
    const k=probes++%6;
    let x=[17,185,19,187,model.x>>8,Math.min(190,(model.x>>8)+16)][k];
    let y=[48,120,120,40,Math.max(40,(152-(model.y>>8))-20),Math.max(40,(152-(model.y>>8))-20)][k];
    model.siniX=(x+24)<<8;model.siniY=(126-y)<<8;model.siniVX=0;model.siniVY=0;
    for(const [addr,value] of [[symbols.sx,model.siniX],[symbols.sy,model.siniY],[symbols.svx,0],[symbols.svy,0]]){m.ram[addr]=value&255;m.ram[addr+1]=(value>>8)&255;}
   }
   detailAt=m.tstates;detailName='bounds';start=m.tstates;stageAt=m.tstates;phaseName='background_and_face';}
  if([symbols.erase_start,symbols.list_start,symbols.composition_start,symbols.scene_player].includes(a)){detail[detailName]=Math.max(detail[detailName]||0,m.tstates-detailAt);detailAt=m.tstates;detailName=a===symbols.erase_start?'erase':a===symbols.list_start?'list':'face';}
  if(a===symbols.scene_player||a===symbols.compile_scene||a===symbols.ready){
   preparation[phaseName]=Math.max(preparation[phaseName],m.tstates-stageAt);stageAt=m.tstates;
   phaseName=a===symbols.scene_player?'player':a===symbols.compile_scene?'compile':'';
  }
  if(a===symbols.ready)prepared=m.tstates-start;
  if(a===symbols.publish){
   expected=compose();publishTime=m.tstates;
   if(m.ram[0x78ed]){relativeHits++;assert.ok(m.ram[0x78d6]);}
   const renderPath=(m.ram[0x78d6]?'separated':'overlap')+(m.ram[0x78d0]?'_fallback':'_rows');
   renderPaths[renderPath]=(renderPaths[renderPath]||0)+1;
   if(lastPath!==null&&lastPath!==renderPath)pathTransitions++;lastPath=renderPath;
   const faceRects=[symbols.oldface,symbols.newface].filter(p=>m.ram[p+2]).map(p=>[m.ram[p],m.ram[p]+7,m.ram[p+1],m.ram[p+1]+52]);
   const shipRects=[symbols.oldxy,symbols.newxy].map(p=>[m.ram[p],m.ram[p]+3,m.ram[p+1],m.ram[p+1]+12]);
   const envelope=rs=>[Math.min(...rs.map(r=>r[0])),Math.max(...rs.map(r=>r[1])),Math.min(...rs.map(r=>r[2])),Math.max(...rs.map(r=>r[3]))];
   const fenv=envelope(faceRects),penv=envelope(shipRects);
   const separate=faceRects.length>0&&(fenv[1]<=penv[0]||penv[1]<=fenv[0]||fenv[3]<=penv[2]||penv[3]<=fenv[2])&&[fenv,penv].every(r=>r[1]-r[0]<=10&&r[3]-r[2]<=64);
   assert.equal(Boolean(m.ram[0x78d6]),separate,'dynamic fast-path selection');
   if(separate){
    assert.deepEqual(Array.from(m.ram.slice(0x78e0,0x78e8)),[...fenv,...penv]);
    const [ax,bx,ay,by,cx,dx,cy,dy]=m.ram.slice(0x78e0,0x78e8);
    assert.ok(bx<=cx||dx<=ax||by<=cy||dy<=ay,'old/new cell envelopes must be disjoint');
   }
   const end=word(0x78b4);
   assert.ok(end>=0xeb00&&end+2<=0xf000,'threaded records fit below fallback code');
   assert.equal((end-0xeb00)%6,0);assert.equal(word(end),symbols.publication_done);
   maxListBytes=Math.max(maxListBytes,end-0xeb00+2);
   if(m.ram[0x78d0]||m.ram[0x78d6]){
    if(m.ram[0x78d0])fallbackFrames++;
    const codeEnd=word(0x78d4);
    assert.ok(codeEnd>=0xf000&&codeEnd<0xffff);
    assert.equal((codeEnd-0xf000)%5,0);assert.equal(m.ram[codeEnd],0xc9);
    for(let p=0xf000;p<codeEnd;p+=5){
     assert.equal(m.ram[p],0x21);assert.equal(m.ram[p+3],0x36);
     const dest=word(p+1);
     assert.ok((dest>=0x4000&&dest<0x5800)||(dest>=0x6000&&dest<0x7800));
     if(!m.ram[0x78d0])assert.ok(dest>=0x6000,'separated sparse list contains attributes only');
    }
    maxFallbackBytes=Math.max(maxFallbackBytes,codeEnd-0xf000+1);
   }
   if(!m.ram[0x78d0]) {
    for(let p=0xeb00;p<end;p+=6){
     const handler=word(p),dst=word(p+2),src=word(p+4);
     assert.ok(handler===symbols.star_publish||Array.from({length:33},(_,i)=>[symbols['scan_'+i],symbols['mono_'+i]]).flat().includes(handler));
     assert.ok(dst>=0x4000&&dst<0x5800);assert.equal(src,dst+0x6000);
    }
   }

  }
  if(a===symbols.frame_done){
   assert.deepEqual(m.ram.slice(0x4000,0x5800),expected.pix,`bitmap frame ${done}`);
   assert.deepEqual(m.ram.slice(0x6000,0x7800),expected.attr,`attributes frame ${done}`);
   assert.equal(m.portF4,16);assert.equal(m.portFF,2);assert.equal(m.cpu.sp,0x7fff);
   const frame=Math.floor(m.tstates/58688);
   if(lastEnd!==null)cadence[frame-lastEnd]=(cadence[frame-lastEnd]||0)+1;
   lastEnd=frame;maxPublish=Math.max(maxPublish,m.tstates-publishTime);maxWork=Math.max(maxWork,prepared+m.tstates-publishTime);done++;
  }
 }
 return reader(a);
};
const testFrames=Number(process.argv[2]||2400);
for(let f=0;f<testFrames;f++){
 api.runFrame(m);
 const rasterExpected=expected;
 if(done>1&&rasterExpected){
  let bad=0;
  for(let y=0;y<192;y++)for(let x=0;x<256;x++){
   const o=off(x>>3,y),a=rasterExpected.attr[o],v=rasterExpected.pix[o]&(128>>(x&7))?a&7:(a>>3)&7;
   if(m.pixels[(y+24)*640+64+x*2]!==v||m.pixels[(y+24)*640+65+x*2]!==v)bad++;
  }
  if(bad){rasterBad++;rasterPixels+=bad;}
 }
 if(f===700)fs.writeFileSync(path.join(root,'build/scene-screen.ram'),m.ram);
}
const elapsed=Object.entries(cadence).reduce((s,[k,v])=>s+Number(k)*v,0);
assert.ok(stoppedTicks>0);
const report={stopped_ticks:stoppedTicks,relative_transition_frames:relativeHits,stress_probes:probes,path_transitions:pathTransitions,render_paths:renderPaths,test_refreshes:testFrames,detail,fallback_frames:fallbackFrames,max_threaded_list_bytes:maxListBytes,max_fallback_code_bytes:maxFallbackBytes,dck_sha256:createHash('sha256').update(cartridge).digest('hex'),frames:done,cadence,average_visible_fps:3528000/58688*(done-1)/elapsed,max_work_tstates:maxWork,max_publish_tstates:maxPublish,max_preparation_phase_tstates:preparation,wrong_display_writes:wrongWrites,unchanged_display_writes:unchanged,rom_writes:romWrites,raster_mismatch_frames:rasterBad,raster_mismatch_pixels:rasterPixels,headings:headings.size,pixel_phases:phases.size,physics_steps:physicsSteps,face_frames:faceFrames,face_ship_overlaps:faceOverlaps,star_wraps:starWraps,star_ship_overlaps:overlaps,ranges};
fs.writeFileSync(path.join(root,controls?'build/scene-controls-verification.json':stress?'build/scene-separated-stress.json':'build/scene-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(report);
assert.ok(done>100&&faceFrames>100&&faceOverlaps>0);assert.equal(wrongWrites+unchanged+romWrites+rasterBad,0);
assert.equal(headings.size,32);assert.equal(phases.size,8);

if(stress){assert.ok(probes>=6);assert.ok(renderPaths.separated_rows>20);assert.ok(pathTransitions>10);}
