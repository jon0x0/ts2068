// Reproduces v16 stale Sinistar pixels on picture 21 at column 8, row 106.
// Native pursuit and deterministic direction changes cross radar and screen edges.
import {acceptTitle} from './accept_title.mjs';
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=process.env.TSRUN_ROOT ? path.resolve(process.env.TSRUN_ROOT) : path.resolve(root,'../../../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck')),assets=JSON.parse(fs.readFileSync(path.join(root,'build/mining-assets.json')));
const damagePieces=JSON.parse(fs.readFileSync(path.join(root,'build','damage-pieces.json')));
const fastTest=process.argv.includes('--fast');let priorFast=false,restorationPicture=false;
const coverTest=process.argv.includes('--cover');let chaseInitialized=false,coveredFastPictures=0;
const keys=new Uint8Array(8).fill(31),m=api.createMachine(keys,new Uint8Array(2).fill(255));
m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));api.insertDock(m,cart);api.resetMachine(m);acceptTitle(m,sym);
const get=n=>m.ram[sym[n]],set=(n,v)=>m.ram[sym[n]]=v,word=a=>m.ram[a]|m.ram[a+1]<<8,put=(a,v)=>{m.ram[a]=v;m.ram[a+1]=v>>8;};
const records=[...Array.from({length:8},(_,i)=>0x79b0+i*10),...Array.from({length:8},(_,i)=>0x7db0+i*10),0x58b4];
const wrap=n=>n&511,relative=n=>((n+256)&511)-256,off=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;
function compose(){
 const pix=new Uint8Array(6144),attr=new Uint8Array(6144).fill(7);
 function sprite(kind,index,x,y,w,h,shift=0,opaque=false){
  let raw=assets.find(a=>a.kind===kind&&a.index===index).data;
  if(opaque&&shift){const original=raw;raw=[...raw];for(let i=0;i<raw.length;i+=3){raw[i]=0;if(original[i]===255)raw[i+2]=7;}}
  if(shift){const src=raw;raw=[...src];for(let r=0;r<h;r++){let previous=7;for(let c=0;c<w;c++){
   const i=(r*w+c)*3,mask=opaque?0:src[i],priorMask=opaque?0:(c?src[i-3]:255);
   raw[i]=((mask>>>shift)|((c?priorMask:255)<<(8-shift)))&255;
   raw[i+1]=((src[i+1]>>>shift)|((c?src[i-2]:0)<<(8-shift)))&255;
   if((kind==='assembly'||kind==='arcade-explosion')&&raw[i]!==255&&raw[i+2]===1)raw[i+2]=previous;
   if(raw[i]!==255)previous=raw[i+2];
  }}}
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
  if(get('sinistar_built'))sprite('awakening',get('eye_phase')*3+get('awake_mouth'),...f,7,52,f[0]&7,!get('awake_done')||!!get('awake_mouth'));
  else sprite('assembly',get('assembly_count')-1,...f,7,52,f[0]&7);
 }
 if(get('bs_hits')>0&&get('bs_hits')<13&&get('assembly_count'))for(const r of damagePieces.slice(0,get('bs_hits'))){
  for(let yy=f[1]+r.y;yy<f[1]+r.y+r.height;yy++)for(let xx=f[0]+r.x;xx<f[0]+r.x+r.width;xx++){
   if(xx<0||xx>=256||yy<64||yy>=176)continue;const o=off(xx>>3,yy);pix[o]&=~(128>>(xx&7));if(!pix[o])attr[o]=7;
  }
 }
 let p=xy('rock_x','rock_y',0);if(get('rock_alive'))sprite('rock',p[0]&7,...p,5,28);
 for(const a of records)if(m.ram[a+7]){const x=relative(word(a)-word(0x5884)),y=relative(word(a+2)-word(0x5886));sprite('rock',x&7,x,y,5,28);}
 p=xy('worker_x','worker_y',8);if(get('worker_alive')===2)sprite('arcade-explosion',((32-m.ram[0x5c27])>>3),...p,4,26,p[0]&7);else if(get('worker_alive'))sprite('worker',p[0]&7,...p,3,12);
 p=pos('cx','cy',2);if(get('crystal_alive'))sprite('crystal',p[0]&7,...p,2,4);
 p=pos('bx','by',4);if(get('bullet_alive'))sprite('bullet',p[0]&7,...p,2,2);
 p=pos('px','py',6);if(m.ram[sym.rects+14])sprite('ship',((get('angle')+4)&248)|(p[0]&7),...p,3,12);
 p=xy('bs_x','bs_y',12);if(get('bs_active'))sprite('sinibomb',p[0]&7,...p,2,6);
 if(m.ram[0x783e]){const x=relative(m.ram[0x783c]+256*m.ram[0x7cbe]),y=relative(m.ram[0x783d]+256*m.ram[0x7cbf]);sprite('arcade-explosion',(4-m.ram[0x783e])&3,x,y,4,26,x&7);}
 for(let a=0x58c0;a<0x58d4;a+=2){const sx=m.ram[a]>>3,sy=m.ram[a+1]+64;
  if((m.ram[0x5bcb]&2)&&!get('bs_hits')&&get('awake_done')&&get('assembly_count')&&get('bs_hits')<13&&sx>=Math.floor(f[0]/8)&&sx<Math.floor(f[0]/8)+7&&sy>=f[1]&&sy<f[1]+52)continue;
  const o=off(sx,sy);if(!pix[o]){pix[o]=128>>(m.ram[a]&7);attr[o]=7;}}
 return {pix,attr};
}
function radarModel(){
 const pixels=new Uint8Array(128),attrs=new Uint8Array(128).fill(7);
 const px=m.ram[sym.px+1]+256*m.ram[0x7c96],py=m.ram[sym.py+1]+256*m.ram[0x7c97];
 const position=(x,y)=>[((wrap(x-px)>>3)+32)&63,((wrap(y-py)>>5)+8)&15];
 const dot=(x,y,color,shape)=>{let at=(y&15)*8+((x>>3)&7);if(![7,1,color].includes(attrs[at])&&color!==0x47)at=(at+8)&127;attrs[at]=color;pixels[at]|=shape>>(x&7);};
 const [x,y]=position(word(0x5884),word(0x5886)+64);dot(x,y,1,0xe0);for(let dx=0;dx<32;dx++)for(const dy of [0,3])dot(x+dx,y+dy,1,0x80);for(const dx of [0,31])for(const dy of [1,2])dot(x+dx,y+dy,1,0x80);
 const mark=(x,y,c,s)=>dot(...position(x,y),c,s);
 if(get('rock_alive'))mark(get('rock_x')+256*m.ram[0x586e],get('rock_y')+256*m.ram[0x586f],5,0xc0);
 for(const a of records)if(m.ram[a+7])mark(word(a),word(a+2),5,0xc0);
 if(get('worker_alive')===1)mark(get('worker_x')+256*m.ram[0x7c98],get('worker_y')+256*m.ram[0x7c99],2,0x80);
 if(get('assembly_count')&&get('bs_hits')<13)mark(m.ram[sym.face_x+1]+256*m.ram[0x7c9a],m.ram[sym.face_y+1]+256*m.ram[0x7c9b],0x46,0xe0);
 dot(32,8,0x47,0xe0);return {pixels,attrs};
}
let incrementalFaces=0,incrementalRestores=0,retainedRockRows=0;
let pictures=0,radars=0,maxRecords=0,rasterLate=0,romWrites=0,expected=null,start=0,firstPopulation=null,radarExpected;
const write=m.bus.write;m.bus.write=(a,v)=>{if(expected&&((a>=0x4000&&a<0x5800)||(a>=0x6000&&a<0x7800))){const y=((a&0x1800)>>5)|((a&0x700)>>8)|((a&0xe0)>>2);if(y>=64&&m.tstates-start>=(40+y)*224)rasterLate++;}if(expected&&(m.portF4&(1<<(a>>13))))romWrites++;write(a,v);};
const inject=false;const caseIndex=0;
const rd=m.bus.read;m.bus.read=a=>{if(a===m.cpu.pc){
 if(coverTest&&a===sym.frame_start)m.ram[0x5bcb]=3;
 if(!inject&&a===sym.game_step){
  if(!chaseInitialized){chaseInitialized=true;put(sym.face_x,210*256);put(sym.face_y,100*256);set('speech_started',1);set('sinistar_built',1);set('awake_done',1);set('assembly_count',20);}
  set('worker_alive',0);set('worker_delay',255);set('invulnerable',255);set('game_status',0);
 }
 if(a===sym.publish&&m.ram[0x78f6])coveredFastPictures++;
 if(a===sym.rock_row_skip&&(m.portF4&4))retainedRockRows++;
 if(a===sym.inc_draw&&(m.portF4&4))incrementalFaces++;
 if(a===sym.inc_restore&&(m.portF4&4))incrementalRestores++;
 if(a===sym.publish){restorationPicture=fastTest&&priorFast&&!m.ram[0x5bb1];priorFast=!!m.ram[0x5bb1];expected=compose();start=m.tstates;}
 if(a===sym.publication_done){if(fastTest&&m.ram[0x5bb1]){let visible=get('rock_alive')&&m.ram[sym.rects+2]?1:0;for(let p=0xbc82;p<0xbd19;p+=9)if(m.ram[p])visible++;assert.ok(visible<=2,'fast mode visible cap');}if(!restorationPicture)for(let y=64;y<176;y++)for(let x=0;x<32;x++){const o=off(x,y);assert.equal(m.ram[0x4000+o],expected.pix[o],`bitmap picture ${pictures} case ${caseIndex} ${x},${y}`);assert.equal(m.ram[0x6000+o],expected.attr[o],`attr picture ${pictures} case ${caseIndex} ${x},${y}`);}pictures++;expected=null;}
 if(a===sym.radar_entry)radarExpected=radarModel();
 if(a===sym.radar_done){radars++;maxRecords=Math.max(maxRecords,m.ram[0x5868]);assert.ok(m.ram[0x5868]<=117);assert.deepEqual(m.ram.slice(0x7e00,0x7e80),radarExpected.pixels,'world-to-radar pixels');assert.deepEqual(m.ram.slice(0x7e80,0x7f00),radarExpected.attrs,'world-to-radar colors');}
 if(a===sym.frame_done&&!firstPopulation){firstPopulation=records.map(p=>m.ram[p+9]);assert.deepEqual([1,...firstPopulation].reduce((o,n)=>(o[n]=(o[n]||0)+1,o),{}),{1:10,2:2,3:2,4:2,5:2});}
}return rd(a);};
let seed=1982;for(let i=0;i<18000;i++){if(i%100===0){seed=(Math.imul(seed,1664525)+1013904223)>>>0;keys.fill(31);const d=seed%8;if([0,1,7].includes(d))keys[2]&=~1;if([3,4,5].includes(d))keys[1]&=~1;if([1,2,3].includes(d))keys[5]&=~1;if([5,6,7].includes(d))keys[5]&=~2;}if(i===250)keys[1]&=~8;if(i===300)keys[1]|=8;api.runFrame(m);}
keys.fill(31);assert.ok(word(0x5884)||word(0x5886),'camera must move with native keyboard input');
assert.equal(romWrites,0);assert.equal(rasterLate,0);assert.ok(pictures>3000);
if(coverTest)assert.ok(coveredFastPictures>0,'star/player overlap direct updates exercised');
const report={coveredFastPictures,retainedRockRows,incrementalFaces,incrementalRestores,dck_sha256:createHash('sha256').update(cart).digest('hex'),pictures,nativeRefreshes:18000,radars,maxRadarRecords:maxRecords,rasterLate,romWrites,firstWavePlanetoids:18};fs.writeFileSync(path.join(root,coverTest?'build/stress-covered-verification.json':fastTest?'build/stress-fast-verification.json':'build/stress-verification.json'),JSON.stringify(report,null,2));console.log(report);
