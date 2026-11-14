import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api,z,root,off}from'./r22_test_machine.mjs';
const out=path.join(root,'build/fullgame/responsive_game_r50'),engine=fs.readFileSync(path.join(root,'build/fullgame/responsive_game_r50/overlay.bin')),phases=fs.readFileSync(path.join(root,'build/diagnostics/pixel_movement_trial/ship_phases.bin'));
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/fullgame/responsive_game_r50/overlay.sym'),'utf8').matchAll(/(\w+): EQU 0x([0-9a-f]+)/ig)].map(v=>[v[1],parseInt(v[2],16)]));
const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));api.insertDock(m,Buffer.concat([Buffer.from([0,...Array(8).fill(3)]),Buffer.alloc(65536)]));m.portF4=0x89;m.portFF=2;m.dock[7].set(engine,0x400);m.dock[7].set(phases.subarray(768,1536),0xd80);m.dock[7].fill(0,0x1680,0x1b00);m.ram[0x5bc2]=1;m.dock[3][0x1aa4]=3;m.dock[3][0x1a98]=1;
const get=a=>m.dock[7][a-0xe000],set=(a,v)=>m.dock[7][a-0xe000]=v;
let basePix=Buffer.alloc(6144),baseAttr=Buffer.alloc(6144);for(let y=0;y<160;y++)for(let c=0;c<32;c++){let i=off(y)+c;basePix[i]=((c*13+y*7)%19===0)?0x81:0;baseAttr[i]=7;}
m.ram.set(basePix,0x4000);m.ram.set(baseAttr,0x6000);set(0xf680,40);set(0xf682,40);set(0xf681,80);set(0xf683,80);
let inspectWrites=true,beforeWrite=null,expectedWrite=null,checkedWrites=0;const originalWrite=m.bus.write;m.bus.write=(addr,v)=>{if(inspectWrites&&beforeWrite&&addr>=0x4000&&addr<0x5800&&!(m.portF4&4)){expectedWrite??=reference();const at=addr-0x4000,common=beforeWrite[at]&expectedWrite.p[at];assert.equal(v&common,common,'A shared background/player pixel was temporarily erased');checkedWrites++;}originalWrite(addr,v);};
function call(pc){beforeWrite=Buffer.from(m.ram.slice(0x4000,0x5800));expectedWrite=null;Object.assign(m.cpu,{pc,sp:0x5ce0,iff1:false,iff2:false});m.ram[0x5ce0]=0;m.ram[0x5ce1]=0x80;let n=0;const start=m.tstates;while(m.cpu.pc!==0x8000&&n++<200000)z.runZ80(m.cpu,m.bus,1,m);assert(n<200000,'Hang '+m.cpu.pc.toString(16));assert.equal(m.portF4,0x89);assert.equal(m.cpu.sp,0x5ce2);return m.tstates-start;}
function reference(){let p=Buffer.from(basePix),a=Buffer.from(baseAttr),x=get(0xf680),y=get(0xf681),src=(8+(x&7))*96;for(let r=0;r<8;r++)for(let c=0;c<4;c++){let i=off(y+r)+(x>>3)+c,mask=phases[src+64+r*4+c];p[i]=(p[i]&~mask)|phases[src+r*4+c];if(mask)a[i]=phases[src+32+r*4+c];}return{p,a};}
function check(){const e=reference();assert(Buffer.from(m.ram.slice(0x4000,0x5800)).equals(e.p),'Pixels '+get(0xf680)+','+get(0xf681));assert(Buffer.from(m.ram.slice(0x6000,0x7800)).equals(e.a),'Attrs '+get(0xf680)+','+get(0xf681));}
call(sym.render);check();let times=[];
for(const [input,count]of [[2,185],[4,72],[8,130],[1,230],[4,152],[10,120],[0,5]]){m.dock[3][0x14fa]=input;for(let i=0;i<count;i++){times.push(call(sym.tick));check();}}
// A real scene refresh must preserve both retained planes after temporary overlay.
for(let i=0;i<6144;i++){m.dock[3][i]=basePix[i];m.dock[2][i]=baseAttr[i];}m.dock[3].fill(0x81,0x1e00);m.ram.fill(0x81,0x8000,0x8080);
const p0=Buffer.from(m.dock[3].slice(0,6144)),a0=Buffer.from(m.dock[2].slice(0,6144));call(sym.prepare_copy);assert.equal(m.ram[0x5bc3],1);m.ram.set(m.dock[3].slice(0,6144),0x4000);m.ram.set(m.dock[2].slice(0,6144),0x6000);call(sym.restore_copy);assert.equal(m.ram[0x5bc3],0);assert(Buffer.from(m.dock[3].slice(0,6144)).equals(p0),'Retained pixel restore');assert(Buffer.from(m.dock[2].slice(0,6144)).equals(a0),'Retained colour restore');check();
inspectWrites=false;
// Stationary collision uses composed pixels, not merely shared character cells.
const px=get(0xf680),py=get(0xf681),p=(8+(px&7))*96;let target=null;
for(let r=0;r<8&&!target;r++)for(let c=0;c<4;c++){const mask=phases[p+64+r*4+c];if(mask&&mask!==255){target={r,c,mask};break;}}
assert(target);const ti=off(py+target.r)+(px>>3)+target.c,cell=((py+target.r)>>3)*32+(px>>3)+target.c;
function meta(v){if(cell<512)m.dock[3][0x1e00+cell]=v;else m.ram[0x8000+cell-512]=v;}
m.dock[3].fill(0,0,6144);m.dock[2].fill(7,0,6144);m.dock[3].fill(0,0x1e00);m.ram.fill(0,0x8000,0x8080);m.dock[3][0x1a98]=0;meta(0x81);
const outside=(~target.mask)&255;m.dock[3][ti]=outside&-outside;m.ram[0x5bc4]=0;call(sym.prepare_copy);assert.equal(m.ram[0x5bc4],0,'Disjoint pixels in same cell must not collide');call(sym.restore_copy);
meta(0x81);m.dock[3][ti]=target.mask&-target.mask;m.ram[0x5bc4]=0;call(sym.prepare_copy);assert.equal(m.ram[0x5bc4],1,'Stationary overlapping pixels must collide');call(sym.restore_copy);
const result={passed:true,stationary_pixel_collision:true,common_pixels_never_erased:true,checked_bitmap_writes:checkedWrites,disjoint_shared_cell_no_hit:true,native_ticks:times.length,mean_tick_cycles:times.reduce((a,b)=>a+b,0)/times.length,max_tick_cycles:Math.max(...times),scope:'Background-aware accelerated player-overlay component tests; separate from full-game routes',retained_planes_restored:true};fs.writeFileSync(path.join(out,'overlay_component_validation.json'),JSON.stringify(result,null,2));console.log(result);
