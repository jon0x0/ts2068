import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api,z}from'./r22_test_machine.mjs';import{out,symbols,demandFixture}from'./debug_ram_fixture.mjs';
const f=demandFixture({delay:true,selectorDelay:500000}),{m,joy,controller:c,store}=f;let cacheRound=0,cachedVisits=[];let playedLevel=0;let updates=0,last=-1,frame=0,stage=0,initial=null,changes=[],mountCount=0;const read=m.bus.read;
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x8634)m.ram[0x91f2]=201;if(a===0x8b06&&read(0x7aa4)>0){const n=read(0x719c)-48;if(n!==playedLevel){playedLevel=n;updates=0;}updates++;}}return read(a);};
for(frame=0;frame<65000;frame++){
 joy[0]=c.booted&&frame%180<90?239:255;api.runFrame(m);if(c.mounts.length!==mountCount){mountCount=c.mounts.length;updates=0;}
 if(c.booted&&!initial){initial={frame,mounts:[...c.mounts],blocks:c.blocks};assert.deepEqual(c.mounts,['RTBOOT.TAP']);assert.equal(c.blocks,16);assert(c.initialLoadedSnapshot.equals(fs.readFileSync(path.join(out,'boot_region.bin'))),'Startup image byte mismatch before launch');console.log('Boot',initial);}
 const level=m.dock[3][0x119c]-48;
 if(cacheRound===1&&playedLevel===8&&updates>120){cachedVisits.push(8);break;}if(c.booted&&level>=1&&level<=8&&updates>120&&stage===level-1){if(cacheRound===1)cachedVisits.push(level);m.dock[3][0x1a9b]=1;stage++;updates=0;changes.push({frame,level,force_victory:true});console.log('Victory',level,frame);}
 if(stage===8&&playedLevel===1&&level===1&&updates>50){assert.equal(cacheRound,0);cacheRound=1;stage=0;updates=0;console.log('Second circuit: disk cache only');}
 if(m.cpu.pc===56){fs.writeFileSync(path.join(out,'failed.home.bin'),m.ram);fs.writeFileSync(path.join(out,'failed.store.bin'),store);throw Error('ROM38 '+JSON.stringify({frame,region:c.region,commands:c.commands,sp:m.cpu.sp,desired:m.ram[0xfda4],page:m.ram[0xd600],op:m.ram[0xd609]}));}if(m.cpu.pc===symbols.fatal_halt)throw Error('Loader error '+Buffer.from(m.ram.slice(symbols.error_text,symbols.error_text+23)).toString()+' step '+m.ram[0xd609]+' page '+m.ram[0xd600]);
}
assert(frame<65000,'Progression stalled '+JSON.stringify({stage,pc:m.cpu.pc,level:m.dock[3][0x119c],mounts:c.mounts,updates}));assert.equal(c.region,7);assert.deepEqual(cachedVisits,[1,2,3,4,5,6,7,8]);assert.deepEqual(c.mounts,['RTBOOT.TAP','LEVEL02.TAP','LEVEL03.TAP','LEVEL04.TAP','LEVEL05.TAP','LEVEL06.TAP','LEVEL07.TAP','LEVEL08.TAP'],'Each level loaded at most once');assert.equal(m.ram[0xfd4a],255,'All8 cache valid bits');assert(!c.mounts.includes('LEVEL01.TAP'),'Level1 must be reused without disk');assert(c.mounts.includes('LEVEL08.TAP'));assert.equal(f.fifoCount,0);assert(c.commands.every(v=>!v.startsWith('tpi:cd')));
const snap=c.snapshots.find(v=>v.file==='LEVEL03.TAP');if(snap)fs.writeFileSync(path.join(out,'loading_level3.home.bin'),snap.home);
const result={frames:frame,initial,mounts:c.mounts,blocks:c.blocks,current_directory:c.cwd,reverse_table_checks:c.reverseChecks||0,core_and_workspace_checks:c.coreChecks||0,max_selector_prime_reads:c.maxPriming||0,all_levels:true,all8_revisited_without_disk:true,cachedVisits,ending_restart:true,changes,delayed_replies:true,passed:true};fs.writeFileSync(path.join(out,'cache_progression_validation.json'),JSON.stringify(result,null,2));console.log(result);



