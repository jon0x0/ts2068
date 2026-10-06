// Native scrolling workload. Rock positions are never pinned or relocated.
// --cover enables the fully-covered-player rendering experiment at HOME 5BCB.
import {acceptTitle} from './accept_title.mjs';
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
const variant=process.argv.includes('--baseline-v17')?'v17':'current',build=variant==='v17'?path.join(root,'revisions/playable-clipped-cleanup-v17/build'):path.join(root,'build');
const cart=fs.readFileSync(path.join(build,'sinistar-mining.dck'));
const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const records=[...Array.from({length:8},(_,i)=>0x79b0+i*10),...Array.from({length:8},(_,i)=>0x7db0+i*10),0x58b4];
const names=['game_step','wb_population','wb_worker','wb_move_player','mining_pursuit_step','render','population_clear','population_draw','stage','scene_sprite','clear_four','compile','radar_entry','stars_clear','stars_draw','draw_assembly','assembly_cache_call','wb_shift_assembly','draw_cached_face','fast_select','wb_pop_prepare','wb_clip_sprite','fast_publish','radar_publish','isr','mode_filter','draw_rock','draw_ship','world_project','world_restore','wb_bullet','game_rules','speech_tick','sfx_tick'];
function runScene(name,pieces,phase,overlap){
 const fast=true,face=false,busy=false,cover=false,stars=true;
 const keys=new Uint8Array(8).fill(31),m=api.createMachine(keys,new Uint8Array(2).fill(255));
 m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));api.insertDock(m,cart);api.resetMachine(m);acceptTitle(m,sym);
 const assets=JSON.parse(fs.readFileSync(path.join(build,'mining-assets.json')));
 const assembly=pieces?assets.find(a=>a.kind==='assembly'&&a.index===pieces-1).data:null;
 const word=a=>m.ram[a]|m.ram[a+1]<<8,put=(a,v)=>{m.ram[a]=v;m.ram[a+1]=v>>8;},set=(n,v)=>m.ram[sym[n]]=v;
 const stats=Object.fromEntries([...names,'cache_build','cache_draw','cache_prepare','cache_overlap','wait_for_refresh','visible_publish'].map(n=>[n,{calls:0,inclusive:0,exclusive:0}]));
 let renderNumber=0;let initialized=false,measuring=false,finished=false,start=0,end=0,pictures=0,fastPictures=0,visibleFacePictures=0;
 let overlapChecks=[],overlapRejections={};let gateCounts={},comparedBytes=0,changedBytes=0;let pending=[],hist={},speedSamples=0,playerMax=0,faceMax=0,playerSum=0,faceSum=0;
 const begin=(n,ret,sp)=>{stats[n].calls++;pending.push({n,ret,sp,time:m.tstates,children:0});};
 const signed=v=>(v<<16)>>16;
 const read=m.bus.read;
 m.bus.read=a=>{if(a===m.cpu.pc){
  if(a===sym.game_step){
   if(!initialized){initialized=true;put(sym.face_x,210*256);put(sym.face_y,100*256);set('speech_started',1);set('sinistar_built',Number(face));set('awake_done',Number(face));set('assembly_count',face?20:0);keys[5]&=~1;if(fast)keys[1]&=~8;if(busy)keys[7]&=~1;}
   if(face){set('worker_alive',0);set('worker_delay',255);}if(!busy){set('bullet_alive',0);set('bs_active',0);}set('invulnerable',255);set('game_status',0);if(busy&&!m.ram[sym.speech_left]&&!m.ram[sym.speech_pending])set('speech_pending',2);if(m.tstates>240*58688)keys[1]|=8;
  }
  if(a===sym.render){
   // Controlled render workload, not a natural-game fps claim. Pin one rock
   // and the face relative to the actual camera; retain native publication/ISR.
   keys.fill(31);
   const fixed=(n,axis,x,y)=>{const wx=(word(0x5884)+x)&511,wy=(word(0x5886)+y)&511;put(sym[n+'_x'],(wx&255)*256);put(sym[n+'_y'],(wy&255)*256);m.ram[0x7c90+axis]=wx>>8;m.ram[0x7c91+axis]=wy>>8;};
   const drawPhase=name.includes('scrolling')?(renderNumber++&7):phase;
   fixed('face',10,96+drawPhase,88);
   const wx=(word(0x5884)+(overlap?112:24))&511,wy=(word(0x5886)+108)&511;
   put(sym.px,(wx&255)*256);put(sym.py,(wy&255)*256);m.ram[0x7c96]=wx>>8;m.ram[0x7c97]=wy>>8;
   const rx=(word(0x5884)+200)&511,ry=(word(0x5886)+130)&511;
   set('rock_x',rx&255);set('rock_y',ry&255);m.ram[0x586e]=rx>>8;m.ram[0x586f]=ry>>8;set('rock_alive',1);set('mass',96);
   for(const r of records)m.ram[r+7]=0;
   for(const n of ['worker_alive','crystal_alive','bullet_alive','bs_active','awake_done','sinistar_built','awake_mouth','awake_previous','speech_left','speech_pending'])set(n,0);
   set('assembly_count',pieces);set('assembly_previous',pieces);
   if(assembly)m.ram.set(assembly,0xd800);
  }
  if(a===sym.frame_start){
   m.ram[0x5bcb]=Number(cover)|(stars?2:0);
   if(!measuring&&m.tstates>360*58688){measuring=true;start=m.tstates;pending=[];}
  }
  if(measuring&&!finished){
   for(let j=overlapChecks.length-1;j>=0;j--){const p=overlapChecks[j];if(a===p.ret&&m.cpu.sp===p.sp){if(!(m.cpu.f&64)){let key=p.name;if(key==='actors'){const iy=m.cpu.yh*256+m.cpu.yl;key='actor '+Math.floor(((iy-sym.rects+32)%32)/4);}overlapRejections[key]=(overlapRejections[key]||0)+1;}overlapChecks.splice(j,1);}}
   for(const [label,name] of [['fs_objects','actors'],['wb_star_overlap','stars'],['wb_pop_overlap','population']])if(a===sym[label])overlapChecks.push({name,ret:word(m.cpu.sp),sp:m.cpu.sp+2});
   if(a===sym.fast_select){
    const g=n=>m.ram[sym[n]];
    let reason=m.ram[0x580f]?'previous fallback':!g('awake_done')?'not awake':g('speech_pending')||g('speech_left')?'speech active':g('awake_mouth')||g('awake_previous')?'mouth transition':g('eye_phase')!==g('eye_previous')?'eye transition':m.ram[sym.rects+23]!==52||m.ram[sym.oldrects+23]!==52||m.ram[sym.rects+22]!==7||m.ram[sym.oldrects+22]!==7?'clipped':Math.abs(((m.ram[sym.face_x+1]-g('face_oldx')+128)&255)-128)>1||Math.abs(((m.ram[sym.face_y+1]-g('face_oldy')+128)&255)-128)>1?'movement exceeds one pixel':'later overlap/stream gates';
    gateCounts[reason]=(gateCounts[reason]||0)+1;
   }
   if(a===sym.span_lookup){const count=m.ram[0x7bc2],shadow=word(0x7bc4),live=word(0x7bc6);for(let j=0;j<count;j++){comparedBytes++;if(m.ram[shadow-j]!==m.ram[live-j])changedBytes++;}}
   for(let i=pending.length-1;i>=0;i--){const p=pending[i];if(a===p.ret&&m.cpu.sp===p.sp){const elapsed=m.tstates-p.time;stats[p.n].inclusive+=elapsed;stats[p.n].exclusive+=elapsed-p.children;pending.splice(i,1);if(i>0)pending[i-1].children+=elapsed;}}
   for(const n of names)if(a===sym[n])begin(n,word(m.cpu.sp),m.cpu.sp+2);
   if(a===sym.assembly_cache_call)begin(['cache_build','cache_draw','cache_prepare','cache_overlap'][m.cpu.a],word(m.cpu.sp),m.cpu.sp+2);
   if(a===sym.ready)begin('wait_for_refresh',sym.publish,m.cpu.sp);
   if(a===sym.publish)begin('visible_publish',sym.publication_done,m.cpu.sp);

   if(a===sym.frame_done){let visible=m.ram[sym.rects+2]?1:0;for(let p=0xbc80;p<0xbc80+153;p+=9)if(m.ram[p+2])visible++;hist[visible]=(hist[visible]||0)+1;if(fast)assert.ok(visible<=2);pictures++;if(m.ram[0x78f7])fastPictures++;if(m.ram[sym.rects+22])visibleFacePictures++;if(pictures===40){finished=true;end=m.tstates;}}
   if(a===sym.move_player){const p=Math.hypot(signed(word(sym.pvx)),signed(word(sym.pvy)))/256,f=Math.hypot(signed(word(sym.face_vx)),signed(word(sym.face_vy)))/256;speedSamples++;playerSum+=p;faceSum+=f;playerMax=Math.max(playerMax,p);faceMax=Math.max(faceMax,f);}
  }
 }return read(a);};
 for(let f=0;f<6000&&!finished;f++)api.runFrame(m);assert.ok(finished,'benchmark completed');
 const total=end-start,group={physics:0,composition:0,dirty_comparison:0,radar_preparation:0,screen_publication:0,refresh_wait:0,interrupts:0,other:0};
 for(const [n,s] of Object.entries(stats)){
  const k=['game_step','wb_population','wb_worker','wb_move_player','mining_pursuit_step','wb_bullet','game_rules'].includes(n)?'physics':n==='compile'?'dirty_comparison':n==='radar_entry'?'radar_preparation':['visible_publish','fast_publish','radar_publish'].includes(n)?'screen_publication':n==='wait_for_refresh'?'refresh_wait':['isr','speech_tick','sfx_tick'].includes(n)?'interrupts':'composition';group[k]+=s.exclusive;
 }
 group.other=total-Object.values(group).reduce((a,b)=>a+b,0);assert.ok(group.other>=0,'non-overlapping accounting');
 return {overlapRejections,fastPathGateCounts:gateCounts,comparedBitmapBytes:comparedBytes,changedBitmapBytes:changedBytes,unchangedBitmapComparisonPercent:100*(comparedBytes-changedBytes)/comparedBytes,name,fast,active_sinistar:face,continuousSpeechAndFiring:busy,seconds:total/3528000,fps:pictures/(total/3528000),pictures,visibleFacePictures,fastPictures,visible_histogram:hist,speed_pixels_per_tick:{player_average:playerSum/speedSamples,player_peak:playerMax,sinistar_average:faceSum/speedSamples,sinistar_peak:faceMax},time_percent:Object.fromEntries(Object.entries(group).map(([n,v])=>[n,Math.round(v/total*1000)/10])),tstates_per_picture:total/pictures,routines:stats};
}
const scenes=[];
if(!process.argv.includes('--scroll-only')){
 for(const overlap of [false,true])for(const phase of [0,1,4,7])scenes.push(runScene(`10 pieces, phase ${phase}, ${overlap?'overlap':'apart'}`,10,phase,overlap));
 scenes.push(runScene('no Sinistar, one rock',0,0,false));
 scenes.push(runScene('19 pieces, phase 7, overlap',19,7,true));
}
scenes.push(runScene('10 pieces, scrolling phases, overlap',10,0,true));
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),conditions:'Controlled one-rock workload: face and player pinned relative to camera, assembly image fixed, worker/combat disabled; 40 pictures after 360-refresh warmup. Measures native rendering cost, not general gameplay fps.',scenes};
fs.writeFileSync(path.join(root,process.argv.includes('--scroll-only')?'build/assembly-scroll-profile.json':variant==='v17'?'build/assembly-baseline-v17-profile.json':'build/assembly-detailed-profile.json'),JSON.stringify(report,null,2));
for(const s of scenes)console.log(JSON.stringify({name:s.name,fps:s.fps,tstates:s.tstates_per_picture,shift:s.routines.wb_shift_assembly.exclusive/40,assembly:s.routines.draw_assembly.exclusive/40,compile:s.routines.compile.exclusive/40,clear:s.routines.clear_four.exclusive/40,render:s.routines.render.inclusive/40}));
