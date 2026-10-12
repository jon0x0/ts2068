import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {pathToFileURL,fileURLToPath} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js'))),cpuapi=await import(pathToFileURL(path.join(up,'z80.js')));
const cart=fs.readFileSync(path.join(root,'build/diagnostic-v02.dck'));
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)]));
Object.assign(sym,Object.fromEntries([...fs.readFileSync(path.join(root,'build/cpu-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)])));
const evidence=[];
function machine({irq=false,readFault=null,writeFault=null,ioFault=null}={}){
 const keys=new Uint8Array(8).fill(31),joy=new Uint8Array(2).fill(255),m=api.createMachine(keys,joy);
 m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));
 assert.equal(api.insertDock(m,cart),null);api.resetMachine(m);m.portF4=1;m.portFF=0x40;m.cpu.pc=sym.menu_draw;m.cpu.sp=0xbeef;m.cpu.iff1=false;m.ram.fill(0);
 const seen=new Set(),ports=[],r=m.bus.read,w=m.bus.write,io=m.bus.ioWrite,ir=m.bus.ioRead;
 m.bus.read=a=>{if(a===m.cpu.pc){seen.add(a);assert.ok(a<0x2000 || (a>=0x3f00&&a<0x3fd0&&(m.portF4&2)) || (a>=0x4000&&a<0x5fd0&&(m.portF4&4)) || (a>=0x8000&&a<0x8200) || (a>=0xc000&&a<0xc100),'opcode outside declared anchors');if(!irq)assert.equal(m.cpu.sp,0xbeef);}
 let v=r(a);return readFault?readFault(m,a,v):v;};
 m.bus.write=(a,v)=>{assert.ok(a>=0x4000 || (a>=0x2000 && (m.portF4&2)),`unexpected low-memory write ${a.toString(16)} pc ${m.cpu.pc.toString(16)}`);w(a,writeFault?writeFault(m,a,v):v);};
 m.bus.ioWrite=(p,v)=>{ports.push([p,v]);io(p,v);};m.bus.ioRead=p=>ioFault?ioFault(m,p,ir(p)):ir(p);
 return {m,keys,joy,seen,ports};
}
function frames(t,n){for(let i=0;i<n;i++)api.runFrame(t.m);}
function until(t,label,budget=2000){const a=sym[label];assert.ok(a!==undefined,label);for(let i=0;i<budget&&!t.seen.has(a);i++)api.runFrame(t.m);assert.ok(t.seen.has(a),`did not reach ${label}; pc=${t.m.cpu.pc.toString(16)}`);}
function enter(t,label){t.seen.clear();t.m.cpu.pc=sym[label];until(t,label.endsWith('_ready')?label:label.replace('load_','')+'_ready');frames(t,2);}
function record(name,details={}){evidence.push({name,result:'PASS',...details});console.log(name+': PASS');}
{const t=machine();until(t,'menu_poll');t.keys[6]&=~8;t.seen.clear();until(t,'inputs_ready');assert.ok(t.ports.some(([p,v])=>(p&255)===246&&v===63));record('main J opens joystick/EAR observation with AY port input-safe');}
{const t=machine();t.keys[6]&=~8;until(t,'menu_poll');frames(t,4);assert.ok(!t.seen.has(sym.inputs_ready));t.keys.fill(31);frames(t,2);t.keys[6]&=~8;t.seen.clear();until(t,'inputs_ready');record('held J quarantined; release/repress opens joystick entry');}
// Result dispatch and acknowledgement must not depend on a RAM stack.
{const t=machine();t.keys[2]&=~8;t.m.cpu.pc=sym.tests_done;t.m.cpu.i=34;until(t,'rampass_ready');frames(t,4);assert.ok(!t.seen.has(sym.menu_draw),'held startup R must not dismiss RAM pass');fs.writeFileSync(path.join(root,'build/ram-pass-active-v02.bin'),t.m.ram.slice(0x4000,0x5b00));t.keys.fill(31);frames(t,2);t.keys[1]&=~1;t.seen.clear();until(t,'menu_ready');record('complete RAM all-six-chip result and held-key quarantine/new-key return');}
{const t=machine();t.m.cpu.h2=1;t.m.cpu.pc=sym.tests_done;until(t,'fault_report');assert.ok(!t.seen.has(sym.rampass_ready));record('RAM mismatch never displays all-chip pass');}
// CPU tests execute from fixed ROM2, with a low-ROM all-HOME alias bridge.
{const t=machine();t.m.cpu.pc=sym.cpu_select;until(t,'cpu_start',1000);fs.writeFileSync(path.join(root,'build/cpu-guide-active-v02.bin'),t.m.ram.slice(0x4000,0x5b00));until(t,'cpu_pass',12000);assert.equal(t.m.cpu.sp,0xbeef);assert.ok(t.seen.has(sym.alias_next));record('Z80 five stages and all16 address-bit probes pass without stack');}
for(const [label,stage,alter] of [
 ['cpu_register_check',1,m=>m.cpu.b^=1],
 ['cpu_arithmetic_check',2,m=>m.cpu.f&=~1],
 ['cpu_shift_check',3,m=>m.cpu.b^=4],
 ['cpu_alternate_check',4,m=>m.cpu.b^=1],
 ['cpu_index_check',5,m=>m.cpu.xh^=1]]){
 let fired=false;const t=machine({readFault:(m,a,v)=>{if(a===m.cpu.pc&&a===sym[label]){alter(m);fired=true;}return v;}});
 t.m.cpu.pc=sym.cpu_select;until(t,'cpu_failed_poll',12000);assert.ok(fired);assert.equal(t.m.cpu.i,stage);assert.equal(t.m.cpu.e,stage);assert.equal(t.m.cpu.sp,0xbeef);
 assert.ok(t.ports.some(([p,v])=>(p&255)===254&&v===23));t.keys[7]&=~4;t.seen.clear();until(t,'menu_ready');record('Z80 stage'+stage+' injected fault reports and returns without stack');
}
for(let bit=0;bit<16;bit++){
 const mask=1<<bit;let fired=false;
 const t=machine({writeFault:(m,a,v)=>{if(m.portF4===1&&m.cpu.i>=16&&m.cpu.i<32&&a>=0x4000){const base=bit===14?0x8000:0x4000,pair=base^mask;if(a===pair){m.ram[base]=v;fired=true;}}return v;}});
 t.m.cpu.pc=sym.cpu_select;until(t,'cpu_failed_poll',12000);assert.ok(fired);assert.equal(t.m.cpu.i,16+bit);assert.equal(t.m.cpu.e,bit+1);assert.equal(t.m.portF4,5);record('address A'+bit+' alias localized with ROM recovery');
}
// Model data copies: compare full target planes, not only a menu checkpoint.
for(const [name,files,mode] of [['bars',['colorbar-pixels.bin','colorbar-attributes.bin'],0],['standard',['standard-pixels.bin','standard-attributes.bin'],0],['secondary',['secondary-pixels.bin','secondary-attributes.bin'],1],['ecm',['ecm-pixels.bin','ecm-attributes.bin'],2],['hires',['hires-primary.bin','hires-secondary.bin'],6],['mix128',['attribute-128-pixels.bin','attribute-128-attributes.bin'],0]]){
 const t=machine();t.m.cpu.pc=sym['load_'+name];until(t,'video_wait');
 const base=mode===1?0x6000:0x4000,ab=mode===1?0x7800:[2,6].includes(mode)?0x6000:0x5800;
 for(const [f,b] of [[files[0],base],[files[1],ab]]){const data=fs.readFileSync(path.join(root,'assets/video',f));assert.deepEqual(t.m.ram.slice(b,b+data.length),new Uint8Array(data));}
 assert.equal(t.m.portFF,0x40|mode);assert.equal(t.m.portF4,1);t.keys[7]&=~4;t.seen.clear();until(t,'menu_ready');assert.equal(t.m.portFF,0x40);record('video '+name+' exact planes + stop');
}
{const t=machine();until(t,'menu_poll');fs.writeFileSync(path.join(root,'build/menu-v02-screen.bin'),t.m.ram.slice(0x4000,0x5b00));t.keys[3]&=~4;frames(t,1);t.keys.fill(31);until(t,'videomenu_poll');assert.ok(!t.seen.has(sym.load_standard),'held 3 must not select submenu test');record('menu navigation and release gate');}
{const t=machine();t.m.cpu.pc=sym.load_keyboard;until(t,'keyboard_scan');t.keys[2]&=~2;frames(t,2);assert.equal(t.m.ram[0x5b0b],1);assert.equal(t.m.ram[0x5800+8*32+4],0x60);t.keys.fill(31);frames(t,2);assert.equal(t.m.ram[0x5800+8*32+4],0x68);t.keys[0]&=~1;t.keys[7]&=~1;t.seen.clear();until(t,'menu_ready');record('keyboard W press/release + BREAK exit');}
{const t=machine();t.m.cpu.pc=sym.load_bank;until(t,'bank_pass');frames(t,10);assert.ok((t.m.cpu.b2<<8|t.m.cpu.c2)>1);assert.ok(!t.seen.has(sym.bank_failure));t.keys[7]&=~4;t.seen.clear();until(t,'menu_ready');record('bank combinations / ROM write isolation / stop');}
{const t=machine({readFault:(m,a,v)=>a===0x9ff0&&(m.portF4&16)?v^1:v});t.m.cpu.pc=sym.load_bank;until(t,'fail_ready');assert.ok(t.seen.has(sym.bank_failure));assert.equal(t.m.portF4,1);until(t,'aux_fault_poll',500);assert.ok(t.ports.some(([p,v])=>(p&255)===0xfe&&v===23));t.keys[7]&=~4;t.seen.clear();until(t,'menu_ready',500);record('bank signature fault restores anchor, pulses class and stops');}
{const t=machine({writeFault:(m,a,v)=>{if(a===0x5ff0&&(m.portF4&4))m.ram[a]=0;return v;}});t.m.cpu.pc=sym.load_bank;until(t,'fail_ready');assert.ok(t.seen.has(sym.bank_failure));record('overlay leaking write detected');}
{const t=machine();t.m.cpu.pc=sym.ay_test;until(t,'aylisten_ready');until(t,'menu_ready');assert.ok(!t.seen.has(sym.ay_failure));assert.ok(t.ports.some(([p,v])=>(p&255)===0xf6&&v===15));assert.equal(t.m.ay.regs?.[8]??t.m.ay.registers?.[8]??0,0);record('AY masked readback and A/B/C playback exit');}
{const t=machine({ioFault:(m,p,v)=>(p&255)===0xf6?255:v});t.m.cpu.pc=sym.ay_test;until(t,'fail_ready');assert.ok(t.seen.has(sym.ay_failure));assert.equal(t.m.portF4,1);record('missing AY produces bounded failure');}
{const t=machine();t.m.cpu.pc=sym.load_beeper;until(t,'menu_ready');const high=t.ports.filter(([p,v])=>(p&255)===0xfe&&(v&16)).map(([,v])=>v&7);assert.deepEqual(high,[...Array(700).fill(2),...Array(700).fill(3),...Array(700).fill(4)]);for(const color of [2,3,4])assert.equal(t.ports.filter(([p,v])=>(p&255)===0xfe&&v===color).length,700);record('three beeper tones with red/magenta/green borders, matched high/low colors and silence');}
for(const [label,crc] of [['home_crc_select',0xbf44ec3f],['exrom_crc_select',0xae16233a]]){const t=machine();t.m.cpu.pc=sym[label];until(t,'romresult_ready');const measured=((t.m.cpu.b2<<24)|(t.m.cpu.c2<<16)|(t.m.cpu.d2<<8)|t.m.cpu.e2)>>>0;assert.equal(measured,crc);assert.equal(t.m.portFF,0x40);assert.equal(t.m.portF4,1);record(label+' stock CRC + mapping recovery',{crc32:measured.toString(16)});}
{const t=machine();t.m.homeRom[0x1234]^=1;t.m.cpu.pc=sym.home_crc_select;until(t,'romresult_ready');assert.notEqual(((t.m.cpu.b2<<24)|(t.m.cpu.c2<<16)|(t.m.cpu.d2<<8)|t.m.cpu.e2)>>>0,0xbf44ec3f);record('modified HOME identity detected');}
{const t=machine({writeFault:(m,a,v)=>a===0xc020?v^1:v});t.m.cpu.pc=sym.exrom_crc_select;until(t,'fail_ready');assert.ok(!t.seen.has(0xc000));record('EXROM gateway mismatch prevents execution');}
{const t=machine({readFault:(m,a,v)=>a===0x8010&&(m.portF4&16)?v^1:v});t.m.cpu.pc=sym.home_crc_select;until(t,'fail_ready');assert.ok(!t.seen.has(0x8020));record('high ROM code mismatch prevents execution');}
{const t=machine({irq:true});t.m.cpu.pc=sym.irq_start;until(t,'pass_ready');assert.equal(t.m.portFF,0x40);assert.equal(t.m.cpu.iff1,false);record('SCLD IRQ inhibit / arrival fixed checkpoint');}
{const t=machine({irq:true});const io=t.m.bus.ioWrite;t.m.bus.ioWrite=(p,v)=>io(p,(p&255)===0xff?v|0x40:v);t.m.cpu.pc=sym.irq_start;until(t,'fail_ready');assert.equal(t.m.cpu.iff1,false);record('missing IRQ times out');}
{const t=machine({irq:true});const io=t.m.bus.ioWrite;t.m.bus.ioWrite=(p,v)=>io(p,(p&255)===0xff?v&~0x40:v);t.m.cpu.pc=sym.irq_start;until(t,'fail_ready');assert.equal(t.m.cpu.iff1,false);record('failed inhibit produces bounded failure');}
for(const label of ['select_all','select_patterns','select_march','select_address','select_random','select_retention']){const t=machine();t.m.cpu.pc=sym[label];until(t,'ram_start');t.keys[7]&=~4;t.seen.clear();until(t,'menu_ready',100);record(label+' cancellation');}
{const t=machine();t.m.cpu.pc=sym.select_soak;until(t,'soak_pause',10000);assert.equal(t.m.cpu.c2,1);t.keys[7]&=~4;t.seen.clear();until(t,'soakstop_ready');frames(t,4);assert.ok(!t.seen.has(sym.menu_draw),'held stop key cannot dismiss summary');assert.equal(t.m.cpu.c2,1);fs.writeFileSync(path.join(root,'build/soak-stopped.screen'),t.m.ram.slice(0x4000,0x5b00));t.keys.fill(31);frames(t,2);t.keys[1]&=~1;t.seen.clear();until(t,'menu_ready');record('RAM soak pass counted, stopped summary and new-key return');}
{const t=machine({readFault:(m,a,v)=>a===0x8123&&!(m.portF4&16)?v^4:v});t.m.cpu.pc=sym.select_soak;until(t,'fault_report',10000);assert.equal(t.m.cpu.l2,4);frames(t,180);assert.ok(t.ports.some(([p,v])=>(p&255)===0xfe&&(v&16)));record('RAM soak failure latches and reports');}
{const menuAsset=JSON.parse(fs.readFileSync(path.join(root,'build/manifest-v02.json'))).assets.find(a=>a.name==='menu');let fired=false;const t=machine({readFault:(m,a,v)=>{if(a===parseInt(menuAsset.address,16)&&(m.portF4&(1<<menuAsset.bank))){fired=true;return 255;}return v;}});t.m.cpu.pc=sym.load_menu;until(t,'menu_ready');assert.ok(fired,'malformed UI packet must actually be injected');record('corrupt optional UI packet stays bounded');}

{const t=machine();t.m.cpu.pc=sym.select_full;until(t,'keyboard_ready',15000);for(const name of ['bank_pass','beeper_ready','aylisten_ready','video_bars_ready','video_standard_ready','video_secondary_ready','video_ecm_ready','video_hires_ready','video_mix128_ready'])assert.ok(t.seen.has(sym[name]),'full suite missing '+name);record('full digital and guided sequence reaches keyboard');}
{const t=machine({readFault:(m,a,v)=>a===0x4100&&!(m.portF4&4)?m.ram[0x4000]:v,writeFault:(m,a,v)=>{if(a===0x4100&&!(m.portF4&4)){m.ram[0x4000]=v;return m.ram[0x4100];}return v;}});t.m.cpu.pc=sym.select_address;until(t,'fault_report',2000);assert.ok(t.m.cpu.h2);assert.equal(t.m.cpu.e2,31);record('address alias identified without stack use');}
{const t=machine();t.m.dock[5][0x1234]^=1;t.m.cpu.pc=sym.entry;until(t,'cartridge_fault',500);assert.ok(!t.seen.has(sym.ram_start));assert.equal(t.m.portF4,1);frames(t,5);assert.ok(t.ports.some(([p,v])=>(p&255)===0xfe&&(v&16)));record('cartridge payload integrity fails before HOME testing');}
for(const chip of ['U6','U7'])for(let nibble=0;nibble<16;nibble++){
 const mask=chip==='U6'?15:240,forced=chip==='U6'?nibble:nibble<<4;
 const t=machine({readFault:(m,a,v)=>a>=0x4000&&a<0x8000&&!(m.portF4&(1<<(a>>13)))?(v&~mask)|forced:v,writeFault:(m,a,v)=>a>=0x4000&&a<0x8000&&!(m.portF4&(1<<(a>>13)))?(v&~mask)|forced:v});
 t.m.cpu.h2=mask;t.m.cpu.e2=2;t.m.cpu.xh=0x41;t.m.cpu.xl=0x23;t.m.cpu.pc=sym.fault_report;
 until(t,'report_class',300);assert.equal(t.m.cpu.d,chip==='U6'?1:2);assert.equal(t.m.cpu.sp,0xbeef);assert.equal((t.m.cpu.xh<<8)|t.m.cpu.xl,0x4123);
 const colors=[];for(let i=0x5800;i<0x5b00;i++){const a=t.m.ram[i];colors.push(chip==='U6'?(a>>3)&7:a&7);}assert.ok(new Set(colors).size>1,'fault glyph colors must remain distinct');
 if(nibble===0)fs.writeFileSync(path.join(root,'build/fault-'+chip+'-v02.bin'),t.m.ram.slice(0x4000,0x5b00));
}
record('degraded target renderer all32 stuck-nibble values',{cases:32});

{const t=machine({readFault:(m,a,v)=>m.cpu.i===32&&a===0x8123&&!(m.portF4&16)?v^4:v});t.m.cpu.pc=sym.select_random;until(t,'fault_report',2000);assert.equal(t.m.cpu.l2,4);assert.equal(t.m.cpu.e2,32);assert.equal((t.m.cpu.xh<<8)|t.m.cpu.xl,0x8123);record('16-bit random first mismatch stops without state cascade');}

{const t=machine({writeFault:(m,a,v)=>a>=0x4000&&a<0x8000&&!(m.portF4&(1<<(a>>13)))?v&240:v});t.m.cpu.h2=15;t.m.cpu.l2=15;t.m.cpu.e2=2;t.m.cpu.xh=0x41;t.m.cpu.xl=0x23;t.m.cpu.pc=sym.fault_report;const r=t.m.bus.read;let captured=false;t.m.bus.read=a=>{if(a===t.m.cpu.pc&&a===sym.report_class&&t.m.cpu.d===3)captured=true;return r(a);};for(let i=0;i<1000&&!captured;i++)api.runFrame(t.m);assert.ok(captured);const papers=new Set(t.m.ram.slice(0x5800,0x5b00).map(a=>(a>>3)&7));assert.ok(papers.size>1);assert.equal((t.m.cpu.xh<<8)|t.m.cpu.xl,0x4123);record('upper-chip report adapts to simultaneous U6 display fault');}

{const t=machine();t.m.ay.regs[7]=255;t.joy[0]=254;t.joy[1]=253;t.m.cpu.pc=sym.load_inputs;until(t,'input_pause');assert.equal(t.m.ay.regs[7],63);assert.ok(t.seen.has(sym.input_joy1)&&t.seen.has(sym.input_joy2));t.keys[7]&=~4;t.seen.clear();until(t,'menu_ready');record('EAR/joystick observation forces input-safe AY direction and stops');}

{const t=machine();t.keys[3]&=~2;until(t,'menu_poll');frames(t,2);assert.ok(!t.seen.has(sym.load_rammenu));t.keys[3]&=~8;until(t,'keyboard_ready');record('stuck numeric key quarantined; another menu choice works');}
{const t=machine();t.keys[6]&=~16;t.m.cpu.pc=sym.load_rommenu;until(t,'rommenu_poll');frames(t,2);assert.ok(!t.seen.has(sym.home_crc_select),'stuck H must not trigger exposed execution');record('stuck optional-test key does not trigger execution');}

{const t=machine({irq:true,writeFault:(m,a,v)=>0});t.m.cpu.pc=sym.irq_start;until(t,'pass_ready');assert.equal(t.m.portFF,0x40);assert.equal(t.m.cpu.iff1,false);assert.ok(t.ports.some(([p,v])=>(p&255)===0xfe&&v===4));record('IRQ checkpoint survives all HOME writes lost; green border confirms arrival');}
{const t=machine();t.m.cpu.h2=0;t.m.cpu.l2=15;t.m.cpu.e2=2;t.m.cpu.pc=sym.fault_report;until(t,'ram_stop_released',1500);t.keys[7]&=~4;t.seen.clear();until(t,'menu_ready',1500);record('RAM fault acknowledged with M; independent menu remains available');}

{const t=machine({ioFault:(m,p,v)=>(p&255)===0xfe?0:v});t.m.cpu.pc=sym.entry;until(t,'menu_ready',15000);assert.equal(t.m.cpu.h2|t.m.cpu.l2|t.m.cpu.d2,0);assert.ok(t.seen.has(sym.read_2));assert.ok(!t.seen.has(sym.read_3));record('all keyboard inputs stuck low cannot cancel the automatic quick baseline');}

{const t=machine({readFault:(m,a,v)=>a===sym.bank_masks?2:a===sym.bank_masks+18?255:v});t.m.cpu.pc=sym.load_bank;until(t,'bank_home_verify');frames(t,5);assert.ok(!t.seen.has(sym.bank_failure));assert.ok((t.m.cpu.b2<<8|t.m.cpu.c2)>1);record('bank mask corruption cannot remove anchor or extend table count');}
{const t=machine();t.keys[7]&=~4;t.m.cpu.pc=sym.select_full;until(t,'keyboard_ready',18000);assert.ok(t.seen.has(sym.aylisten_ready)&&t.seen.has(sym.video_mix128_ready));record('initially stuck M cannot cancel full digital and guided sequence');}

{const t=machine();t.m.cpu.h2=1;t.m.cpu.e2=2;t.m.cpu.xh=0x41;t.m.cpu.xl=0x23;t.m.cpu.pc=sym.fault_report;const io=t.m.bus.ioWrite,r=t.m.bus.read;let stop=false,previous=-1,edges=[];t.m.bus.ioWrite=(p,v)=>{if((p&255)===0xfe&&!stop){let color=v&7;if(color!==previous){edges.push(color);previous=color;}}io(p,v&~16);};t.m.bus.read=a=>{if(a===t.m.cpu.pc&&a===sym.report_restart_poll)stop=true;return r(a);};until(t,'report_restart_poll',1800);assert.deepEqual(edges,[7,0,7,0,7,0,7,0,7,0]);record('silent beeper still yields visible sync / class2 / chip1 / bit1 border envelopes');}
{const t=machine({ioFault:(m,p,v)=>(p&255)===254?v|4:v});t.m.cpu.pc=sym.select_patterns;until(t,'ram_start');t.keys[2]&=~1;t.seen.clear();until(t,'menu_ready',300);record('Q cancels RAM even when M input cannot close');}
{const t=machine();t.m.cpu.pc=sym.load_bars;until(t,'video_wait');frames(t,1);t.keys[1]&=~1;t.seen.clear();until(t,'menu_ready',300);record('A cancels video through guarded any-key poll');}
{const t=machine();t.m.cpu.pc=sym.load_keyboard;until(t,'keyboard_scan');t.keys[6]&=~1;t.keys[7]&=~1;t.seen.clear();until(t,'menu_ready',300);record('keyboard exits with ENTER + SPACE, no BREAK key needed');}
{const t=machine();t.m.cpu.pc=sym.result_wait;t.keys[2]&=~1;until(t,'menu_ready',300);record('result screen accepts Q rather than requiring M');}
{const t=machine();t.m.cpu.pc=sym.entry;until(t,'fill_1');t.keys[2]&=~1;t.seen.clear();until(t,'menu_ready',300);assert.ok(!t.seen.has(sym.read_2));record('new Q interrupts quick power-on RAM at a safe boundary');}
{const t=machine();t.m.cpu.pc=sym.entry;until(t,'menu_ready',1000);assert.ok(t.seen.has(sym.read_2));assert.ok(!t.seen.has(sym.read_3)&&!t.seen.has(sym.retention_read));record('power-on quick check excludes walking March random and retention');}
{const t=machine();t.keys[2]&=~8;t.m.cpu.pc=sym.entry;let phase=null;const r=t.m.bus.read;t.m.bus.read=a=>{if(a===t.m.cpu.pc&&a===sym.tests_done)phase=t.m.cpu.i;return r(a);};until(t,'rampass_ready',15000);assert.equal(phase,34);assert.ok(t.seen.has(sym.startupfull_ready)&&t.seen.has(sym.retention_read));record('held R selects extensive startup and held selection cannot cancel it');}
{const t=machine();t.keys[2]&=~8;t.m.cpu.pc=sym.entry;until(t,'fill_1');t.keys[2]=31;frames(t,2);t.keys[1]&=~1;t.seen.clear();until(t,'menu_ready',300);assert.ok(!t.seen.has(sym.retention_read));record('release R then A interrupts extensive startup safely');}
{const t=machine();t.keys[2]&=~8;t.keys[1]&=~1;t.m.cpu.pc=sym.entry;until(t,'menu_ready',1500);assert.ok(t.seen.has(sym.startupquick_ready));assert.ok(!t.seen.has(sym.retention_read));record('R with another held column is not a valid extensive startup request');}
{const t=machine();t.keys[2]&=~8;t.m.cpu.pc=sym.entry;until(t,'fill_1');t.m.cpu.h2=1;t.m.cpu.e2=1;t.m.cpu.pc=sym.fault_report;t.seen.clear();until(t,'report_restart_poll',1500);frames(t,400);assert.ok(!t.seen.has(sym.select_all));record('held startup R does not retrigger RAM fault retries');}
{const t=machine();t.m.cpu.pc=sym.select_all;until(t,'rampass_ready',15000);for(const color of [1,5,6,3,4,2])assert.ok(t.ports.some(([p,v])=>(p&255)===254&&v===color));record('complete RAM progress emits pattern walking March address random retention colors');}
{const t=machine();t.keys[1]&=~8;t.m.cpu.pc=sym.entry;until(t,'keyboard_ready',18000);for(const name of ['startupfull_ready','retention_read','bank_pass','aylisten_ready','video_mix128_ready'])assert.ok(t.seen.has(sym[name]));record('held F runs Full digital and guided startup, without cancelling on held F');}
{const t=machine();t.keys[1]&=~8;t.m.cpu.pc=sym.entry;until(t,'startup_notice');assert.deepEqual([...t.m.ram.slice(0x5901,0x591f)],new Array(30).fill(0x46));fs.writeFileSync(path.join(root,'build/startup-F-active-v02.bin'),t.m.ram.slice(0x4000,0x5b00));t.keys[1]=31;until(t,'fill_1');frames(t,2);t.keys[2]&=~1;t.seen.clear();until(t,'menu_ready',300);record('F startup highlighted and release then Q cancels');}
{const t=machine();t.keys[2]&=~8;t.m.cpu.pc=sym.entry;until(t,'startup_notice');assert.deepEqual([...t.m.ram.slice(0x58c1,0x58df)],new Array(30).fill(0x46));fs.writeFileSync(path.join(root,'build/startup-R-active-v02.bin'),t.m.ram.slice(0x4000,0x5b00));record('R startup highlights RAM-only selection');}
{const normal=machine();normal.m.cpu.pc=sym.load_menu;until(normal,'menu_ready');const t=machine();t.m.homeRom.fill(0);t.m.cpu.pc=sym.load_menu;until(t,'menu_ready');assert.deepEqual(t.m.ram.slice(0x4000,0x5b00),normal.m.ram.slice(0x4000,0x5b00));record('post-entry menu/font independent of all HOME ROM bytes; passive boot not implied');}
for(const [label,groups,sync] of [['sounddemo_ram',[2,6,2],true],['sounddemo_bank',[4],false],['sounddemo_cpu',[8,3],false]]){
 const t=machine({writeFault:(m,a,v)=>0});t.m.cpu.pc=sym.load_soundguide;until(t,'soundguide_poll');
 const r=t.m.bus.read,counts=[];t.m.bus.read=a=>{if(a===t.m.cpu.pc&&a===sym.pulse_group)counts.push(t.m.cpu.c);return r(a);};
 t.seen.clear();t.m.cpu.pc=sym[label];until(t,'soundguide_ready',2000);assert.deepEqual(counts,groups.flatMap(n=>Array.from({length:n},(_,i)=>n-i)));assert.equal(t.seen.has(sym.sync_tone),sync);assert.equal(t.m.cpu.sp,0xbeef);
 assert.ok(!t.seen.has(sym.fault_report)&&!t.seen.has(sym.report_restart_poll));record(label+' bounded training groups with all HOME writes lost');
}
{const t=machine();t.m.cpu.pc=sym.load_help;until(t,'help_poll');t.keys[0]&=~8;t.seen.clear();until(t,'soundguide_poll');t.keys.fill(31);frames(t,2);fs.writeFileSync(path.join(root,'build/fault-guide-active-v02.bin'),t.m.ram.slice(0x4000,0x5b00));t.keys[3]&=~1;t.seen.clear();until(t,'sounddemo_ram');t.keys.fill(31);until(t,'soundguide_ready');frames(t,3);t.keys[7]&=~4;t.seen.clear();until(t,'help_ready');record('Help C training / 1 RAM example / M Help operator path');}
{const t=machine();until(t,'menu_poll');t.keys[3]&=~1;t.seen.clear();until(t,'fullinfo_poll');frames(t,4);assert.ok(!t.seen.has(sym.select_full));fs.writeFileSync(path.join(root,'build/full-overview-active-v02.bin'),t.m.ram.slice(0x4000,0x5b00));t.keys.fill(31);frames(t,2);t.keys[3]&=~1;t.seen.clear();until(t,'keyboard_ready',18000);t.keys.fill(31);frames(t,2);t.keys[6]&=~1;t.keys[7]&=~1;t.seen.clear();until(t,'fullsummary_poll',1000);frames(t,4);assert.ok(!t.seen.has(sym.menu_draw),'held exit chord must not dismiss completion');fs.writeFileSync(path.join(root,'build/full-summary-active-v02.bin'),t.m.ram.slice(0x4000,0x5b00));t.keys.fill(31);frames(t,2);t.keys[2]&=~1;t.seen.clear();until(t,'menu_ready');record('Full overview guarded start, all stages, honest summary and held keyboard-chord quarantine');}
{const t=machine();t.m.cpu.pc=sym.load_fullinfo;until(t,'fullinfo_poll');t.keys[7]&=~4;t.seen.clear();until(t,'menu_ready');assert.ok(!t.seen.has(sym.select_full));record('Full overview M returns without running tests');}
{const t=machine();t.m.cpu.pc=sym.select_full;until(t,'fill_1');t.keys[2]&=~1;t.seen.clear();until(t,'menu_ready');assert.ok(!t.seen.has(sym.fullsummary_ready));record('cancelled Full does not show digital-matched completion');}
fs.writeFileSync(path.join(root,'build/suite-verification.json'),JSON.stringify({image_sha256:createHash('sha256').update(cart).digest('hex'),configuration:'TSRun stock TS2068; direct module entry plus explicit fault injections; separate native/RAM suite evidence',result:'PASS',cases:evidence,limitations:['No physical electrical/analog/timing validation','Direct entry does not validate every operator sequence','Passive startup fault limits remain']},null,2)+'\n');



