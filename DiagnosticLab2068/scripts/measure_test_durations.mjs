// Instruction-budget estimates for the exact assembled image, not wall-clock benchmarks.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
const cart=fs.readFileSync(path.join(root,'build/diagnostic-v02.dck'));
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)]));
const labels=['ram_start','tests_done','rampass_ready','bank_pass','beeper_ready','aylisten_ready','video_bars_ready','video_standard_ready','video_secondary_ready','video_ecm_ready','video_hires_ready','video_mix128_ready','keyboard_ready','fullsummary_ready','menu_ready'];
labels.push('pass_ready');
const watched=new Map();
for(const label of labels)watched.set(sym[label],[...(watched.get(sym[label])||[]),label]);
const cases=[];
for(const entry of ['select_all','select_patterns','select_march','select_address','select_random','select_retention','select_full']){
 const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));
 m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));
 assert.equal(api.insertDock(m,cart),null);api.resetMachine(m);
 m.portF4=1;m.portFF=0x40;m.cpu.pc=sym[entry];m.cpu.iff1=false;m.cpu.sp=0xbeef;
 const hits={},read=m.bus.read;let frames=0;
 m.bus.read=a=>{if(a===m.cpu.pc){for(const label of watched.get(a)||[])if(hits[label]===undefined)hits[label]=frames;}return read(a);};
 const end=entry==='select_full'?'fullsummary_ready':entry==='select_all'?'rampass_ready':'pass_ready';
 while(hits[end]===undefined&&frames<100000){api.runFrame(m);frames++;}
 assert.notEqual(hits[end],undefined,entry+' timeout');
 const record={entry,frames,seconds_at_60_hz:frames/60,seconds_at_model_clock:frames*api.tStatesPerFrame/api.cpuHz,checkpoints_frames:hits};cases.push(record);console.log(JSON.stringify(record));
}
fs.writeFileSync(path.join(root,'build/test-duration-estimates.json'),JSON.stringify({image_sha256:createHash('sha256').update(cart).digest('hex'),engine_sha256:createHash('sha256').update(fs.readFileSync(path.join(up,'machine.js'))).digest('hex'),cpu_sha256:createHash('sha256').update(fs.readFileSync(path.join(up,'z80.js'))).digest('hex'),result:'PASS',configuration:'TSRun model; direct menu selection; healthy RAM; no keys; 58688 T-states/frame at 3528000Hz; also reported at nominal60Hz',limitations:['Model estimates, not measured physical durations','Full includes finite keyboard timeout; user exit can shorten it','Faults and cancellation change duration; emulator host speed is irrelevant'],cases},null,2)+'\n');
