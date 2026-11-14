import fs from 'node:fs';import assert from 'node:assert/strict';import {stockFixture}from './stock_fixture.mjs';import {api,off}from './r22_test_machine.mjs';
const{m,call,out}=stockFixture(1),sy=Object.fromEntries([...fs.readFileSync(out+'/stock_controls.sym','utf8').matchAll(/(\w+): EQU 0x([0-9a-f]+)/ig)].map(x=>[x[1],parseInt(x[2],16)]));
let ready=false,startStamp=-1;const bootRead=m.bus.read;
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&startStamp!==m.tstates){startStamp=m.tstates;if(a===0x94f1&&m.ram[0x7aa4]===3){ready=true;throw Error('ACTIVE');}}return bootRead(a);};
try{for(let frame=0;frame<6000&&!ready;frame++){m.keyMatrix.fill(31);if(frame>=600&&frame%240<45)m.keyMatrix[5]&=~1;api.runFrame(m);}}catch(e){if(!ready)throw e;}
if(!ready)throw Error('No actual game start');m.bus.read=bootRead;m.keyMatrix.fill(31);call(sy.boss_jump);Object.assign(m.cpu,{pc:0x8653,sp:0xfffe,iff1:true,iff2:true});


const l=JSON.parse(fs.readFileSync(out+'/player_ram_layout.json')),map=l.allocations.published_owner_map[0];m.ram.set([254,2,254,4,254,8,254,16,127,1,127,2],0xbd80);
let updates=0,last=-1,spawns=0,hits=0,saw=false,dead=false;const rd=m.bus.read,wr=m.bus.write,health=[];
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x94f1&&m.ram[0x7aa4]>0){updates++;m.ram[0x7a98]=255;}if(a===0x9d5c)spawns++;}return rd(a);};
m.bus.write=(a,v)=>{if(a===0x85d0&&m.cpu.pc===0xa57d){hits++;health.push([updates,rd(a),v]);if((v&31)===0)dead=true;}wr(a,v);};
let frame=0;for(;frame<12000&&updates<160&&!dead;frame++){
 m.keyMatrix.fill(31);let ys=[];for(let i=0;i<640;i++)if(m.ram[map+i]===0x98)ys.push(Math.floor(i/32));
 if(ys.length){saw=true;const target=(Math.min(...ys)+.5)*8,player=m.ram[0x5b01];if(player<target-2)m.keyMatrix[0]&=~16;else if(player>target+2)m.keyMatrix[0]&=~8;if(process.argv.includes('--charged')?frame%90<60:frame%12<3)m.keyMatrix[7]&=~1;}
 api.runFrame(m);
}
fs.writeFileSync(out+(process.argv.includes('--charged')?'/walker_charged_attempt.json':'/walker_normal_attempt.json'),JSON.stringify({passed:ready&&saw&&dead&&health.findIndex(v=>(v[2]&31)===0)===7&&!!(m.ram[0x85d8]&128),frame,updates,spawns,hits,saw,dead,health},null,2));assert(ready&&saw&&dead&&health.findIndex(v=>(v[2]&31)===0)===7&&!!(m.ram[0x85d8]&128),'Live walker must take eight native damage hits and reach zero health');console.log({frame,updates,spawns,hits,saw,dead,health});fs.writeFileSync(out+(process.argv.includes('--charged')?'/walker_charged_pilot.json':'/walker_live_pilot.json'),JSON.stringify({passed:true,frame,updates,spawns,hits,saw,dead,health,playerProtectionOnly:true,enemyHealthEdited:false,finalActor:[...m.ram.slice(0x85d0,0x85d9)],scope:'Actual menu start followed by main-loop boss setup and selected-key pilot; normal/held-charge firing, moving last walker; no native death bypass'},null,2));
