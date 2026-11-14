import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api}from'./r22_test_machine.mjs';import{out,demandFixture}from'./boss_motion_fixture_r135.mjs';
const results=[];
for(const level of[1]){
const{m,joy,controller:c}=demandFixture();let boot=-1,last=-1,updates=0,planted=false,attached=0,phase=0,phaseAt=0,frame=0;const q=()=>m.dock[3];const read=m.bus.read;
m.bus.read=a=>{if(a===m.cpu.pc&&m.stepAdded===0&&last!==m.tstates){last=m.tstates;if(a===0x8634)m.ram[0x91f2]=201;if(a===0x94f1&&read(0x7aa4)>0){updates++;m.ram[0x5bc4]=0;
 if(updates>60&&!planted){const d=q();d[0x1aa8]=3;d[0x1aa9]=d[0x1aa1];d[0x1aaa]=d[0x1aa2];d[0x1abe]=1;d[0x1aa3]=0;d[0x1aab]=0;d[0x1aae]=0;d[0x1a98]=0;planted=true;phaseAt=updates;}
 if(phase===3){const d=q();d[0x1ac1]=3;d[0x1ac2]=0;d[0x1ac3]=d[0x1aa1]+1;d[0x1ac4]=d[0x1aa2];phase=4;phaseAt=updates;}
 if(planted&&phase===0&&q()[0x1aa3]>0){attached=updates;phase=1;phaseAt=updates;}
 }}return read(a);};
for(;frame<20000;frame++){m.keyMatrix.fill(31);joy[0]=255;if(c.booted&&boot<0)boot=frame;if(boot<0&&frame>8&&m.ram[0xd610]===1){if(level<=5)m.keyMatrix[3]&=~(1<<(level-1));else m.keyMatrix[4]&=~(1<<(10-level));}if(boot>=0&&frame-boot>=800&&frame-boot<840)joy[0]=127;
 if(phase===1&&updates-phaseAt<4)m.keyMatrix[7]&=~1;
 if(phase===1&&q()[0x1aa3]===0){phase=2;phaseAt=updates;}
 if(phase===2&&updates-phaseAt>20&&updates-phaseAt<24)m.keyMatrix[7]&=~1;
 api.runFrame(m);assert(!c.fatalSeen);if(phase===2&&updates-phaseAt>24&&q()[0x1aa3]>0)phase=3;if(phase===4&&q()[0x1abe]>=2)break;
}
assert(frame<20000,JSON.stringify({level,phase,updates,attached,pod:q()[0x1aa8],mode:q()[0x1aa3],power:q()[0x1abe],pickup:[...q().slice(0x1ac1,0x1ac9)]}));results.push({level,frame,attached_after_updates:attached-61,detach_and_recall:true,native_docking:true,pickup_collected:true,force_upgrade:2});console.log(results.at(-1));fs.writeFileSync(path.join(out,`force_L${level}.home.bin`),m.ram);
}
fs.writeFileSync(path.join(out,'force_validation.json'),JSON.stringify({passed:true,controlled_detached_pod_fixture:true,results},null,2));

