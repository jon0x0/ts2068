import {acceptTitle} from './accept_title.mjs';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck'));
const clips=JSON.parse(fs.readFileSync(path.join(root,'build/mining-assets.json'))).filter(a=>a.kind==='speech');
const keys=new Uint8Array(8).fill(31);const m=api.createMachine(keys,new Uint8Array(2).fill(255));
m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));assert.equal(api.insertDock(m,cart),null);api.resetMachine(m);acceptTitle(m,sym);
const get=n=>m.ram[sym[n]],set=(n,v)=>m.ram[sym[n]]=v,word=(n,v)=>{set(n,v&255);m.ram[sym[n]+1]=v>>8;};

const assets=JSON.parse(fs.readFileSync(path.join(root,'build/mining-assets.json')));
const symbols=sym;
const off=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;
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
   const xx=(x>>3)+c,yy=y+r;const i=(r*w+c)*3;if(xx<0||xx>=32||yy<64||yy>=176||data[i]===255)continue;const o=off(xx,yy);
   pix[o]=(pix[o]&data[i])|data[i+1];attr[o]=data[i+2];
  }
 }
 if(m.ram[symbols.sinistar_built]&&m.ram[symbols.bs_hits]<13)sprite('awakening',3*m.ram[symbols.eye_phase]+m.ram[symbols.awake_mouth],m.ram[symbols.face_x+1],m.ram[symbols.face_y+1],7,52);
 else if(!m.ram[symbols.sinistar_built]&&m.ram[symbols.assembly_count])sprite('assembly',m.ram[symbols.assembly_count]-1,192,80,7,52);
 if(m.ram[symbols.rock_alive])sprite('rock',m.ram[symbols.rock_x]&7,m.ram[symbols.rock_x]-(m.ram[0x586e]?256:0),m.ram[symbols.rock_y]+256*m.ram[0x586f],5,28);
 if(m.ram[symbols.worker_alive])sprite('worker',m.ram[symbols.worker_x]&7,m.ram[symbols.worker_x],m.ram[symbols.worker_y],3,12);
 if(m.ram[symbols.crystal_alive])sprite('crystal',m.ram[symbols.cx+1]&7,m.ram[symbols.cx+1],m.ram[symbols.cy+1],2,4);
 if(m.ram[symbols.bullet_alive])sprite('bullet',m.ram[symbols.bx+1]&7,m.ram[symbols.bx+1],m.ram[symbols.by+1],2,2);
 const x=m.ram[symbols.px+1],y=m.ram[symbols.py+1];
 sprite('ship',(((m.ram[symbols.angle]+4)&248)|(x&7)),x,y,3,12);
 if(m.ram[symbols.bs_active])sprite('sinibomb',m.ram[symbols.bs_x]&7,m.ram[symbols.bs_x],m.ram[symbols.bs_y],2,6);
 return {pix,attr};
}

