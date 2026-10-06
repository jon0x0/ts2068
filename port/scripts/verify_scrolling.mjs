import {acceptTitle} from './accept_title.mjs';
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
const build='build';
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const cart=fs.readFileSync(path.join(root,build,'sinistar-mining.dck')),assets=JSON.parse(fs.readFileSync(path.join(root,build,'mining-assets.json')));
const fastTest=process.argv.includes('--fast');let priorFast=false,restorationPicture=false;
const coverTest=process.argv.includes('--cover');let chaseInitialized=false,coveredFastPictures=0;
const keys=new Uint8Array(8).fill(31),m=api.createMachine(keys,new Uint8Array(2).fill(255));
m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));api.insertDock(m,cart);api.resetMachine(m);acceptTitle(m,sym);
const get=n=>m.ram[sym[n]],set=(n,v)=>m.ram[sym[n]]=v,word=a=>m.ram[a]|m.ram[a+1]<<8,put=(a,v)=>{m.ram[a]=v;m.ram[a+1]=v>>8;};
const records=[...Array.from({length:8},(_,i)=>0x79b0+i*10),...Array.from({length:8},(_,i)=>0x7db0+i*10),0x58b4];
const wrap=n=>n&511,relative=n=>((n+256)&511)-256,off=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;
function compose(){
 const pix=new Uint8Array(6144),attr=new Uint8Array(6144).fill(7);
 function sprite(kind,index,x,y,w,h,shift=0,opaque=false,cached=false){
  let raw=assets.find(a=>a.kind===kind&&a.index===index).data;
  if(opaque&&shift){const original=raw;raw=[...raw];for(let i=0;i<raw.length;i+=3){raw[i]=0;if(original[i]===255)raw[i+2]=7;}}
  if(shift){const src=raw;raw=[...src];for(let r=0;r<h;r++){let previous=7;for(let c=0;c<w;c++){
   const i=(r*w+c)*3,mask=opaque?0:src[i],priorMask=opaque?0:(c?src[i-3]:255);
   raw[i]=((mask>>>shift)|((c?priorMask:255)<<(8-shift)))&255;
   raw[i+1]=((src[i+1]>>>shift)|((c?src[i-2]:0)<<(8-shift)))&255;
   if(kind==='assembly'&&raw[i]!==255&&raw[i+2]===1)raw[i+2]=previous;
   if(raw[i]!==255)previous=raw[i+2];
  }}}
  if(cached){raw=[...raw];for(let r=0;r<h;r++){let previous=7;for(let c=0;c<w;c++){const i=(r*w+c)*3;if(raw[i]===255)raw[i+2]=7;else{if(raw[i+2]===1)raw[i+2]=previous;previous=raw[i+2];}}}}
  for(let r=0;r<h;r++)for(let c=0;c<w;c++){
   const xx=Math.floor(x/8)+c,yy=y+r,i=(r*w+c)*3;
   if(xx<0||xx>=32||yy<64||yy>=176||raw[i]===255)continue;
   const o=off(xx,yy);pix[o]=(pix[o]&raw[i])|raw[i+1];attr[o]=raw[i+2];
  }
 }
 const xy=(x,y,axis)=>[relative(get(x)+256*m.ram[0x7cb0+axis]),relative(get(y)+256*m.ram[0x7cb1+axis])];
 const pos=(x,y,axis)=>[relative(m.ram[sym[x]+1]+256*m.ram[0x7cb0+axis]),relative(m.ram[sym[y]+1]+256*m.ram[0x7cb1+axis])];
 const f=pos('face_x','face_y',10);
 if(get('assembly_count')&&get('bs_hits')<13){
  if(get('sinistar_built'))sprite('awakening',get('eye_phase')*3+get('awake_mouth'),...f,7,52,f[0]&7,!get('awake_done'));
  else if(!get('game_mode')||!sym.assembly_cache_call)sprite('assembly',get('assembly_count')-1,...f,7,52,f[0]&7);
 }
 let p=xy('rock_x','rock_y',0);if(get('rock_alive'))sprite('rock',p[0]&7,...p,5,28);
 for(const a of records)if(m.ram[a+7]){const x=relative(word(a)-word(0x5884)),y=relative(word(a+2)-word(0x5886));sprite('rock',x&7,x,y,5,28);}
 p=xy('worker_x','worker_y',8);if(get('worker_alive'))sprite('worker',p[0]&7,...p,3,12);
 p=pos('cx','cy',2);if(get('crystal_alive'))sprite('crystal',p[0]&7,...p,2,4);
 p=pos('bx','by',4);if(get('bullet_alive'))sprite('bullet',p[0]&7,...p,2,2);
 p=pos('px','py',6);if(m.ram[sym.rects+14])sprite('ship',((get('angle')+4)&248)|(p[0]&7),...p,3,12);
 p=xy('bs_x','bs_y',12);if(get('bs_active'))sprite('sinibomb',p[0]&7,...p,2,6);
 for(let a=0x58c0;a<0x58d4;a+=2){const sx=m.ram[a]>>3,sy=m.ram[a+1]+64;
  if((m.ram[0x5bcb]&2)&&get('awake_done')&&get('assembly_count')&&get('bs_hits')<13&&sx>=Math.floor(f[0]/8)&&sx<Math.floor(f[0]/8)+7&&sy>=f[1]&&sy<f[1]+52)continue;
  const o=off(sx,sy);if(!pix[o]){pix[o]=128>>(m.ram[a]&7);attr[o]=7;}}
 if(sym.assembly_cache_call&&get('game_mode')&&!get('sinistar_built')&&get('assembly_count')&&get('bs_hits')<13&&m.ram[0x5bd0])sprite('assembly',m.ram[0x5bd0]-1,...f,7,52,f[0]&7,false,true);
 return {pix,attr};
}
function radarModel(){
 const pixels=new Uint8Array(128),attrs=new Uint8Array(128).fill(7);
 const px=m.ram[sym.px+1]+256*m.ram[0x7c96],py=m.ram[sym.py+1]+256*m.ram[0x7c97];
 const position=(x,y)=>[((wrap(x-px)>>3)+32)&63,((wrap(y-py)>>5)+8)&15];
 const dot=(x,y,color,shape)=>{let at=(y&15)*8+((x>>3)&7);if(![7,1,color].includes(attrs[at])&&color!==0x47)at=(at+8)&127;attrs[at]=color;pixels[at]|=shape>>(x&7);};
 const [x,y]=position(word(0x5884),word(0x5886)+64);for(const [dx,dy] of [[0,0],[31,0],[0,3],[31,3]])dot(x+dx,y+dy,1,0xe0);
 const mark=(x,y,c,s)=>dot(...position(x,y),c,s);
 if(get('rock_alive'))mark(get('rock_x')+256*m.ram[0x586e],get('rock_y')+256*m.ram[0x586f],5,0xc0);
 for(const a of records)if(m.ram[a+7])mark(word(a),word(a+2),5,0xc0);
 if(get('worker_alive'))mark(get('worker_x')+256*m.ram[0x7c98],get('worker_y')+256*m.ram[0x7c99],2,0x80);
 if(get('assembly_count')&&get('bs_hits')<13)mark(m.ram[sym.face_x+1]+256*m.ram[0x7c9a],m.ram[sym.face_y+1]+256*m.ram[0x7c9b],0x46,0xe0);
 dot(32,8,0x47,0xe0);return {pixels,attrs};
}
let incrementalFaces=0,incrementalRestores=0,retainedRockRows=0;
let pictures=0,radars=0,maxRecords=0,rasterLate=0,romWrites=0,expected=null,start=0,firstPopulation=null,radarExpected;
const write=m.bus.write;m.bus.write=(a,v)=>{if(expected&&!m.ram[0x783c]&&((a>=0x4000&&a<0x5800)||(a>=0x6000&&a<0x7800))){const y=((a&0x1800)>>5)|((a&0x700)>>8)|((a&0xe0)>>2);if(y>=64&&m.tstates-start>=(40+y)*224)rasterLate++;}if(expected&&(m.portF4&(1<<(a>>13))))romWrites++;write(a,v);};
const assemblyTest=process.argv.includes('--assembly');let committedStages=new Set();let retries=0,captured=false;
let inject=false,caseIndex=0;const cases=[];
for(const cam of [0,1,7,248,255,256,480,511])for(const [x,y] of [[-33,70],[-7,50],[0,63],[7,64],[200,124],[231,160],[255,175],[270,180]])for(const assembly of [0,7,20,21])cases.push({cam,x,y,assembly});
// Repeated face coordinates exercise incremental repair rather than only
// full movement redraws. Cross all fine phases and eye changes with actors.
for(let phase=0;phase<8;phase++)for(let n=0;n<18;n++)cases.push({cam:0,x:96+phase,y:90,assembly:20,eye:n%3,shipOffset:[-20,-2,4,18,40,56][n%6],rockOffset:[-30,-8,12,35,50,65][n%6]});
// Stable secondary rocks, moving overlapping actors, fine phases, edge
// clipping, disappearance and return. Each group retains projection identity.
for(let phase=0;phase<8;phase++)for(let n=0;n<10;n++)cases.push({cam:0,x:70+n*4,y:90,assembly:20,eye:n%3,shipOffset:n*3,rockOffset:-40,retainedPhase:phase,retainedStep:n});
// Regression: identical clipped x/y/width, shrinking height must erase the old bottom strip.
for(let phase=0;phase<8;phase++)for(const y of [68,64,62,57,54,50,30,12,-1,-20,12,50,64,68])cases.push({cam:0,x:96+phase,y,assembly:20,shipOffset:100,rockOffset:110});
if(assemblyTest){
 for(const stage of [3,10,19]){
  for(let n=0;n<40;n++)cases.push({cam:0,x:96,y:88,assembly:stage,cacheFixture:true,shipOffset:12,rockOffset:20});
  for(let phase=0;phase<8;phase++)for(const [x,y] of [[96,88],[96,64],[96,62],[96,50],[-9,110],[-7,173],[250,90],[280,90],[96,88]])cases.push({cam:0,x:x+phase,y,assembly:stage,cacheFixture:true,shipOffset:8,rockOffset:20});
 }
 // A newer delivery interrupts preparation. It must never publish the half-built set.
 for(const [stage,count] of [[4,7],[11,7],[18,40]])for(let n=0;n<count;n++)cases.push({cam:0,x:97,y:90,assembly:stage,cacheFixture:true,shipOffset:8,rockOffset:20});
}
const rd=m.bus.read;m.bus.read=a=>{if(a===m.cpu.pc){
 if(a===sym.fast_select&&m.ram[0x580f])retries++;
 if(coverTest&&a===sym.frame_start)m.ram[0x5bcb]=3;
 if(coverTest&&!inject&&a===sym.game_step){
  if(!chaseInitialized){chaseInitialized=true;put(sym.face_x,210*256);put(sym.face_y,100*256);set('speech_started',1);set('sinistar_built',1);set('awake_done',1);set('assembly_count',20);}
  set('worker_alive',0);set('worker_delay',255);set('invulnerable',255);set('game_status',0);
 }
 if(a===sym.publish&&m.ram[0x78f6])coveredFastPictures++;
 if(a===sym.rock_row_skip&&(m.portF4&4))retainedRockRows++;
 if(a===sym.inc_draw&&(m.portF4&4))incrementalFaces++;
 if(a===sym.inc_restore&&(m.portF4&4))incrementalRestores++;
 if(a===sym.frame_start&&inject&&caseIndex<cases.length){const {cam,x,y,assembly,eye=0,shipOffset,rockOffset}=cases[caseIndex];set('game_status',1);put(0x5884,cam);put(0x5886,wrap(cam+31));
  const actor=(name,axis,n)=>{m.ram[sym[name]]=wrap(n)&255;m.ram[0x7c90+axis]=wrap(n)>>8;};
  actor('rock_x',0,cam+x+(rockOffset??0));actor('rock_y',1,wrap(cam+31)+y);m.ram[0x586e]=m.ram[0x7c90];m.ram[0x586f]=m.ram[0x7c91];set('rock_alive',1);
  const fixed=(name,axis,n)=>{put(sym[name],(wrap(n)&255)*256);m.ram[0x7c90+axis]=wrap(n)>>8;};
  fixed('px',6,cam+(shipOffset===undefined?100:x+shipOffset));fixed('py',7,wrap(cam+31)+110);fixed('face_x',10,cam+x);fixed('face_y',11,wrap(cam+31)+y);
  set('assembly_count',Math.min(20,assembly));set('sinistar_built',Number(assembly>=20));set('awake_done',Number(assembly===20));set('awake_mouth',Number(assembly===21));set('eye_phase',eye);set('bs_hits',0);set('worker_alive',0);set('crystal_alive',0);set('bullet_alive',0);set('bs_active',0);
  if(cases[caseIndex].retainedPhase!==undefined){
   const {retainedPhase:p,retainedStep:n}=cases[caseIndex];
   records.forEach((at,i)=>{put(at,i<3?[56+p,103+p,-7+p][i]&511:350);put(at+2,i<3?[125,140,172][i]:350);m.ram[at+7]=(n===7&&i===1)?0:96;});
  }
  // Changing assembly stage in a fixture must invalidate the cached delta chain.
  if(assembly===7){set('assembly_count',1);}
  if(cases[caseIndex].cacheFixture){m.ram.set(assets.find(a=>a.kind==='assembly'&&a.index===assembly-1).data,0xd800);set('assembly_previous',assembly);}
 }
 if(a===sym.publish){restorationPicture=fastTest&&priorFast&&!m.ram[0x5bb1];priorFast=!!m.ram[0x5bb1];expected=compose();start=m.tstates;}
 if(a===sym.publication_done){if(fastTest&&m.ram[0x5bb1]){let visible=get('rock_alive')&&m.ram[sym.rects+2]?1:0;for(let p=0xbc82;p<0xbd19;p+=9)if(m.ram[p])visible++;assert.ok(visible<=2,'fast mode visible cap');}if(!restorationPicture)for(let y=64;y<176;y++)for(let x=0;x<32;x++){const o=off(x,y);assert.equal(m.ram[0x4000+o],expected.pix[o],`bitmap picture ${pictures} case ${caseIndex} ${x},${y}`);assert.equal(m.ram[0x6000+o],expected.attr[o],`attr picture ${pictures} case ${caseIndex} ${x},${y}`);}if(assemblyTest&&inject&&cases[caseIndex]?.cacheFixture&&m.ram[0x5bd0])committedStages.add(m.ram[0x5bd0]);if(process.argv.includes('--capture-assembly')&&!captured&&cases[caseIndex]?.cacheFixture&&cases[caseIndex].assembly===10&&m.ram[0x5bd0]===10&&cases[caseIndex].x===96){fs.writeFileSync(path.join(root,'build/assembly-composite-screen.bin'),Buffer.concat([Buffer.from(m.ram.slice(0x4000,0x5800)),Buffer.from(m.ram.slice(0x6000,0x7800))]));captured=true;}pictures++;expected=null;if(inject)caseIndex++;}
 if(a===sym.radar_entry)radarExpected=radarModel();
 if(a===sym.radar_done){radars++;maxRecords=Math.max(maxRecords,m.ram[0x5868]);assert.ok(m.ram[0x5868]<=117);assert.deepEqual(m.ram.slice(0x7e00,0x7e80),radarExpected.pixels,'world-to-radar pixels');assert.deepEqual(m.ram.slice(0x7e80,0x7f00),radarExpected.attrs,'world-to-radar colors');}
 if(a===sym.frame_done&&!firstPopulation){firstPopulation=records.map(p=>m.ram[p+9]);assert.deepEqual([1,...firstPopulation].reduce((o,n)=>(o[n]=(o[n]||0)+1,o),{}),{1:10,2:2,3:2,4:2,5:2});}
}return rd(a);};
for(let i=0;i<1200;i++){if(fastTest){if(i===250||i===700)keys[1]&=~8;if(i===300||i===750)keys[1]|=8;}if(i>200){keys[5]&=~1;if(i>650){keys[5]=31;keys[1]&=~1;}}api.runFrame(m);}
keys.fill(31);assert.ok(word(0x5884)||word(0x5886),'camera must move with native keyboard input');
inject=true;for(let i=0;i<8000&&caseIndex<cases.length;i++)api.runFrame(m);
assert.equal(caseIndex,cases.length);assert.equal(romWrites,0);assert.equal(rasterLate,0);
assert.ok(retainedRockRows>0);assert.ok(incrementalFaces>0);assert.ok(incrementalRestores>0);
if(coverTest)assert.ok(coveredFastPictures>0,'star/player overlap direct updates exercised');
if(assemblyTest)for(const stage of [3,10,19,18])assert.ok(committedStages.has(stage),`completed stage ${stage} presented`);
if(coverTest)assert.ok(retries>0,'oversized direct publication retries exercised');
const report={retries,committedStages:[...committedStages],coveredFastPictures,retainedRockRows,incrementalFaces,incrementalRestores,dck_sha256:createHash('sha256').update(cart).digest('hex'),pictures,clippingCases:caseIndex,radars,maxRadarRecords:maxRecords,rasterLate,romWrites,firstWavePlanetoids:18};fs.writeFileSync(path.join(root,assemblyTest?'build/assembly-scrolling-verification.json':coverTest?'build/fast-stars-scrolling-verification.json':fastTest?'build/fast-scrolling-verification.json':'build/scrolling-verification.json'),JSON.stringify(report,null,2));console.log(report);
