import fs from 'node:fs';import assert from 'node:assert/strict';import {demandFixture,out}from './boss_motion_fixture_r145.mjs';import {api,off,z}from './r22_test_machine.mjs';
const{m,joy,controller}=demandFixture();
function call(pc){m.portF4=9;m.portFF=2;Object.assign(m.cpu,{pc,sp:0xffe0,iff1:false,iff2:false,halted:false,eiDelay:false});m.ram.set([0,0xf0],0xffe0);let steps=0;while(m.cpu.pc!==0xf000&&steps++<2000000)z.runZ80(m.cpu,m.bus,1,m);assert(steps<2000000);}
let ready=false,startStamp=-1;const bootRead=m.bus.read;
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&startStamp!==m.tstates){startStamp=m.tstates;if(a===0x94f1&&bootRead(0x7aa4)===3){ready=true;throw Error('ACTIVE');}}return bootRead(a);};
try{for(let frame=0;frame<6000&&!ready;frame++){m.keyMatrix.fill(31);joy[0]=controller.booted&&frame%240<45?127:255;api.runFrame(m);}}catch(e){if(!ready)throw e;}
if(!ready)throw Error('No actual game start');m.bus.read=bootRead;m.keyMatrix.fill(31);joy.fill(255);m.keyMatrix[7]&=~16;call(0x1fa3);m.keyMatrix.fill(31);call(0x1fa3);m.keyMatrix[7]&=~16;call(0x1fa3);m.keyMatrix.fill(31);Object.assign(m.cpu,{pc:0x8653,sp:0xfffe,iff1:true,iff2:true});


const map=0x1880;
let updates=0,last=-1,spawns=0,hits=0,saw=false,dead=false;const rd=m.bus.read,wr=m.bus.write,health=[];
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x94f1&&rd(0x7aa4)>0){updates++;m.dock[3][0x1a98]=255;}if(a===0x9d5c)spawns++;}return rd(a);};
m.bus.write=(a,v)=>{if(a===0x85d0&&m.cpu.pc===0xa57d){hits++;health.push([updates,rd(a),v]);if((v&31)===0)dead=true;}wr(a,v);};
let frame=0;for(;frame<12000&&updates<160&&!dead;frame++){
 m.keyMatrix.fill(31);joy.fill(255);let ys=[];for(let i=0;i<640;i++)if(m.dock[7][map+i]===0x98)ys.push(Math.floor(i/32));
 if(ys.length){saw=true;const target=(Math.min(...ys)+.5)*8,player=m.dock[7][0x1681];if(player<target-2)joy[0]&=~2;else if(player>target+2)joy[0]&=~1;if(process.argv.includes('--charged')?frame%36<18:frame%12<3)joy[0]&=~128;}
 api.runFrame(m);
}
console.log({frame,updates,spawns,hits,saw,dead,health,game:rd(0x7aa4),latch:rd(0xfd4b),column:rd(0x7a84)});assert(ready&&saw&&dead&&hits===8,'Live walker must take eight native damage hits and reach zero health');console.log({frame,updates,spawns,hits,saw,dead,health});fs.writeFileSync('build/cartridges/integration_work/level01/'+(process.argv.includes('--charged')?'tap_walker_charged_pilot.json':'tap_walker_live_pilot.json'),JSON.stringify({passed:true,frame,updates,spawns,hits,saw,dead,health,playerProtectionOnly:true,enemyHealthEdited:false,finalActor:[...m.ram.slice(0x85d0,0x85d9)],scope:'Actual TAP menu start followed by main-loop boss shortcut and native joystick pilot; normal/held-charge firing, moving last walker; no native death bypass'},null,2));



