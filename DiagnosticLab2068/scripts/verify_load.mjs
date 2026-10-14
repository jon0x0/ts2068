// Actual mapped cartridge execution, option controls and recoverable load faults.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const api=await import(pathToFileURL(path.resolve('../TSRun/machine.js')));
const image=fs.readFileSync('build/diagnostic-v02.dck');
const sym={};for(const file of ['symbols.txt','load-symbols.txt'])Object.assign(sym,Object.fromEntries([...fs.readFileSync('build/'+file,'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)])));
const cases=[];
function machine({readFault,writeFault,ioFault}={}){
 const keys=new Uint8Array(8).fill(31),m=api.createMachine(keys,new Uint8Array(2).fill(255));
 m.homeRom.set(fs.readFileSync('../TSRun/roms/ts2068-0.rom'));api.insertDock(m,image);api.resetMachine(m);
 m.portF4=0x11;m.portFF=64;m.cpu.iff1=false;m.cpu.sp=0xbfff;m.cpu.e2=0;m.cpu.a2=0;
 const seen=new Set(),ports=[],writes=[],r=m.bus.read,w=m.bus.write,io=m.bus.ioWrite,ir=m.bus.ioRead;
 m.bus.read=a=>{if(a===m.cpu.pc){seen.add(a);assert.ok(a<0x2000||(a>=0x8400&&a<0x8e00&&(m.portF4&16))||(a>=0x7b7b&&a<=0x7b7d&&(m.cpu.e2&3)===3&&!(m.portF4&8)),'opcode mapping '+a.toString(16));}const v=r(a);return readFault?readFault(m,a,v):v;};
 m.bus.write=(a,v)=>{writes.push([a,v]);w(a,writeFault?writeFault(m,a,v):v);};
 m.bus.ioWrite=(p,v)=>{ports.push([p,v]);io(p,v);};m.bus.ioRead=p=>ioFault?ioFault(m,p,ir(p)):ir(p);
 return {m,keys,seen,ports,writes};
}
function run(t,label,budget=10000){const target=sym[label];assert.ok(target!==undefined,label);const r=t.m.bus.read,stop={};let hit=false;
 t.m.bus.read=a=>{if(a===t.m.cpu.pc&&a===target){hit=true;throw stop;}return r(a);};
 try{for(let i=0;i<budget;i++)api.runFrame(t.m);}catch(e){if(e!==stop)throw e;}finally{t.m.bus.read=r;}
 assert.ok(hit,label+' pc='+t.m.cpu.pc.toString(16)+' fault='+JSON.stringify({phase:t.m.cpu.e2,expected:t.m.cpu.b2,observed:t.m.cpu.c2,address:(t.m.cpu.xh<<8)|t.m.cpu.xl,ramFault:t.seen.has(sym.load_ram_fault),loadFailure:t.seen.has(sym.load_failure)}));
}
function record(name,extra={}){cases.push({name,result:'PASS',...extra});console.log(name+': PASS');}
function frames(t,n=1){for(let i=0;i<n;i++)api.runFrame(t.m);}
{const t=machine();t.m.cpu.pc=sym.menu_draw;run(t,'menu_poll');frames(t,2);t.keys[6]&=~2;run(t,'load_config_poll');assert.equal(t.m.cpu.a2,0x83);
 for(let k=0;k<8;k++){t.keys.fill(31);frames(t);t.keys[k<5?3:4]&=~(1<<(k<5?k:9-k));run(t,'load_config_ready');assert.equal(t.m.cpu.a2,0x83^((1<<(k+1))-1));run(t,'load_config_poll');}
 t.keys.fill(31);frames(t);t.keys[7]&=~8;run(t,'load_config_ready');assert.ok(t.m.cpu.e2&4);run(t,'load_config_poll');
 assert.ok(t.m.ram.slice(0x5a2b,0x5a30).every(v=>v===0x44));assert.ok(t.m.ram.slice(0x5a33,0x5a3f).every(v=>v===0x47));
 t.keys.fill(31);frames(t);t.keys[0]&=~8;run(t,'load_config_ready');assert.ok(!(t.m.cpu.e2&4));run(t,'load_config_poll');
 assert.ok(t.m.ram.slice(0x5a2b,0x5a30).every(v=>v===0x47));assert.ok(t.m.ram.slice(0x5a33,0x5a3f).every(v=>v===0x44));
 record('main L entry, all eight toggles and finite/continuous controls');
}
{const t=machine();t.m.cpu.pc=sym.load_config_ready;t.m.cpu.a2=0;run(t,'load_config_poll');frames(t);t.keys[2]&=~8;
 run(t,'load_warning_poll');frames(t,3);assert.ok(!t.seen.has(sym.load_start),'held R cannot confirm its own warning');
 t.keys.fill(31);frames(t);t.keys[2]&=~16;run(t,'load_warning_poll');frames(t);assert.ok(t.m.cpu.e2&2);
 t.keys.fill(31);frames(t);t.keys[2]&=~8;run(t,'load_running_ready');assert.ok(t.m.cpu.e2&1);assert.ok(t.m.cpu.a2&8);
 record('return-profile warning requires release/new R; T selects IM2');
}
{const t=machine();t.m.cpu.pc=sym.load_running_ready;t.m.cpu.a2=0;const start=t.m.tstates;run(t,'load_batch_start');
 const seconds=(t.m.tstates-start)/3528000;assert.ok(seconds>=6&&seconds<6.01);record('six-second mixed-load notice remains register-only',{seconds});
}
{const t=machine();t.m.cpu.pc=sym.load_batch_start;t.m.cpu.a2=0;t.m.cpu.e2=4;run(t,'fullsummary_poll');assert.equal((t.m.cpu.b2<<8)|t.m.cpu.c2,1);assert.equal(t.m.portF4,1);record('one-batch preset completes and displays stopped count');}
function slice(mask){const t=machine();t.m.cpu.pc=sym.load_work_ram;t.m.cpu.a2=mask;t.m.cpu.i=7;t.m.cpu.xh=0x40;t.m.cpu.xl=0x00;return t;}
// Every authoritative mask must remain bounded; no RAM data chooses control.
for(let mask=0;mask<256;mask++){
 const t=slice(mask);run(t,'load_ram_resume',300);
 assert.equal(t.m.cpu.a2,mask);assert.equal(t.m.cpu.i,7);assert.equal(t.m.portF4,0x11);
 assert.equal(t.m.cpu.xh,0x40);assert.equal(t.m.cpu.xl,0);
 const ay=t.ports.filter(([p])=>(p&255)===0xf6),bank=t.ports.filter(([p,v])=>(p&255)===0xf4&&[0xd1,0x51,0x19,0x91].includes(v));
 assert.equal(ay.length,mask&64?(mask&32?14:13):0);assert.equal(bank.length,mask&16?4:0);
}
record('all256 option masks: bounded slice, preserved registers and disabled-load absence');
{const t=slice(255),modes=new Set();let quiet=0,busy=0;
 for(let n=0;n<16;n++){t.m.cpu.pc=sym.load_work_ram;const first=t.ports.length;run(t,'load_ram_resume');const ports=t.ports.slice(first);
  for(const [p,v] of ports)if((p&255)===255)modes.add(v&7);
  if(t.m.cpu.e2&8){busy++;assert.equal(ports.filter(([p])=>(p&255)===246).length,14);assert.ok(ports.some(([p,v])=>(p&255)===254&&(v&16)));}
  else {quiet++;assert.ok(!ports.some(([p,v])=>(p&255)===254&&(v&16)));assert.equal(t.m.portFF,64);}
 }
 assert.deepEqual([...modes].sort(),[0,2,6]);assert.equal(quiet,8);assert.equal(busy,8);record('power cycles quiet/busy, all three video modes, envelope/audio/beeper and preserved RAM pointer');
}
for(const region of [0x4000,0x8000,0xc000])for(const mask of [1,2,4,8,16,32,64,128,0x26]){
 const address=region+0x40,t=machine();t.m.portF4=1;t.m.cpu.pc=sym.load_stack_pair;t.m.cpu.h=address>>8;t.m.cpu.l=address&255;t.m.cpu.i=8;
 const r=t.m.bus.read;t.m.bus.read=a=>{const v=r(a);return a===address&&t.m.cpu.pc===sym.load_stack_read+1?v^mask:v;};
 run(t,'fault_report');assert.equal(t.m.cpu.b2^t.m.cpu.c2,mask);assert.equal((t.m.cpu.xh<<8)|t.m.cpu.xl,address);
 record('exact bit-mask '+mask.toString(16)+' at '+address.toString(16));
}
{const t=slice(64),framesSeen=[];for(let n=0;n<20;n++){t.m.cpu.pc=sym.load_work_ram;const before=t.ports.length;run(t,'load_ram_resume');framesSeen.push(t.ports.slice(before).filter(([p])=>(p&255)===246).map(([,v])=>v));}
 assert.equal(new Set(framesSeen.map(JSON.stringify)).size,16);assert.deepEqual(framesSeen[0],framesSeen[16]);record('AY traffic cycles all16 distinct bounded Speech2AY-style frames');}
for(const mask of [0,1,2,128,0x83,0xff]){
 const t=machine();t.m.cpu.a2=mask;t.m.cpu.pc=sym.load_batch_start;
 run(t,'load_batch_completed',20000);assert.ok(!t.seen.has(sym.load_ram_fault));assert.equal(t.m.cpu.a2,mask);
 if(mask&1)assert.ok(t.seen.has(sym.load_ram_hash_read));if(mask&2)assert.ok(t.seen.has(sym.load_ram_desc));if(mask&128)assert.ok(t.seen.has(sym.load_stack_read));
 record('complete healthy batch mask '+mask.toString(16));
}
for(const address of [0x4001,0x5ecf,0x8122,0xbfff,0xc122]){
 const t=machine({readFault:(m,a,v)=>a===address&&m.cpu.pc===sym.load_stack_read?v&253:v});
 // Inject at the actual stack-data bus read rather than at opcode fetch.
 let fired=false;const r=t.m.bus.read;t.m.bus.read=a=>{let v=r(a);if(a===address&&t.m.cpu.pc>=sym.load_stack_read&&t.m.cpu.pc<sym.load_stack_read+2){fired=true;v&=253;}return v;};
 t.m.cpu.pc=sym.load_stack_begin;t.m.cpu.a2=128;t.m.cpu.i=8;
 run(t,'fault_report');assert.ok(fired);assert.equal(t.m.cpu.b2^t.m.cpu.c2,2);assert.equal(t.m.portF4,1);assert.equal(t.m.portFF,64);
 record('D1 stack-data loss at '+address.toString(16)+' reaches ROM reporter');
}
{const t=slice(8);t.m.bus.ioWrite=((base)=>((p,v)=>base(p,(p&255)===255?v|64:v)))(t.m.bus.ioWrite);run(t,'load_failure');record('missing frame IRQ bounded timeout');}
{const t=slice(8);t.m.bus.ioWrite=((base)=>((p,v)=>base(p,(p&255)===255?v&~64:v)))(t.m.bus.ioWrite);run(t,'load_failure');record('failed IRQ inhibit becomes bounded IRQ failure');}
{const t=machine();t.m.cpu.pc=sym.load_batch_done;t.m.cpu.a2=8;t.m.cpu.e2=1;t.m.cpu.i=8;
 t.m.bus.ioWrite=((base)=>((p,v)=>base(p,(p&255)===255?v|64:v)))(t.m.bus.ioWrite);run(t,'load_failure');assert.ok(!t.seen.has(sym.load_return_start));record('fresh IRQ qualification failure gates genuine return profile');}
{const t=slice(16);const r=t.m.bus.read;t.m.bus.read=a=>a===0xfff0?r(a)^2:r(a);run(t,'load_failure');record('bad bank signature bounded failure');}
{const t=slice(64);const r=t.m.bus.ioRead;t.m.bus.ioRead=p=>(p&255)===246?255:r(p);run(t,'load_failure');record('absent AY masked readback becomes bounded audio failure');}
{const t=slice(64),r=t.m.bus.read;t.m.bus.read=a=>{const v=r(a);return a>=sym.load_ay_table&&a<sym.load_ay_table+256&&(a-sym.load_ay_table)%16===7?v|192:v;};run(t,'load_ram_resume');const ay=t.ports.filter(([p])=>(p&255)===246);assert.equal(ay.length,13);assert.equal(ay[7][1]&192,0);record('corrupt AY frame cannot change I/O direction or fixed13-write bound');}
{const t=slice(0xff);t.m.cpu.e2=128;t.keys[1]=30;run(t,'load_exit');record('new key cancels load slice');}
for(const im2 of [false,true]){
 const t=machine();t.m.cpu.pc=sym.load_return_start;t.m.cpu.a2=0x5c;t.m.cpu.e2=1|(im2?2:0);t.m.cpu.d2=9;t.m.cpu.h2=3;
 run(t,'load_batch_completed',3000);assert.ok(t.seen.has(sym.load_return_after_af));assert.equal(t.m.cpu.sp,0xbfff);
 assert.ok(t.ports.some(([p])=>(p&255)===0xf6));record((im2?'IM2':'IM1')+' fresh qualification, real stack/audio IRQ returns and bounded completion');
}
for(const im2 of [false,true]){const t=machine();t.m.cpu.pc=sym.load_batch_start;t.m.cpu.a2=255;t.m.cpu.e2=5|(im2?2:0);run(t,'fullsummary_poll',20000);assert.equal(t.m.cpu.c2,1);assert.ok(t.seen.has(sym.load_return_after_af));record('all-load one-batch '+(im2?'IM2':'IM1')+' profile preserves RAM comparisons and returns count');}
{const t=machine({writeFault:(m,a,v)=>a===0x7a00?v^2:v});t.m.cpu.pc=sym.load_return_start;t.m.cpu.a2=12;t.m.cpu.e2=3;t.m.cpu.d2=9;t.m.cpu.h2=3;run(t,'fault_report');assert.ok(!t.seen.has(sym.load_return_foreground));record('IM2 table qualification mismatch prevents exposed transfer');}
{const t=machine({writeFault:(m,a,v)=>a>=0x4000?v^2:v});t.m.cpu.pc=sym.load_ram_begin;t.m.cpu.a2=2;t.m.cpu.i=0;run(t,'fault_report');record('lost RAM writes detected before healthy batch completion');}
{const t=slice(0xff);t.m.cpu.e2=128;t.m.bus.write=()=>{};t.keys[1]=30;run(t,'fullsummary_poll');t.keys.fill(31);frames(t);t.keys[2]=30;run(t,'menu_ready');record('lost UI writes cannot prevent cancellation/acknowledgement');}
fs.writeFileSync('build/load-verification.json',JSON.stringify({image_sha256:createHash('sha256').update(image).digest('hex'),result:'PASS',cases,
 limitations:['TSRun software/mapping models; physical supply, contention, refresh timing and thermal validation pending','Genuine interrupt returns/IM2 table faults can defeat software recovery; no claim of arbitrary saved-PC corruption survival']},null,2)+'\n');
