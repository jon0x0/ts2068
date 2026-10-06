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
const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));
m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));assert.equal(api.insertDock(m,cart),null);api.resetMachine(m);acceptTitle(m,sym);
const get=n=>m.ram[sym[n]],set=(n,v)=>m.ram[sym[n]]=v,word=(n,v)=>{set(n,v&255);m.ram[sym[n]+1]=v>>8;};
let contact=false,hit=false,protect=false,stream=null,offset=0,writes=0,starts=[],runs=[],counts=[0,0,0],pictures=0;
const reader=m.bus.read,writer=m.bus.ioWrite;
m.bus.ioWrite=(p,v)=>{if((p&255)===0xf6&&get('speech_left')){assert.ok(m.ayLatch<14);assert.equal(v,stream.data[offset+m.ayLatch]);writes++;}writer(p,v);};
m.bus.read=a=>{
 if(a===m.cpu.pc){
  if(a===sym.game_contact&&protect&&!contact)set('invulnerable',255);
  if(a===sym.game_vulnerable&&contact){contact=false;const x=m.ram[sym.face_x+1]+256*m.ram[0x7c9a]+15,y=m.ram[sym.face_y+1]+256*m.ram[0x7c9b]+10;word('px',(x&255)*256);word('py',(y&255)*256);m.ram[0x7c96]=(x>>8)&1;m.ram[0x7c97]=(y>>8)&1;}
  if(a===sym.wbm_track&&hit){hit=false;const x=m.ram[sym.face_x+1]+256*m.ram[0x7c9a]+24,y=m.ram[sym.face_y+1]+256*m.ram[0x7c9b]+26;word('bs_px',(x&255)*256);word('bs_py',(y&255)*256);m.ram[0x7c9c]=(x>>8)&1;m.ram[0x7c9d]=(y>>8)&1;word('bs_vx',0);word('bs_vy',0);}
  if(a===sym.speech_bytes){stream=clips[get('speech_active')-1];assert.ok(stream);const packedOffset=m.ram[sym.speech_ptr]+256*m.ram[sym.speech_ptr+1]-stream.address;offset=stream.data.length-14*get('speech_left');assert.equal(packedOffset,offset/2);if(!offset){starts.push(stream.index);runs.push(0);}runs[runs.length-1]++;counts[stream.index]++;}
  if(a===sym.speech_register&&m.ram[sym.speech_ptr]+256*m.ram[sym.speech_ptr+1]===stream.address+offset/2+7){assert.deepEqual(Array.from(m.ram.slice(0x5874,0x5881)),stream.data.slice(offset,offset+13));}
  if(a===sym.publication_done){pictures++;assert.equal(m.cpu.sp,0x7ffd);}
 }
 return reader(a);
};
function run(n){for(let i=0;i<n;i++)api.runFrame(m);}
function until(test){for(let i=0;i<600&&!test();i++)run(1);assert.ok(test(),'event timed out');}
run(300);protect=true;set('sinistar_built',1);set('awake_done',1);set('assembly_count',20);
until(()=>get('speech_active')===1);until(()=>!get('speech_active'));assert.equal(counts[0],125);
contact=true;set('invulnerable',0);until(()=>get('speech_active')===2);assert.equal(get('lives'),2);until(()=>!get('speech_active'));assert.equal(counts[1],135);
function bomb(){hit=true;set('bs_active',1);set('bs_fuel',180);until(()=>!hit);until(()=>get('speech_active')===3);}
bomb();run(12);const interrupted=counts[2];bomb();until(()=>!get('speech_active'));assert.equal(get('bs_hits'),2);assert.ok(runs[2]>=interrupted);assert.equal(runs[3],170);assert.deepEqual(starts,[0,1,2,2]);assert.equal(writes,counts.reduce((a,b)=>a+b)*13);assert.ok(pictures>20);assert.equal(get('speech_pending'),0);
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),starts,clip_run_frames:runs,frames:counts,ay_writes:writes,pictures,player_death_trigger:true,bomb_hit_trigger:true,roar_interrupt_and_restart:true};
fs.writeFileSync(path.join(root,'build/voices-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(report);
