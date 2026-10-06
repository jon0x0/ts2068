import {acceptTitle} from './accept_title.mjs';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck'));
function machine(){const keys=new Uint8Array(8).fill(31),joy=new Uint8Array(2).fill(255),m=api.createMachine(keys,joy);m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));api.insertDock(m,cart);api.resetMachine(m);acceptTitle(m,sym);return {m,keys};}
const fastTest=process.argv.includes("--fast");
const {m,keys}=machine();const get=n=>m.ram[sym[n]],set=(n,v)=>m.ram[sym[n]]=v,word=(n,v)=>{set(n,v&255);m.ram[sym[n]+1]=v>>8;};
let followMine=false,winPositions=null,winChecks=0,attributeFlashes=0;
const read=m.bus.read;m.bus.read=a=>{if(a===m.cpu.pc&&a===sym.ring_red&&(m.portF4&128))attributeFlashes++;if(a===m.cpu.pc&&a===sym.frame_done&&get('game_status')===1){const position=[get('face_x'),m.ram[sym.face_x+1],get('px'),m.ram[sym.px+1],m.ram[0x7c96],m.ram[0x7c9a]];if(winPositions)assert.deepEqual(position,winPositions,'won world positions remain stationary');else winPositions=position;winChecks++;}if(a===m.cpu.pc&&a===sym.manual_target&&followMine){set('worker_alive',0);set('worker_delay',255);const x=(get('rock_x')+256*m.ram[0x586e]-4)&511,y=(get('rock_y')+256*m.ram[0x586f]+10)&511;word('px',(x&255)*256);word('py',(y&255)*256);m.ram[0x7c96]=x>>8;m.ram[0x7c97]=y>>8;word('pvx',0);word('pvy',0);set('angle',64);}return read(a);};
function run(n){for(let i=0;i<n;i++)api.runFrame(m);}
// Optional lifecycle timing audit. Does not alter the cartridge or fixtures.
const lifecycle={pictures:[],effects:[]};
if(process.argv.includes('--profile')){
 const observedRead=m.bus.read;let previous=null,effectStart=null,effectSincePicture=false;
 m.bus.read=a=>{
  if(a===m.cpu.pc){
   if(a===sym.ring_effect&&(m.portF4&128)&&m.ram[0x783e]&&m.ram[0x783e]!==10){effectStart=m.tstates;}
   if(a===sym.mode_exit&&(m.portF4&128)&&effectStart!==null){const duration=m.tstates-effectStart;if(duration>3528){lifecycle.effects.push(duration);effectSincePicture=true;}effectStart=null;}
   if(a===sym.frame_done){
    const state=get('game_status')?'ending':get('awake_done')?'chase':get('sinistar_built')?'awakening':get('assembly_count')?'partial assembly':'mining';
    const fast=!!m.ram[0x5bb1];
    if(previous&&previous.state===state&&previous.fast===fast)lifecycle.pictures.push({state,fast,tstates:m.tstates-previous.time,effect:effectSincePicture,speech:!!get('speech_left'),faceVisible:!!m.ram[sym.rects+22]});
    previous={state,fast,time:m.tstates};effectSincePicture=false;
   }
  }
  return observedRead(a);
 };
}
run(300);assert.equal(get('game_mode'),1);assert.equal(get('control_mode'),1);assert.equal(get('lives'),3);assert.equal(get('bombs'),3);assert.equal(get('hits'),0);
if(fastTest){keys[1]&=~8;run(30);keys[1]|=8;assert.equal(m.ram[0x5bb1],1);}
// Native movement and fire input, no browser-side movement.
const initialX=get('px')+256*m.ram[sym.px+1];keys[5]&=~1;keys[7]&=~1;run(20);assert.ok(get('px')+256*m.ram[sym.px+1]>initialX);keys.fill(31);
// Place the pilot at the mining seam, then earn ammo through actual shots/pickups.
word('px',148*256);word('py',(get('rock_y')+10)*256);word('pvx',0);word('pvy',0);set('angle',64);keys[7]&=~1;
set('worker_alive',0);followMine=true;run(2200);followMine=false;set('worker_alive',1);keys.fill(31);assert.ok(get('crystals_taken')>=3,`pickups ${get('crystals_taken')}`);assert.ok(get('bombs')>=12,`ammo ${get('bombs')}`);let earned=get('bombs');const beforeCrystals=get('crystals_taken');
// Leave the mine to workers. More native firing produces the initial delivery.
word('px',72*256);word('py',112*256);word('pvx',0);word('pvy',0);set('angle',64);keys[7]&=~1;
for(let i=0;i<60000&&!get('sinistar_built');i++)run(1);
assert.equal(get('sinistar_built'),1);assert.equal(get('bombs'),Math.min(24,earned+3*(get('crystals_taken')-beforeCrystals)),'only collected crystals grant bombs');earned=get('bombs');keys.fill(31);keys[7]&=~16;
for(let i=0;i<1600&&!get('game_status');i++)run(1);
assert.equal(get('game_status'),1,'earned Sinibombs must win');assert.equal(get('bs_hits'),13);assert.equal(get('bs_fired'),13+get('bs_expired')+get('bs_active'),'every launched bomb is accounted for');assert.equal(get('bombs'),earned-get('bs_fired'));
run(120);assert.ok(winChecks>3);
// Native R restarts a won game and clears inventory/damage/end state.
keys.fill(31);keys[2]&=~8;run(12);keys.fill(31);run(250);assert.equal(get('game_status'),0);assert.equal(get('lives'),3);assert.equal(get('bombs'),3);assert.equal(get('bs_hits'),0);
// Exercise contact, respawn protection and game over with controlled encounters.
set('sinistar_built',1);set('awake_done',1);
for(let life=3;life>0;life--){set('invulnerable',0);word('face_x',80*256);word('face_y',90*256);word('face_vx',0);word('face_vy',0);word('px',95*256);word('py',100*256);for(const a of [0x7c96,0x7c97,0x7c9a,0x7c9b])m.ram[a]=0;word('pvx',0);word('pvy',0);for(let i=0;i<120&&get('lives')===life;i++)run(1);assert.equal(get('lives'),life-1);if(life>1){assert.ok(get('invulnerable')>0);run(15);assert.equal(get('lives'),life-1);}}
assert.equal(get('game_status'),2);const loss=get('frames');run(60);assert.equal(get('lives'),0);
assert.ok(attributeFlashes>0);
const report={attributeFlashes,dck_sha256:createHash('sha256').update(cart).digest('hex'),earned_ammo:earned,win:true,restart:true,contact_damage:true,respawn_protection:true,loss:true};console.log(report);fs.writeFileSync(path.join(root,fastTest?'build/fast-playable-verification.json':'build/playable-verification.json'),JSON.stringify(report,null,2)+'\n');
if(process.argv.includes('--profile'))fs.writeFileSync(path.join(root,fastTest?'build/fast-lifecycle-profile.json':'build/lifecycle-profile.json'),JSON.stringify({dck_sha256:report.dck_sha256,conditions:'Scripted playable verification, including pinned mining seam, earned resources, native assembly and bombs, and forced contact encounters. Timing audit, not natural-play averages.',...lifecycle},null,2));
