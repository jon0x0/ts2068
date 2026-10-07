import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const upstream=process.env.TSRUN_ROOT ? path.resolve(process.env.TSRUN_ROOT) : path.resolve(root,'../../../TSRun');
const {createZ80,runZ80}=await import(pathToFileURL(path.join(upstream,'z80.js')));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
let mapping=16,selected=0,romWrites=0,keyC=false;const ay=new Uint8Array(16);
const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){if(mapping&(1<<(a>>13)))romWrites++;else ram[a]=v;},ioRead:p=>p===0xfefe&&keyC?247:255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;else if((p&255)===0xf5)selected=v;else if((p&255)===0xf6)ay[selected&15]=v;}};
function invoke(name,bank=0x50,regs={},stack=0x7ffd){mapping=bank;ram[0x78df]=bank;Object.assign(cpu,regs);cpu.pc=sym[name];assert.ok(cpu.pc,name);cpu.sp=stack;ram[stack]=0;ram[stack+1]=1;cpu.halted=false;const before=clock.tstates;for(let n=0;cpu.pc!==0x100;n++){assert.ok(n<200000,`bounded ${name}`);runZ80(cpu,bus,1,clock);}assert.equal(cpu.sp,stack+2,name);return clock.tstates-before;}
const set=(n,v)=>ram[sym[n]]=v,word=(n,v)=>{set(n,v&255);ram[sym[n]+1]=(v>>8)&255;},value=n=>{const v=ram[sym[n]]+256*ram[sym[n]+1];return v&32768?v-65536:v;};
function axis(n,high,v){word(n,(v&255)*256);ram[high]=(v>>8)&1;}
function reset(){ram.fill(0);ay.fill(0);set('game_mode',1);}

let workerCases=0;
for(const x of [100,508])for(const carrying of [false,true]){
 reset();axis('bx',0x7c94,(x+5)&511);axis('by',0x7c95,106);set('worker_x',x&255);ram[0x7c98]=x>>8;set('worker_y',100);set('worker_alive',1);set('worker_mission',carrying?6:0);set('crystal_alive',carrying?2:0);set('bullet_alive',1);ram[0x5891]=60;
 invoke('wb_bullet');assert.equal(ram[sym.worker_alive],2,'worker enters explosion');assert.equal(ram[sym.bullet_alive],0);assert.equal(ram[0x5c24],1);assert.equal(ram[sym.sfx_pending],5);assert.equal(ram[sym.crystal_alive],carrying?1:0,'carried crystal released');
 for(let i=0;i<32;i++)invoke('wb_worker');assert.equal(ram[sym.worker_alive],0);
 for(let i=0;i<180;i++)invoke('wb_worker');assert.equal(ram[sym.worker_alive],1,'respawns even before first assembly piece');workerCases++;
}
reset();set('worker_alive',1);set('worker_x',100);set('worker_y',100);axis('bx',0x7c94,200);axis('by',0x7c95,106);set('bullet_alive',1);ram[0x5891]=60;invoke('wb_bullet');assert.equal(ram[sym.worker_alive],1);assert.equal(ram[sym.bullet_alive],1,'miss remains live');

