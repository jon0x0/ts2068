import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
let mapping=0x10,latch=0,regs=new Uint8Array(14),writes=0;
const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0,'no ROM writes');ram[a]=v;},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;if((p&255)===0xf5)latch=v;if((p&255)===0xf6){assert.ok(latch<14);regs[latch]=v;writes++;}}};
function call(label){mapping=0x10;cpu.pc=sym[label];assert.ok(cpu.pc,label);cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;for(let n=0;cpu.pc!==0x100;n++){assert.ok(n<100000,label);runZ80(cpu,bus,1,clock);}}
const get=n=>ram[sym[n]],set=(n,v)=>ram[sym[n]]=v;
ram.set(fs.readFileSync(path.join(root,'../assets/sfx-explosion.packed')),23979);
ram[0x7bfb]=1;ram[0x7bfc]=96;call('death_attack');assert.equal(get('sfx_pending'),6);assert.equal(ram[0x7bfc],96);assert.equal(ram[0x7bfd],1,'first visual burst begins immediately');assert.equal(get('worker_alive'),2);assert.equal(ram[0x783e],0,'player uses one burst at a time');
const expected=fs.readFileSync(path.join(root,'../assets/sfx-player-impact-real.ay'));
for(let i=0;i<30;i++){call('sfx_tick');assert.equal(get('sfx_active'),6);ram[0x7bfd]=2;call('death_sound');assert.equal(get('sfx_pending'),0,'visual bursts cannot interrupt attack');for(const r of [0,1,6,7,8,9,10])assert.equal(regs[r],expected[i*14+r],`frame ${i}, register ${r}`);}
call('sfx_tick');assert.equal(get('sfx_active'),5);assert.equal(get('sfx_left'),62);
// Physics may lag the audio: its first visual burst must not restart either clip.
set('sfx_pending',0);ram[0x7bfd]=1;call('death_sound');assert.equal(get('sfx_pending'),0);
ram[0x7bfd]=2;call('death_sound');assert.equal(get('sfx_pending'),5);
// Existing speech wins over the attack and also cancels an ongoing attack.
for(const n of ['speech_pending','speech_active','speech_left']){set('sfx_pending',0);set(n,1);call('death_attack');assert.equal(get('sfx_pending'),0,n);set(n,0);}
set('sfx_active',6);set('sfx_left',4);set('speech_active',1);call('sfx_tick');assert.equal(get('sfx_active'),0);assert.equal(get('sfx_left'),0);
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),attackBytes:90,attackRefreshes:30,blastStartRefresh:31,delaySeconds:30/60.1145,registerStreamExact:true,speechPriority:true,physicsDoesNotRestartAttack:true,immediateVisualBurst:true,romWrites:0};
fs.writeFileSync(path.join(root,'build/player-impact-verification.json'),JSON.stringify(report,null,2));console.log(report);
