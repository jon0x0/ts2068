import fs from 'node:fs';import assert from 'node:assert/strict';import{stockFixture}from './stock_fixture.mjs';import{api}from './r22_test_machine.mjs';
const f=stockFixture(4),{m,call,out}=f,joy=m.joystick,rd=m.bus.read,sy=Object.fromEntries([...fs.readFileSync(out+'/stock_controls.sym','utf8').matchAll(/(\w+): EQU 0x([0-9a-f]+)/ig)].map(x=>[x[1],parseInt(x[2],16)]));
m.ram[0x91f2]=0xc9;m.ram[0x7aa4]=3;call(sy.boss_jump);m.ram.set([254,2,254,4,254,8,254,16,127,1,127,2],0xbd80);Object.assign(m.cpu,{pc:0x8653,sp:0xfffe,iff1:true,iff2:true});
let encounter=0,last=-1; m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x94f1){encounter++;m.ram[0x7a98]=255;}}return rd(a)};
let collected=false,docked=false;for(let k=0;k<10000&&!docked;k++){m.keyMatrix.fill(31);joy.fill(255);if(m.ram[0x7abe]<2)m.keyMatrix[0]&=~4;api.runFrame(m);collected ||= m.ram[0x7abe]>=2;docked=collected&&m.ram[0x7aa3]>0;}
assert(docked,'Collectible Force must dock '+JSON.stringify({encounter,pc:m.cpu.pc,xy:[m.ram[0x5b00],m.ram[0x5b01]],nativeXY:[m.ram[0x7aa1],m.ram[0x7aa2]],power:m.ram[0x7abe],side:m.ram[0x7aa3],game:m.ram[0x7aa4],pickups:[...m.ram.slice(0x7ac1,0x7ac9)]}));

const cycles=[];for(let iteration=0;iteration<2;iteration++){
 for(let k=0;k<8000&&encounter<200;k++){m.keyMatrix.fill(31);joy.fill(255);api.runFrame(m);}
 m.bus.read=rd;m.ram[0x91f2]=0xcd;m.ram[0x7a98]=0;let death=-1,respawn=-1,frame=0,lastStamp=-1;
 m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&lastStamp!==m.tstates){lastStamp=m.tstates;if(a===0x91f2&&death<0)death=frame;if(a===0x8bae&&death>=0&&respawn<0)respawn=frame;}return rd(a)};m.ram[0x5c87]=1;
 for(;frame<7000;frame++){m.keyMatrix.fill(31);joy.fill(255);api.runFrame(m);if(respawn>=0&&m.ram[0x7aa4]===3&&m.ram[0x7ac1]===2&&m.ram[0x7ac5]===2)break;}
 assert(death>=0&&respawn>death&&frame<7000,JSON.stringify({death,respawn,frame,pc:m.cpu.pc,column:m.ram[0x7a84],power:m.ram[0x7abe],pickup:[...m.ram.slice(0x7ac1,0x7ac9)]}));assert.equal(m.ram[0x7abe],0);m.ram[0x91f2]=0xc9;
 let regained=false,rear=false;for(let k=0;k<7000&&!rear;k++){m.keyMatrix.fill(31);joy.fill(255);if(m.ram[0x7abe]<2||m.ram[0x5b00]<216)m.keyMatrix[0]&=~4;if(regained&&m.ram[0x7aa3]===1&&k%240<120)m.keyMatrix[7]&=~2;api.runFrame(m);regained ||= m.ram[0x7abe]>=2;rear=regained&&m.ram[0x7aa3]===2;}
 assert(rear,'Recollect and rear docking '+JSON.stringify({iteration,power:m.ram[0x7abe],side:m.ram[0x7aa3],game:m.ram[0x7aa4],xy:[m.ram[0x5b00],m.ram[0x5b01]],pickups:[...m.ram.slice(0x7ac1,0x7ac9)]}));let rearFire=false;for(let k=0;k<1600&&!rearFire;k++){m.keyMatrix.fill(31);joy.fill(255);if(k%180<120){joy[0]=127;m.keyMatrix[7]&=~1;}api.runFrame(m);for(const p of[0x5f00,0x5f34,0x5f68])if(m.ram[p]&&[1,3,5].includes(m.ram[p+3])&&m.ram[0x7aa3]===2)rearFire=true;}
 assert(rearFire);cycles.push({deathFrame:death,respawnFrame:respawn,pickupFrame:frame,equipmentLost:true,collected:true,rearDocked:true,rearFire:true});
}
const r={passed:true,cycles,romWrites:f.romWrites,scope:'Two real native deaths at L4 boss, equipment loss, ordinary replacement pickups, native collection/rear docking/rear fire; simulated player-hit flag only, real death entry restored for each death; death entry bypassed only during automated recollection/fire pilot'};fs.writeFileSync(out+'/l4_recovery_validation.json',JSON.stringify(r,null,2));console.log(r);
