import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import assert from 'node:assert/strict';
import {runtimeControls}from './paired_runtime_controls.mjs';
import {demandFixture,out as tapRoot}from './boss_motion_fixture_r145.mjs';import {stockFixture}from './stock_fixture.mjs';import {api,root,z}from './r22_test_machine.mjs';
const level=Number(process.argv[2]||4),seeded=process.argv.includes('--seeded'),boss=process.argv.includes('--boss'),internal=process.argv.includes('--internal'),O=path.join(root,'build/cartridges/motion_reachability',`level${String(level).padStart(2,'0')}${boss?'_boss':''}${seeded?'_seeded':''}${internal?'_candidate':''}${process.argv.includes('--safe')?'_safe':''}`);fs.mkdirSync(O,{recursive:true});
const cartFile=internal?path.join(root,`build/cartridges/integration_work/level${String(level).padStart(2,'0')}/L${level}_shared_cache_internal.dck`):path.join(root,`build/cartridges/r153_colour_fix_test/rt_l${level}_r153_test.dck`);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function trace(kind){
 const cartPath=cartFile;
 const f=kind==='tap'?demandFixture():stockFixture(level,cartPath),m=f.m,c=f.controller;
 const baseRead=m.bus.read,baseWrite=m.bus.write,read=a=>baseRead(a),records=[],events=[],spawnTrace=[],drawTrace=[],coordinateTrace=[],pcHistory=[],rngTrace=[],motionDraws=[];
 let deaths=0;let startConsumed=false;let bossStarted=false;let last=-1,active=false,updates=0,irqs=0,music=0,shots=0,actors=0,romWrites=0,done=false,frame=0,activeFrame=-1,bootFrame=-1,startIrq=0,startMusic=0;
 m.bus.read=a=>{if(done)return baseRead(a);if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;pcHistory.push([a,m.portF4]);if(pcHistory.length>35)pcHistory.shift();if(level===8&&a===0xc225&&spawnTrace.length<3)spawnTrace.push({entry:true,clock:read(0x7a89),history:[...pcHistory],stack:Array.from({length:14},(_,k)=>read(m.cpu.sp+k))});
  if(a===0xc069||(level===8&&a===0xf122)){rngTrace.push({original:m.cpu.a,pointer:read(0x7acd)|read(0x7ace)<<8});if(seeded){m.cpu.a=1;m.cpu.h=1;m.cpu.l=rngTrace.length&255;m.cpu.f=0x10;m.bus.write(0x7acd,m.cpu.l);m.bus.write(0x7ace,1);}}if(seeded&&a===0x8696)m.bus.write(0x7a89,0);if(seeded&&read(a)===0xed&&read(a+1)===0x5f)m.cpu.r=0x42;if(updates>=30&&updates<=31&&[0x8e85,0x8e8c,0x8cfd,0x8e57].includes(a))drawTrace.push({pc:a,id:m.cpu.a,hl:m.cpu.h*256+m.cpu.l,de:m.cpu.d*256+m.cpu.e,iy:m.cpu.yh*256+m.cpu.yl,ret:read(m.cpu.sp)|read(m.cpu.sp+1)<<8});if(a===0x863d){startConsumed=true;m.joystick.fill(255);}if(a===0x91f2&&active)deaths++;if(kind==='tap'&&[0x8cfd,0x8d65,0x8dd3,0x8e29].includes(a)){const p=m.dock[7];for(let at=0x2d0;at<0x350;at+=4)if(p[at]!==255&&p[at+1]>=25&&p[at+1]<=27)motionDraws.push({update:updates,actor:p[at],id:p[at+1],x:p[at+2],y:p[at+3],px:(p[at+2]&6)>>1,py:(p[at+3]&6)>>1});}if(a===0xfd20)irqs++;if(a===0xf930)music++;if(a===0x9d5c)shots++;if(a===0x8e85)actors++;
  if(a===0x865f&&active&&updates===100){fs.writeFileSync(path.join(O,kind+'_completed100.screen.bin'),Buffer.concat([Buffer.from(m.ram.slice(0x4000,0x5800)),Buffer.from(m.ram.slice(0x6000,0x7800))]));}
  if(a===0x94f1&&read(0x7aa4)===3&&(!c||c.region===level-1)){
   if(boss&&!bossStarted)throw Error('BOSS_START');if(!active){active=true;activeFrame=frame;startIrq=irqs;startMusic=music;}
   updates++;m.bus.write(0x7a98,255); // Player protection only: identical neutral scenario.
   const column=read(0x7a84),phase=read(0x7a83),pixel=read(0x7a82),event=read(0x7a90)|read(0x7a91)<<8;
   const actorState=[];for(let i=0;i<28;i++){const a=0x8501+i*9,h=read(a);if(h&63)actorState.push({slot:i,h,script:read(a+1)|read(a+2)<<8,x:read(a+3),y:read(a+4),raw:Array.from({length:9},(_,k)=>read(a+k))});}
   records.push({update:updates,column,phase,pixel,event,clock:read(0x7a89),actors:actorState,ship:[kind==='tap'?m.dock[7][0x1680]:m.ram[0x5b00],kind==='tap'?m.dock[7][0x1681]:m.ram[0x5b01]]});
   if(!events.length||events.at(-1).event!==event)events.push({column,phase,pixel,event});
   if([32,64,120].includes(updates)){const ownerBase=kind==='cart'?JSON.parse(fs.readFileSync(path.join(root,`build/cartridges/integration_work/level${String(level).padStart(2,'0')}/player_ram_layout.json`))).allocations.published_owner_map[0]:0;fs.writeFileSync(path.join(O,`${kind}_${updates}.owner.bin`),kind==='tap'?Buffer.from(m.dock[7].slice(0x1880,0x1b00)):Buffer.from(m.ram.slice(ownerBase,ownerBase+640)));fs.writeFileSync(path.join(O,`${kind}_${updates}.screen.bin`),Buffer.concat([Buffer.from(m.ram.slice(0x4000,0x5800)),Buffer.from(m.ram.slice(0x6000,0x7800))]));}
   if(updates===600){done=true;throw Error('TRACE_DONE');}
  }
 }return baseRead(a);};
 m.bus.write=(a,v)=>{if(boss&&((level===2&&a===0x8504&&updates>=93&&updates<=97)||(level===5&&[0x8516,0x8517,0x8567,0x8568].includes(a)&&updates>=80&&updates<=83)))coordinateTrace.push({update:updates,a,v,old:read(a),pc:m.cpu.pc,bc:m.cpu.b*256+m.cpu.c,de:m.cpu.d*256+m.cpu.e,hl:m.cpu.h*256+m.cpu.l,stack:Array.from({length:10},(_,i)=>read(m.cpu.sp+i)),history:[...pcHistory]});if(level===8&&a===0x850a&&v===0&&read(a)===1)spawnTrace.push({removed:true,pc:m.cpu.pc,clock:read(0x7a89),raw:Array.from({length:9},(_,k)=>read(a+k)),history:[...pcHistory]});if(level===8&&a>=0x8501&&a<0x85fd&&(a-0x8501)%9===0&&v===1&&read(a)===0)spawnTrace.push({a,pc:m.cpu.pc,frame,clock:read(0x7a89),hl:m.cpu.h*256+m.cpu.l,de:m.cpu.d*256+m.cpu.e,bc:m.cpu.b*256+m.cpu.c,iy:m.cpu.yh*256+m.cpu.yl,ret:read(m.cpu.sp)|read(m.cpu.sp+1)<<8});if(kind==='cart'&&(m.portF4&(1<<(a>>>13)))){romWrites++;throw Error('ROM_WRITE '+a.toString(16));}baseWrite(a,v);};
 while(!done&&frame<80000){try{for(;frame<80000&&!done;frame++){
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
  m.keyMatrix.fill(31);m.joystick.fill(255);m.ram[0x91f2]=201;if(process.argv.includes('--safe')){m.portF4=kind==='tap'?9:3;m.bus.write(0x7aa1,4);m.bus.write(0x7aa2,2);}m.bus.read=hooked;Object.assign(m.cpu,{pc:0x8653,sp:0xfffe,iff1:true,iff2:true});bossStarted=true;continue;
 }if(!done){fs.writeFileSync(path.join(O,kind+'_failure.json'),JSON.stringify({error:String(e),frame,updates,pc:m.cpu.pc,region:c?.region},null,2));throw e;}}}
 assert(done,kind+' active game trace did not finish');assert(records.some(r=>r.actors.length>0),kind+' no live actor state');
 const controls=process.argv.includes('--controls')?runtimeControls(m,kind,level):null;
 const result={motionDraws,deaths,controls,kind,updates,framesAfterActive:frame-activeFrame,acceptedIrqs:irqs-startIrq,musicCalls:music-startMusic,shots,actorSelections:actors,romWrites,region:c?.region,playerProtected:true,deathBypass:false,records,events,spawnTrace,drawTrace,coordinateTrace,rngTrace};
 fs.writeFileSync(path.join(O,kind+'_native.bin'),Buffer.from(Array.from({length:0x4000},(_,i)=>read(0xc000+i))));fs.writeFileSync(path.join(O,kind+'_trace.json'),JSON.stringify(result,null,2));return result;
}

const t=trace('tap');const phases={};for(const r of t.motionDraws){phases[r.id]??={};const k=r.px+','+r.py;phases[r.id][k]=(phases[r.id][k]||0)+1;}fs.writeFileSync(path.join(O,'phase_reachability.json'),JSON.stringify({level,updates:t.updates,deaths:t.deaths,phases,deathBypassForStress:true,scope:'600 actual TAP boss updates with native death entry bypass only for phase coverage; observed set, not proof of all script reachability'},null,2));console.log(phases);
