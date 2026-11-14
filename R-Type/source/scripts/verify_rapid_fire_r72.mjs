import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api,root}from'./r22_test_machine.mjs';import{out,demandFixture}from'./boss_motion_fixture_r72.mjs';
const {m,joy,controller:c}=demandFixture();let boot=-1,start=-1,main=0,last=-1,shots=0,selected=null,frames=0,irqShots=0,beams=0;const fired=[];
const read=m.bus.read;m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x8634)m.ram[0x91f2]=201;if(a===0x94f1)main++;if(a===0x9aa2&&start>=0)beams++;if(a===0x9d5c&&start>=0){shots++;if(m.cpu.iff1===false)irqShots++;fired.push({frame:frames,x:m.cpu.e,y:m.cpu.d,irq:!m.cpu.iff1});}}return read(a);};
for(;frames<6000;frames++){
 if(c.booted&&boot<0)boot=frames;const t=frames-boot;m.keyMatrix.fill(31);joy[0]=boot>=0&&t>=800&&t<840?127:255;
 if(main>=60&&start<0&&m.ram[0x5bc2]){start=frames;selected={port:m.dock[3][0x1788],mask:m.dock[3][0x1789]};}
 if(start>=0){m.dock[3][0x1a98]=1;m.ram[0x5bc4]=0;const elapsed=frames-start;if(elapsed<120&&elapsed%8<4)for(let row=0;row<8;row++)if(!(selected.port&(1<<row)))m.keyMatrix[row]&=31^selected.mask;}
 api.runFrame(m);if(start>=0&&frames-start>=400)break;
}
assert(start>=0);const end=119;const late=fired.filter(f=>f.frame-start>end+12);assert.equal(beams,0);assert(shots>=10&&shots<=15,'burst shots '+shots);assert.equal(late.length,0,'Delayed shots after release');assert.equal(m.dock[7][0x16a4],0);const result={passed:true,requested_pulses:15,shots,beams,latest_fired_after_start:Math.max(...fired.map(f=>f.frame-start)),burst_end:end,late_shots:late,queue_count:m.dock[7][0x16a4],scope:'Actual game 15 rapid short presses then release; no queued catch-up beyond 12 display refreshes'};fs.writeFileSync(path.join(out,'rapid_fire_validation.json'),JSON.stringify(result,null,2));console.log(result);