const speeds=[];
for(const angle of [0,64,128,192]){
 reset();set('control_power',127);invoke('player_sincos',16,{a:angle});ram[0x78e8]=cpu.e;ram[0x78e9]=cpu.d;
 invoke('wb_thrust');assert.ok(Math.max(Math.abs(value('pvx')),Math.abs(value('pvy')))<128,'acceleration is gradual');
 for(let i=0;i<250;i++)invoke('wb_thrust');speeds.push([angle,value('pvx'),value('pvy')]);assert.ok(Math.max(Math.abs(value('pvx')),Math.abs(value('pvy')))>480,'higher target speed reached');
 const before=[value('pvx'),value('pvy')];set('control_power',0);invoke('wb_thrust');assert.deepEqual([value('pvx'),value('pvy')],before,'coasting');
}
assert.ok(speeds[0][2]<0&&speeds[2][2]>0,'both vertical polarities');
let bounceCases=0,maxBounce=0;
for(const rockX of [100,508])for(const side of [-1,1]){
 reset();axis('px',0x7c96,(rockX+7+side*13+512)&511);axis('py',0x7c97,108);word('pvx',-side*500);
 maxBounce=Math.max(maxBounce,invoke('wb_bounce_call',0x50,{h:rockX>>8,l:rockX&255,d:0,e:100,a:0}));assert.equal(value('pvx'),side*500,'normal bounce, including seam');assert.equal(ram[0x5c25],8);
 const reflected=value('pvx');invoke('wb_bounce_call',0x50,{h:rockX>>8,l:rockX&255,d:0,e:100,a:0});assert.equal(value('pvx'),reflected,'contact does not invert repeatedly');set('control_power',127);ram[0x78e9]=127;invoke('wb_thrust');assert.equal(value('pvx'),reflected,'held thrust does not erase rebound immediately');bounceCases++;
}
reset();axis('px',0x7c96,94);axis('py',0x7c97,108);word('pvx',-500);invoke('wb_bounce_call',0x50,{h:0,l:100,d:0,e:100,a:0});assert.equal(value('pvx'),-500,'separating contact does not bounce');

