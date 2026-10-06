import fs from 'node:fs';import {pathToFileURL} from 'node:url';import path from 'node:path';
const api=await import(pathToFileURL(path.resolve('../../TSRun/machine.js')));
const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));
m.homeRom.set(fs.readFileSync('../../TSRun/roms/ts2068-0.rom'));m.exRom.set(fs.readFileSync('../../TSRun/roms/ts2068-1.rom'));
api.insertDock(m,fs.readFileSync('build/sinistar.dck'));api.resetMachine(m);
const symbols=Object.fromEntries([...fs.readFileSync('build/symbols.txt','utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const names=['go','no_speech','color_delta','draw_sprite','stars_update','frame_done'];
const watch=new Map(names.map(n=>[symbols[n],n]));const read=m.bus.read;const log=[];
m.bus.read=a=>{if(m.cpu.pc===a&&watch.has(a)&&m.ram[0x7814]===9&&m.ram[0x7815]===0)log.push({name:watch.get(a),t:m.tstates});return read(a);};
for(let i=0;i<700;i++)api.runFrame(m);
console.log(log.map((v,i)=>({...v,untilNext:log[i+1]?.t-v.t}))); 
console.log({pc:m.cpu.pc,sp:m.cpu.sp,hsr:m.portF4,frame:m.ram[0x7814],ticks:m.ram[0x7810]});


