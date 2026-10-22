import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const base=path.resolve(process.argv[2] || '../../TSRun');
const api=await import(pathToFileURL(path.join(base,'machine.js')));
const keys=new Uint8Array(8).fill(255);
const m=api.createMachine(keys,new Uint8Array(2).fill(255));
api.setHomeRom(m,fs.readFileSync(path.join(base,'roms/ts2068-0.rom')));
api.setExRom(m,fs.readFileSync(path.join(base,'roms/ts2068-1.rom')));
assert.equal(api.insertDock(m,fs.readFileSync('build/ts2068-cpm.dck')),null);
function frames(n){for(let i=0;i<n;i++)api.runFrame(m);}
function log(){return Buffer.from(Array.from({length:0x600},(_,i)=>m.bus.read(0xf800+i))).toString('ascii').replaceAll('\0','');}
frames(300);
console.log({pc:m.cpu.pc.toString(16),f4:m.portF4,ff:m.portFF,log:log()});
fs.writeFileSync('build/tsrun-screen.bin',m.ram);
assert.match(log(),/HELLO from a .COM/);
assert.match(log(),/A>/);
assert.equal(m.portFF & 7,6);
assert.equal(m.portF4,15);
// Type through the physical keyboard matrix, never inject CONIN data.
const keymap=['\0ZXCV','ASDFG','QWERT','12345','09876','POIUY','\rLKJH',' \0MNB'];
function type(s){for(let c of s){const symbol=c==='.';if(symbol){keys[7]&=~2;c='M';}let done=false;for(let r=0;r<8&&!done;r++){let bit=keymap[r].indexOf(c);if(bit>=0){keys[r]&=~(1<<bit);frames(4);keys.fill(255);frames(4);done=true;}}assert(done,`unmapped ${c}`);}}
type('DIR\r');frames(60);
assert.match(log(),/README/);
type('TYPE README.TXT\r');frames(300);
assert.match(log(),/RAM disk is volatile/);
type('HELLO\r');frames(120);
type('SAVE 1 COPY.COM\r');frames(120);
type('DIR\r');frames(60);
assert.match(log(),/COPY/);
type('MEMTEST\r');frames(60);
assert.match(log(),/Screen shadow RAM PASS/);
// Exercise scrolling in both display planes, then a true CP/M warm boot.
for(let i=0;i<4;i++){type('DIR\r');frames(160);}
keys[0]&=~1;frames(2);keys[0]&=~8;frames(4);keys.fill(255);frames(30);
const hellosBefore=(log().match(/HELLO from a \.COM/g)||[]).length;
type('COPY\r');frames(30);
assert.equal((log().match(/HELLO from a \.COM/g)||[]).length,hellosBefore+1);
assert.doesNotMatch(log(),/Screen shadow RAM FAIL|IR\?/);
assert.equal(m.portF4,15);
assert.equal(m.portFF,62);
// Successive different keys without an all-released interval used to be lost.
const beforeRollover=(log().match(/HELLO from a \.COM/g)||[]).length;
let previous='';
for(const c of 'HELLO\r'){
    if(c===previous){keys.fill(255);frames(3);}
    keys.fill(255);
    for(let r=0;r<8;r++){const bit=keymap[r].indexOf(c);if(bit>=0){keys[r]&=~(1<<bit);break;}}
    frames(3);previous=c;
}
keys.fill(255);frames(90);
assert.equal((log().match(/HELLO from a \.COM/g)||[]).length,beforeRollover+1);
fs.writeFileSync('build/tsrun-transcript.txt',log());
fs.writeFileSync('build/tsrun-scrolled-screen.bin',m.ram);
fs.writeFileSync('build/tsrun-drive-a-after.img',Buffer.concat(m.exCart.slice(1,7).map(p=>Buffer.from(p))));
console.log(log());
console.log('TSRun native boot, HELLO, keyboard, directory, read and write PASS');