const sfxNames=['shot','pickup','assembly','bomb-launch'];
const effects=sfxNames.map(n=>fs.readFileSync(path.join(root,'../assets/sfx-'+n+'.packed')));
let sfxScope=false,sfxOffset=0,sfxStream=null,sfxFrames=[0,0,0,0],ayWrites=0,shotsDuringSpeech=0,radarChecks=0,pictures=0,followMine=false;
let radarWriting=false,prepared=null,maxRadarRecords=0;let radarActive=false,radarCycles=0,radarStart=0,radarWrites=0;let motionProbe=0;let motionExpected=null,motionChecks=0;const velocityCases=new Set();
const sourceTable=fs.readFileSync(path.join(root,'reference/original/SAM/SAMTABLE.SRC'),'utf8').split('SCIVELT\tFCB')[1].split('ESCIVEL')[0];
const directions=[[-1,0],...[...sourceTable.matchAll(/FCB\s+(-?\d+),(-?\d+)/g)].map(m=>[Number(m[1]),Number(m[2])])];assert.equal(directions.length,9);
const positions=new Set();const reader=m.bus.read,io=m.bus.ioWrite;
m.bus.ioWrite=(p,v)=>{if((p&255)===0xf6&&sfxScope){assert.equal(get('speech_active'),0,'SFX must never write during speech');const i=[0,1,6,7,8].indexOf(m.ayLatch);assert.ok(i>=0);assert.equal(v,sfxStream[sfxOffset+i]);ayWrites++;}io(p,v);};
m.bus.read=a=>{if(a===m.cpu.pc){
 if(a===sym.world_step&&get('game_mode')&&get('rock_alive')){if(motionProbe<18){m.ram[0x586c]=2*(motionProbe%9);motionProbe++;}const i=m.ram[0x586c]/2,[vl,vs]=directions[i];velocityCases.add(i);let xx=(get('rock_x')*256+m.ram[0x586e]*65536+m.ram[0x586a]+Math.round(vs*128*256/304))&131071,yy=(get('rock_y')*256+m.ram[0x586f]*65536+m.ram[0x586b]+Math.round(-vl*64*112/256))&131071;motionExpected=[(xx>>8)&255,(yy>>8)&255,xx&255,yy&255,xx>>16,yy>>16];}
 if(a===sym.fire_input&&motionExpected){assert.deepEqual([get('rock_x'),get('rock_y'),m.ram[0x586a],m.ram[0x586b],m.ram[0x586e],m.ram[0x586f]],motionExpected);motionChecks++;motionExpected=null;}
 if(a===sym.radar_entry){radarActive=true;radarStart=m.tstates;}
 if(a===sym.radar_done){radarActive=false;radarCycles=Math.max(radarCycles,m.tstates-radarStart);}
 if(a===sym.radar_publish&&m.ram[0x5868])radarWriting=true;
 if(a===sym.radar_published){radarWriting=false;for(let yy=0;yy<16;yy++)for(let xx=0;xx<8;xx++){assert.equal(m.ram[0x4000+off(xx+12,yy)],prepared.pix[yy*8+xx]);assert.equal(m.ram[0x6000+off(xx+12,yy)],prepared.attr[yy*8+xx]);}}
 if(a===sym.sfx_frame){sfxScope=true;sfxStream=effects[get('sfx_active')-1];sfxOffset=sfxStream.length-5*get('sfx_left');sfxFrames[get('sfx_active')-1]++;}
 if(a===sym.sfx_frame_done||a===sym.speech_bytes||a===sym.sfx_zero)sfxScope=false;
 if(a===sym.fire_shot&&get('speech_active'))shotsDuringSpeech++;
 if(a===sym.manual_target&&followMine){word('px',(get('rock_x')-4)*256);word('py',(get('rock_y')+10)*256);word('pvx',0);word('pvy',0);set('angle',64);}
 if(a===sym.publication_done){pictures++;positions.add(get('rock_x')+','+get('rock_y'));const expected=compose();for(let y=64;y<176;y++)for(let x=0;x<32;x++){const o=off(x,y);assert.equal(m.ram[0x4000+o],expected.pix[o],`bitmap ${x},${y}`);assert.equal(m.ram[0x6000+o],expected.attr[o],`attr ${x},${y}`);}}
 if(a===sym.radar_done){
 const pix=new Uint8Array(128),attr=new Uint8Array(128).fill(7);
 const dot=(x,y,color,shape)=>{let n=((y&15)*8)|((x>>3)&7);const mask=shape>>(x&7);if(attr[n]!==7&&attr[n]!==1&&attr[n]!==color&&color!==0x47)n=(n+8)&127;attr[n]=color;pix[n]|=mask;};
 const x=m.ram[sym.px+1],y=m.ram[sym.py+1],left=32-(x>>3),top=12-(y>>4);
 for(const dx of [0,31])for(const dy of [0,6])dot(left+dx,top+dy,1,224);
 const obj=(ox,oy,c,shape)=>dot(32+Math.floor((ox-x)/8),8+Math.floor((oy-y)/16),c,shape);
 if(get('rock_alive'))obj(get('rock_x')+256*m.ram[0x586e],get('rock_y'),5,192);
 if(get('worker_alive'))obj(get('worker_x'),get('worker_y'),2,128);
 if(get('assembly_count')&&get('bs_hits')<13)obj(m.ram[sym.face_x+1],m.ram[sym.face_y+1],0x46,224);
 dot(32,8,0x47,224);
 assert.deepEqual(m.ram.slice(0x7e00,0x7e80),pix);assert.deepEqual(m.ram.slice(0x7e80,0x7f00),attr);
 prepared={pix,attr};maxRadarRecords=Math.max(maxRadarRecords,m.ram[0x5868]);assert.ok(m.ram[0x5868]*3<=352);
 radarChecks++;
 }
}return reader(a);};
const write=m.bus.write;m.bus.write=(a,v)=>{if(radarWriting&&a>=0x4000&&a<0x7800&&a!==0x5867){const bitmap=(a<0x5800),attribute=(a>=0x6000);if(bitmap||attribute){assert.notEqual(m.ram[a],v,'scanner writes only changed bytes');assert.ok((m.tstates%58688)<40*224,'scanner writes before top scanlines');radarWrites++;}}write(a,v);};
function run(n){for(let i=0;i<n;i++)api.runFrame(m);}
run(300);
// No shots or supplied crystals: worker must mine real rocks and assemble.
for(let i=0;i<60000&&!get('sinistar_built');i++)run(1);
assert.equal(get('sinistar_built'),1,'autonomous worker must finish assembly');assert.equal(get('worker_deliveries'),20);assert.equal(get('worker_pickups'),20);assert.ok(get('releases')>=20);assert.ok(positions.size>40);assert.ok(radarChecks>100);
// Speech must survive shooting attempts without SFX writes taking ownership.
keys[7]&=~1;run(160);keys.fill(31);assert.ok(shotsDuringSpeech>0);
// Restart clears all sound/world state; follow the moving mine to exercise pickups.
keys[2]&=~8;run(8);keys.fill(31);run(250);assert.equal(get('game_status'),0);followMine=true;keys[7]&=~1;run(2600);keys.fill(31);followMine=false;assert.ok(get('crystals_taken')>0);
// Trigger a launch through keyboard input, outside speech.
keys[7]&=~16;run(8);keys.fill(31);run(85);
assert.ok(sfxFrames.every(n=>n>0),JSON.stringify(sfxFrames));assert.equal(ayWrites,sfxFrames.reduce((a,b)=>a+b)*5);assert.ok(pictures>1000);assert.equal(velocityCases.size,9);
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),motion_checks:motionChecks,velocity_cases:[...velocityCases],radar_max_records:maxRadarRecords,radar_max_tstates:radarCycles,radar_writes:radarWrites,autonomous_worker_assembly:true,rock_positions:positions.size,radar_checks:radarChecks,pictures,sfx_frames:sfxFrames,ay_writes:ayWrites,shots_during_speech:shotsDuringSpeech,speech_priority:true};fs.writeFileSync(path.join(root,'build/world-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(report);
