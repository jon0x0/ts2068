import assert from'node:assert/strict';import{api}from'./r22_test_machine.mjs';import{demandFixture}from'./old_transition_fixture.mjs';
const{m,joy,controller:c}=demandFixture();let boot=-1,caught=null;
try{for(let f=0;f<10000;f++){if(c.booted&&boot<0)boot=f;m.keyMatrix.fill(31);if(boot>=0&&f-boot>=600&&f-boot<700)m.keyMatrix[3]=27;joy[0]=boot>=0&&f-boot>=800&&f%120<70?239:255;api.runFrame(m);}}catch(e){caught=e.message;}
assert(caught&&/secondary|Secondary/.test(caught),'Old transition must reproduce visible scratch');console.log('Negative control reproduced:',caught);
