// Cold reset with no DOCK inserted and deliberately absent EXROM.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const up=path.resolve('../TSRun'),api=await import(pathToFileURL(path.join(up,'machine.js')));
const rom=fs.readFileSync('build/home/diagnostic-home-u16.bin');assert.equal(rom.length,16384);
const sym=Object.fromEntries([...fs.readFileSync('build/home/symbols.txt','utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)]));
const cases=[];
function machine({fault=null,heldR=false,irq=false}={}){
 const keys=new Uint8Array(8).fill(31),m=api.createMachine(keys,new Uint8Array(2).fill(255));m.homeRom.set(rom);m.exRom.fill(255);api.resetMachine(m);m.cpu.sp=0xbeef;m.ram.fill(0xa7);if(heldR)keys[2]&=~8;
 const r=m.bus.read,w=m.bus.write,io=m.bus.ioWrite,seen=new Set(),ports=[];let entered=false;
 m.bus.read=a=>{if(a===m.cpu.pc){seen.add(a);assert.ok(a<0x4000,'HOME ROM opcode anchor');if(!irq)assert.equal(m.cpu.sp,0xbeef);if(a===sym.entry)entered=true;}let v=r(a);if(fault&&entered&&a>=fault.region&&a<fault.region+16384)v&=~(1<<fault.bit);return v;};
 m.bus.write=(a,v)=>{assert.ok(a>=0x4000,'no ROM writes');w(a,v);};
 m.bus.ioWrite=(p,v)=>{ports.push([p&255,v]);if((p&255)===244)assert.equal(v,0,'HOME never overlays active code/targets');io(p,v);};return {m,keys,seen,ports};
}
function until(t,label,budget=2000){for(let i=0;i<budget&&!t.seen.has(sym[label]);i++)api.runFrame(t.m);assert.ok(t.seen.has(sym[label]),label+' timeout PC='+t.m.cpu.pc.toString(16));}
function record(name){cases.push({name,result:'PASS'});console.log(name+': PASS');}
{const t=machine();until(t,'menu_ready');assert.ok(t.seen.has(sym.boot_shift_check)&&t.seen.has(sym.home_sum));fs.writeFileSync('build/home/menu.actual.screen',t.m.ram.slice(0x4000,0x5b00));record('PC0 reset, no DOCK/EXROM, dirty RAM, no stack, quick CPU/RAM/address checks');}
{const t=machine({heldR:true});until(t,'rampass_ready',15000);assert.ok(t.seen.has(sym.retention_read));for(let i=0;i<3;i++)api.runFrame(t.m);assert.ok(!t.seen.has(sym.menu_draw));t.keys.fill(31);for(let i=0;i<2;i++)api.runFrame(t.m);t.keys[1]&=~1;t.seen.clear();until(t,'menu_ready');record('heldR cold reset completeRAM and guarded pass acknowledgement');}
for(const region of [0x4000,0x8000,0xc000])for(const bit of [0,3,4,7]){
 const t=machine({fault:{region,bit}});until(t,'report_class');assert.equal(t.m.cpu.d,(region-0x4000)/8192+(bit<4?1:2));assert.equal(t.m.cpu.e,bit%4+1);assert.ok(t.ports.some(([p,v])=>p===254&&v===23));record('cold reset stuck HOME'+region.toString(16)+' D'+bit+' chip/bit code');
}
{const t=machine();t.m.homeRom[0x2100]^=1;until(t,'cartridge_alarm_poll');assert.ok(!t.seen.has(sym.ram_start));record('HOME image integrity mismatch reports before RAM use');}
{const t=machine();t.m.ram.fill(0);t.m.bus.write=()=>{};until(t,'report_class');assert.equal(t.m.cpu.d,1);assert.equal(t.m.cpu.e,5);record('cold reset with every HOME RAM write lost still reports chip1/multiple bits');}
{const t=machine();t.m.cpu.pc=sym.load_bank;until(t,'unavailable_ready');assert.ok(!t.seen.has(sym.beeper_ready));record('unsupported standalone bank selection shows unavailable rather than entering RAM');}
{const t=machine();until(t,'menu_poll');t.keys[6]&=~8;t.seen.clear();until(t,'inputs_ready');assert.ok(t.ports.some(([p,v])=>p===246&&v===63));record('main J opens input-safe joystick/EAR observer');}
for(const name of ['fullinfo','fullsummary','rammenu','rampass','beeper','keyboard','inputs']){
 const t=machine();t.m.cpu.pc=sym['load_'+name];const read=t.m.bus.read,stop={};let done=false;t.m.bus.read=a=>{if(a===t.m.cpu.pc&&a===sym[name+'_ready']){done=true;throw stop;}return read(a);};try{for(let i=0;i<100;i++)api.runFrame(t.m);}catch(e){if(e!==stop)throw e;}
 assert.ok(done);assert.deepEqual(Buffer.from(t.m.ram.slice(0x4000,0x5b00)),fs.readFileSync('build/home/'+name+'.screen'));record('HOME packed '+name+' screen');
}
{const t=machine();t.m.cpu.pc=sym.select_full;until(t,'keyboard_ready',16000);assert.ok(t.seen.has(sym.retention_read)&&t.seen.has(sym.aylisten_ready));assert.ok(!t.seen.has(sym.bank_ready));t.keys[6]&=~1;t.keys[7]&=~1;t.seen.clear();until(t,'fullsummary_ready',2000);record('HOME Full completes RAM/beeper/AY then keyboard and honest HOME summary');}
{const t=machine({irq:true});t.m.cpu.pc=sym.irq_start;until(t,'pass_ready');assert.ok(t.m.cpu.sp>=0xbffb&&t.m.cpu.sp<=0xbfff);record('HOME fixed-vector IRQ inhibit/arrival without stack reads');}
fs.writeFileSync('build/home/verification.json',JSON.stringify({image_sha256:createHash('sha256').update(rom).digest('hex'),result:'PASS',configuration:'TSRun HOME ROM replaced; no DOCK; EXROM FF; PC0 reset and dirty RAM',cases,limitations:['Electrical ROM/socket adapter and cold hardware boot not physically verified','Localized HOME data faults; global opcode/address/control-bus failure may prevent execution','SCLD HOME mapping/reset/opcode paths required']},null,2)+'\n');
