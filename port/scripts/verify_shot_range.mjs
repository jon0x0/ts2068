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
 return {cart,ram,cpu,call,get,set,reset,hold:()=>held=true};
}
const now=machine(path.join(root,'build')),old=machine(path.join(root,'revisions/playable-black-text-v55/build'));let velocityCases=0;
function start(m,angle){m.reset();m.set('control_mode',1);m.hold();m.cpu.a=angle;m.call('player_sincos');m.ram[0x78e8]=m.cpu.e;m.ram[0x78e9]=m.cpu.d;m.call('fire_input');}
// Fixed cartridge state addresses are stable across these two revisions.
const signed=(m,a)=>((m.ram[a]|m.ram[a+1]<<8)<<16)>>16;
// Resolve velocities through the cartridge symbol files.
function symbols(dir){return Object.fromEntries([...fs.readFileSync(path.join(dir,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));}
const ns=symbols(path.join(root,'build')),os=symbols(path.join(root,'revisions/playable-black-text-v55/build'));
for(let angle=0;angle<256;angle++){start(old,angle);start(now,angle);for(const n of ['bvx','bvy'])assert.equal(signed(now,ns[n])*2,signed(old,os[n])*3);assert.equal(now.ram[0x5891],24);velocityCases++;}
function distantWorker(m,s){start(m,64);m.ram[s.px+1]=40;m.ram[s.py+1]=100;m.set('bullet_alive',0);m.set('worker_alive',1);m.set('worker_x',160);m.set('worker_y',106);m.call('fire_input');for(let i=0;i<24;i++)m.call('bullet_step');return m.get('worker_alive');}
assert.equal(distantWorker(old,os),1);assert.equal(distantWorker(now,ns),2);
let secondaryHitCases=0;
for(let phase=0;phase<4;phase++){
 start(now,64);now.ram[ns.px+1]=40;now.ram[ns.py+1]=100;now.set('bullet_alive',0);now.ram[0x5893]=1;now.ram[0x5865]=phase;
 now.ram[0x79b0]=160;now.ram[0x79b2]=90;now.ram[0x79b7]=96;
 now.call('fire_input');for(let tick=0;tick<24;tick++){now.call('world_step');now.call('bullet_step');}
 assert.ok(now.get('hits')>0,'long-range secondary rock hit at each population phase');secondaryHitCases++;
}
const report={dck_sha256:createHash('sha256').update(now.cart).digest('hex'),velocityCases,secondaryHitCases,speedMultiplier:1.5,lifetimeTicks:24,distantWorkerNowHit:true,cardinalTravelBeforeApprox:91,cardinalTravelAfterApprox:137};fs.writeFileSync(path.join(root,'build/shot-range-verification.json'),JSON.stringify(report,null,2));console.log(report);
