// Actual ROM0 boot execution; injections start after passive cartridge entry.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=process.cwd(),up=path.resolve(root,'../TSRun'),api=await import(pathToFileURL(path.join(up,'machine.js')));
const cart=fs.readFileSync('build/diagnostic-v02.dck'),sym=Object.fromEntries([...fs.readFileSync('build/symbols.txt','utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)]));
const cases=[];
function machine(inject={}){
 const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));
 m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));assert.equal(api.insertDock(m,cart),null);api.resetMachine(m);m.portF4=1;m.portFF=64;m.cpu.pc=sym.entry;m.cpu.sp=0xbeef;
 const r=m.bus.read,w=m.bus.write,io=m.bus.ioWrite,t={m,seen:new Set(),pulses:[],ports:[],writes:0};
 m.bus.read=a=>{if(a===m.cpu.pc){t.seen.add(a);assert.ok(a<0x2000,'boot opcodes must stay ROM0');assert.equal(m.cpu.sp,0xbeef);if(a===sym.pulse_group)t.pulses.push(m.cpu.c);inject.opcode?.(m,a);}
 let v=r(a);return inject.read?inject.read(m,a,v):v;};
 m.bus.write=(a,v)=>{t.writes++;if(inject.write)inject.write(m,a,v,w);else w(a,v);};
 m.bus.ioWrite=(p,v)=>{t.ports.push([p&255,v]);io(p,v);};return t;
}
function until(t,label,budget=2000){for(let n=0;n<budget&&!t.seen.has(sym[label]);n++)api.runFrame(t.m);assert.ok(t.seen.has(sym[label]),label+' pc='+t.m.cpu.pc.toString(16)+' i='+t.m.cpu.i+' e='+t.m.cpu.e+' iy='+((t.m.cpu.yh<<8)|t.m.cpu.yl)+' pulse='+t.pulses.slice(0,20));}
function record(name,t,detail={}){cases.push({name,result:'PASS',...detail});console.log(name+': PASS');}
{const t=machine();until(t,'menu_ready');assert.ok(t.seen.has(sym.boot_shift_check)&&t.seen.has(sym.boot_alias_compare));record('default boot register/math/shift and16 qualified opposing address pairs',t);}
for(const [label,stage,change] of [['boot_register_check',1,m=>m.cpu.b^=1],['boot_math_check',2,m=>m.cpu.f&=~1],['boot_shift_check',3,m=>m.cpu.b^=4]]){
 let fired=false;const t=machine({opcode:(m,a)=>{if(a===sym[label]&&!fired){change(m);fired=true;}}});until(t,'boot_fault_repeat',4000);assert.equal(t.m.cpu.e,stage);assert.equal(t.m.cpu.i,8);assert.equal(t.writes,0);assert.ok(t.ports.some(([p,v])=>p===254&&v===23));assert.ok(!t.seen.has(sym.cartridge_check));record('CPU boot stage'+stage+' mismatch repeats8/'+stage+' before any HOME writes',t);
}
for(let bit=0;bit<16;bit++){
 const base=bit===14?0x8000:0x4000,pair=base^(1<<bit);let fired=false;
 const t=machine({read:(m,a,v)=>m.cpu.i===48+bit&&a===pair?m.ram[base]:v,write:(m,a,v,w)=>{if(m.cpu.i===48+bit&&a===pair){a=base;fired=true;}w(a,v);}});
 until(t,'boot_fault_repeat',4000);assert.ok(fired);assert.equal(t.m.cpu.i,9);assert.equal(t.m.cpu.e,bit+1);assert.ok(!t.seen.has(sym.menu_ready));record('post-entry HOME address-pair A'+bit+' alias repeats9/'+(bit+1),t,{scope:'pair alias during boot probe; ROM/I/O fetch healthy'});
}
for(const [bit,value] of [[0,0x54],[3,0x5d],[4,0x45],[7,0xd5]]){
 let fired=false;const t=machine({read:(m,a,v)=>{if(m.cpu.i===48&&a===0x4000&&m.cpu.pc!==a&&!fired){fired=true;return value;}return v;}});
 until(t,'fault_report');assert.ok(fired);assert.equal(t.m.cpu.h2,1<<bit);assert.equal(t.m.cpu.b2,0x55);assert.equal(t.m.cpu.c2,value);assert.ok(!t.seen.has(sym.boot_fault_repeat));record('pair qualifier D'+bit+' mismatch uses RAM chip classifier rather than address code',t);
}
{const t=machine({write:(m,a,v,w)=>{if(m.cpu.i>=48&&m.cpu.i<64)w(a,v&~1);else w(a,v);}});until(t,'fault_report');assert.ok(!t.seen.has(sym.boot_alias_compare));record('new late data-write failure caught before alias attribution',t);}
for(const [a,b] of [[0,1],[3,4]]){
 const mask=(1<<a)|(1<<b);const t=machine({read:(m,address,v)=>address>=0x4000&&!(m.portF4&(1<<(address>>13)))&&(v&mask)!==mask?v&~mask:v});
 until(t,'fault_report');assert.ok(t.seen.has(sym.boot_pair_qualify),'bridge must pass uniform00/FF before failing mixed pattern');assert.ok(!t.seen.has(sym.boot_alias_compare));record('HOME data D'+a+'/D'+b+' dominant-AND bridge passes00/FF and fails boot55/AA qualifier',t,{scope:'HOME read data path; opcode/I/O path healthy'});
}
fs.writeFileSync('build/boot-verification.json',JSON.stringify({result:'PASS',image_sha256:createHash('sha256').update(cart).digest('hex'),cases,limitations:['Faults injected after passive entry; not proof of HOME bootstrap survival','CPU injections alter selected internal results, not physical transistor faults','Address cases model localized HOME aliases with healthy ROM/I/O, not universal global stuck lines','No physical electrical/thermal validation']},null,2)+'\n');



