import {acceptTitle} from './accept_title.mjs';import fs from 'node:fs';import path from 'node:path';import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../../TSRun'),api=await import(pathToFileURL(path.join(up,'machine.js')));
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const results=[];
for(const fast of [false,true]){
 const keys=new Uint8Array(8).fill(31),m=api.createMachine(keys,new Uint8Array(2).fill(255));m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));api.insertDock(m,fs.readFileSync(path.join(root,'build/sinistar-mining.dck')));api.resetMachine(m);acceptTitle(m,sym);
 const put=(a,v)=>{m.ram[a]=v;m.ram[a+1]=v>>8;};let init=false,frame=0;const pictures=[],hist={};let zeroAt=null;
 const read=m.bus.read;m.bus.read=a=>{if(a===m.cpu.pc){
 if(a===sym.game_step){if(!init){init=true;put(sym.face_x,210*256);put(sym.face_y,100*256);for(const [n,v] of Object.entries({speech_started:1,sinistar_built:1,awake_done:1,assembly_count:20}))m.ram[sym[n]]=v;keys[5]&=~1;if(fast)keys[1]&=~8;}
 for(const [n,v] of Object.entries({worker_alive:0,worker_delay:255,crystal_alive:0,bullet_alive:0,bs_active:0,invulnerable:255,game_status:0}))m.ram[sym[n]]=v;}
 if(a===sym.frame_done&&frame>=120){let n=m.ram[sym.rects+2]?1:0;for(let p=0xbc82;p<0xbd19;p+=9)if(m.ram[p])n++;hist[n]=(hist[n]||0)+1;pictures.push({frame,time:m.tstates,rocks:n});if(fast&&m.ram[0x5bb2]&&Array.from(m.ram.slice(0x5bb4,0x5bc6)).every(n=>n)&&zeroAt===null)zeroAt=frame;}
 }return read(a);};
 for(frame=0;frame<1800;frame++){if(frame===120)keys[1]|=8;api.runFrame(m);}
 const rates=[{name:'whole measured interval',start:120,end:1800},{name:'last ten seconds',start:1200,end:1800}].map(w=>{const p=pictures.filter(p=>p.frame>=w.start&&p.frame<w.end);return {...w,pictures:p.length,fps:(p.length-1)*3528000/(p.at(-1).time-p[0].time)};});
 results.push({fast,enabled:m.ram[0x5bb1],active:m.ram[0x5bb2],retired: Array.from(m.ram.slice(0x5bb4,0x5bc6)).filter(n=>n).length,allRetiredAtRefresh:zeroAt,visibleHistogram:hist,rates});
}
const report={dck_sha256:createHash('sha256').update(fs.readFileSync(path.join(root,'build/sinistar-mining.dck'))).digest('hex'),conditions:'Same native world and continuous right input, active Sinistar, invulnerable fixture, no worker/shooting/audio; fast mode toggled using F. First 120 refreshes excluded. World movement is not repositioned.',results};fs.writeFileSync(path.join(root,'build/fast-mode-profile.json'),JSON.stringify(report,null,2));console.log(report);
