import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {PicoModel} from './tspico_model.mjs';
const base=path.resolve(process.argv[2]||'../../TSRun');
const api=await import(pathToFileURL(path.join(base,'machine.js')));
const disk=fs.readFileSync('build/drive-a.img');
const symbols=Object.fromEntries([...fs.readFileSync('build/bios.bin.sym','utf8').matchAll(/^(\w+): EQU 0x([\da-f]+)/gmi)].map(x=>[x[1],parseInt(x[2],16)]));
function machine(mode,physical=false){
  const keys=new Uint8Array(8).fill(255);const m=api.createMachine(keys,new Uint8Array(2).fill(255));
  api.setHomeRom(m,fs.readFileSync(path.join(base,'roms/ts2068-0.rom')));
  api.setExRom(m,fs.readFileSync(path.join(base,'roms/ts2068-1.rom')));
  assert.equal(api.insertDock(m,fs.readFileSync('build/ts2068-cpm.dck')),null);
  if(physical){m.exCart.fill(null);m.exCartRam.fill(false);m.dockRam.fill(true);}
  const pico=new PicoModel(disk,{mode,files:{'/CPM/NEW.COM':fs.readFileSync('build/hello.bin'),'/CPM/ALL.BIN':Buffer.from(Array.from({length:256},(_,i)=>i))}});
  const rd=m.bus.ioRead,wr=m.bus.ioWrite;
  m.bus.ioRead=p=>[14,15].includes(p&255)?pico.read(p):rd(p);
  m.bus.ioWrite=(p,v)=>{if([14,15].includes(p&255))pico.write(p,v);else wr(p,v);};
  let text='';const memwrite=m.bus.write;
  m.bus.write=(a,v)=>{if(a>=0xf800&&a<0xfe00&&m.cpu.pc>=symbols.conout&&m.cpu.pc<symbols.logok)text+=String.fromCharCode(v);memwrite(a,v);};
  const frames=n=>{for(let i=0;i<n;i++)api.runFrame(m);};
  const keymap=['\0ZXCV','ASDFG','QWERT','12345','09876','POIUY','\rLKJH',' \0MNB'];
  const sym={'.':'M','/':'V','=':'L'};
  function type(s){for(let c of s){if(sym[c]){keys[7]&=~2;c=sym[c];}let found=false;for(let r=0;r<8&&!found;r++){const bit=keymap[r].indexOf(c);if(bit>=0){keys[r]&=~(1<<bit);frames(4);keys.fill(255);frames(4);found=true;}}assert(found,c);}}
  function command(s,n=400){type(s+'\r');frames(n);}
  return {m,pico,frames,command,log:()=>text};
}
for(const mode of ['absent','legacy','busy','stale','badcrc']){
  const t=machine(mode);t.frames(400);assert.match(t.log(),/HELLO from a \.COM/);assert.equal(t.m.bus.read(symbols.storage_kind),0);
  if(mode!=='badcrc')assert.equal(t.pico.syncs,0,mode+' must not receive SYNC');
  if(['legacy','busy'].includes(mode))assert.equal(t.pico.writes.length,0);
}
const stock=machine('stock',true);stock.frames(500);
assert.equal(stock.m.bus.read(symbols.storage_kind),2);assert.match(stock.log(),/READ ONLY/);assert.match(stock.log(),/HELLO from a \.COM/);
const live=machine('service',true);live.frames(500);
assert.equal(live.m.bus.read(symbols.storage_kind),1);assert.match(live.log(),/TSPico SD image R\/W/);
live.command('PIP COPY.COM=HELLO.COM');live.command('COPY');assert.match(live.log(),/HELLO from a \.COM/);
live.command('ERA COPY.COM');
live.command('SUBMIT DEMO',2200);assert.match(live.log(),/Assembled on the TS2068!/);
fs.writeFileSync('build/tspico-service-transcript.txt',live.log());
// Import an ordinary raw SD file into emulator RAM disk with stock channels.
const importer=machine('absent');importer.frames(400);importer.pico.mode='stock';
importer.command('TPIMPORT /CPM/NEW.COM NEW.COM',800);
fs.writeFileSync('build/tspico-import-transcript.txt',importer.log());
assert.match(importer.log(),/Imported\./);importer.command('NEW');
assert.equal((importer.log().match(/HELLO from a \.COM/g)||[]).length,2);
importer.command('TPIMPORT /CPM/ALL.BIN ALL.BIN',800);
fs.writeFileSync('build/tspico-import-transcript.txt',importer.log());
assert.equal((importer.log().match(/Imported\./g)||[]).length,2);
const result=Buffer.concat(importer.m.exCart.slice(1,7).map(p=>Buffer.from(p)));
const slot=Array.from({length:64},(_,i)=>i*32).find(i=>result.subarray(i+1,i+12).toString()==='ALL     BIN');
assert.notEqual(slot,undefined);const block=result[slot+16];
assert.deepEqual(result.subarray(block*1024,block*1024+256),Buffer.from(Array.from({length:256},(_,i)=>i)));
importer.command('TPIMPORT /CPM/ALL.BIN ALL.BIN',800);assert.match(importer.log(),/Destination exists; no overwrite/);
console.log('TSPico models: absent/legacy/busy/stale fallback, SRAM-only read-only boot, binary-safe SD PIP + SUBMIT, raw SD import PASS');
