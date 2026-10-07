import {acceptTitle} from './accept_title.mjs';
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
function run(directory,modern,fast,distance){
 const build=path.join(root,directory,'build'),cart=fs.readFileSync(path.join(build,'sinistar-mining.dck'));
 const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
 const keys=new Uint8Array(8).fill(31),m=api.createMachine(keys,new Uint8Array(2).fill(255));m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));api.insertDock(m,cart);api.resetMachine(m);acceptTitle(m,sym);
 const set=(n,v)=>m.ram[sym[n]]=v,get=n=>m.ram[sym[n]],word=(n,v)=>{set(n,v&255);m.ram[sym[n]+1]=v>>8;};
 let initialized=false,start=0,lastFired=0,lastHit=0,lastPicture=0,romWrites=0,impactStages=new Set(),visible=new Set(),pictures=[],launches=[],hits=[],overlap=false,expectedImpact=null;
 const read=m.bus.read,write=m.bus.write;
 m.bus.write=(a,v)=>{if(initialized&&(m.portF4&(1<<(a>>13))))romWrites++;write(a,v);};
 m.bus.read=a=>{
  if(a===m.cpu.pc&&a===sym.manual_target){
   if(!initialized){initialized=true;start=m.tstates;set('sinistar_built',1);set('assembly_count',20);set('awake_done',1);set('speech_started',1);set('bombs',24);set('bs_hits',0);set('bs_active',0);set('bs_fired',0);set('bs_expired',0);m.ram[0x5bb1]=+fast;for(const p of [...Array.from({length:8},(_,i)=>0x79b0+10*i),...Array.from({length:8},(_,i)=>0x7db0+10*i),0x58b4])m.ram[p+7]=0;keys[7]&=~16;}
   set('rock_alive',0);set('rock_respawn',255);set('worker_alive',0);set('worker_delay',255);set('invulnerable',255);word('px',(126-distance)*256);word('py',116*256);word('pvx',0);word('pvy',0);word('face_x',108*256);word('face_y',90*256);word('face_vx',0);word('face_vy',0);m.ram.fill(0,0x5884,0x5888);for(const p of [0x7c96,0x7c97,0x7c9a,0x7c9b])m.ram[p]=0;
  }
  if(initialized&&a===m.cpu.pc){
   if(get('bs_fired')!==lastFired){lastFired=get('bs_fired');launches.push(m.tstates-start);}
   if(modern&&a===sym.bomb_impact)expectedImpact=[(get('bs_x')+256*m.ram[0x7c9c]-8)&511,(get('bs_y')+256*m.ram[0x7c9d]-10)&511];
   if(get('bs_hits')!==lastHit){lastHit=get('bs_hits');hits.push(m.tstates-start);if(modern)assert.ok(visible.has(lastFired),'each nearby bomb is displayed before collision');}
   if(modern&&a===sym.bs_kill&&expectedImpact){assert.deepEqual([m.ram[0x783c]+256*m.ram[0x7c9e],m.ram[0x783d]+256*m.ram[0x7c9f]],expectedImpact,'burst follows bomb impact, not face center');expectedImpact=null;}
   if(a===sym.publication_done){
    if(get('bs_active')&&m.ram[sym.rects+26])visible.add(lastFired);
    if(modern&&m.ram[0x783e]&&m.ram[sym.rects+30]){impactStages.add(m.ram[0x783e]);overlap||=!!get('bs_active');}
    if(lastPicture&&get('bs_hits')<13)pictures.push(m.tstates-lastPicture);lastPicture=m.tstates;
    if(modern&&distance===60&&fast&&m.ram[0x783e]===3)fs.writeFileSync(path.join(root,'build/bomb-impact-screen.bin'),Buffer.concat([m.ram.slice(0x4000,0x5800),m.ram.slice(0x6000,0x7800)]));
   }
  }
  return read(a);
 };
 for(let frame=0;frame<1600&&get('bs_hits')<13;frame++)api.runFrame(m);
 if(!modern&&get('bs_hits')!==13)return {fast,distance,hits:get('bs_hits'),stalled:true,pc:m.cpu.pc,mapping:m.portF4};
 assert.equal(get('bs_hits'),13,JSON.stringify({modern,fast,distance,state:Object.fromEntries(['bs_x','bs_y','bs_fuel','bs_fired','bs_expired','bs_active','bs_vx','bs_vy','game_status'].map(n=>[n,get(n)]))}));assert.equal(romWrites,0);assert.equal(get('bs_fired'),13);assert.equal(get('bombs'),11);
 if(modern){assert.equal(visible.size,13);assert.ok(overlap,'next bomb can fly while prior impact animates');}
 const ms=t=>t/3528,avg=a=>a.reduce((x,y)=>x+y,0)/a.length,intervals=launches.slice(1).map((t,i)=>ms(t-launches[i]));
 return {fast,distance,dck_sha256:createHash('sha256').update(cart).digest('hex'),hits:13,visibleBombs:visible.size,explosionWhileNextBombFlies:overlap,impactStages:[...impactStages],meanLaunchIntervalMs:avg(intervals),maxLaunchIntervalMs:Math.max(...intervals),meanPictureMs:ms(avg(pictures)),maxPictureMs:ms(Math.max(...pictures)),timeTo13HitsMs:ms(hits.at(-1)),romWrites};
}
const results=[];for(const fast of [false,true])for(const distance of [18,60]){const before=run('revisions/playable-arcade-taunts-v25',false,fast,distance),after=run('.',true,fast,distance);results.push({before,after});console.log({before,after});}
fs.writeFileSync(path.join(root,'build/bomb-response-verification.json'),JSON.stringify({dck_sha256:results[0].after.dck_sha256,conditions:'Native held-B fixture, fixed player/Sinistar positions, no rocks, no contact damage. Hit-triggered roar enabled. Normal and fast mode, near and farther launches.',results},null,2));
