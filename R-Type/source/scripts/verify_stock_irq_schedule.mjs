import fs from 'node:fs';import assert from 'node:assert/strict';import {stockFixture} from './stock_fixture.mjs';
const level=Number(process.argv[2]||4),f=stockFixture(level),{m,call,out}=f,l=JSON.parse(fs.readFileSync(out+'/player_ram_layout.json')),flags=l.clock_flags[0],s=l.allocations.player_state[0];
const reference=fs.readFileSync('build/fullgame/visible_hits_r145/gateway.bin');
// Assert the actual TAP binary's busy branch and alternating-publication branch.
assert.equal(reference.subarray(3,21).toString('hex'),'3acd5bb7c2250e3ac55bee0132c55bc2250e');
m.ram.fill(0,s,s+512);m.ram[flags+2]=1;m.ram[0x7aa4]=3;
m.ram[0x7aa1]=8;m.ram[0x7aa2]=10;m.ram[0x7a98]=255;
m.ram.set(fs.readFileSync(out+'/stock_player_phases.bin'),l.allocations.player_phases[0]);
m.ram.set([254,2,254,4,254,8,254,16,127,1,127,2],0xbd80);
let ticks=0,samples=0,last=-1;const rd=m.bus.read;
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x2400)ticks++;if(a===0x240c)samples++;}return rd(a);};
for(let i=0;i<12;i++)call(0x1003);
assert.deepEqual([ticks,samples],[6,6]);
const regular={ticks,samples};ticks=0;samples=0;m.ram[flags+13]=1;
// A complete short tap during backing capture must survive for the next tick.
for(let i=0;i<12;i++){m.keyMatrix.fill(31);if(i<3)m.keyMatrix[7]&=~1;call(0x1003);}
assert.deepEqual([ticks,samples],[0,12]);assert.equal(m.ram[flags+8],1,'Busy-copy short fire edge must be retained');
const result={passed:true,level,regular,busy:{ticks,samples,pendingShot:m.ram[flags+8]},romWrites:f.romWrites,scope:'Actual stock gateway scheduling and busy-copy edge retention; reference branch opcodes checked against archived TAP r145 gateway. Not full gameplay/timing parity.'};
fs.writeFileSync(out+'/irq_schedule_validation.json',JSON.stringify(result,null,2));console.log(result);

