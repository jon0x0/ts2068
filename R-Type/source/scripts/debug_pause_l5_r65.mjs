import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api}from'./r22_test_machine.mjs';import{out,demandFixture}from'./boss_motion_fixture_r65.mjs';
const level=Number(process.env.TEST_LEVEL||1),{m,joy,controller:c}=demandFixture();let boot=-1,u=0,frame=0,phase=0,mark=0,before,updates,vol;const sy=Object.fromEntries([...fs.readFileSync(path.join(out,level===5?'ui_home.sym':'ui.sym'),'utf8').matchAll(/([\w.]+): EQU 0x([0-9a-f]+)/ig)].map(x=>[x[1],parseInt(x[2],16)]));const trace=[];const rr=m.bus.read;m.bus.read=a=>{if(a===m.cpu.pc&&m.stepAdded===0){trace.push([a,m.portF4,m.cpu.sp]);if(trace.length>100)trace.shift();if(a===0x8101&&m.portF4===25)throw Error(JSON.stringify({frame,boot,trace}));if(a===0x8634)m.ram[0x91f2]=201;if(a===0x94f1){u++;m.dock[3][0x1a98]=1;}}return rr(a);};
for(;frame<10000;frame++){
 m.keyMatrix.fill(31);joy.fill(255);if(c.booted&&boot<0)boot=frame;if(boot<0&&frame>8&&m.ram[0xd610]===1)m.keyMatrix[3]&=~(1<<(level-1));if(boot>=0&&frame-boot>=800&&frame-boot<840)joy[Number(process.env.JOY_SOCKET||0)]=127;
 if(phase===0&&u>20&&m.ram[0x5bc2]){phase=1;mark=frame;}
 if(phase===1){m.keyMatrix[5]&=~1;m.keyMatrix[0]&=~1;}
 if(phase===1&&frame-mark>4&&m.cpu.pc>=sy.released&&m.cpu.pc<sy.title){phase=2;mark=frame;before=Buffer.concat([Buffer.from(m.ram.slice(0x4000,0x5800)),Buffer.from(m.ram.slice(0x6000,0x7800))]);updates=u;fs.writeFileSync(path.join(out,`paused_L${level}.home.bin`),m.ram);}
 if(phase===2&&frame-mark>30){assert.equal(u,updates);assert(before.equals(Buffer.concat([Buffer.from(m.ram.slice(0x4000,0x5800)),Buffer.from(m.ram.slice(0x6000,0x7800))])));phase=3;mark=frame;}
 if(phase===3&&frame-mark<3)m.keyMatrix[5]&=~1;
 api.runFrame(m);assert(!c.fatalSeen);
 if(phase===3&&frame-mark>10&&u>updates){phase=4;break;}
}
assert.equal(phase,4,JSON.stringify({frame,u,phase,pc:m.cpu.pc,map:m.portF4,sy}));const result={passed:true,level,frames:frame,updates:u,pause_freezes_world:true,pause_screen_stable:true,resumed:true,physical_fire_socket:Number(process.env.JOY_SOCKET||0)};fs.writeFileSync(path.join(out,`pause_L${level}.json`),JSON.stringify(result,null,2));console.log(result);
