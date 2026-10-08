import fs from 'node:fs';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const root=path.resolve('.'),upstream=path.resolve(process.env.TSRUN_ROOT||'../../TSRun');
const api=await import(pathToFileURL(path.join(upstream,'machine.js')));
const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));
m.homeRom.set(fs.readFileSync(path.join(upstream,'roms/ts2068-0.rom')));
m.exRom.set(fs.readFileSync(path.join(upstream,'roms/ts2068-1.rom')));
assert.equal(api.insertDock(m,fs.readFileSync('build/sinistar.dck')),null);
api.resetMachine(m);api.setSoundRate(m,22050);api.enableSound(m,true);
let writes=0,exactAudioWrites=0;const audioTimes=[];
const io=m.bus.ioWrite;m.bus.ioWrite=(p,v)=>{
 if((p&255)===246){
  writes++;
  if(m.ram[0x7805]&&m.ayLatch<13){
   const ptr=m.ram[0x7800]+256*m.ram[0x7801];
   assert.equal(v,m.ram[ptr+m.ayLatch],'Speech register stream mismatch');exactAudioWrites++;
   if(m.ayLatch===0)audioTimes.push(m.tstates);
  }
 }
 io(p,v);
};
const symbols=Object.fromEntries([...fs.readFileSync('build/symbols.txt','utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const rom=fs.readFileSync('build/sinistar-picorom.bin');
const scene=JSON.parse(fs.readFileSync('build/fast-scene.json'));
let verified=0,displayWrites=0,unchangedWrites=0,romWrites=0,expected=null;
let frameStarts=[],frameEnds=[];
const assetCache=new Map();
function reference(){
 const index=(m.ram[0x7814]+256*m.ram[0x7815])%scene.metadata.length;
 const frame=scene.metadata[index],pix=new Uint8Array(6144),attr=new Uint8Array(6144).fill(7);
 const protectedCell=(x,y)=>frame.rectangles.some(([rx,ry,w,h])=>x>=rx&&x<rx+w&&y>=ry&&y<ry+h);
 for(const [x,y] of frame.stars){
  if(!protectedCell(x>>3,y)){const o=y*32+(x>>3);pix[o]|=128>>(x&7);}
 }
 for(const kind of ['face','ship']){
  const [x,y,pose]=frame[kind],w=kind==='face'?7:3,h=kind==='face'?52:12;
  const name=`assets/${kind}-${String(pose).padStart(2,'0')}-${x%8}.bin`;
  if(!assetCache.has(name))assetCache.set(name,fs.readFileSync(name));
  const data=assetCache.get(name);let p=0;
  for(let dy=0;dy<h;dy++)for(let dx=0;dx<w;dx++){
   const mask=data[p++],bits=data[p++],color=data[p++],o=(y+dy)*32+(x>>3)+dx;
   if(mask!==255){pix[o]=(pix[o]&mask)|bits;attr[o]=color;}
  }
 }
 return {pix,attr,index};
}
const writer=m.bus.write;
m.bus.write=(addr,value)=>{
 if(m.cpu.pc>=0x8000&&m.cpu.pc<0xa000){
  if(m.portF4&(1<<(addr>>13)))romWrites++;
  if(expected&&((addr>=0x4000&&addr<0x5800)||(addr>=0x6000&&addr<0x7800))){
   displayWrites++;if(m.ram[addr]===value)unchangedWrites++;
   const off=addr&0x1fff,y=((off>>5)&0xc0)|((off>>8)&7)|((off>>2)&0x38),x=off&31;
   assert.equal(value,(addr<0x6000?expected.pix:expected.attr)[y*32+x],`Unfinished write frame ${expected.index} at ${addr.toString(16)}`);
  }
 }
 writer(addr,value);
};
const reader=m.bus.read;
m.bus.read=addr=>{
 if(m.cpu.pc===addr){
  if(addr===symbols.go)frameStarts.push(m.tstates);
  if(addr===symbols.no_speech)expected=reference();
  if(addr===symbols.frame_done){
   for(let y=0;y<192;y++)for(let x=0;x<32;x++){
    const o=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x,l=y*32+x;
    assert.equal(m.ram[0x4000+o],expected.pix[l],`Bitmap mismatch frame ${expected.index} at ${x},${y}`);
    assert.equal(m.ram[0x6000+o],expected.attr[l],`Attribute mismatch frame ${expected.index} at ${x},${y}`);
   }
   assert.equal(m.portF4,16);assert.equal(m.portFF,2);assert.ok(m.cpu.sp>=0x7e00&&m.cpu.sp<0x8000);
   verified++;frameEnds.push(m.tstates);
  }
 }
 return reader(addr);
};
let rasterMismatchFrames=0,rasterMismatchPixels=0;const rasterKinds={face:0,ship:0,other:0};const rasterExamples=[];
const reports=[],audio=[],cadence=[];let last=0,lastAt=0;
const video=process.argv.includes('--record')?fs.openSync('build/capture.rgb','w'):null;
fs.mkdirSync('build/capture',{recursive:true});
for(let f=0;f<2400;f++){
 api.runFrame(m);const a=api.takeAudio(m);
 if(expected&&verified>1){
  let bad=0;
  for(let y=0;y<192;y++)for(let x=0;x<256;x++){
   const off=y*32+(x>>3),att=expected.attr[off],want=(expected.pix[off]&(128>>(x&7)))?(att&7):((att>>3)&7);
   if(m.pixels[(y+24)*640+64+x*2]!==want||m.pixels[(y+24)*640+65+x*2]!==want){bad++;const rects=scene.metadata[expected.index].rectangles;const kind=rects.findIndex(([rx,ry,w,h])=>x>=rx*8&&x<(rx+w)*8&&y>=ry&&y<ry+h);rasterKinds[kind===0?'face':kind===1?'ship':'other']++;}
  }
  if(bad){rasterMismatchFrames++;rasterMismatchPixels+=bad;if(rasterExamples.length<12)rasterExamples.push({index:expected.index,bad});}
 }

 if(video!==null&&f%1===0){
  const rgb=Buffer.alloc(640*240*3);
  for(let j=0;j<m.pixels.length;j++){const c=m.pixels[j],v=204,br=c&8?51:0;rgb[j*3]=br+v*((c>>1)&1);rgb[j*3+1]=br+v*((c>>2)&1);rgb[j*3+2]=br+v*(c&1);}
  fs.writeSync(video,rgb);
 }
 for(let i=0;i<a.n;i++)audio.push(Math.max(-32768,Math.min(32767,Math.round((a.a[i]+a.b[i]+a.c[i])*10000))));
 const count=verified;
 if(count!==last){if(last)cadence.push(f-lastAt);last=count;lastAt=f;}
 if([250,320,480,700,1100,1500,2200].includes(f)){
   fs.writeFileSync(`build/capture/frame-${f}.ram`,m.ram);
   reports.push({frame:f,updates:count,pc:m.cpu?.pc,writes});
 }
}
assert.ok(last>200,'No sustained animation');assert.ok(writes>1000,'No speech');
if(video!==null)fs.closeSync(video);
const hist={};for(const v of cadence)hist[v]=(hist[v]||0)+1;
assert.equal(rasterMismatchPixels,0);assert.ok(cadence.every(n=>n===1), "Missed a video-frame update");
assert.equal(romWrites,0);assert.equal(unchangedWrites,0);
const withinClipGaps=audioTimes.slice(1).map((t,i)=>t-audioTimes[i]).filter(t=>t<352800);
const costs=frameEnds.map((t,i)=>t-frameStarts[i]);
const report={cartridgeSha256:createHash("sha256").update(fs.readFileSync("build/sinistar.dck")).digest("hex"),raster:{kinds:rasterKinds,mismatchFrames:rasterMismatchFrames,mismatchPixels:rasterMismatchPixels,examples:rasterExamples},workTstates:{min:Math.min(...costs),max:Math.max(...costs),mean:costs.reduce((a,b)=>a+b,0)/costs.length},emulator:'TSRun local checkout',frames:2400,updates:last,verifiedCompleteScreens:verified,displayWrites,unchangedWrites,romWrites,cadence:hist,ayWrites:writes,exactAudioWrites,audioTickGapTstates:{min:Math.min(...withinClipGaps),max:Math.max(...withinClipGaps)},checkpoints:reports};
fs.writeFileSync('build/runtime-report.json',JSON.stringify(report,null,2));
const pcm=Buffer.alloc(audio.length*2);audio.forEach((v,i)=>pcm.writeInt16LE(v,i*2));
const wav=Buffer.alloc(44);wav.write('RIFF');wav.writeUInt32LE(36+pcm.length,4);wav.write('WAVEfmt ',8);wav.writeUInt32LE(16,16);wav.writeUInt16LE(1,20);wav.writeUInt16LE(1,22);wav.writeUInt32LE(22050,24);wav.writeUInt32LE(44100,28);wav.writeUInt16LE(2,32);wav.writeUInt16LE(16,34);wav.write('data',36);wav.writeUInt32LE(pcm.length,40);
fs.writeFileSync('build/emulated-audio.wav',Buffer.concat([wav,pcm]));
console.log(JSON.stringify(report,null,2));

