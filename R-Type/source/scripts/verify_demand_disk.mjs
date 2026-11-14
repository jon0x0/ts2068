import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api,z}from'./r22_test_machine.mjs';import{out,symbols,demandFixture}from'./demand_disk_fixture.mjs';
const f=demandFixture({delay:true}),{m,joy,controller:c,store}=f;let updates=0,last=-1,frame=0,stage=0,initial=null,changes=[],mountCount=0;const read=m.bus.read;
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x8634)m.ram[0x91f2]=201;if(a===0x8b06&&read(0x7aa4)>0)updates++;}return read(a);};
for(frame=0;frame<40000;frame++){
 joy[0]=c.booted&&frame%180<90?239:255;api.runFrame(m);if(c.mounts.length!==mountCount){mountCount=c.mounts.length;updates=0;}
 if(c.booted&&!initial){initial={frame,mounts:[...c.mounts],blocks:c.blocks};assert.deepEqual(c.mounts,['RTBOOT.TAP']);assert.equal(c.blocks,16);assert(c.initialLoadedSnapshot.equals(fs.readFileSync(path.join(out,'boot_region.bin'))),'Startup image byte mismatch before launch');console.log('Boot',initial);}
 const level=m.dock[3][0x119c]-48;
 if(c.booted&&level>=1&&level<=8&&updates>120&&stage===level-1){m.dock[3][0x1a9b]=1;stage++;updates=0;changes.push({frame,level,force_victory:true});console.log('Victory',level,frame);}
 if(stage===8&&c.mounts.at(-1)==='LEVEL01.TAP'&&level===1&&updates>50)break;
 if(m.cpu.pc===56){fs.writeFileSync(path.join(out,'failed.home.bin'),m.ram);fs.writeFileSync(path.join(out,'failed.store.bin'),store);throw Error('ROM38 '+JSON.stringify({frame,region:c.region,commands:c.commands,sp:m.cpu.sp,desired:m.ram[0xfda4],page:m.ram[0xd600],op:m.ram[0xd609]}));}if(m.cpu.pc===symbols.fatal_halt)throw Error('Loader error '+Buffer.from(m.ram.slice(symbols.error_text,symbols.error_text+23)).toString()+' step '+m.ram[0xd609]+' page '+m.ram[0xd600]);
}
assert(frame<40000,'Progression stalled '+JSON.stringify({stage,pc:m.cpu.pc,level:m.dock[3][0x119c],mounts:c.mounts,updates}));assert.equal(c.region,0);assert(c.mounts.includes('LEVEL08.TAP'));assert.equal(f.fifoCount,0);assert(c.commands.every(v=>!v.startsWith('tpi:cd')));
const snap=c.snapshots.find(v=>v.file==='LEVEL03.TAP');if(snap)fs.writeFileSync(path.join(out,'loading_level3.home.bin'),snap.home);
const result={frames:frame,initial,mounts:c.mounts,blocks:c.blocks,current_directory:c.cwd,all_levels:true,ending_restart:true,changes,delayed_replies:true,passed:true};fs.writeFileSync(path.join(out,'progression_validation.json'),JSON.stringify(result,null,2));console.log(result);


