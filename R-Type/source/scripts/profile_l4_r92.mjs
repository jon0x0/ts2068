import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';
import{api,root}from'./r22_test_machine.mjs';import{out,demandFixture}from'./boss_motion_fixture_r92.mjs';
const profileOut=path.join(root,'build/diagnostics/l4_speed_r92_fast');fs.mkdirSync(profileOut,{recursive:true});const results=[];let wrapperCount=0;const overrides={};let captured=-1;let trace=[];
for(const level of(process.env.RTYPE_BOSS_LEVELS||'4').split(',').map(Number)){
 const{m,joy,controller:c}=demandFixture();let boot=-1,updates=0,last=-1,jumps=0,before=0,after=0,phase=0,phaseAt=0,stops=0;const seen=new Set();
 const write=m.bus.write;m.bus.write=(a,v)=>{if(c.booted&&c.region===4&&(m.cpu.pc!==0x5e04)&&a<8192&&(m.portF4&1)&&m.dock[0][a]!==v){fs.writeFileSync(path.join(out,'bad_write.home.bin'),m.ram);fs.writeFileSync(path.join(out,'trace.json'),JSON.stringify(trace));throw Error('ROM WRITE '+JSON.stringify({a,v,pc:m.cpu.pc,sp:m.cpu.sp,hl:(m.cpu.h<<8)|m.cpu.l,de:(m.cpu.d<<8)|m.cpu.e,map:m.portF4,active:m.ram[0x5c80],stage:c.region}));}write(a,v);};const read=m.bus.read;m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(phase>=4&&m.cpu.sp<0xfd00&&!(m.cpu.sp>=0x5c60&&m.cpu.sp<=0x5cf2 || m.cpu.sp>=0x5b60&&m.cpu.sp<=0x5bc0)){fs.writeFileSync(path.join(out,'trace.json'),JSON.stringify(trace));throw Error('BAD SP '+m.cpu.sp.toString(16));}if(a===0x8634)m.ram[0x91f2]=201;
 if(a===0x94f1&&!(m.portF4&16)&&read(0x7aa4)>0){updates++;if(phase>=4)after++;}
 if(a===0x8cfd&&phase>=4){const id=read(0x7a9c);if(id>=9&&id<=26){const key=id+':'+read(0x8eb1);overrides[key]=(overrides[key]||0)+1;}}

 if(a===jumpPC){jumps++;console.log('jump',level,updates);}
 if(a===0x90b5&&phase>=4)stops++;
 if(a===0x9172&&phase>=4&&m.portF4===9&&m.cpu.sp>=0xfd00)seen.add(m.cpu.a);
 }return read(a);};
 const sym=fs.readFileSync(path.join(out,'boss_preview.sym'),'utf8');const jumpPC=parseInt(sym.match(/boss_jump: EQU 0x([0-9a-f]+)/i)[1],16);
 const buckets={},hot={};let lastBucket="other",bucketT=0;const bucketRead=m.bus.read;m.bus.read=a=>{if(profileStart>=0&&m.stepAdded===0&&a===m.cpu.pc&&m.tstates!==bucketT){if(bucketT){buckets[lastBucket]=(buckets[lastBucket]||0)+m.tstates-bucketT;}const key=m.portF4.toString(16)+":"+(a&0xff00).toString(16);hot[key]=(hot[key]||0)+1;bucketT=m.tstates;lastBucket=(m.portF4&64)&&a>=0xdc50&&a<0xdcef?"paint":(m.portF4&64)&&a>=0xdcef&&a<0xde43?"prepare":(m.portF4&64)&&a>=0xde73&&a<0xdeae?"palette":(m.portF4&64)&&a>=0xdf50?"synth":(m.portF4&32)&&a>=0xa44a&&a<0xa48d?"synth_helpers":(m.portF4&32)&&a>=0xa000&&a<0xa4ae?"motion":"other";}return bucketRead(a);};let projectilePhases=0,boltTrace=[];const shotWrite=m.bus.write;m.bus.write=(a,v)=>{if(profileStart>=0&&m.portF4===9&&a===0x5eb5)boltTrace.push({frame:frame-profileStart,x:v,pc:m.cpu.pc});shotWrite(a,v);};
 let frame=0,profileStart=-1,profileUpdates=0,irq=0,ticks=0,busy=0,diCycles=0,lastCycle=0,shots=0,beams=0,minStack=0x5bc0;const positions=[];const oldRead=m.bus.read;m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&m.tstates!==lastCycle){if(profileStart>=0){if(!m.cpu.iff1)diCycles+=m.tstates-lastCycle;if(m.portF4===9&&m.cpu.sp>=0x5b60&&m.cpu.sp<=0x5bc0)minStack=Math.min(minStack,m.cpu.sp);if(a===0x9d5c&&!(m.portF4&16))shots++;if(a===0x9aa2&&!(m.portF4&16))beams++;if(a===0xfb00){irq++;if(m.ram[0x5bcd])busy++;}if(a===0xe400&&(m.portF4&128))ticks++;if(a===0x5883&&(m.portF4&4))projectilePhases++;}lastCycle=m.tstates;}return oldRead(a);};
 for(;frame<50000;frame++){
  if(c.booted&&boot<0)boot=frame;
  m.keyMatrix.fill(31);const t=frame-boot;
  if(boot>=0&&t>=600&&t<700){if(level<=5)m.keyMatrix[3]=31^(1<<(level-1));else m.keyMatrix[4]=31^(1<<(10-level));}
  joy[0]=boot>=0&&t>=800&&t<840?127:255;
  if(updates>=15&&phase===0){phase=1;phaseAt=updates;before=m.bus.read(0x7a84);}
  if(phase===1||phase===3)m.keyMatrix[7]&=~16;
  if(phase===4&&updates-phaseAt<10)m.keyMatrix[7]&=~16;
  if(after>=100&&profileStart<0){profileStart=frame;profileUpdates=after;}if(profileStart>=0){const t=frame-profileStart;const slot=t%64<32?0x1782:0x1780;const port=m.dock[3][slot],mask=m.dock[3][slot+1];for(let r=0;r<8;r++)if(!(port&(1<<r)))m.keyMatrix[r]&=31^mask;if((t<128&&t%16<4)||(t>=256&&t<352)){const fp=m.dock[3][0x1788],fm=m.dock[3][0x1789];for(let r=0;r<8;r++)if(!(fp&(1<<r)))m.keyMatrix[r]&=31^fm;}m.ram[0x5bc4]=0;m.dock[3][0x1a98]=1;}api.runFrame(m);if(profileStart>=0)positions.push({frame:frame-profileStart,x:m.dock[7][0x1680],y:m.dock[7][0x1681],copy:m.ram[0x5bc3],busy:m.ram[0x5bcd]});
  if(phase===1&&updates-phaseAt>=10){assert.equal(jumps,0,'Held first B must not jump');phase=2;phaseAt=updates;}
  if(phase===2&&updates-phaseAt>=4){phase=3;phaseAt=updates;}
  if(phase===3&&jumps===1){phase=4;phaseAt=updates;}
  // Keep the second press held for several updates to verify latch, then release.
  if(profileStart>=0&&frame-profileStart>=479){fs.writeFileSync(path.join(profileOut,"buckets.json"),JSON.stringify({buckets,hot},null,2));const result={level,irq,ticks,busy,shots,beams,minStack,projectilePhases,boltTrace,world_updates:after-profileUpdates,diCycles,positions};fs.writeFileSync(path.join(profileOut,'masked_L'+level+'.json'),JSON.stringify(result,null,2));console.log({level,irq,ticks,busy,shots,beams,minStack,projectilePhases,boltTrace,world_updates:after-profileUpdates,diCycles,moves:positions.filter((p,i)=>i&&p.x!==positions[i-1].x).length,travel:positions.reduce((n,p,i)=>n+(i?Math.abs(p.x-positions[i-1].x):0),0)});break;}
 }

}

