// Capture the rendered target menus (not host-generated previews).
import fs from 'node:fs';import path from 'node:path';import {pathToFileURL} from 'node:url';import assert from 'node:assert/strict';
const api=await import(pathToFileURL(path.resolve('../TSRun/machine.js'))),sym={};
for(const file of ['symbols.txt','load-symbols.txt'])Object.assign(sym,Object.fromEntries([...fs.readFileSync('build/'+file,'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)])));
const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));api.insertDock(m,fs.readFileSync('build/diagnostic-v02.dck'));api.resetMachine(m);m.portF4=1;m.portFF=64;m.cpu.iff1=false;
for(const [entry,stopLabel,name] of [['load_select','load_config_poll','load-config-active'],['load_loadwarning','load_warning_poll','load-warning-active'],['load_loadrun','load_notice_loop','load-running-active']]){
 m.cpu.pc=sym[entry];const r=m.bus.read,stop={};let hit=false;
 m.bus.read=a=>{if(a===m.cpu.pc&&a===sym[stopLabel]){hit=true;throw stop;}return r(a);};
 try{for(let i=0;i<100;i++)api.runFrame(m);}catch(e){if(e!==stop)throw e;}finally{m.bus.read=r;}
 assert.ok(hit);fs.writeFileSync('build/'+name+'.screen',m.ram.slice(0x4000,0x5b00));
}
