import fs from 'node:fs';
import assert from 'node:assert/strict';
import {stockFixture} from './stock_fixture.mjs';
const level=Number(process.argv[2]||4);
function exercise(path,mode="keyboard"){
 const f=stockFixture(level,path),{m,call,out}=f;
 const l=JSON.parse(fs.readFileSync(out+'/player_ram_layout.json')),a=l.allocations,s=a.player_state[0],flags=l.clock_flags[0];
 m.ram.fill(0,s,s+512);m.ram.fill(0,0x4000,0x7800);m.ram.fill(0,...a.published_owner_map);
 m.ram.set(fs.readFileSync(out+'/stock_player_phases.bin'),a.player_phases[0]);
 m.ram[0xbe00]=2;m.ram[0x7aa4]=3;m.ram[0x7aa1]=8;m.ram[0x7aa2]=10;m.ram[0x7a98]=255;
 // Native selected keys; fire=Space. No hardwired gameplay bindings in ROM.
 m.ram.set([254,2,254,4,254,8,254,16,127,1,127,2],0xbd80);
 m.ram.fill(0,0x5eb4,0x5ee4);call(0x1b26);call(0x2409);
 let spawns=0,last=-1;const rd=m.bus.read;
 m.bus.read=addr=>{if(m.stepAdded===0&&addr===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(addr===0x9d5c)spawns++;}return rd(addr);};
 const taps=[];
 for(let tap=0;tap<6;tap++){
  const before=spawns;
  for(let tick=0;tick<20;tick++){m.keyMatrix.fill(31);m.joystick.fill(255);if(tick<3){if(mode==="keyboard")m.keyMatrix[7]&=~1;else m.joystick[mode]=127;}call(0x1003);}
  taps.push(spawns-before);
 }
 return {spawns,taps,pending:m.ram[flags+8],romWrites:f.romWrites};
}
const baseline=exercise(`build/cartridges/r148/level${level}/rt_l${level}_r148.dck`);
const fixed=exercise();
const joysticks=[0,1].map(socket=>exercise(undefined,socket));
for(const result of joysticks){assert.deepEqual(result.taps,[1,1,1,1,1,1]);assert.equal(result.pending,0);assert.equal(result.romWrites,0);}
assert.equal(baseline.spawns,0,'Baseline must reproduce missing shot handoff');
assert.deepEqual(fixed.taps,[1,1,1,1,1,1],'Each tap must spawn exactly one normal shot');
assert.equal(fixed.pending,0);assert.equal(fixed.romWrites,0);
const result={passed:true,level,baseline,fixed,joysticks,scope:'Actual stock IRQ gateway calls with selected keyboard, six short press/release cycles and independent projectile ticks; deterministic component test, not hardware timing'};
fs.writeFileSync(`build/cartridges/integration_work/level${String(level).padStart(2,'0')}/repeated_fire_validation.json`,JSON.stringify(result,null,2));console.log(result);
