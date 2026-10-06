import {acceptTitle} from './accept_title.mjs';
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck'));
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));
m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));api.insertDock(m,cart);api.resetMachine(m);acceptTitle(m,sym);
const cases=[{x:103,y:97,event:7},{x:96,y:90,event:7},{x:-20,y:50,event:7},{x:244,y:160,event:7},{x:-100,y:90,event:7},{x:96,y:90,event:10},{x:96,y:90,event:37}];
let index=0,state=null,ay=0,romWrites=0;const effects=[];
const off=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;
const put=(a,v)=>{m.ram[a]=v;m.ram[a+1]=v>>8;};
const io=m.bus.ioWrite;m.bus.ioWrite=(p,v)=>{if((p&255)===0xf6&&state)ay++;io(p,v);};
const write=m.bus.write;m.bus.write=(a,v)=>{if(state&&(m.portF4&(1<<(a>>13))))romWrites++;if(state&&m.ram[0x783c]&&((a>=0x4000&&a<0x5800)||(a>=0x6000&&a<0x7800))){assert.ok(a>=0x6000,'attribute writes only');assert.ok(state.masks.has((a&0x1fff)),'only disc cells');state.writes++;}write(a,v);};
const read=m.bus.read;m.bus.read=a=>{if(a===m.cpu.pc){
 if(a===sym.frame_start&&index<cases.length){const q=cases[index];put(0x5884,0);put(0x5886,0);put(sym.face_x,(q.x&255)*256);put(sym.face_y,(q.y&255)*256);m.ram[0x7c9a]=(q.x&511)>>8;m.ram[0x7c9b]=(q.y&511)>>8;put(sym.px,32*256);put(sym.py,110*256);m.ram[0x7c96]=m.ram[0x7c97]=0;for(const n of ['assembly_count','sinistar_built','awake_done','awake_mouth','bs_hits','invulnerable','worker_alive','game_status'])m.ram[sym[n]]={assembly_count:20,sinistar_built:1,awake_done:1,invulnerable:255}[n]||0;m.ram[0x783e]=q.event;if(index===0)m.ram[sym.speech_pending]=1;}
 if(a===sym.inc_flash&&(m.portF4&4)&&m.ram[0x783e]){const [x,y,w,h]=m.ram.slice(sym.oldrects+20,sym.oldrects+24),masks=new Map();let cx=m.ram[sym.face_oldx];if(x===0&&cx>=128)cx-=256;cx+=24;let cy=m.ram[sym.face_oldy];if(y===64&&cy>=128)cy-=256;cy+=26;for(let dy=-49;dy<=49;dy++){const yy=cy+dy,half=Math.floor(Math.sqrt(2401-dy*dy));if(yy<64||yy>=176)continue;for(let xx=Math.max(0,Math.floor((cx-half)/8));xx<=Math.min(31,Math.floor((cx+half-1)/8));xx++){const inner=Math.abs(dy)<=40?Math.floor(Math.sqrt(1600-dy*dy)):-1;if(inner>=0&&xx>=Math.floor((cx-inner)/8)&&xx<=Math.floor((cx+inner-1)/8))continue;const radius=[43,45,47,49].findIndex(r=>Math.abs(dy)<=r&&xx>=Math.floor((cx-Math.floor(Math.sqrt(r*r-dy*dy)))/8)&&xx<=Math.floor((cx+Math.floor(Math.sqrt(r*r-dy*dy))-1)/8));masks.set(off(xx,yy),radius);}}state={start:m.tstates,rect:[x,y,w,h],masks,attrs:m.ram.slice(0x6000,0x7800),bitmap:m.ram.slice(0x4000,0x5800),writes:0,ay,stages:[],skip:cases[index].event===10||!w||!h};}
 for(const [label,color,phase] of [['ring_gray',63,0],['ring_yellow',118,1],['ring_red',82,2],['ring_white',127,3]])if(a===sym[label]&&(m.portF4&128)){assert.ok(state&&!state.skip);for(let i=0;i<6144;i++){assert.equal(m.ram[0x4000+i],state.bitmap[i],'bitmap unchanged');assert.equal(m.ram[0x6000+i],(state.masks.has(i)&&state.masks.get(i)<=phase)?[118,127,82,127][(((i>>8)&3)+phase)&3]:state.attrs[i],'filled disc attribute');}state.stages.push({color,tstates:m.tstates});}
 if(a===sym.ring_done&&(m.portF4&128))state.finished=m.tstates;
 if(a===sym.frame_done&&state){assert.deepEqual(m.ram.slice(0x6000,0x7800),state.attrs);assert.deepEqual(m.ram.slice(0x4000,0x5800),state.bitmap);assert.equal(state.stages.length,state.skip?0:4);effects.push({case:cases[index],rect:state.rect,skipped:state.skip,totalTstates:(state.finished||m.tstates)-state.start,cells:state.masks.size,stages:state.stages,ayWrites:ay-state.ay,restoredExactly:true});state=null;index++;}
 }return read(a);};
for(let i=0;i<2000&&index<cases.length;i++)api.runFrame(m);assert.equal(index,cases.length);assert.equal(romWrites,0);assert.ok(effects[0].ayWrites>0,'speech continues during effect');
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),mode:'expanding attribute halo with vertically cycling color bands',effects,exactBitmapAndAttributeRestore:true,romWrites};fs.writeFileSync(path.join(root,'build/attribute-flash-verification.json'),JSON.stringify(report,null,2));console.log(report);

