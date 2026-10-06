import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const upstream=path.resolve(root,'../../../TSRun');
const api=await import(pathToFileURL(path.join(upstream,'machine.js')));
const read=n=>fs.readFileSync(path.join(root,n));
const symbols=Object.fromEntries([...read('build/mining-symbols.txt').toString().matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const keys=new Uint8Array(8).fill(31),joy=new Uint8Array(2).fill(255);
const m=api.createMachine(keys,joy);
m.homeRom.set(fs.readFileSync(path.join(upstream,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(upstream,'roms/ts2068-1.rom')));
const cartridge=read('build/sinistar-mining.dck');assert.equal(api.insertDock(m,cartridge),null);api.resetMachine(m);
const assets=JSON.parse(read('build/mining-assets.json'));
const expiryTest=process.argv.includes("--expiry");let expirySupplied=false;
const bombTest=process.argv.includes("--bombs");
let speechFrames=0,verifiedAyWrites=0;
const captureAudio=process.argv.includes('--audio'),audio=[];
if(captureAudio){api.setSoundRate(m,22050);api.enableSound(m,true);}
const ioWriter=m.bus.ioWrite;
m.bus.ioWrite=(port,value)=>{
 if((port&255)===0xf6&&speechFrames>0&&m.ram[symbols.speech_left]>0){
  assert.ok(m.ayLatch<14);
  assert.equal(value,assets.find(a=>a.kind==='speech').data[(speechFrames-1)*14+m.ayLatch]);verifiedAyWrites++;
 }
 ioWriter(port,value);
};
const controls=process.argv.includes('--controls');
const playerOnly=process.argv.includes('--player');
const word=a=>m.ram[a]+256*m.ram[a+1];
const off=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;
let expected=null,frames=0,wrong=0,unchanged=0,romWrites=0,rasterBad=0,maxCode=0,maxPublication=0,publishAt=0,active=false,steps=0,probes=0;
const stages=new Set(),mouths=new Set(),eyes=new Set(),facePositions=new Set();
const wakeSequence=JSON.parse(read('build/awakening-sequence.json'));
let eyeTicks=0;
let wakeModel={index:0,timer:0,mouth:0,done:0},wakeTicks=0;
function checkWake(){
 assert.equal(m.ram[symbols.eye_phase],Math.floor(eyeTicks/16)%3);
 assert.equal(m.ram[symbols.eye_timer],eyeTicks%16);
 for(const [field,symbol] of [['index','awake_index'],['timer','awake_timer'],['mouth','awake_mouth'],['done','awake_done']])assert.equal(m.ram[symbols[symbol]],field==='index'?wakeModel[field]*2:wakeModel[field],symbol);
}
let lastAssembly=0;
function compose(){
 const pix=new Uint8Array(6144),attr=new Uint8Array(6144).fill(7);
 function sprite(kind,index,x,y,w,h){
  let data=assets.find(a=>a.kind===kind&&a.index===index).data;
  if(kind==='awakening'&&m.ram[symbols.awake_done]&&(x&7)){
   const original=data;data=[...data];const shift=x&7;
   for(let r=0;r<h;r++)for(let c=0;c<w;c++){
    const i=(r*w+c)*3;
    data[i]=((original[i]>>>shift)|((c?original[i-3]:255)<<(8-shift)))&255;
    data[i+1]=((original[i+1]>>>shift)|((c?original[i-2]:0)<<(8-shift)))&255;
   }
  }
  for(let r=0;r<h;r++)for(let c=0;c<w;c++){
   const i=(r*w+c)*3,o=off((x>>3)+c,y+r);if(data[i]===255)continue;
   pix[o]=(pix[o]&data[i])|data[i+1];attr[o]=data[i+2];
  }
 }
 if(m.ram[symbols.sinistar_built]&&m.ram[symbols.bs_hits]<12)sprite('awakening',3*m.ram[symbols.eye_phase]+m.ram[symbols.awake_mouth],m.ram[symbols.face_x+1],m.ram[symbols.face_y+1],7,52);
 else if(!m.ram[symbols.sinistar_built]&&m.ram[symbols.assembly_count])sprite('assembly',m.ram[symbols.assembly_count]-1,192,80,7,52);
 if(m.ram[symbols.rock_alive])sprite('rock',m.ram[symbols.rock_x]&7,m.ram[symbols.rock_x],100,5,28);
 if(m.ram[symbols.worker_alive])sprite('worker',m.ram[symbols.worker_x]&7,m.ram[symbols.worker_x],m.ram[symbols.worker_y],3,12);
 if(m.ram[symbols.crystal_alive])sprite('crystal',m.ram[symbols.cx+1]&7,m.ram[symbols.cx+1],m.ram[symbols.cy+1],2,4);
 if(m.ram[symbols.bullet_alive])sprite('bullet',m.ram[symbols.bx+1]&7,m.ram[symbols.bx+1],m.ram[symbols.by+1],2,2);
 const x=m.ram[symbols.px+1],y=m.ram[symbols.py+1];
 sprite('ship',(((m.ram[symbols.angle]+4)&248)|(x&7)),x,y,3,12);
 if(m.ram[symbols.bs_active])sprite('sinibomb',m.ram[symbols.bs_x]&7,m.ram[symbols.bs_x],m.ram[symbols.bs_y],2,6);
 return {pix,attr};
}
const writer=m.bus.write;m.bus.write=(a,v)=>{
 if(active&&(m.portF4&(1<<(a>>13))))romWrites++;
 if(expected&&((a>=0x4000&&a<0x5800)||(a>=0x6000&&a<0x7800))){
  if(v===m.ram[a])unchanged++;
  if(v!==(a<0x6000?expected.pix:expected.attr)[a&8191])wrong++;
 }
 writer(a,v);
};
const reader=m.bus.read;m.bus.read=a=>{
 if(a===m.cpu.pc){
  if(a===symbols.speech_bytes){
   const ptr=word(symbols.speech_ptr);
   assert.equal(ptr,symbols.speech_source+14*speechFrames);
   assert.deepEqual(Array.from({length:14},(_,i)=>reader(ptr+i)),assets.find(a=>a.kind==='speech').data.slice(14*speechFrames,14*speechFrames+14));
   speechFrames++;
  }
  if(a===symbols.start)active=true;
  if(a===symbols.awakening_step){
   checkWake();
   if(m.ram[symbols.sinistar_built])eyeTicks++;
   if(m.ram[symbols.sinistar_built]&&!wakeModel.done){
    wakeTicks++;
    if(wakeModel.timer>0)wakeModel.timer--;
    if(wakeModel.timer===0){
     const [mouth,duration]=wakeSequence[wakeModel.index];
     if(mouth===255)wakeModel.done=1;
     else {wakeModel.index++;wakeModel.mouth=mouth;wakeModel.timer=duration;}
    }
   }
  }
  if(a===symbols.game_step){
   steps++;
   if(steps===1){m.ram[symbols.game_mode]=0;m.ram[symbols.control_mode]=0;m.ram[symbols.bombs]=0;}

   if(expiryTest&&m.ram[symbols.bs_hits]===12&&!expirySupplied){m.ram[symbols.bombs]=1;expirySupplied=true;}

   if(bombTest&&m.ram[symbols.awake_done])keys[7]&=~16;
   if(playerOnly&&steps===1)m.ram[symbols.worker_alive]=0;
   if(controls&&steps>7000){
    keys.fill(31);joy.fill(255);const n=Math.floor((steps-7001)/128)%10;
    if(n<8){const bits=[1,9,8,10,2,6,4,5][n];joy[0]=255^bits;keys[7]&=~1;}
    else if(n===9)keys[1]&=~4;
   }
  }
  if(a===symbols.frame_start&&controls&&steps>7000&&frames%120===0){
   // Reintroduce the rock at all horizontal phases to exercise live-object
   // composition during manual flight, after the ordinary collection sequence.
   m.ram[symbols.rock_alive]=1;m.ram[symbols.rock_x]=144+(probes++%8);
   // Cross the installed piece at all eight player pixel phases.
   m.ram[symbols.px]=0;m.ram[symbols.px+1]=204+(probes%8);
   m.ram[symbols.py]=0;m.ram[symbols.py+1]=80;
   m.ram[symbols.mass]=96;m.ram[symbols.richter]=0;
  }
  if(a===symbols.publish){
   checkWake();
   if(m.ram[symbols.awake_done]){
    const x=m.ram[symbols.face_x+1],y=m.ram[symbols.face_y+1];
    assert.ok(x<=200&&y>=64&&y<=124);facePositions.add(`${x},${y}`);
   }
   const count=m.ram[symbols.assembly_count];
   if(m.ram[symbols.sinistar_built]){mouths.add(m.ram[symbols.awake_mouth]);eyes.add(m.ram[symbols.eye_phase]);}
   assert.equal(m.ram[symbols.sinistar_built],Number(count===20));
   assert.ok(count===lastAssembly||count===lastAssembly+1);lastAssembly=count;stages.add(count);
   assert.ok(count<=20);
   assert.equal(m.ram[symbols.assembly_count],m.ram[symbols.worker_deliveries]);
   const carrying=m.ram[symbols.crystal_alive]===2;
   assert.equal(m.ram[symbols.worker_pickups],m.ram[symbols.worker_deliveries]+Number(carrying));
   if(carrying){assert.equal(m.ram[symbols.worker_alive],1);assert.equal(m.ram[symbols.worker_mission],6);assert.equal(m.ram[symbols.cx+1],m.ram[symbols.worker_x]+4);assert.equal(m.ram[symbols.cy+1],m.ram[symbols.worker_y]-2);}
   expected=compose();publishAt=m.tstates;
   const fast=m.ram[0x78f6]===1;
   const base=fast?0x5800:0xe000;
   const bytes=word(0x78f0)-base+1;assert.ok(bytes>0&&bytes<=(fast?2048:8191),bytes);maxCode=Math.max(maxCode,bytes);
   for(let p=base;p<word(0x78f0);p+=fast?9:5){
    if(fast&&m.ram[p]===0x18){assert.equal(m.ram[p+1],16);p+=9;continue;}
    assert.equal(m.ram[p],0x21);assert.equal(m.ram[p+3],fast?0x11:0x36);
    if(fast){assert.equal(m.ram[p+6],0xcd);const target=word(p+7);assert.ok(target>=symbols.fast_cells&&target<symbols.fast_cells+32*7);assert.equal((target-symbols.fast_cells)%7,0);}
   }
  }
  if(a===symbols.publication_done){
   frames++;maxPublication=Math.max(maxPublication,m.tstates-publishAt);
   assert.deepEqual(m.ram.subarray(0x4000,0x5800),expected.pix);
   assert.deepEqual(m.ram.subarray(0x6000,0x7800),expected.attr);
   assert.equal(m.cpu.sp,0x7ffd);
  }
 }
 return reader(a);
};
const refreshes=Number(process.argv[2]||9000);
for(let f=0;f<refreshes;f++){
 api.runFrame(m);
 if(captureAudio){const a=api.takeAudio(m);if(speechFrames>0&&audio.length<22050*2.4)for(let i=0;i<a.n;i++)audio.push(Math.max(-32768,Math.min(32767,Math.round((a.a[i]+a.b[i]+a.c[i])*10000))));}
 if(expected&&frames>1){
  let bad=0;
  for(let y=0;y<192;y++)for(let x=0;x<256;x++){
   const o=off(x>>3,y),a=expected.attr[o],v=expected.pix[o]&(128>>(x&7))?a&7:(a>>3)&7;
   if(m.pixels[(y+24)*640+64+x*2]!==v||m.pixels[(y+24)*640+65+x*2]!==v)bad++;
  }
  if(bad)rasterBad++;
 }
}
if(!playerOnly)assert.deepEqual([...stages],Array.from({length:21},(_,i)=>i));
if(!playerOnly){assert.deepEqual([...mouths].sort(),[0,1,2]);assert.deepEqual([...eyes].sort(),[0,1,2]);assert.equal(m.ram[symbols.awake_done],1);}
if(!playerOnly&&!bombTest)assert.ok(facePositions.size>10);
assert.equal(speechFrames,playerOnly?0:assets.find(a=>a.kind==='speech').data.length/14);
if(bombTest){assert.equal(m.ram[symbols.bs_hits],12);assert.equal(m.ram[symbols.bs_fired],expiryTest?13:12);if(expiryTest)assert.equal(m.ram[symbols.bs_expired],1);assert.equal(m.ram[symbols.bombs],0);}
const report={verified_ay_writes:verifiedAyWrites,speech_frames:speechFrames,bombs_fired:m.ram[symbols.bs_fired],bomb_hits:m.ram[symbols.bs_hits],pursuit_positions:facePositions.size,eye_frames:[...eyes],awakening_ticks:wakeTicks,mouth_frames:[...mouths],assembly_stages:[...stages],dck_sha256:createHash('sha256').update(cartridge).digest('hex'),refreshes,frames,relocation_probes:probes,physics_steps:steps,hits:m.ram[symbols.hits],releases:m.ram[symbols.releases],collected:m.ram[symbols.bombs],shattered:m.ram[symbols.shattered],assembly_pieces:m.ram[symbols.assembly_count],worker_pickups:m.ram[symbols.worker_pickups],worker_deliveries:m.ram[symbols.worker_deliveries],wrong,unchanged,romWrites,rasterBad,max_code_bytes:maxCode,max_publication_tstates:maxPublication};
console.log(report);assert.equal(wrong+unchanged+romWrites+rasterBad,0);assert.ok(frames>100&&report.hits>0&&report.releases>0&&(playerOnly?report.collected===1&&report.worker_deliveries===0:report.worker_deliveries===20)&&report.shattered===1);
fs.writeFileSync(path.join(root,expiryTest?'build/mining-bomb-expiry-verification.json':bombTest?'build/mining-bombs-verification.json':playerOnly?'build/mining-player-verification.json':controls?'build/mining-controls-verification.json':'build/mining-scene-verification.json'),JSON.stringify(report,null,2)+'\n');

if(captureAudio){
 const pcm=Buffer.alloc(audio.length*2);audio.forEach((v,i)=>pcm.writeInt16LE(v,i*2));
 const wav=Buffer.alloc(44);wav.write('RIFF');wav.writeUInt32LE(36+pcm.length,4);wav.write('WAVEfmt ',8);wav.writeUInt32LE(16,16);wav.writeUInt16LE(1,20);wav.writeUInt16LE(1,22);wav.writeUInt32LE(22050,24);wav.writeUInt32LE(44100,28);wav.writeUInt16LE(2,32);wav.writeUInt16LE(16,34);wav.write('data',36);wav.writeUInt32LE(pcm.length,40);
 fs.writeFileSync(path.join(root,'build/mining-assembly-speech.wav'),Buffer.concat([wav,pcm]));
}
