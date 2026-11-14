import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api}from'./r22_test_machine.mjs';import{out,demandFixture}from'./boss_motion_fixture_r61.mjs';
const rows=[];
for(const n of (process.env.RTYPE_START_LEVELS||'1,2,3,4,5,6,7,8').split(',').map(Number)){
 const{m,joy,controller:c}=demandFixture();let boot=-1,last=-1,updates=0,frame=0;const rr=m.bus.read;m.bus.read=a=>{if(a===m.cpu.pc&&m.stepAdded===0&&last!==m.tstates){last=m.tstates;if(a===0x8634)m.ram[0x91f2]=201;if(a===0x94f1&&rr(0x7aa4)>0)updates++;}return rr(a);};
 for(;frame<20000;frame++){
  m.keyMatrix.fill(31);joy[0]=255;if(c.booted&&boot<0)boot=frame;
  if(boot<0&&frame>8&&m.ram[0xd610]===1){if(n<=5)m.keyMatrix[3]&=~(1<<(n-1));else m.keyMatrix[4]&=~(1<<(10-n));}
  if(boot>=0&&frame-boot>=800&&frame-boot<840)joy[0]=239;
  api.runFrame(m);assert(!c.fatalSeen,'LOADERFAIL '+JSON.stringify({n,pc:m.cpu.pc,step:m.ram[0xd609],page:m.ram[0xd600],mounts:c.mounts}));if(updates>150)break;
 }
 assert(frame<20000,JSON.stringify({n,pc:m.cpu.pc,map:m.portF4,mounts:c.mounts,boot,updates}));assert.equal(c.region,n-1);assert.equal(m.dock[3][0x119c],48+n);assert.equal(m.ram[0xfd95],n);assert.equal(m.ram[0xfd4a],1<<(n-1));
 fs.writeFileSync(path.join(out,`cold_L${n}.home.bin`),m.ram);rows.push({n,frame,boot,updates,mounts:c.mounts,slot:c.region,passed:true});console.log(rows.at(-1));
}
fs.writeFileSync(path.join(out,'direct_start_validation.json'),JSON.stringify({passed:true,rows},null,2));
