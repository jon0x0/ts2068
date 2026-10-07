// Execute cartridge routines, not a JS model of the firing/audio gates.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
function machine(directory){
 const cart=fs.readFileSync(path.join(directory,'sinistar-mining.dck'));
 const rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
 const sym=Object.fromEntries([...fs.readFileSync(path.join(directory,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
 let mapping=16,romWrites=0,held=false;
 const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){if(mapping&(1<<(a>>13)))romWrites++;else ram[a]=v;},ioRead:p=>held&&p===0x7ffe?30:255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;}};
 function call(name){mapping=16;ram[0x78df]=16;cpu.pc=sym[name];assert.ok(cpu.pc,name);cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;cpu.halted=false;for(let n=0;cpu.pc!==0x100;n++){assert.ok(n<200000,`bounded ${name}`);runZ80(cpu,bus,1,clock);}assert.equal(romWrites,0);}
 const get=n=>ram[sym[n]],set=(n,v)=>ram[sym[n]]=v;
 function reset(){ram.fill(0);set('game_mode',1);let dest=0x5c40;for(const {name} of JSON.parse(fs.readFileSync(path.join(root,'../assets/sfx-manifest.json'))).effects){const data=fs.readFileSync(path.join(root,`../assets/sfx-${name}.packed`));ram.set(data,dest);dest+=data.length;}}
 return {cart,ram,call,get,set,reset,hold:()=>held=true};
}
function measure(directory){
 const m=machine(directory);m.reset();m.set('control_mode',1);m.hold();m.ram[0x78e9]=127;
 const launches=[];
 for(let tick=0;tick<300;tick++){
  const alive=m.get('bullet_alive');m.call('fire_input');
  if(!alive&&m.get('bullet_alive'))launches.push(tick);
  m.call('bullet_step');
 }
 m.reset();m.call('sfx_explosion');m.call('sfx_shot');assert.equal(m.get('sfx_pending'),5,'pending explosion attack wins');
 let firingSoundResumesAfterRefreshes=null;
 for(let tick=1;tick<=200;tick++){
  m.call('sfx_tick');m.call('sfx_shot');
  if(m.get('sfx_pending')===1){firingSoundResumesAfterRefreshes=tick;break;}
 }
 return {launchTicks:launches,firingSoundResumesAfterRefreshes};
}
const baseline=measure(path.join(root,'revisions/playable-worker-combat-v21/build'));
const current=measure(path.join(root,'build'));
assert.deepEqual(current.launchTicks,Array.from({length:13},(_,i)=>i*24));
assert.deepEqual(baseline.launchTicks,[0,60,120,180,240]);
assert.equal(baseline.firingSoundResumesAfterRefreshes,190);
assert.equal(current.firingSoundResumesAfterRefreshes,10);
const m=machine(path.join(root,'build'));
for(const state of ['speech_left','speech_active','speech_pending']){
 m.reset();m.set('sfx_active',5);m.set('sfx_left',20);m.set(state,1);m.call('sfx_shot');assert.equal(m.get('sfx_pending'),0,`${state} protects speech`);
}
for(const id of [2,3,4]){
 m.reset();m.set('sfx_active',id);m.call('sfx_shot');assert.equal(m.get('sfx_pending'),0,'other active events protected');
 m.reset();m.set('sfx_pending',id);m.call('sfx_shot');assert.equal(m.get('sfx_pending'),id,'pending event protected');
}
m.reset();m.call('sfx_explosion');for(let n=0;n<10;n++)m.call('sfx_tick');m.call('sfx_shot');m.call('sfx_tick');assert.equal(m.get('sfx_active'),1,'real shot replaces explosion tail');assert.equal(m.ram[0x5c26],0,'three-refresh explosion hold does not slow shot');
const report={dck_sha256:createHash('sha256').update(m.cart).digest('hex'),baseline,current,speechPriority:true,otherEventPriority:true,romWrites:0};
fs.writeFileSync(path.join(root,'build/firing-verification.json'),JSON.stringify(report,null,2));console.log(report);
