// Native Z80 display correctness and cycle benchmark (no host rendering).
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const api=await import(pathToFileURL(path.resolve('../../TSRun/machine.js')));
const {runZ80}=await import(pathToFileURL(path.resolve('../../TSRun/z80.js')));
const keys=new Uint8Array(8).fill(255);
const m=api.createMachine(keys,new Uint8Array(2).fill(255));
api.setHomeRom(m,fs.readFileSync('../../TSRun/roms/ts2068-0.rom'));
api.setExRom(m,fs.readFileSync('../../TSRun/roms/ts2068-1.rom'));
assert.equal(api.insertDock(m,fs.readFileSync('build/ts2068-cpm.dck')),null);
m.ram.set(fs.readFileSync('build/bios.bin'),0xe600);m.portF4=15;
const s=Object.fromEntries([...fs.readFileSync('build/bios.bin.sym','utf8').matchAll(/^(\w+): EQU 0x([\da-f]+)/gmi)].map(x=>[x[1],parseInt(x[2],16)]));
function call(name,c=0){
  m.cpu.pc=s[name];m.cpu.c=c;m.cpu.sp=0xfefe;
  m.bus.write(0xfefe,0);m.bus.write(0xfeff,0xf7);
  const clock={tstates:0};let n=0;
  while(m.cpu.pc!==0xf700&&n++<200000)runZ80(m.cpu,m.bus,1,clock);
  assert(n<200000);assert.equal(m.portF4,15);return clock.tstates;
}
function address(row,col,scan){return 0x4000+((col&1)<<13)+((row&24)<<8)+(scan<<8)+((row&7)<<5)+(col>>1);}
const timings={};
for(const top of s.scroll_top?[0,1]:[0]){
  for(let i=0x4000;i<0x7800;i++)m.ram[i]=(i*37+(i>>8)*13)&255;
  const before=Buffer.from(m.ram);
  m.bus.write(s.row,23);m.bus.write(s.col,0);if(s.scroll_top)m.bus.write(s.scroll_top,top);
  // A held key must still enter the FIFO while scrolling.
  m.bus.write(s.qhead,0);m.bus.write(s.qtail,0);m.bus.write(s.held,0);keys[1]&=~1;
  timings['scroll_top_'+top]=call('conout',10);keys.fill(255);
  assert.equal(m.bus.read(s.qhead),1);assert.equal(m.bus.read(s.keyqueue),65);
  for(let r=0;r<24;r++)for(let c=0;c<64;c++)for(let y=0;y<8;y++){
    const expected=r<top?before[address(r,c,y)]:r===23?0:before[address(r+1,c,y)];
    assert.equal(m.ram[address(r,c,y)],expected,`scroll ${top} row ${r} col ${c} scan ${y}`);
  }
  assert.deepEqual(Buffer.from(m.ram.slice(0x5800,0x6000)),before.subarray(0x5800,0x6000));
}
for(const r of [0,7,8,15,16,23])for(const c of [0,1,62,63]){
  call('cls');m.bus.write(s.row,r);m.bus.write(s.col,c);
  // Avoid last-cell autoscroll here; wrapping/scrolling is tested separately.
  if(r===23&&c===63)continue;
  const t=call('conout',65);timings.character=t;
  const glyph=fs.readFileSync('build/font.bin').subarray((65-32)*8,(65-31)*8);
  for(let y=0;y<8;y++)assert.equal(m.ram[address(r,c,y)],glyph[y]);
}
timings.clear=call('cls');
for(let r=0;r<24;r++)for(let c=0;c<64;c++)for(let y=0;y<8;y++)assert.equal(m.ram[address(r,c,y)],0);
fs.writeFileSync(process.argv[2]||'build/console-timing.json',JSON.stringify(timings,null,2)+'\n');
console.log(timings);
console.log('Both planes, third boundaries, status preservation, keyboard during scroll, glyphs and clear PASS');
