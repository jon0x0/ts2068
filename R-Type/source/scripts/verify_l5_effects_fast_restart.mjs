import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api}from'./r22_test_machine.mjs';import{out,demandFixture}from'./l5_effects_fast_fixture.mjs';
const results=[];let bossDraws=0;
for(const level of[5]){
 const{m,joy,controller:c}=demandFixture({delay:true,selectorDelay:500000});let bootFrame=-1,updates=0,last=-1,gameover=-1,afterGameover=false,tape=0;
 const read=m.bus.read;m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x9172&&m.portF4===9&&m.cpu.sp>=0xfd00&&m.cpu.a===8)bossDraws++;if(a===0x8634)m.ram[0x91f2]=201;if(a===0x94f1&&read(0x7aa4)>0){updates++;if(updates>=180&&gameover<0){assert.equal(m.dock[3][0x119c],48+level);assert.equal(m.portF4,9);assert(m.cpu.sp>=0xfd00);assert.equal(m.dock[7][0x3f0],1,'Boss phase cache was not initialized before game over');assert(bossDraws>0,'First boss did not render');bossDraws=0;m.cpu.pc=0x92a4;gameover=frame;updates=0;return read(0x92a4);}}if(a===0xfe03)tape++;}return read(a);};
 let frame=0;
 for(;frame<35000;frame++){
  if(c.booted&&bootFrame<0)bootFrame=frame;
  m.keyMatrix.fill(31);const t=frame-bootFrame;
  if(bootFrame>=0&&t>=600&&t<700){if(level<=5)m.keyMatrix[3]=31^(1<<(level-1));else m.keyMatrix[4]=31^(1<<(10-level));}
  if(updates>=15&&updates<25||updates>=29&&updates<39)m.keyMatrix[7]&=~16;
  joy[0]=(bootFrame>=0&&t>=800&&t<830)||(gameover>=0&&frame-gameover>1600&&frame%180<90)?239:255;api.runFrame(m);
  if(gameover>=0&&frame-gameover>1600&&updates>=180&&m.dock[3][0x119c]===48+level){assert.equal(m.dock[7][0x3f0],1,'Boss cache not rebuilt on cached restart');assert(bossDraws>0,'Restarted boss did not render');afterGameover=true;break;}
  assert(!c.fatalSeen,'Loader failed');
 }
 assert(afterGameover,'Selected restart failed '+level+' '+JSON.stringify({pc:m.cpu.pc,region:c.region,level:m.dock[3][0x119c],updates,gameover,flags:m.ram[0xfd4a],holder:m.ram[0xfd48],mounts:c.mounts}));assert.equal(tape,0);assert((c.maxPriming||0)>8,'Delayed selector must exercise readiness polling');assert.equal(m.ram[0xfd95],level);assert(c.commands.every(v=>!v.startsWith('tpi:cd')));assert.deepEqual(c.mounts,['RTBOOT.TAP',`LEVEL0${level}.TAP`],'Replays must reuse both cached levels');results.push({level,frames:frame,mounts:c.mounts,reverse_table_checks:c.reverseChecks||0,executable_bank_audit_checks:c.codeAuditChecks||0,core_and_workspace_checks:c.coreChecks||0,max_selector_prime_reads:c.maxPriming||0,gameover_restart:true,tape_entries:tape,passed:true});console.log(results.at(-1));
}
fs.writeFileSync(path.join(out,'cache_restart_validation.json'),JSON.stringify(results,null,2));


