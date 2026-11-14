import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {runtimeControls}from './paired_runtime_controls.mjs';
import {demandFixture,out as tapRoot}from './boss_motion_fixture_r145.mjs';import {stockFixture}from './stock_fixture.mjs';import {api,root,z}from './r22_test_machine.mjs';
const level=Number(process.argv[2]||4),seeded=process.argv.includes('--seeded'),boss=process.argv.includes('--boss'),internal=process.argv.includes('--internal'),O=path.join(root,'build/cartridges/tap_comparison',`level${String(level).padStart(2,'0')}${boss?'_boss':''}${seeded?'_seeded':''}${internal?'_candidate':''}${process.argv.includes('--safe')?'_safe':''}${process.argv.includes('--shield-native')?'_native_shield':''}`);fs.mkdirSync(O,{recursive:true});
const cartFile=internal?path.join(root,`build/cartridges/integration_work/level${String(level).padStart(2,'0')}/L${level}_shared_cache_internal.dck`):path.join(root,`build/cartridges/r153_colour_fix_test/rt_l${level}_r153_test.dck`);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function trace(kind){
 const cartPath=cartFile;
 const f=kind==='tap'?demandFixture():stockFixture(level,cartPath),m=f.m,c=f.controller;
 const baseRead=m.bus.read,baseWrite=m.bus.write,read=a=>baseRead(a),records=[],events=[],spawnTrace=[],drawTrace=[],coordinateTrace=[],pcHistory=[],rngTrace=[];
 let selectedActor=null;let repairCapture=null,repairCaptures=0;let deaths=0;let nativeShieldInstalled=false;let startConsumed=false;let bossStarted=false;let last=-1,active=false,updates=0,irqs=0,music=0,shots=0,actors=0,romWrites=0,done=false,frame=0,activeFrame=-1,bootFrame=-1,startIrq=0,startMusic=0;
 m.bus.read=a=>{if(done)return baseRead(a);if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;pcHistory.push([a,m.portF4]);if(pcHistory.length>35)pcHistory.shift();if(level===8&&a===0xc225&&spawnTrace.length<3)spawnTrace.push({entry:true,clock:read(0x7a89),history:[...pcHistory],stack:Array.from({length:14},(_,k)=>read(m.cpu.sp+k))});
  if(a===0xc069||(level===8&&a===0xf122)){rngTrace.push({original:m.cpu.a,pointer:read(0x7acd)|read(0x7ace)<<8});if(seeded){m.cpu.a=1;m.cpu.h=1;m.cpu.l=rngTrace.length&255;m.cpu.f=0x10;m.bus.write(0x7acd,m.cpu.l);m.bus.write(0x7ace,1);}}if(seeded&&a===0x8696)m.bus.write(0x7a89,0);if(seeded&&read(a)===0xed&&read(a+1)===0x5f)m.cpu.r=0x42;if(updates>=30&&updates<=31&&[0x8e85,0x8e8c,0x8cfd,0x8e57].includes(a))drawTrace.push({pc:a,id:m.cpu.a,hl:m.cpu.h*256+m.cpu.l,de:m.cpu.d*256+m.cpu.e,iy:m.cpu.yh*256+m.cpu.yl,ret:read(m.cpu.sp)|read(m.cpu.sp+1)<<8});if(a===0x863d){startConsumed=true;m.joystick.fill(255);}if(a===0x91f2&&active)deaths++;if(a===0xfd20)irqs++;if(a===0xf930)music++;if(a===0x9d5c)shots++;if(a===0x9172)actors++;
  if(process.argv.includes('--draw-coordinates')){
   if(selectedActor&&a===selectedActor.ret&&m.cpu.sp===selectedActor.sp){coordinateTrace.push({...selectedActor,origin:[m.cpu.b,m.cpu.c],size:[m.cpu.d,m.cpu.e],data:m.cpu.h*256+m.cpu.l,...(process.argv.includes('--draw-data')?{frameData:(()=>{let p=m.cpu.h*256+m.cpu.l;const tags=[],bits=[];for(let i=0;i<m.cpu.d*m.cpu.e;i++){const t=read(p++);tags.push(t);if(t===54)bits.push(...Array(8).fill(0));else for(let y=0;y<8;y++)bits.push(read(p++));}return{tags,bits:Buffer.from(bits).toString('hex'),flip:read(m.cpu.sp+1)&3};})()} :{}),...(process.argv.includes('--draw-owners')?{mapping:m.portF4,owners:Array.from({length:640},(_,i)=>read(0x7e00+i)),cellFlags:Array.from(m.ram.slice(0x8100,0x8380))}:{})});selectedActor=null;}
   if(active&&a===0x9172){selectedActor={update:updates,id:m.cpu.a,actor:m.cpu.yh*256+m.cpu.yl,input:[m.cpu.b,m.cpu.c],ret:0x9175,sp:m.cpu.sp};}
  }
  if(level===2&&kind==='cart'&&process.argv.includes('--repair-probe')){
   const snap=(tag)=>{fs.writeFileSync(path.join(O,`repair_${repairCaptures}_${tag}.ram.bin`),Buffer.from(m.ram));};
   if(repairCapture&&a===repairCapture.pc&&m.cpu.sp===repairCapture.sp){snap('after');repairCapture=null;repairCaptures++;}
   if(a===0xc09&&read(0x7a8e)&&repairCaptures<3&&!repairCapture){repairCapture={pc:read(m.cpu.sp)|read(m.cpu.sp+1)<<8,sp:(m.cpu.sp+2)&65535};snap('before');}
  }
  if(a===0x865f&&active&&updates===100){fs.writeFileSync(path.join(O,kind+'_completed100.screen.bin'),Buffer.concat([Buffer.from(m.ram.slice(0x4000,0x5800)),Buffer.from(m.ram.slice(0x6000,0x7800))]));}
  if(a===0x94f1&&read(0x7aa4)===3&&(!c||c.region===level-1)){
   if(process.argv.includes('--shield-native')&&updates===0&&!nativeShieldInstalled){assert.equal(m.ram[0xc380],0x38);assert.equal(m.ram[0xc381],0x4b);m.ram[0xc381]=0x2d;nativeShieldInstalled=true;}
   if(boss&&!bossStarted)throw Error('BOSS_START');if(!active){active=true;activeFrame=frame;startIrq=irqs;startMusic=music;}
   updates++;m.bus.write(0x7a98,255); // Player protection only: identical neutral scenario.
   const column=read(0x7a84),phase=read(0x7a83),pixel=read(0x7a82),event=read(0x7a90)|read(0x7a91)<<8;
   const actorState=[];for(let i=0;i<28;i++){const a=0x8501+i*9,h=read(a);if(h&63)actorState.push({slot:i,h,script:read(a+1)|read(a+2)<<8,x:read(a+3),y:read(a+4),raw:Array.from({length:9},(_,k)=>read(a+k))});}
   records.push({update:updates,column,phase,pixel,event,scrollStopped:read(0x7a8e),clock:read(0x7a89),actors:actorState,ship:[kind==='tap'?m.dock[7][0x1680]:m.ram[0x5b00],kind==='tap'?m.dock[7][0x1681]:m.ram[0x5b01]]});
   if(!events.length||events.at(-1).event!==event)events.push({column,phase,pixel,event});
   if([32,64,120].includes(updates)){const ownerBase=kind==='cart'?JSON.parse(fs.readFileSync(path.join(root,`build/cartridges/integration_work/level${String(level).padStart(2,'0')}/player_ram_layout.json`))).allocations.published_owner_map[0]:0;fs.writeFileSync(path.join(O,`${kind}_${updates}.owner.bin`),kind==='tap'?Buffer.from(m.dock[7].slice(0x1880,0x1b00)):Buffer.from(m.ram.slice(ownerBase,ownerBase+640)));fs.writeFileSync(path.join(O,`${kind}_${updates}.screen.bin`),Buffer.concat([Buffer.from(m.ram.slice(0x4000,0x5800)),Buffer.from(m.ram.slice(0x6000,0x7800))]));}
   if(updates===120){done=true;throw Error('TRACE_DONE');}
  }
 }return baseRead(a);};
 m.bus.write=(a,v)=>{if(boss&&((level===2&&a===0x8504&&updates>=93&&updates<=97)||(level===5&&[0x8516,0x8517,0x8567,0x8568].includes(a)&&updates>=80&&updates<=83)))coordinateTrace.push({update:updates,a,v,old:read(a),pc:m.cpu.pc,bc:m.cpu.b*256+m.cpu.c,de:m.cpu.d*256+m.cpu.e,hl:m.cpu.h*256+m.cpu.l,stack:Array.from({length:10},(_,i)=>read(m.cpu.sp+i)),history:[...pcHistory]});if(level===8&&a===0x850a&&v===0&&read(a)===1)spawnTrace.push({removed:true,pc:m.cpu.pc,clock:read(0x7a89),raw:Array.from({length:9},(_,k)=>read(a+k)),history:[...pcHistory]});if(level===8&&a>=0x8501&&a<0x85fd&&(a-0x8501)%9===0&&v===1&&read(a)===0)spawnTrace.push({a,pc:m.cpu.pc,frame,clock:read(0x7a89),hl:m.cpu.h*256+m.cpu.l,de:m.cpu.d*256+m.cpu.e,bc:m.cpu.b*256+m.cpu.c,iy:m.cpu.yh*256+m.cpu.yl,ret:read(m.cpu.sp)|read(m.cpu.sp+1)<<8});if(kind==='cart'&&(m.portF4&(1<<(a>>>13)))){romWrites++;throw Error('ROM_WRITE '+a.toString(16));}baseWrite(a,v);};
 while(!done&&frame<16000){try{for(;frame<16000&&!done;frame++){
  m.keyMatrix.fill(31);m.joystick.fill(255);
  if(c&&c.booted&&bootFrame<0)bootFrame=frame;
  if(kind==='tap'&&level!==1&&frame>=30&&(bootFrame<0||frame-bootFrame<120)){
   if(level<=5)m.keyMatrix[3]&=~(1<<(level-1));else m.keyMatrix[4]&=~(1<<(10-level));
  }
  if(!active&&!startConsumed&&(kind==='tap'?bootFrame>=0&&frame-bootFrame>300:frame>60)&&frame%240<45)m.joystick[0]=127;
  api.runFrame(m);
 }}catch(e){if(e.message==='BOSS_START'){
  const hooked=m.bus.read;m.bus.read=baseRead;m.keyMatrix.fill(31);m.joystick.fill(255);
  function invoke(pc){m.portF4=kind==='tap'?9:3;m.portFF=2;Object.assign(m.cpu,{pc,sp:0xffe0,iff1:false,iff2:false,halted:false,eiDelay:false});m.ram.set([0,0xf0],0xffe0);let steps=0;while(m.cpu.pc!==0xf000&&steps++<2000000)z.runZ80(m.cpu,m.bus,1,m);assert(steps<2000000,'Boss setup hang');}
  if(kind==='tap'){m.ram[0xfd4b]=0;m.keyMatrix[7]&=~16;invoke(0x1fa3);m.keyMatrix.fill(31);invoke(0x1fa3);m.keyMatrix[7]&=~16;invoke(0x1fa3);}else{
   const sy=Object.fromEntries([...fs.readFileSync(path.join(root,`build/cartridges/integration_work/level${String(level).padStart(2,'0')}/stock_controls.sym`),'utf8').matchAll(/(\w+): EQU 0x([0-9a-f]+)/ig)].map(v=>[v[1],parseInt(v[2],16)]));invoke(sy.boss_jump);
  }
  m.keyMatrix.fill(31);m.joystick.fill(255);if(process.argv.includes('--safe')){m.portF4=kind==='tap'?9:3;m.bus.write(0x7aa1,4);m.bus.write(0x7aa2,2);}m.bus.read=hooked;Object.assign(m.cpu,{pc:0x8653,sp:0xfffe,iff1:true,iff2:true});bossStarted=true;continue;
 }if(!done){fs.writeFileSync(path.join(O,kind+'_failure.json'),JSON.stringify({error:String(e),frame,updates,pc:m.cpu.pc,region:c?.region},null,2));throw e;}}}
 assert(done,kind+' active game trace did not finish');assert(records.some(r=>r.actors.length>0),kind+' no live actor state');
 const controls=process.argv.includes('--controls')?runtimeControls(m,kind,level):null;
 const result={deaths,controls,kind,updates,framesAfterActive:frame-activeFrame,acceptedIrqs:irqs-startIrq,musicCalls:music-startMusic,shots,actorSelections:actors,romWrites,region:c?.region,playerProtected:true,deathBypass:process.argv.includes('--shield-native'),nativeKillShieldForComparison:process.argv.includes('--shield-native'),records,events,spawnTrace,drawTrace,coordinateTrace,rngTrace};
 fs.writeFileSync(path.join(O,kind+'_native.bin'),Buffer.from(Array.from({length:0x4000},(_,i)=>read(0xc000+i))));fs.writeFileSync(path.join(O,kind+'_trace.json'),JSON.stringify(result,null,2));return result;
}
const tap=trace('tap'),cart=trace('cart'),key=r=>boss?String(r.update):[r.column,r.phase,r.pixel].join('/'),byKey=new Map(tap.records.map(r=>[key(r),r]));
const matched=[],differences=[],actorDifferences=[];for(const r of cart.records){const t=byKey.get(key(r));if(t){matched.push(key(r));if(JSON.stringify(t.actors)!==JSON.stringify(r.actors))actorDifferences.push({camera:key(r),tap:t.actors,cart:r.actors,tapClock:t.clock,cartClock:r.clock});if(t.event!==r.event)differences.push({camera:key(r),tapEvent:t.event,cartEvent:r.event});}}
const controlsMatch=tap.controls&&cart.controls?JSON.stringify(tap.controls)===JSON.stringify(cart.controls):null;
const report={nativeKillShieldForComparison:process.argv.includes('--shield-native'),fixturePatch:process.argv.includes('--shield-native')?{address:0xc381,old:0x4b,new:0x2d,reason:'Native coarse projectile death ignores7A98; comparison-only protection absorbs those hits in both machines'}:null,safeStart:process.argv.includes('--safe'),deaths:{tap:tap.deaths,cart:cart.deaths},controlsMatch,level,passed:tap.deaths===0&&cart.deaths===0&&matched.length>=80&&differences.length===0&&actorDifferences.length===0&&controlsMatch!==false,seeded,boss,actorDifferenceCount:actorDifferences.length,actorDifferences,scope:`Actual TAP loader/selected level vs ${process.argv.includes('--internal')?'internal candidate':'packaged r153 ROM'}; neutral input, matched native camera coordinates/event pointers, player protection only. Screens and actor state captured; not cycle/pixel equivalence or boss victory.`,matchedCameraStates:matched.length,eventDifferences:differences,tap:{framesAfterActive:tap.framesAfterActive,acceptedIrqs:tap.acceptedIrqs,musicCalls:tap.musicCalls,actorSelections:tap.actorSelections},cart:{framesAfterActive:cart.framesAfterActive,acceptedIrqs:cart.acceptedIrqs,musicCalls:cart.musicCalls,actorSelections:cart.actorSelections,romWrites:cart.romWrites},inputs:{tapLevel:sha(fs.readFileSync(path.join(tapRoot,`rtype/LEVEL${String(level).padStart(2,'0')}.TAP`))),tapStart:sha(fs.readFileSync(path.join(tapRoot,`rtype/START${String(level).padStart(2,'0')}.TAP`))),cart:sha(fs.readFileSync(cartFile))}};
fs.writeFileSync(path.join(O,'comparison.json'),JSON.stringify(report,null,2));console.log({...report,actorDifferences:actorDifferences.slice(0,1)});
