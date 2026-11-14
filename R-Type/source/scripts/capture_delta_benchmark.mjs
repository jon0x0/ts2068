import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';
import{api,root}from'./r22_test_machine.mjs';import{out as sourceOut,demandFixture}from'./bellmite_fixture.mjs';const out=path.join(root,'build/diagnostics/delta_benchmark');fs.mkdirSync(out,{recursive:true});
const results=[];const overrides={};let captured=-1;let commands=[];
for(const level of(process.env.RTYPE_BOSS_LEVELS||'5').split(',').map(Number)){
 const{m,joy,controller:c}=demandFixture();let boot=-1,updates=0,last=-1,jumps=0,before=0,after=0,phase=0,phaseAt=0,stops=0;const seen=new Set();
 const read=m.bus.read;m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x8634)m.ram[0x91f2]=201;
 if(a===0x8b06&&read(0x7aa4)>0){updates++;if(phase>=4)after++;}
 if(a===0x8cfd&&phase>=4){const id=read(0x7a9c);if(id>=9&&id<=26){const key=id+':'+read(0x8eb1);overrides[key]=(overrides[key]||0)+1;}}
 if(a===0x8649)commands=[];
 if([0x8cfd,0x8dd3,0x8d65,0x8e29].includes(a)&&phase>=4){const ptr=(m.cpu.h<<8)|m.cpu.l;if([0xefa1,0xf3f1,0xf481,0xf511].includes(ptr))commands.push({entry:a,pointer:ptr,x:m.cpu.c,y:m.cpu.b,width:m.cpu.e,height:m.cpu.d,mode:read(0x8ebf)});}
 if(a===0x868c&&phase>=4&&after>=150&&after<=210&&captured!==after){captured=after;fs.writeFileSync(path.join(out,'sample_'+after+'.commands.json'),JSON.stringify(commands));fs.writeFileSync(path.join(out,'sample_'+after+'.home.bin'),m.ram);}
 if(a===jumpPC){jumps++;console.log('jump',level,updates);}
 if(a===0x90b5&&phase>=4)stops++;
 if(a===0x8e85&&phase>=4)seen.add(m.cpu.a);
 }return read(a);};
 const sym=fs.readFileSync(path.join(sourceOut,'boss_preview.sym'),'utf8');const jumpPC=parseInt(sym.match(/boss_jump: EQU 0x([0-9a-f]+)/i)[1],16);
 let frame=0;
 for(;frame<32000;frame++){
  if(c.booted&&boot<0)boot=frame;
  m.keyMatrix.fill(31);const t=frame-boot;
  if(boot>=0&&t>=600&&t<700){if(level<=5)m.keyMatrix[3]=31^(1<<(level-1));else m.keyMatrix[4]=31^(1<<(10-level));}
  joy[0]=boot>=0&&t>=800&&t<840?239:255;
  if(updates>=15&&phase===0){phase=1;phaseAt=updates;before=m.bus.read(0x7a84);}
  if(phase===1||phase===3)m.keyMatrix[7]&=~16;
  if(phase===4&&updates-phaseAt<10)m.keyMatrix[7]&=~16;
  api.runFrame(m);
  if(phase===1&&updates-phaseAt>=10){assert.equal(jumps,0,'Held first B must not jump');phase=2;phaseAt=updates;}
  if(phase===2&&updates-phaseAt>=4){phase=3;phaseAt=updates;}
  if(phase===3&&jumps===1){phase=4;phaseAt=updates;}
  // Keep the second press held for several updates to verify latch, then release.
  if(phase===4&&after>=211)break;
 }
 assert(frame<32000,'No sustained boss preview L'+level+' '+JSON.stringify({phase,updates,jumps,pc:m.cpu.pc}));
 assert.equal(jumps,1);assert.equal(m.dock[3][0x119c],48+level,'Unexpected stage transition');
 assert(seen.has([8,3,41,27,8,18,53,42][level-1]),'Native boss artwork not rendered L'+level);
 assert(m.dock[3][0x1a84]>= [99,63,9,74,73,8,61,32][level-1],'Checkpoint not reached '+JSON.stringify({column:m.dock[3][0x1a84],state:m.ram[0xfd4b],stops,seen:[...seen]}));
 fs.writeFileSync(path.join(out,`boss_level${level}.home.bin`),m.ram);
 fs.writeFileSync(path.join(out,'palette_overrides.json'),JSON.stringify(overrides,null,2));
 results.push({level,frame,updates,after,jumps,scrollStops:stops,renderedDescriptors:[...seen],column:m.dock[3][0x1a84],passed:true});console.log(results.at(-1));
 fs.writeFileSync(path.join(out,`boss_level${level}.json`),JSON.stringify(results.at(-1),null,2));
}
fs.writeFileSync(path.join(out,'boss_preview_validation.json'),JSON.stringify({results,passed:true,death_bypass_diagnostic:true},null,2));
