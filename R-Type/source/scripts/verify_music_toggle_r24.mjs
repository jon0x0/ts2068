import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import crypto from'node:crypto';import{root,fixture,call}from'./r24_test_machine.mjs';const results=[];
for(const target of['sram','rom']){
 const{m,cart}=fixture(target),{m:control}=fixture(target);for(const chip of[m,control]){chip.bus.write(0x7aa4,3);chip.ram.fill(0,0xfbc0,0xfbca);chip.ram.fill(0,0xfd92,0xfd95);}
 const capture=chip=>{const regs=new Uint8Array(16);let selected=0;const writes=[],out=chip.bus.ioWrite;chip.bus.ioWrite=(p,v)=>{if((p&255)===0xf5)selected=v;if((p&255)===0xf6){assert(selected<14,'No joystick register writes');regs[selected]=v;writes.push([selected,v]);}out(p,v);};return{regs,writes};};const actual=capture(m),reference=capture(control);let transitions=0,previous=0,mutedTicks=0,sfxTicks=0;
 for(let tick=0;tick<160;tick++){
  const down=tick>=10&&tick<30||tick>=40&&tick<50||tick>=90&&tick<110||tick>=120&&tick<130;m.keyMatrix[7]=down?27:31;
  for(const chip of[m,control]){if(tick===15)call(chip,0xf87c,{h:4});if(tick===25)call(chip,0xf87c,{h:11});call(chip,0xf8e9);}
  const muted=m.ram[0xfd93];if(muted!==previous)transitions++;previous=muted;assert.equal(muted,tick>=10&&tick<40||tick>=90&&tick<120?1:0,'One toggle per key press');assert.deepEqual(m.ram.slice(0xfd84,0xfd92),control.ram.slice(0xfd84,0xfd92),'Music position continues while muted');
  const effect=m.ram[0xfbc1],owned=effect===11?[8,9]:effect?[8]:[];for(const r of[8,9,10])if(owned.includes(r)){assert.equal(actual.regs[r],reference.regs[r],'SFX retained while music muted');sfxTicks++;}else if(muted){assert.equal(actual.regs[r],0,'Music volume muted');mutedTicks++;}else assert.equal(actual.regs[r],reference.regs[r],'Music restored without restart');
 }
 assert.equal(transitions,4);assert(mutedTicks>50&&sfxTicks>50);
 m.ram[0xfbc9]=0;m.ram[0xfd93]=m.ram[0xfd94]=1;m.keyMatrix[7]=31;call(m,0xf930);assert.equal(m.ram[0xfd93],0,'Boot default music on');assert.equal(m.ram[0xfd94],0);
 results.push({target,bin_sha256:crypto.createHash('sha256').update(cart.subarray(9)).digest('hex'),ticks:160,toggles:transitions,muted_volume_checks:mutedTicks,sfx_volume_checks:sfxTicks,held_key_debounced:true,music_position_preserved:true,sound_effects_preserved:true,passed:true});console.log(results.at(-1));
}fs.writeFileSync(path.join(root,'build/audio/music_toggle_validation_r24.json'),JSON.stringify(results,null,2));
