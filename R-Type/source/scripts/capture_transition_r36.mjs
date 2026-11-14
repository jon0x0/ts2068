import fs from'node:fs';import path from'node:path';import{root,api}from'./r22_test_machine.mjs';import{demandFixture}from'./transition_disk_fixture.mjs';
const{m,joy,controller:c}=demandFixture();let boot=-1,count=0;const io=m.bus.ioWrite;
m.bus.ioWrite=(p,v)=>{io(p,v);if((p&255)===255&&(v&7)===1&&c.booted){fs.writeFileSync(path.join(root,'build/diagnostics/transition_r36/new_secondary.home.bin'),m.ram);count++;}};
for(let f=0;f<7000;f++){if(c.booted&&boot<0)boot=f;m.keyMatrix.fill(31);if(boot>=0&&f-boot>=600&&f-boot<700)m.keyMatrix[3]=27;joy[0]=boot>=0&&f-boot>=800&&f%120<70?239:255;api.runFrame(m);}console.log('Black secondary handoffs',count);
