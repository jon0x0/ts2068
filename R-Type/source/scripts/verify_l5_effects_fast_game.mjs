import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';
import{api,root}from'./r22_test_machine.mjs';import{out,demandFixture}from'./l5_effects_fast_fixture.mjs';
let selectedID=0,targetX=0,targetY=0;const motion=[];const actors=new Map();const results=[];let wrapperCount=0;const overrides={};let captured=-1;let trace=[];
for(const level of(process.env.RTYPE_BOSS_LEVELS||'1,2,3,4,5,6,7,8').split(',').map(Number)){
 const{m,joy,controller:c}=demandFixture();let boot=-1,updates=0,last=-1,jumps=0,before=0,after=0,phase=0,phaseAt=0,stops=0;const seen=new Set();
 const write=m.bus.write;m.bus.write=(a,v)=>{if(c.booted&&c.region===4&&(m.cpu.pc!==0x5e04)&&a<8192&&(m.portF4&1)&&m.dock[0][a]!==v){fs.writeFileSync(path.join(out,'bad_write.home.bin'),m.ram);fs.writeFileSync(path.join(out,'trace.json'),JSON.stringify(trace));throw Error('ROM WRITE '+JSON.stringify({a,v,pc:m.cpu.pc,sp:m.cpu.sp,hl:(m.cpu.h<<8)|m.cpu.l,de:(m.cpu.d<<8)|m.cpu.e,map:m.portF4,active:m.ram[0x5c80],stage:c.region}));}write(a,v);};const read=m.bus.read;m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(phase>=4&&m.cpu.sp<0xfd00&&!(m.cpu.sp>=0x5c80&&m.cpu.sp<=0x5cf2 || m.cpu.sp>=0x5b60&&m.cpu.sp<=0x5bc0)){fs.writeFileSync(path.join(out,'trace.json'),JSON.stringify(trace));throw Error('BAD SP '+m.cpu.sp.toString(16));}if(a===0x8634)m.ram[0x91f2]=201;
 if(a===0x94f1&&!(m.portF4&16)&&read(0x7aa4)>0){updates++;if(phase>=4)after++;}
 if(a===0x8cfd&&phase>=4&&m.portF4===9&&m.cpu.sp>=0xfd00){const id=read(0x7a9c);if(id>=9&&id<=26){const key=id+':'+read(0x8eb1);overrides[key]=(overrides[key]||0)+1;}}
 if(a===0x868c&&phase>=4&&after>=40&&after<=400&&after%20===0&&captured!==after){captured=after;fs.writeFileSync(path.join(out,'sample_'+after+'.home.bin'),m.ram);}

 if(a===jumpPC){jumps++;console.log('jump',level,updates);}
 if(a===0x90b5&&phase>=4)stops++;
 if(a===0x9172&&phase>=4&&m.portF4===9&&m.cpu.sp>=0xfd00){seen.add(m.cpu.a);selectedID=m.cpu.a;targetX=(m.cpu.c*8)&255;targetY=(m.cpu.b*8)&255;}
 if(a===0x8cfd&&phase>=4&&m.portF4===9&&m.cpu.sp>=0xfd00&&[8,30,31,32,33].includes(selectedID)){const iy=m.cpu.yh*256+m.cpu.yl,at=0x300+((((m.cpu.yl-1)*57)&255)*2),x=m.dock[7][at],y=m.dock[7][at+1],old=actors.get(iy);if(old){const tx=targetX,ty=targetY;for(const[k,t]of[['x',tx],['y',ty]]){const delta=(t-old[k]+256)%256;if(delta<=8||delta>=248)assert(Math.min(Math.abs((k==='x'?x:y)-old[k]),256-Math.abs((k==='x'?x:y)-old[k]))<=2,'Movement exceeded two pixels '+JSON.stringify({k,t,old,x,y,iy,after}));}}assert.equal(m.cpu.c*8+m.dock[4][0xee3]*2,x,JSON.stringify({iy,id:selectedID,bc:m.cpu.b*256+m.cpu.c,after,sp:m.cpu.sp,mode:m.dock[4][0xee0]}));assert.equal(m.cpu.b*8+m.dock[4][0xee4],y,JSON.stringify({iy,id:selectedID,bc:m.cpu.b*256+m.cpu.c,after,sp:m.cpu.sp}));actors.set(iy,{x,y});motion.push({u:after,iy,x,y});}

 }return read(a);};
 const sym=fs.readFileSync(path.join(out,'boss_preview.sym'),'utf8');const jumpPC=parseInt(sym.match(/boss_jump: EQU 0x([0-9a-f]+)/i)[1],16);
 let frame=0;
 for(;frame<50000;frame++){
  if(c.booted&&boot<0)boot=frame;
  m.keyMatrix.fill(31);const t=frame-boot;
  if(boot>=0&&t>=600&&t<700){if(level<=5)m.keyMatrix[3]=31^(1<<(level-1));else m.keyMatrix[4]=31^(1<<(10-level));}
  joy[0]=boot>=0&&t>=800&&t<840?239:255;
  if(updates>=15&&phase===0){phase=1;phaseAt=updates;before=m.bus.read(0x7a84);}
  if(phase===1||phase===3)m.keyMatrix[7]&=~16;
  if(phase===4&&updates-phaseAt<10)m.keyMatrix[7]&=~16;
  api.runFrame(m);
  if(phase===1&&updates-phaseAt>=10){assert.equal(jumps,0,'Held first B must not jump');phase=2;phaseAt=updates;}
  if(phase===2&&updates-phaseAt>=4){phase=3;phaseAt=updates;}
  if(phase===3&&jumps===1){phase=4;phaseAt=updates;}
  // Keep the second press held for several updates to verify latch, then release.
  if(phase===4&&after>=700)break;
 }
 if(frame>=50000){fs.writeFileSync(path.join(out,'failed.home.bin'),m.ram);fs.writeFileSync(path.join(out,'failed.dock4.bin'),m.dock[4]);console.log('FAIL',{map:m.portF4,sp:m.cpu.sp,stage:m.dock[3][0x119c],active:m.ram[0x5c80]});}assert(frame<50000,'No sustained boss preview L'+level+' '+JSON.stringify({phase,updates,jumps,pc:m.cpu.pc}));
 assert.equal(jumps,1);assert.equal(m.dock[3][0x119c],48+level,'Unexpected stage transition');
 assert(seen.has([8,3,41,27,8,18,53,42][level-1]),'Native boss artwork not rendered L'+level);
 assert(m.dock[3][0x1a84]>= [99,63,9,74,73,8,61,32][level-1],'Checkpoint not reached '+JSON.stringify({column:m.dock[3][0x1a84],state:m.ram[0xfd4b],stops,seen:[...seen]}));
 fs.writeFileSync(path.join(out,`boss_level${level}.home.bin`),m.ram);
 fs.writeFileSync(path.join(out,`boss_level${level}.dock7.bin`),m.dock[7]);
 const phaseBytes=fs.readFileSync(path.join(root,'build/diagnostics/pixel_movement_trial/ship_phases.bin')).subarray(768,1536);assert(Buffer.from(m.dock[7].slice(0xd80,0x1080)).equals(phaseBytes),'Phase cache changed');
 fs.writeFileSync(path.join(out,'palette_overrides.json'),JSON.stringify(overrides,null,2));
 results.push({level,frame,updates,after,jumps,scrollStops:stops,renderedDescriptors:[...seen],column:m.dock[3][0x1a84],passed:true});console.log(results.at(-1));
 fs.writeFileSync(path.join(out,`boss_level${level}.json`),JSON.stringify(results.at(-1),null,2));
}
fs.writeFileSync(path.join(out,'boss_preview_validation.json'),JSON.stringify({results,passed:true,death_bypass_diagnostic:true},null,2));





assert(motion.length>1000&&actors.size>=24,'Missing live actor motion samples');fs.writeFileSync(path.join(out,'motion_trace.json'),JSON.stringify({passed:true,actors:actors.size,samples:motion}));