// Native C matrix input: no auto-repeat toggling, immediate recovery release,
// both the primary and secondary rock entry points, and native notice expiry.
reset();ram[0x5c25]=8;keyC=true;invoke('mode_bounce_key',0x90);
assert.equal(ram[0x5c2b],1);assert.equal(ram[0x5c25],0);
for(let i=0;i<20;i++)invoke('mode_bounce_key',0x90);
assert.equal(ram[0x5c2b],1,'holding C toggles only once');
const noticeBaseline=path.join(root,'revisions/playable-edited-roar-v29/build');
const noticeRom=fs.readFileSync(path.join(noticeBaseline,'sinistar-mining.dck')).subarray(9);
const noticeSymbols=Object.fromEntries([...fs.readFileSync(path.join(noticeBaseline,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
function noticeExpected(label){for(let y=0;y<7;y++)for(let x=0;x<13;x++){
 const line=52+y,addr=0x4000+((line&7)<<8)+((line&56)<<2)+9+x;
 assert.equal(ram[addr],label?noticeRom[noticeSymbols[label]+y*13+x]:0,'notice bitmap');
 assert.equal(ram[addr+0x2000],7,'notice attributes use normal black');
}}
invoke('mode_notice',0x90);noticeExpected('mode_bounce_off');
ram[0x7802]=89;invoke('mode_notice',0x90);noticeExpected('mode_bounce_off');
ram[0x7802]=90;invoke('mode_notice',0x90);noticeExpected(null);
axis('px',0x7c96,94);axis('py',0x7c97,108);word('pvx',500);
invoke('wb_bounce_call',0x50,{h:0,l:100,d:0,e:100,a:0});assert.equal(value('pvx'),500,'primary rock ignored when disabled');
ram.set([100,0,100,0,0,0,0],0x7f00);invoke('wb_planet_bounce',0x50,{ix:0x7f00});assert.equal(value('pvx'),500,'secondary rock ignored when disabled');
keyC=false;invoke('mode_bounce_key',0x90);keyC=true;invoke('mode_bounce_key',0x90);
assert.equal(ram[0x5c2b],0);invoke('mode_notice',0x90);noticeExpected('mode_bounce_on');
invoke('wb_bounce_call',0x50,{h:0,l:100,d:0,e:100,a:0});assert.equal(value('pvx'),-500,'bounce restored');
keyC=false;
for(const enabled of [0,1]){ram[0x5bb1]=enabled;ram[0x5c2d]=0;ram[0x5bc6]=2;invoke('mode_notice',0x90);noticeExpected(enabled?'mode_on_text':'mode_off_text');}

let fragmentCases=0;
const explosionAssets=JSON.parse(fs.readFileSync(path.join(root,'build/mining-assets.json'))).filter(a=>a.kind==='arcade-explosion');
function explosionExpected(frame,phase){const src=explosionAssets.find(a=>a.index===frame).data,raw=[...src];if(phase)for(let y=0;y<26;y++){let previous=7;for(let x=0;x<4;x++){const i=(y*4+x)*3;raw[i]=((src[i]>>>phase)|((x?src[i-3]:255)<<(8-phase)))&255;raw[i+1]=((src[i+1]>>>phase)|((x?src[i-2]:0)<<(8-phase)))&255;if(raw[i]!==255){if(raw[i+2]===1)raw[i+2]=previous;previous=raw[i+2];}}}return raw;}
let maximumExplosionStage=0;
for(let phase=0;phase<8;phase++)for(const ticks of [32,24,16,8]){
 reset();set('worker_alive',2);set('worker_x',phase);ram[0x5c27]=ticks;ram.fill(0x55,0xb7f0,0xb948);maximumExplosionStage=Math.max(maximumExplosionStage,invoke('wb_explosion_sprite'));assert.equal(mapping,0x50);assert.ok(ram.subarray(0xb7f0,0xb800).every(v=>v===0x55));assert.ok(ram.subarray(0xb938,0xb948).every(v=>v===0x55));
 assert.deepEqual([...ram.slice(0xb800,0xb938)],explosionExpected((32-ticks)/8,phase),'original IEXPLO worker frame');
 ram[0x783c]=phase;ram[0x783e]=ticks/8;invoke('ring_effect',0x94);assert.deepEqual([...ram.slice(0xb800,0xb938)],explosionExpected((32-ticks)/8,phase),'same original frame for bomb impact');fragmentCases++;
}

reset();axis('px',0x7c96,128);axis('py',0x7c97,112);ram[0x5886]=48;invoke('radar_entry');
const dot=(x,y)=>ram[0x7e00+y*8+(x>>3)]&(128>>(x&7));
for(let x=16;x<=47;x++){assert.ok(dot(x,8),'top scanner outline');assert.ok(dot(x,11),'bottom scanner outline');}for(const y of [9,10])for(const x of [16,47])assert.ok(dot(x,y),'side scanner outline');assert.ok(dot(32,8),'player stays centered');

const effects=JSON.parse(fs.readFileSync(path.join(root,'../assets/sfx-manifest.json'))).effects;let audioFrames=0;
for(let i=0;i<effects.length;i++){
 reset();let dest=0x5c40;for(const fx of effects){const data=fs.readFileSync(path.join(root,`../assets/sfx-${fx.name}.packed`));ram.set(data,dest);dest+=data.length;}assert.ok(dest<=0x5ea0);
 const fx=effects[i],raw=fs.readFileSync(path.join(root,`../assets/sfx-${fx.name}.ay`));set('sfx_pending',i+1);
 for(let tick=0;tick<fx.frames*fx.refresh_step;tick++){invoke('sfx_tick',16,{},tick&1?0xfffd:0x7ffd);const frame=Math.floor(tick/fx.refresh_step)*fx.refresh_step;for(const reg of [0,1,6,7,8])assert.equal(ay[reg],raw[frame*14+reg],`${fx.name} tick ${tick} reg ${reg}`);audioFrames++;}
 invoke('sfx_tick',16);assert.equal(ay[8],0,'effect ends silent');
}
reset();set('speech_left',30);invoke('sfx_explosion',16);assert.equal(ram[sym.sfx_pending],0,'speech rejects explosion');set('speech_active',1);set('sfx_active',5);set('sfx_left',10);invoke('sfx_tick',16);assert.equal(ram[sym.sfx_left],0,'speech preempts effect');
assert.equal(romWrites,0);
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),workerCases,bounceCases,bounceToggle:true,bounceNotice:true,maxBounceTstates:maxBounce,speeds,fragmentCases,audioFrames,radarOutline:true,speechPriority:true,romWrites};
fs.writeFileSync(path.join(root,'build/gameplay-features-verification.json'),JSON.stringify(report,null,2));console.log(report);
