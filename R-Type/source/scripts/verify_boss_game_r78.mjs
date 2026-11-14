import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';
import{api,root}from'./r22_test_machine.mjs';import{out as base,demandFixture}from'./boss_motion_fixture_r78.mjs';
const out=base;const manifests=JSON.parse(fs.readFileSync(path.join(out,'generic_manifest.json')));const movement=[];const oldPositions=new Map();const actorsByLevel={};const targets=[];let selectedID=0,targetX=0,targetY=0;const motion=[];const actors=new Map();const results=[];let wrapperCount=0;const overrides={};let captured=-1;let trace=[];
for(const level of(process.env.RTYPE_BOSS_LEVELS||'1,2,3,4,5,6,7,8').split(',').map(Number)){
 const{m,joy,controller:c}=demandFixture();let boot=-1,updates=0,last=-1,jumps=0,before=0,after=0,phase=0,phaseAt=0,stops=0;const seen=new Set(),captures=[];
 const write=m.bus.write;m.bus.write=(a,v)=>{if(c.booted&&(m.cpu.pc!==0x5e04)&&a<8192&&(m.portF4&1)&&m.dock[0][a]!==v){fs.writeFileSync(path.join(out,'bad_write.home.bin'),m.ram);fs.writeFileSync(path.join(out,'trace.json'),JSON.stringify(trace));throw Error('ROM WRITE '+JSON.stringify({a,v,pc:m.cpu.pc,sp:m.cpu.sp,hl:(m.cpu.h<<8)|m.cpu.l,de:(m.cpu.d<<8)|m.cpu.e,map:m.portF4,active:m.ram[0x5c80],stage:c.region}));}write(a,v);};const read=m.bus.read;m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(phase>=4&&m.cpu.sp<0xfd00&&!(m.cpu.sp>=0x5c80&&m.cpu.sp<=0x5cf2 || m.cpu.sp>=0x5b60&&m.cpu.sp<=0x5bc0)){fs.writeFileSync(path.join(out,'trace.json'),JSON.stringify(trace));throw Error('BAD SP '+m.cpu.sp.toString(16));}if(a===0x8634)m.ram[0x91f2]=201;
 if(a===0x94f1&&!(m.portF4&16)&&read(0x7aa4)>0){updates++;if(phase>=4)after++;}
 if(a===0x8cfd&&phase>=4&&m.portF4===9&&m.cpu.sp>=0xfd00){const id=read(0x7a9c);if(id>=9&&id<=26){const key=id+':'+read(0x8eb1);overrides[key]=(overrides[key]||0)+1;}}
 if(a===0x868c&&phase>=4&&after>=100&&after<=115&&captured!==after){captured=after;const file=`scene_L${level}_${after}.home.bin`;fs.writeFileSync(path.join(out,file),m.ram);captures.push({update:after,frame,file});}


 if(a===jumpPC){jumps++;console.log('jump',level,updates);}
 if(a===0x90b5&&phase>=4)stops++;
 if(a===0x9172&&phase>=4&&m.portF4===9&&m.cpu.sp>=0xfd00){seen.add(m.cpu.a);selectedID=m.cpu.a;targets.push({level,u:after,iy:m.cpu.yh*256+m.cpu.yl,id:selectedID,x:m.cpu.c*8,y:m.cpu.b*8});targetX=(m.cpu.c*8)&255;targetY=(m.cpu.b*8)&255;}

 if(a===0x8cfd&&phase>=4&&m.portF4===9&&m.cpu.sp>=0xfd00){const rec=manifests.find(r=>r.level===level);const ptr=m.cpu.h*256+m.cpu.l;if(level===5&&[8,30,31,32,33].includes(selectedID)||rec&&level!==1&&ptr===rec.plan_start){const iy=m.cpu.yh*256+m.cpu.yl;let x,y;if(level===5){const at=0x300+((((m.cpu.yl-1)*57)&255)*2);x=m.dock[7][at];y=m.dock[7][at+1];}else{const states=m.dock[7];let at=-1;for(let q=0x2d0;q<0x350;q+=4)if(states[q]===m.cpu.yl&&states[q+1]===(level===4?selectedID:0)){at=q;break;}assert(at>=0,'Missing component state');x=states[at+2];y=states[at+3];}assert.equal((m.cpu.c*8+(level===5?m.dock[4][0xee3]:m.dock[6][0x1f33])*2)&255,x,'Rendered X differs');assert.equal((m.cpu.b*8+(level===5?m.dock[4][0xee4]:m.dock[6][0x1f34]))&255,y,'Rendered Y differs');const key=level+':'+iy+':'+(level===4?selectedID:0),old=oldPositions.get(key);if(old){for(const[k,t]of[['x',targetX&255],['y',targetY&255]]){if(level===6&&selectedID>=9&&selectedID<=17)continue;const delta=(t-old[k]+256)%256;if(delta<=8||delta>=248){const actual=k==='x'?x:y;assert(Math.min((actual-old[k]+256)%256,(old[k]-actual+256)%256)<=2,'More than 2px '+JSON.stringify({level,selectedID,k,t,old,x,y}));}}}oldPositions.set(key,{x,y});actorsByLevel[level]??=new Set();actorsByLevel[level].add(iy);movement.push({level,id:selectedID,u:after,iy,x,y});}}


 }return read(a);};
 const sym=fs.readFileSync(path.join(base,'boss_preview.sym'),'utf8');const jumpPC=parseInt(sym.match(/boss_jump: EQU 0x([0-9a-f]+)/i)[1],16);
 let frame=0;
 for(;frame<90000;frame++){
  if(c.booted&&boot<0)boot=frame;
  m.keyMatrix.fill(31);const t=frame-boot;
  if(boot>=0&&t>=600&&t<700){if(level<=5)m.keyMatrix[3]=31^(1<<(level-1));else m.keyMatrix[4]=31^(1<<(10-level));}
  joy[0]=boot>=0&&t>=800&&t<840?127:255;
  if(updates>=15&&phase===0){phase=1;phaseAt=updates;before=m.bus.read(0x7a84);}
  if(phase===1||phase===3)m.keyMatrix[7]&=~16;
  if(phase===4&&updates-phaseAt<10)m.keyMatrix[7]&=~16;
  api.runFrame(m);
  if(phase===1&&updates-phaseAt>=10){assert.equal(jumps,0,'Held first B must not jump');phase=2;phaseAt=updates;}
  if(phase===2&&updates-phaseAt>=4){phase=3;phaseAt=updates;}
  if(phase===3&&jumps===1){phase=4;phaseAt=updates;}
  // Keep the second press held for several updates to verify latch, then release.
  if(phase===4&&after>=(level===7?700:160))break;
 }
 if(frame>=90000){fs.writeFileSync(path.join(out,'failed.home.bin'),m.ram);fs.writeFileSync(path.join(out,'failed.dock4.bin'),m.dock[4]);console.log('FAIL',{map:m.portF4,sp:m.cpu.sp,stage:m.dock[3][0x119c],active:m.ram[0x5c80]});}assert(frame<90000,'No sustained boss preview L'+level+' '+JSON.stringify({phase,updates,jumps,pc:m.cpu.pc}));
 assert.equal(jumps,1);assert.equal(m.dock[3][0x119c],48+level,'Unexpected stage transition');
 fs.writeFileSync(path.join(out,'native_targets.json'),JSON.stringify(targets));
 assert(seen.has([8,3,41,27,8,18,53,42][level-1]),'Native boss artwork not rendered L'+level);
 assert(m.dock[3][0x1a84]>= [99,63,9,74,73,8,61,32][level-1],'Checkpoint not reached '+JSON.stringify({column:m.dock[3][0x1a84],state:m.ram[0xfd4b],stops,seen:[...seen]}));
 fs.writeFileSync(path.join(out,`boss_level${level}.home.bin`),m.ram);
 fs.writeFileSync(path.join(out,`boss_level${level}.dock7.bin`),m.dock[7]);
 const phaseBytes=fs.readFileSync(path.join(root,'build/diagnostics/pixel_movement_trial/ship_phases.bin')).subarray(768,1536);assert(Buffer.from(m.dock[7].slice(0xd80,0x1080)).equals(phaseBytes),'Phase cache changed');
 fs.writeFileSync(path.join(out,'palette_overrides.json'),JSON.stringify(overrides,null,2));
 results.push({level,frame,updates,after,jumps,scrollStops:stops,renderedDescriptors:[...seen],column:m.dock[3][0x1a84],passed:true});console.log(results.at(-1));
 fs.writeFileSync(path.join(out,`captures_L${level}.json`),JSON.stringify(captures));fs.writeFileSync(path.join(out,`boss_level${level}.json`),JSON.stringify(results.at(-1),null,2));
}
fs.writeFileSync(path.join(out,'boss_preview_validation.json'),JSON.stringify({results,passed:true,death_bypass_diagnostic:true},null,2));





fs.writeFileSync(path.join(out,'native_targets.json'),JSON.stringify(targets));console.log('Targets',targets.length);if(actorsByLevel[5])assert(actorsByLevel[5].size===13,'Expected core and12 spheres');fs.writeFileSync(path.join(out,'movement_validation.json'),JSON.stringify({passed:true,samples:movement.length,actors:Object.fromEntries(Object.entries(actorsByLevel).map(([k,v])=>[k,v.size]))}));fs.writeFileSync(path.join(out,'movement_trace.json'),JSON.stringify(movement));
