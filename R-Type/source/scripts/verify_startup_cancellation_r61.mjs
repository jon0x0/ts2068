import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api}from'./r22_test_machine.mjs';import{out,demandFixture}from'./boss_motion_fixture_r61.mjs';
const cases=[{name:'latest_wins',level:8,earlier:2,ready:(m,c)=>c.mounts.at(-1)==='START01.TAP'&&m.ram[0xd614]>=2},{name:'asset',level:4,ready:(m,c)=>c.mounts.at(-1)==='START01.TAP'&&m.ram[0xd614]>=2},{name:'core',level:8,ready:(m,c)=>c.mounts.at(-1)==='RTCORE.TAP'&&m.ram[0xd615]>=3},{name:'verify',level:3,ready:(m,c)=>m.ram[0xd614]>=70&&c.blocks>=140&&m.ram[0xd615]>=10&&m.ram[0xd615]<64},{name:'final_setup',level:6,ready:(m,c)=>m.ram[0xd614]>=70&&c.blocks>=140&&m.ram[0xd615]===64},{name:'delayed_reply',level:7,options:{delay:true,selectorDelay:500000},ready:(m,c)=>c.mounts.at(-1)==='START01.TAP'&&m.ram[0xd614]>=1}];const rows=[];
for(const test of cases){const f=demandFixture(test.options||{}),{m,controller:c}=f;let fired=-1,shown=-1,boot=-1,frame=0,last=-1;const rr=m.bus.read;m.bus.read=a=>{if(a===m.cpu.pc&&m.stepAdded===0&&a===0x8634&&boot<0)boot=frame;return rr(a);};
 for(;frame<18000&&boot<0;frame++){
  m.keyMatrix.fill(31);if(fired<0&&m.ram[0xd610]===1&&test.ready(m,c))fired=frame;
  if(fired>=0&&frame-fired<12){const n=test.earlier&&frame-fired<4?test.earlier:test.level;if(n<=5)m.keyMatrix[3]&=~(1<<(n-1));else m.keyMatrix[4]&=~(1<<(10-n));}
  api.runFrame(m);if(fired>=0&&shown<0&&m.ram[0xd616]===48+test.level)shown=frame;assert(!c.fatalSeen,test.name);
 }
 assert(fired>=0&&boot>=0,test.name+' did not reach selected boot '+JSON.stringify({fired,boot,pc:m.cpu.pc,mounts:c.mounts}));assert(shown-fired-(test.earlier?4:0)<=4,'Selection display lag '+test.name);assert.equal(c.region,test.level-1);assert.equal(m.ram[0xfd95],test.level);assert.equal(m.ram[0xfd4a],1<<(test.level-1));assert.equal(f.fifoCount,0,'Old file reply was not drained');assert(c.commands.every(v=>!v.startsWith('tpi:cd')));rows.push({name:test.name,level:test.level,fired,shown,display_latency_frames:shown-fired,boot,mounts:c.mounts,passed:true});console.log(rows.at(-1));
}
fs.writeFileSync(path.join(out,'startup_cancellation_validation.json'),JSON.stringify({passed:true,rows},null,2));
