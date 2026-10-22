// Exercise native BIOS scanning, including a host Caps+0 event mid-scan.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const base=path.resolve('../../TSRun');
const api=await import(pathToFileURL(path.join(base,'machine.js')));
const {runZ80}=await import(pathToFileURL(path.join(base,'z80.js')));
const keys=new Uint8Array(8).fill(255);
const m=api.createMachine(keys,new Uint8Array(2).fill(255));
api.setHomeRom(m,fs.readFileSync(path.join(base,'roms/ts2068-0.rom')));
api.setExRom(m,fs.readFileSync(path.join(base,'roms/ts2068-1.rom')));
// Install the assembled BIOS directly: keyboard testing needs no disk hardware.
m.ram.set(fs.readFileSync('build/bios.bin'),0xe600);
m.portF4=0;
const syms=Object.fromEntries([...fs.readFileSync('build/bios.bin.sym','utf8').matchAll(/^(\w+): EQU 0x([\da-f]+)/gmi)].map(x=>[x[1],parseInt(x[2],16)]));
function poll(){
  m.cpu.pc=syms.keypoll;m.cpu.sp=0xfefe;
  m.bus.write(0xfefe,0);m.bus.write(0xfeff,0xf7);
  let n=0;while(m.cpu.pc!==0xf700&&n++<5000)runZ80(m.cpu,m.bus,1,m);
  assert(n<5000);
}
function reset(){keys.fill(255);for(const s of ['qhead','qtail','held'])m.bus.write(syms[s],0);}
function queued(){return Array.from({length:m.bus.read(syms.qhead)},(_,i)=>m.bus.read(syms.keyqueue+i));}
reset();keys[4]&=~1;poll();poll();assert.deepEqual(queued(),[48]);
reset();keys[0]&=~1;keys[4]&=~1;poll();poll();assert.deepEqual(queued(),[8]);
const original=m.bus.ioRead;
for(const port of [0xfdfe,0xfbfe,0xf7fe,0xeffe]){
  reset();let fired=false;
  m.bus.ioRead=p=>{if(!fired&&(p&65535)===port){keys[0]&=~1;keys[4]&=~1;fired=true;}return original(p);};
  poll();poll();assert(fired);assert.deepEqual(queued(),[8],`Caps+0 event at ${port.toString(16)}`);
  m.bus.ioRead=original;
}
reset();keys[0]&=~1;keys[0]&=~8;poll();assert.deepEqual(queued(),[3]);
console.log('Plain zero, Delete, mid-scan Delete, held-key suppression, Ctrl-C PASS');
