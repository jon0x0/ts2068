import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {api} from './r22_test_machine.mjs';import {out,demandFixture} from './boss_motion_fixture_r67.mjs';
const f=demandFixture({delay:true,selectorDelay:500000}),{m,joy,controller:c}=f;
const route=[2,1,2,3,2,5,2,6];let frame=0,boot=-1,last=-1,updates=0,phase=0,at=0,index=0,init=0,reset=0,ship=0,jumpUpdates=0;const results=[];const read=m.bus.read;
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x8634)m.ram[0x91f2]=201;if(a===0x8640)init++;if(a===0x8721)reset++;if(a===0x8bae)ship++;if(a===0x94f1&&read(0x7aa4)>0)updates++;}return read(a);};
let before=null;
for(;frame<100000;frame++){
 m.keyMatrix.fill(31);joy[0]=255;if(c.booted&&boot<0)boot=frame;if(boot>=0&&frame-boot>=800&&frame-boot<840)joy[0]=127;
 if(phase===0&&updates>50){if(index===7)m.ram[0xfd4a]&=~32;before={init,reset,ship,mounts:c.mounts.length,updates,valid:m.ram[0xfd4a]};phase=1;at=frame;}
 if(phase===1){if(frame-at<100)m.keyMatrix[6]&=~2;else if(frame-at<130){}else if(frame-at<230){const n=route[index];if(n<=5)m.keyMatrix[3]&=~(1<<(n-1));else m.keyMatrix[4]&=~(1<<(10-n));}else phase=2;}
 api.runFrame(m);assert(!c.fatalSeen,'Loader error');
 if(phase===2&&updates>before.updates+60&&c.region===route[index]-1&&m.dock[3][0x119c]===48+route[index]){
  assert(init>before.init,'Skipped normal ECM initialization');assert(reset>before.reset,'Skipped actor/terrain reset');assert(ship>before.ship,'Skipped ship setup');
  const n=route[index],wasCached=!!(before.valid&(1<<(n-1)));assert.equal(c.mounts.length-before.mounts,wasCached?0:1,'Resident status must control loading');assert(m.ram[0xfd4a]&(1<<(n-1)));
  fs.writeFileSync(path.join(out,`jump_${index}_L${n}.home.bin`),m.ram);results.push({from:index?route[index-1]:1,to:n,frame,cached:wasCached,init:init-before.init,reset:reset-before.reset,mounts:c.mounts.slice(before.mounts)});console.log(results.at(-1));
  index++;if(index===route.length)break;phase=0;
 }
}
assert.equal(index,route.length,JSON.stringify({index,frame,phase,pc:m.cpu.pc,updates,region:c.region}));assert.equal(f.fifoCount,0);fs.writeFileSync(path.join(out,'repeated_jumps_validation.json'),JSON.stringify({passed:true,results,mounts:c.mounts},null,2));
