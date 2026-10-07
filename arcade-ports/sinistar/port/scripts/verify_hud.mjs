import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/effects-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
let writes=0;const bus={read:a=>0xd0&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(0xd0&(1<<(a>>13)),0,'no ROM writes');if(a>=0x4000&&a<0x7800)writes++;ram[a]=v;},ioRead:()=>255,ioWrite:()=>{}};
function call(){cpu.pc=sym.hud_tick;assert.ok(cpu.pc);cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;const start=clock.tstates;for(let n=0;cpu.pc!==0x100;n++){assert.ok(n<10000);runZ80(cpu,bus,1,clock);}return clock.tstates-start;}
function score(text){const glyphs=['75557','26227','71747','71717','55711','74717','74757','71222','75757','75717'];for(let c=0;c<6;c++)for(let y=0;y<5;y++)assert.equal(ram[0x4201+y*256+c],parseInt(glyphs[+text[c]][y])*16,`score ${text}, digit ${c}, row ${y}`);}
const initT=call();for(let y=0;y<5;y++)for(const base of [0x6201,0x6221,0x6223,0x6224])assert.equal(ram[base+y*256],7,"HUD text normal black");score('000000');assert.ok(ram.slice(0x47e0,0x4800).every(x=>x===255));assert.ok(ram.slice(0x67e0,0x6800).every(x=>x===65));
ram[sym.frames]=1;writes=0;const skipT=call();assert.equal(writes,0);
ram[sym.frames]=16;const sameT=call();assert.equal(writes,0);
ram[0x5c24]=1;ram[sym.crystals_taken]=2;ram[sym.bs_hits]=3;const changeT=call();score('002050');assert.equal(writes,60,'only six five-row digits and their attributes');
ram[sym.bs_hits]=13;call();score('021550');
ram[0x5c24]=100;ram[sym.crystals_taken]=200;call();score('076000');
const before=ram.slice(0x4000,0x7800);writes=0;const highSameT=call();assert.equal(writes,0);assert.deepEqual(ram.slice(0x4000,0x7800),before);
ram[sym.frames]=0;ram[0x5c24]=0;ram[sym.crystals_taken]=0;ram[sym.bs_hits]=0;call();score('000000');
// Actual displayed inventory: zero, launch/decrement, and two-digit values.
ram[sym.frames]=16;
const glyphs=['75557','26227','71747','71717','55711','74717','74757','71222','75757','75717'];
for(const ammo of [3,2,0,9,10,24]){ram[sym.bombs]=ammo;writes=0;call();for(let row=0;row<5;row++){assert.equal(ram[0x4221+row*256],parseInt('65656'[row])*16,'B label');assert.equal(ram[0x4223+row*256],parseInt(glyphs[Math.floor(ammo/10)][row])*16,'tens');assert.equal(ram[0x4224+row*256],parseInt(glyphs[ammo%10][row])*16,'ones');}assert.equal(writes,30);writes=0;call();assert.equal(writes,0,'unchanged inventory does not redraw');}
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),initT,skipT,sameT,highSameT,changeT,typicalCpuPercent:(15*skipT+sameT)/16*60.1145/3528000*100,changedWrites:60,unchangedWrites:0,scoreCases:5,ammoCases:6,ammoUnchangedWrites:0,divider:true};fs.writeFileSync(path.join(root,'build/frontend-hud-verification.json'),JSON.stringify(report,null,2));console.log(report);
