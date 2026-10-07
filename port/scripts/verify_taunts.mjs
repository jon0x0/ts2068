import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
let mapping=16,selected=0,romWrites=0,shapeWrites=0;const ay=new Uint8Array(16);
const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){if(mapping&(1<<(a>>13))){romWrites++;console.error({a,pc:cpu.pc,mapping,sp:cpu.sp});}else ram[a]=v;},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;else if((p&255)===0xf5)selected=v;else if((p&255)===0xf6){ay[selected&15]=v;if(selected===13)shapeWrites++;}}};
function call(name,bank=0x50,regs={},stack=0x7ffd){mapping=bank;ram[0x78df]=bank;Object.assign(cpu,regs);cpu.pc=sym[name];assert.ok(cpu.pc,name);cpu.sp=stack;ram[stack]=0;ram[stack+1]=1;cpu.halted=false;const start=clock.tstates;for(let n=0;cpu.pc!==0x100;n++){assert.ok(n<200000,name);runZ80(cpu,bus,1,clock);}assert.equal(cpu.sp,stack+2);assert.equal(romWrites,0);return clock.tstates-start;}
const get=n=>ram[sym[n]],set=(n,v)=>ram[sym[n]]=v;
function reset(){ram.fill(0);ram.set(fs.readFileSync(path.join(root,'build/roar-mixer.bin')),0x7f60);ay.fill(0);set('sinistar_built',1);set('speech_started',1);set('awake_done',1);set('lives',3);}
const clips=JSON.parse(fs.readFileSync(path.join(root,'build/mining-assets.json'))).filter(x=>x.kind==='speech');
let frames=0,maxSpeech=0;const mouths=new Set();
for(const clip of clips){
 reset();set('speech_pending',clip.index+1);
 for(let frame=0;frame<clip.data.length/14;frame++){
  const shapesBefore=shapeWrites,oldShape=ay[13],shape=clip.data[frame*14+13];
  maxSpeech=Math.max(maxSpeech,call('speech_tick',16,{},frame&1?0xfffd:0x7ffd));
  assert.deepEqual([...ay.slice(0,13)],clip.data.slice(frame*14,frame*14+13),`clip ${clip.index} frame ${frame}`);
  assert.equal(shapeWrites-shapesBefore,shape===255?0:1,'R13 sentinel/restart');
  assert.equal(ay[13],shape===255?oldShape:shape,'exact envelope shape');
  mouths.add(ram[0x5c3d]);frames++;
 }
 call('speech_tick',16);assert.equal(get('speech_active'),0);assert.equal(ram[0x5c3d],0);
 assert.equal(ay[8]|ay[9]|ay[10],0);
}
// Duplicate hit/taunt requests cannot rewind the current roar, including its last frame.
reset();set('speech_pending',3);let maxHybrid=0;
for(let frame=0;frame<170;frame++){
 if([0,12,169].includes(frame)){set('speech_pending',3);ram[0x7f53]=12;}
 const burst=ram[0x7f53];maxHybrid=Math.max(maxHybrid,call('speech_tick',16));
 const expected=clips[2].data.slice(frame*14,frame*14+13);
 if(burst){expected[6]=17-burst;expected[7]=(expected[7]&0x1b)|0x24;expected[10]=burst+3;}
 assert.deepEqual([...ay.slice(0,13)],expected,'roar advances while impact mixes');
 assert.equal(get('speech_left'),169-frame);
 assert.equal(get('speech_pending'),0);
}
call('speech_tick',16);assert.equal(get('speech_active'),0);assert.equal(ram[0x7f53],0,'impact does not leak into next roar');
assert.deepEqual([...mouths].sort(),[0,1,2]);
const counts={};
for(let random=0;random<256;random++){
 reset();call('wb_taunt_select',0x50,{a:random});const id=get('speech_pending');counts[id]=(counts[id]??0)+1;
 const expected=random<=0x28?4:random<=0x50?5:random<=0x78?6:random<=0xa0?7:random<=0xc8?8:3;
 assert.equal(id,expected,'inclusive arcade thresholds');
}
assert.deepEqual(counts,{3:55,4:41,5:40,6:40,7:40,8:40});
for(const field of ['speech_active','speech_left','speech_pending']){
 reset();set(field,1);call('wb_taunt_select',0x50,{a:0x60});assert.equal(get('speech_pending'),field==='speech_pending'?1:0,'normal taunt never interrupts');
}
reset();set('speech_active',2);set('speech_left',20);call('wb_taunt_select',0x50,{a:0xff});assert.equal(get('speech_pending'),3,'roar may interrupt speech');
for(const [field,value] of [['sinistar_built',0],['lives',0],['invulnerable',1],['game_status',1],['bs_hits',13]]){
 reset();set(field,value);call('wb_taunt_select',0x50,{a:0x60});assert.equal(get('speech_pending'),0,field);
}
reset();ram[0x5c35]=1;call('wb_taunt_select',0x50,{a:0x60});assert.equal(get('speech_pending'),0,'out-of-sector gate');
reset();ram[0x5c31]=1;ram[0x5c33]=1;for(let n=0;n<63;n++){call('wb_taunt_step');assert.equal(get('speech_pending'),0);}call('wb_taunt_step');assert.equal(get('speech_pending'),4,'Task64 opportunity');
reset();ram[0x5c2f]=63;ram[0x5c33]=0x80;ram[0x5c34]=0x1c;call('wb_taunt_step');assert.equal(get('speech_pending'),0,'random byte 39h exceeds inclusive 38h trial');
reset();ram[0x5c36]=1;ram[0x5c31]=1;call('wb_taunt_step');assert.equal(get('speech_pending'),4,'sector entry requests a taunt');
let seed=0xace1;
reset();ram[0x5c31]=seed&255;ram[0x5c32]=seed>>8;
for(let i=0;i<1000;i++){const hi=seed>>8;seed=((seed<<1)|((((hi<<1)^hi)>>6)&1))&65535;call('wb_taunt_random',0x50,{h:0x5c,l:0x31});assert.equal(ram[0x5c31]+256*ram[0x5c32],seed);assert.equal(cpu.a,seed>>8);}
// Compressed transition tables reproduce every pair index, including shared parents.
const transition=JSON.parse(fs.readFileSync(path.join(root,'build/fast-transitions.json'))),pairIds=new Map();let maxTransition=0;
for(const test of transition.cases){
 reset();ram.fill(0x55,0x7f00,0x7f40);ram[0x580a]=test.address&255;ram[0x580b]=test.address>>8;
 maxTransition=Math.max(maxTransition,call('wb_transition_unpack'));
 const expected=test.pairs.map(p=>{const key=p.join(',');if(!pairIds.has(key))pairIds.set(key,pairIds.size);return pairIds.get(key);});
 assert.deepEqual([...ram.slice(0x7f00,0x7f00+expected.length)],expected);assert.ok(ram.slice(0x7f35,0x7f40).every(x=>x===0x55));
}
const assets=JSON.parse(fs.readFileSync(path.join(root,'build/mining-assets.json'))),previous=Uint8Array.from(Array.from({length:364},()=>[255,0,1]).flat());ram.set(previous,0xd800);
for(const asset of assets.filter(x=>x.kind==='assembly')){
 const i=sym.assembly_lengths+2*asset.index,size=rom[i]+256*rom[i+1];ram.set(rom.slice(asset.address,asset.address+size),0xb800);call('mr_assembly_patch',16);assert.deepEqual([...ram.slice(0xd800,0xdc44)],asset.data,'lossless assembly delta');
}
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),clips:clips.length,frames,ayRegistersExact:true,selectionCounts:counts,task64:true,sectorGate:true,roarPriority:true,mouthStates:[...mouths].sort(),rngSteps:1000,transitionCases:transition.cases.length,maxTransitionTstates:maxTransition,maxSpeechTickTstates:maxSpeech,maxHybridTickTstates:maxHybrid,assemblyStages:20,romWrites};
fs.writeFileSync(path.join(root,'build/taunts-verification.json'),JSON.stringify(report,null,2));console.log(report);
