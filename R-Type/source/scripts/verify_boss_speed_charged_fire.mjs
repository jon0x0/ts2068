import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api,root}from'./r22_test_machine.mjs';import{out,demandFixture}from'./boss_speed_fixture.mjs';
const {m,joy,controller:c}=demandFixture();let boot=-1,start=-1,main=0,last=-1,shots=0,selected=null,frames=0,irqShots=0,beams=0;const fired=[];
const read=m.bus.read;m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x8634)m.ram[0x91f2]=201;if(a===0x94f1)main++;if(a===0x9aa2&&start>=0)beams++;if(a===0x9d5c&&start>=0){shots++;if(m.cpu.iff1===false)irqShots++;fired.push({frame:frames,x:m.cpu.e,y:m.cpu.d,irq:!m.cpu.iff1});}}return read(a);};
for(;frames<6000;frames++){
 if(c.booted&&boot<0)boot=frames;const t=frames-boot;m.keyMatrix.fill(31);joy[0]=boot>=0&&t>=800&&t<840?239:255;
 if(main>=60&&start<0&&m.ram[0x5bc2]){start=frames;selected={port:m.dock[3][0x1788],mask:m.dock[3][0x1789]};}
 if(start>=0){m.dock[3][0x1a98]=1;m.ram[0x5bc4]=0;const elapsed=frames-start;if((elapsed<96&&elapsed%12<6)||(elapsed>=200&&elapsed<270))for(let row=0;row<8;row++)if(!(selected.port&(1<<row)))m.keyMatrix[row]&=31^selected.mask;}
 api.runFrame(m);if(start>=0&&frames-start>=400)break;
}
assert(start>=0);assert(shots>=7&&shots<=8,'Expected eight release shots (no duplicates); '+shots);assert(irqShots>0,'No interrupt-dispatched normal shots');assert.equal(beams,1,'Charged hold must release one beam');const result={passed:true,physical_presses:8,normal_shots:shots,charged_beams:beams,irq_dispatched:irqShots,selected_binding:selected,queue_count:m.dock[7][0x16a4],fired,scope:'Actual full-game native release-shot allocation from selected key, invulnerable route; no fixed key assignment'};fs.writeFileSync(path.join(out,'charged_fire_validation.json'),JSON.stringify(result,null,2));console.log(result);
