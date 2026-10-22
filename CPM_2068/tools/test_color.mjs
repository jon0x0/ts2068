// Run COLOR through real CP/M and the native TS2068 keyboard/port model.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const api=await import(pathToFileURL(path.resolve('../../TSRun/machine.js')));
const keys=new Uint8Array(8).fill(255);
const m=api.createMachine(keys,new Uint8Array(2).fill(255));
api.setHomeRom(m,fs.readFileSync('../../TSRun/roms/ts2068-0.rom'));
api.setExRom(m,fs.readFileSync('../../TSRun/roms/ts2068-1.rom'));
assert.equal(api.insertDock(m,fs.readFileSync('build/ts2068-cpm.dck')),null);
const frames=n=>{for(let i=0;i<n;i++)api.runFrame(m);};
const map=['\0ZXCV','ASDFG','QWERT','12345','09876','POIUY','\rLKJH',' \0MNB'];
function type(s){for(const c of s){let found=false;for(let r=0;r<8;r++){const b=map[r].indexOf(c);if(b>=0){keys[r]&=~(1<<b);frames(4);keys.fill(255);frames(4);found=true;break;}}assert(found,c);}frames(90);}
function log(){return Buffer.from(m.ram.slice(0xf800,0xfe00)).toString('ascii').replaceAll('\0','');}
frames(300);assert.match(log(),/A>/);
type('COLOR\r');assert.match(log(),/Black on white/);assert.match(log(),/White on black/);assert.equal(m.portFF,62);
for(let n=0;n<8;n++){
  type('COLOR '+n+'\r');assert.equal(m.portFF,6+(n<<3));assert.equal(m.border,n^7);assert.equal(m.portF4,15);
  // DIR exercises disk reads and a normal command return, without resetting color.
  type('DIR\r');assert.equal(m.portFF,6+(n<<3));
}
for(const tail of ['8','07','1 8','1 2 3','1 22','   ']){type('COLOR '+tail+'\r');assert.equal(m.portFF,62);}
for(let border=0;border<8;border++){type('COLOR 7 '+border+'\r');assert.equal(m.portFF,62);assert.equal(m.border,border);}
type('COLOR 7\r');assert.equal(m.border,0);
type('COLOR   4   \r');assert.equal(m.portFF,38);
// CP/M warm boot must retain the selected colors.
keys[0]&=~1;keys[0]&=~8;frames(4);keys.fill(255);frames(90);
assert.equal(m.portFF,38);assert.match(log(),/A>/);
console.log('COLOR help, all eight schemes, invalid/trailing arguments, disk access and warm boot PASS');
