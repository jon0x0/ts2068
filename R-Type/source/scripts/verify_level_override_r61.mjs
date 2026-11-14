import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api}from'./r22_test_machine.mjs';import{out,demandFixture}from'./boss_motion_fixture_r61.mjs';
const {m,joy,controller:c}=demandFixture();let boot=-1,last=-1,updates=0,frame=0,phase=0,at=0,first=0,second=0,gameRegion=-1;const rr=m.bus.read;m.bus.read=a=>{if(a===m.cpu.pc&&m.stepAdded===0&&last!==m.tstates){last=m.tstates;if(a===0x3a00&&phase===3)console.log('KEY',frame,m.ram[0xfda5],m.keyMatrix[6],m.keyMatrix[3]);if(a===0x8634)m.ram[0x91f2]=201;if(a===0x94f1&&rr(0x7aa4)>0)updates++,gameRegion=c.region;}return rr(a);};
for(;frame<35000;frame++){
 m.keyMatrix.fill(31);joy[0]=255;if(c.booted&&boot<0)boot=frame;if(boot>=0&&frame-boot>=800&&frame-boot<840)joy[0]=239;
 if(updates>40&&phase===0){phase=1;at=frame;}
 if(phase===1){if(frame-at<90)m.keyMatrix[6]&=~2;else if(frame-at<110){}else if(frame-at<210)m.keyMatrix[3]&=~4;else phase=2;}
 if(phase===2&&updates>250&&gameRegion===2&&c.region===2&&m.dock[3][0x119c]===51&&m.ram[0x5bc2]){first=frame;phase=3;at=frame;}
 if(phase===3){if(frame-at<90)m.keyMatrix[6]&=~2;else if(frame-at<110){}else if(frame-at<210)m.keyMatrix[3]&=~1;else phase=4;}
 api.runFrame(m);assert(!c.fatalSeen);if(phase===4&&gameRegion===0&&c.region===0&&m.dock[3][0x119c]===49&&m.ram[0x5bc2]){second=frame;break;}
}
assert(first&&second,JSON.stringify({phase,frame,pc:m.cpu.pc,region:c.region,updates,state:m.ram[0xfda5],selected:m.ram[0xfd95],mounts:c.mounts}));assert(!c.mounts.includes('LEVEL01.TAP'));assert.equal(c.mounts.filter(x=>x==='LEVEL03.TAP').length,1);fs.writeFileSync(path.join(out,'override_validation.json'),JSON.stringify({passed:true,first,second,mounts:c.mounts,selected:m.ram[0xfd95],cached_return:true},null,2));console.log({passed:true,first,second,mounts:c.mounts});
