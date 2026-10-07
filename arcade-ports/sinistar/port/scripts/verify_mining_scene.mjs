import {acceptTitle} from './accept_title.mjs';
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
const cartridge=read('build/sinistar-mining.dck');assert.equal(api.insertDock(m,cartridge),null);api.resetMachine(m);acceptTitle(m,symbols);
const assets=JSON.parse(read('build/mining-assets.json'));
const expiryTest=process.argv.includes("--expiry");let expirySupplied=false;
const bombTest=process.argv.includes("--bombs");
let speechFrames=0,verifiedAyWrites=0,speechClip=null,speechOffset=0;const voiceFrames=[0,0,0];
const captureAudio=process.argv.includes('--audio'),audio=[];
if(captureAudio){api.setSoundRate(m,22050);api.enableSound(m,true);}
const ioWriter=m.bus.ioWrite;
m.bus.ioWrite=(port,value)=>{
 if((port&255)===0xf6&&speechFrames>0&&m.ram[symbols.speech_left]>0){
  assert.ok(m.ayLatch<14);
  assert.equal(value,speechClip.data[speechOffset+m.ayLatch]);verifiedAyWrites++;
 }
 ioWriter(port,value);
};
const transitionTest=process.argv.includes('--transitions');
let transitionStarted=false, transitionStep=0, transitionInjectedFrame=-1, transitionExpected=null, fastFrames=0, transitionCases=0, overlapFallbacks=0;
const transitionCasesData=[];
for(let eye=0;eye<3;eye++)for(let phase=0;phase<8;phase++)for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++)transitionCasesData.push({eye,phase,dx,dy});
const eyeTest=process.argv.includes('--eyes');
const coveredTest=process.argv.includes('--covered');
if(eyeTest){const base=transitionCasesData.splice(0);for(const t of base)for(let oldEye=0;oldEye<3;oldEye++)if(oldEye!==t.eye)transitionCasesData.push({...t,oldEye});}
const transitionLimit=transitionCasesData.length*4;
let eyeFastCases=0;
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
 if(transitionStarted)return;
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
 if(m.ram[symbols.sinistar_built]&&m.ram[symbols.bs_hits]<13)sprite('awakening',3*m.ram[symbols.eye_phase]+m.ram[symbols.awake_mouth],m.ram[symbols.face_x+1],m.ram[symbols.face_y+1],7,52);
 else if(!m.ram[symbols.sinistar_built]&&m.ram[symbols.assembly_count])sprite('assembly',m.ram[symbols.assembly_count]-1,192,80,7,52);
 if(m.ram[symbols.rock_alive])sprite('rock',m.ram[symbols.rock_x]&7,m.ram[symbols.rock_x],100,5,28);
 if(m.ram[symbols.worker_alive])sprite('worker',m.ram[symbols.worker_x]&7,m.ram[symbols.worker_x],m.ram[symbols.worker_y],3,12);
 if(m.ram[symbols.crystal_alive])sprite('crystal',m.ram[symbols.cx+1]&7,m.ram[symbols.cx+1],m.ram[symbols.cy+1],2,4);
 if(m.ram[symbols.bullet_alive])sprite('bullet',m.ram[symbols.bx+1]&7,m.ram[symbols.bx+1],m.ram[symbols.by+1],2,2);
 const x=m.ram[symbols.px+1],y=m.ram[symbols.py+1];
 if(m.ram[symbols.rects+14])sprite('ship',(((m.ram[symbols.angle]+4)&248)|(x&7)),x,y,3,12);
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
   speechClip=assets.find(a=>a.kind==='speech'&&a.index===m.ram[symbols.speech_active]-1);
   assert.ok(speechClip);speechOffset=(ptr-speechClip.address)*2;
   assert.equal(speechOffset,speechClip.data.length-14*m.ram[symbols.speech_left]);
   assert.equal((ptr-speechClip.address)%7,0);
   voiceFrames[speechClip.index]++;
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

   if(expiryTest&&m.ram[symbols.bs_hits]===13&&!expirySupplied){m.ram[symbols.bombs]=1;expirySupplied=true;}

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
  if(a===symbols.render&&transitionTest&&m.ram[symbols.awake_done]&&!m.ram[symbols.speech_left]&&transitionStep<transitionLimit&&transitionInjectedFrame!==frames){
   transitionStarted=true;transitionInjectedFrame=frames;
   const index=Math.floor(transitionStep/4),part=transitionStep%4,t=transitionCasesData[index];
   const x=64+t.phase,y=[65,71,79,95,111,123][index%6];
   for(const name of ['rock_alive','crystal_alive','bullet_alive','worker_alive','bs_active'])m.ram[symbols[name]]=0;
   m.ram[symbols.face_x]=0;m.ram[symbols.face_x+1]=x+(part?t.dx:0);
   m.ram[symbols.face_y]=0;m.ram[symbols.face_y+1]=y+(part?t.dy:0);
   m.ram[symbols.eye_phase]=eyeTest&&part===0?t.oldEye:t.eye;m.ram[symbols.awake_mouth]=0;
   m.ram[symbols.px]=0;m.ram[symbols.py]=0;
   m.ram[symbols.px+1]=part===2?x+t.dx+16:232;
   m.ram[symbols.py+1]=part===2?y+t.dy+20:152;
   if(coveredTest){m.ram[0x5bcb]=1;if(part===1){m.ram[symbols.px+1]=x+t.dx+16;m.ram[symbols.py+1]=y+t.dy+20;}if(part===2)m.ram[symbols.px+1]=x+t.dx-8;}
   transitionExpected=part===1?(eyeTest?null:1):part>=2?0:null;
  }
  if(a===symbols.publish){
   if(m.ram[0x78f6]){
    fastFrames++;
    const [x0,x1,y0,y1,w,h]=m.ram.subarray(0x5800,0x5806);
    assert.ok(w>=7&&w<=8&&h>=52&&h<=53&&y0>=64);
    for(const base of [symbols.rects,symbols.oldrects])for(let i=0;i<7;i++){
     if(i===5)continue;
     const [x,y,rw,rh]=m.ram.subarray(base+i*4,base+i*4+4);
     assert.ok(!rw||x>=x1||x+rw<=x0||y>=y1||y+rh<=y0,'Fast path overlaps object');
    }
    assert.ok(word(0x78f0)-0xe000<word(0x580c));
    assert.ok(m.ram[0x582a]<=106&&word(0x5834)>=0xd800&&word(0x5834)<=0xdb00||m.ram[0x582a]===0);
   }
   if(transitionStarted&&transitionStep<transitionLimit){
    if(transitionExpected!==null)assert.equal(m.ram[0x78f6],transitionExpected,JSON.stringify({step:transitionStep,case:transitionCasesData[Math.floor(transitionStep/4)]}));
    if(transitionStep%4===1){transitionCases++;if(m.ram[0x78f6]&&eyeTest)eyeFastCases++;}
    if(transitionExpected===0)overlapFallbacks++;
   }
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
   const start=word(0x7bb2),bytes=0xfffe-start;
   assert.ok(start>=0xe200 && !(bytes&3),'packed records leave stack headroom');
   assert.equal(word(0x78f0)-0xe000,bytes/4*7,'publication budget');
   maxCode=Math.max(maxCode,bytes);
   const destinations=new Set();
   for(let p=start;p<0xfffe;p+=4){
    const dest=word(p+2),value=m.ram[p+1];
    assert.ok((dest>=0x4000&&dest<0x5800)||(dest>=0x6000&&dest<0x7800));
    assert.ok(!destinations.has(dest),'one final record per changed byte');destinations.add(dest);
    assert.notEqual(m.ram[dest],value,'only changed bytes emitted');
    assert.equal(value,dest<0x6000?expected.pix[dest-0x4000]:expected.attr[dest-0x6000]);
   }
  }
  if(a===symbols.publication_done){
   if(transitionStarted&&transitionStep<transitionLimit)transitionStep++;
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
assert.equal(voiceFrames[0],playerOnly?0:125);
if(bombTest){assert.equal(m.ram[symbols.bs_hits],13);assert.equal(m.ram[symbols.bs_fired],expiryTest?14:13);if(expiryTest)assert.equal(m.ram[symbols.bs_expired],1);assert.equal(m.ram[symbols.bombs],0);}
if(transitionTest)assert.equal(transitionCases,transitionCasesData.length);
if(eyeTest)assert.ok(eyeFastCases>0,'eye-changing direct updates exercised');
const report={eye_fast_cases:eyeFastCases,voice_frames:voiceFrames,fast_frames:fastFrames,transition_cases:transitionCases,overlap_fallbacks:overlapFallbacks,verified_ay_writes:verifiedAyWrites,speech_frames:speechFrames,bombs_fired:m.ram[symbols.bs_fired],bomb_hits:m.ram[symbols.bs_hits],pursuit_positions:facePositions.size,eye_frames:[...eyes],awakening_ticks:wakeTicks,mouth_frames:[...mouths],assembly_stages:[...stages],dck_sha256:createHash('sha256').update(cartridge).digest('hex'),refreshes,frames,relocation_probes:probes,physics_steps:steps,hits:m.ram[symbols.hits],releases:m.ram[symbols.releases],collected:m.ram[symbols.bombs],shattered:m.ram[symbols.shattered],assembly_pieces:m.ram[symbols.assembly_count],worker_pickups:m.ram[symbols.worker_pickups],worker_deliveries:m.ram[symbols.worker_deliveries],wrong,unchanged,romWrites,rasterBad,max_packed_record_bytes:maxCode,max_publication_tstates:maxPublication};
console.log(report);assert.equal(wrong+unchanged+romWrites+rasterBad,0);assert.ok(frames>100&&report.hits>0&&report.releases>0&&(playerOnly?report.collected===1&&report.worker_deliveries===0:report.worker_deliveries===20)&&report.shattered===1);
fs.writeFileSync(path.join(root,coveredTest?'build/mining-covered-verification.json':eyeTest?'build/mining-eyes-verification.json':transitionTest?'build/mining-transitions-verification.json':expiryTest?'build/mining-bomb-expiry-verification.json':bombTest?'build/mining-bombs-verification.json':playerOnly?'build/mining-player-verification.json':controls?'build/mining-controls-verification.json':'build/mining-scene-verification.json'),JSON.stringify(report,null,2)+'\n');

if(captureAudio){
 const pcm=Buffer.alloc(audio.length*2);audio.forEach((v,i)=>pcm.writeInt16LE(v,i*2));
 const wav=Buffer.alloc(44);wav.write('RIFF');wav.writeUInt32LE(36+pcm.length,4);wav.write('WAVEfmt ',8);wav.writeUInt32LE(16,16);wav.writeUInt16LE(1,20);wav.writeUInt16LE(1,22);wav.writeUInt32LE(22050,24);wav.writeUInt32LE(44100,28);wav.writeUInt16LE(2,32);wav.writeUInt16LE(16,34);wav.write('data',36);wav.writeUInt32LE(pcm.length,40);
 fs.writeFileSync(path.join(root,'build/mining-assembly-speech.wav'),Buffer.concat([wav,pcm]));
}
