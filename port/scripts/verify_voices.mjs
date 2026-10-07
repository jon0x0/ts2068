let minAudioStack=0xffff;
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
let contact=false,hit=false,protect=false,stream=null,offset=0,writes=0,starts=[],runs=[],counts=Array(clips.length).fill(0),pictures=0,roarRows=[],expected=[],countedHybrid=false,hybridFrames=0,minStack=0x7fff,shapeWrites=0;
const reader=m.bus.read,writer=m.bus.ioWrite;
m.bus.ioWrite=(p,v)=>{if((p&255)===0xf6&&get('speech_left')){assert.ok(m.ayLatch<14);assert.equal(v,expected[m.ayLatch],JSON.stringify({pc:m.cpu.pc,latch:m.ayLatch,stream:stream?.index,offset,left:get('speech_left'),mapping:m.portF4,helper:Array.from(m.ram.slice(0x7f60,0x7f68))}));writes++;if(m.ayLatch===13)shapeWrites++;}if((p&255)===0xf6 && m.ayLatch===12 && get('speech_active')===3)roarRows.push([...expected]);writer(p,v);};
m.bus.read=a=>{
 if(a===m.cpu.pc){
  if(a===sym.game_contact&&protect&&!contact)set('invulnerable',255);
  if(a===sym.game_vulnerable&&contact){contact=false;const x=m.ram[sym.face_x+1]+256*m.ram[0x7c9a]+15,y=m.ram[sym.face_y+1]+256*m.ram[0x7c9b]+10;word('px',(x&255)*256);word('py',(y&255)*256);m.ram[0x7c96]=(x>>8)&1;m.ram[0x7c97]=(y>>8)&1;}
  if(a===sym.wbm_track&&hit){hit=false;const x=m.ram[sym.face_x+1]+256*m.ram[0x7c9a]+24,y=m.ram[sym.face_y+1]+256*m.ram[0x7c9b]+26;word('bs_px',(x&255)*256);word('bs_py',(y&255)*256);m.ram[0x7c9c]=(x>>8)&1;m.ram[0x7c9d]=(y>>8)&1;word('bs_vx',0);word('bs_vy',0);}
  if(a===sym.speech_bytes){countedHybrid=false;stream=clips[get('speech_active')-1];assert.ok(stream);const packedOffset=m.ram[sym.speech_ptr]+256*m.ram[sym.speech_ptr+1]-stream.address;offset=stream.data.length-14*get('speech_left');if(stream.index===2){let delta=0;for(let at=0;at<offset;at+=14){delta+=2;for(let r=0;r<14;r++)if(!at||stream.data[at+r]!==stream.data[at-14+r])delta++;}assert.equal(packedOffset,delta);}else assert.equal(packedOffset,Math.floor(offset/28)*11+(offset%28?6:0));if(!offset){starts.push(stream.index);runs.push(0);}runs[runs.length-1]++;counts[stream.index]++;}
  if(a===sym.speech_register){
   expected=stream.data.slice(offset,offset+14);
   if(get('speech_active')===3 && (m.ram[0x587a]!==expected[6] || m.ram[0x587b]!==expected[7] || m.ram[0x587e]!==expected[10])){
    const remaining=m.ram[0x7f53];assert.ok(remaining<12);expected[6]=16-remaining;expected[7]=(expected[7]&0x1b)|0x24;expected[10]=remaining+4;if(!countedHybrid){hybridFrames++;countedHybrid=true;}
   }
   assert.deepEqual(Array.from(m.ram.slice(0x5874,0x5881)),expected.slice(0,13));
  }
  if(m.cpu.sp>=0x5e80&&m.cpu.sp<=0x5ed0){minAudioStack=Math.min(minAudioStack,m.cpu.sp);assert.ok(m.cpu.sp>=0x5e90,'audio stack overlaps roar state');}
  if(m.cpu.sp>=0x7f00 && m.cpu.sp<=0x7fff){minStack=Math.min(minStack,m.cpu.sp);assert.ok(m.cpu.sp>=0x7fd0,'stack overlaps audio helper');}
  if(a===sym.publication_done){pictures++;assert.equal(m.cpu.sp,0x7ffd);}
 }
 return reader(a);
};
function run(n){for(let i=0;i<n;i++)api.runFrame(m);}
function until(test){for(let i=0;i<600&&!test();i++)run(1);assert.ok(test(),'event timed out');}
run(300);for(const rock of JSON.parse(fs.readFileSync(path.join(root,'build/mining-assets.json'))).filter(a=>a.kind==='rock'))assert.deepEqual([...m.ram.slice(rock.address,rock.address+rock.data.length)],rock.data,'boot-expanded rock cache');protect=true;set('sinistar_built',1);set('awake_done',1);set('assembly_count',20);
until(()=>get('speech_active')===1);until(()=>!get('speech_active'));assert.equal(counts[0],125);
contact=true;set('invulnerable',0);until(()=>get('speech_active')===2);assert.equal(get('lives'),2);until(()=>!get('speech_active'));assert.equal(counts[1],135);
function bomb(){hit=true;set('bs_active',1);set('bs_fuel',180);until(()=>!hit);until(()=>get('speech_active')===3);}
bomb();run(12);const played=counts[2];bomb();until(()=>!get('speech_active'));assert.equal(get('bs_hits'),2);assert.equal(runs[2],170);assert.ok(counts[2]>played);assert.deepEqual(starts,[0,1,2]);assert.equal(writes,counts.reduce((a,b)=>a+b)*13+shapeWrites);assert.ok(pictures>20);assert.equal(get('speech_pending'),0);assert.ok(hybridFrames>=20);
// A fresh impact after completion can start another complete roar.
bomb();until(()=>!get('speech_active'));assert.equal(runs[3],170);assert.equal(get('bs_hits'),3);
for(let id=4;id<=8;id++){set('speech_pending',id);until(()=>get('speech_active')===id);until(()=>!get('speech_active'));assert.equal(counts[id-1],clips[id-1].data.length/14);}
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),starts,clip_run_frames:runs,frames:counts,ay_writes:writes,pictures,player_death_trigger:true,bomb_hit_trigger:true,roar_completes_without_restart:true,hybridFrames,minStack,minAudioStack,shapeWrites};
fs.writeFileSync(path.join(root,'build/roar-live-frames.json'),JSON.stringify(roarRows.slice(0,170)));
fs.writeFileSync(path.join(root,'build/voices-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(report);
