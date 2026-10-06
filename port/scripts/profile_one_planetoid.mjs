// Controlled scene, native physics and rendering: retain 18 simulated rocks,
// place unwanted rocks outside the camera before drawing, suppress combat.
import {acceptTitle} from './accept_title.mjs';
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
const variant=process.argv[2]||'current',build=variant==='v1'?path.join(root,'revisions/playable-scrolling-world-v1/build'):path.join(root,'build');
const cart=fs.readFileSync(path.join(build,'sinistar-mining.dck'));
const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const records=[...Array.from({length:8},(_,i)=>0x79b0+i*10),...Array.from({length:8},(_,i)=>0x7db0+i*10),0x58b4];
const names=['game_step','wb_population','wb_worker','wb_move_player','mining_pursuit_step','render','population_clear','population_draw','stage','scene_sprite','clear_four','compile','radar_entry','stars_clear','stars_draw','draw_assembly','draw_cached_face','fast_select','wb_pop_prepare','wb_clip_sprite','fast_publish','radar_publish','isr'];
function runScene(rocks,face){
 const keys=new Uint8Array(8).fill(31),m=api.createMachine(keys,new Uint8Array(2).fill(255));
 m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));api.insertDock(m,cart);api.resetMachine(m);acceptTitle(m,sym);
 const word=a=>m.ram[a]|m.ram[a+1]<<8,put=(a,v)=>{m.ram[a]=v;m.ram[a+1]=v>>8;},set=(n,v)=>m.ram[sym[n]]=v;
 const stats=Object.fromEntries([...names,'wait_for_refresh','visible_publish'].map(n=>[n,{calls:0,inclusive:0,exclusive:0}]));
 let initialized=false,measuring=false,finished=false,start=0,end=0,pictures=0,fastPictures=0,visibleFacePictures=0;
 let pending=[],hist={},speedSamples=0,playerMax=0,faceMax=0,playerSum=0,faceSum=0;
 const begin=(n,ret,sp)=>{stats[n].calls++;pending.push({n,ret,sp,time:m.tstates,children:0});};
 const signed=v=>(v<<16)>>16;
 const read=m.bus.read;
 m.bus.read=a=>{if(a===m.cpu.pc){
  if(a===sym.game_step){
   if(!initialized){initialized=true;put(sym.face_x,210*256);put(sym.face_y,100*256);set('speech_started',1);set('sinistar_built',Number(face));set('awake_done',Number(face));set('assembly_count',face?20:0);keys[5]&=~1;}
   set('worker_alive',0);set('worker_delay',255);set('crystal_alive',0);set('bullet_alive',0);set('bs_active',0);set('invulnerable',255);set('game_status',0);
  }
  if(a===sym.frame_start){
   const camx=word(0x5884),camy=word(0x5886);
   const x=(camx+24)&511,y=(camy+76)&511;set('rock_alive',1);set('rock_x',x&255);set('rock_y',y&255);m.ram[0x586e]=x>>8;m.ram[0x586f]=y>>8;
   records.forEach((p,i)=>{put(p,(camx+(i<rocks-1?72+i*134:320))&511);put(p+2,(camy+(i<rocks-1?68+i*74:300))&511);m.ram[p+7]=96;});
   if(!measuring&&m.tstates>360*58688){measuring=true;start=m.tstates;pending=[];}
  }
  if(measuring&&!finished){
   for(let i=pending.length-1;i>=0;i--){const p=pending[i];if(a===p.ret&&m.cpu.sp===p.sp){const elapsed=m.tstates-p.time;stats[p.n].inclusive+=elapsed;stats[p.n].exclusive+=elapsed-p.children;pending.splice(i,1);if(i>0)pending[i-1].children+=elapsed;}}
   for(const n of names)if(a===sym[n])begin(n,word(m.cpu.sp),m.cpu.sp+2);
   if(a===sym.ready)begin('wait_for_refresh',sym.publish,m.cpu.sp);
   if(a===sym.publish)begin('visible_publish',sym.publication_done,m.cpu.sp);
   if(a===sym.fast_select){let visible=m.ram[sym.rects+2]?1:0;for(let p=0xbc80;p<0xbc80+153;p+=9)if(m.ram[p+2])visible++;hist[visible]=(hist[visible]||0)+1;assert.equal(visible,rocks);}
   if(a===sym.frame_done){pictures++;if(m.ram[0x78f7])fastPictures++;if(m.ram[sym.rects+22])visibleFacePictures++;if(pictures===120){finished=true;end=m.tstates;}}
   if(a===sym.move_player){const p=Math.hypot(signed(word(sym.pvx)),signed(word(sym.pvy)))/256,f=Math.hypot(signed(word(sym.face_vx)),signed(word(sym.face_vy)))/256;speedSamples++;playerSum+=p;faceSum+=f;playerMax=Math.max(playerMax,p);faceMax=Math.max(faceMax,f);}
  }
 }return read(a);};
 for(let f=0;f<6000&&!finished;f++)api.runFrame(m);assert.ok(finished,'benchmark completed');
 const total=end-start,group={physics:0,composition:0,dirty_comparison:0,radar_preparation:0,screen_publication:0,refresh_wait:0,interrupts:0,other:0};
 for(const [n,s] of Object.entries(stats)){
  const k=['game_step','wb_population','wb_worker','wb_move_player','mining_pursuit_step'].includes(n)?'physics':n==='compile'?'dirty_comparison':n==='radar_entry'?'radar_preparation':['visible_publish','fast_publish','radar_publish'].includes(n)?'screen_publication':n==='wait_for_refresh'?'refresh_wait':n==='isr'?'interrupts':'composition';group[k]+=s.exclusive;
 }
 group.other=total-Object.values(group).reduce((a,b)=>a+b,0);assert.ok(group.other>=0,'non-overlapping accounting');
 return {visible_planetoids:rocks,active_sinistar:face,seconds:total/3528000,fps:pictures/(total/3528000),pictures,visibleFacePictures,fastPictures,visible_histogram:hist,speed_pixels_per_tick:{player_average:playerSum/speedSamples,player_peak:playerMax,sinistar_average:faceSum/speedSamples,sinistar_peak:faceMax},time_percent:Object.fromEntries(Object.entries(group).map(([n,v])=>[n,Math.round(v/total*1000)/10])),tstates_per_picture:total/pictures,routines:stats};
}
const report={variant,dck_sha256:createHash('sha256').update(cart).digest('hex'),conditions:'Continuous right input; 18 simulated planetoids; one or three positioned in view before each render; no worker, firing, speech or damage; active Sinistar follows native pursuit; 360-refresh warmup, 120 measured pictures.',scenes:[runScene(1,false),runScene(1,true),runScene(3,true)]};
fs.writeFileSync(path.join(root,`build/one-planetoid-profile-${variant}.json`),JSON.stringify(report,null,2));console.log(JSON.stringify(report.scenes.map(({routines,...s})=>s),null,2));
