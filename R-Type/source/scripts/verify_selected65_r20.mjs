import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import crypto from 'node:crypto';
import {root,fixture,call} from './r20_test_machine.mjs';
const source=JSON.parse(fs.readFileSync(path.join(root,'build/audio/death_triangle_trials/65.json'))),results=[];
for(const target of ['sram','rom']){
 const {m,cart}=fixture(target);m.ram.fill(0,0xfbc0,0xfbca);
 const sym=fs.readFileSync(path.join(root,'build/audio',target==='rom'?'ay_rom.sym':'ay_sram.sym'),'utf8');const tick=parseInt(sym.match(/ay_tick: EQU 0x([0-9a-f]+)/i)[1],16);
 let reg=0;const writes=[],out=m.bus.ioWrite;m.bus.ioWrite=(p,v)=>{if((p&255)===0xf5)reg=v;if((p&255)===0xf6)writes.push([reg,v]);out(p,v);};
 call(m,0xf87c,{h:11});for(let i=0;i<source.register_frames.length+1;i++)call(m,tick);
 assert.deepEqual(writes.filter(([r])=>r===13),[[13,14]],'Triangle retriggers once, never writes255 sentinel');
 assert(!writes.some(([r])=>[4,5,10,14,15].includes(r)),'C music and joystick registers untouched');
 results.push({target,bin_sha256:crypto.createHash('sha256').update(cart.subarray(9)).digest('hex'),choice:65,envelope_shape_writes:[[13,14]],passed:true});
}
fs.writeFileSync(path.join(root,'build/audio/selected65_validation_r20.json'),JSON.stringify({passed:true,results},null,2));console.log('Selected65 triangle envelope retriggers exactly once on both targets');
