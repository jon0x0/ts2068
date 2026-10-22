// Exercise actual Z80 backend calls across all six banks, then stock utilities.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const base=path.resolve(process.argv[2]||'../../TSRun');
const api=await import(pathToFileURL(path.join(base,'machine.js')));
const {runZ80}=await import(pathToFileURL(path.join(base,'z80.js')));
const keys=new Uint8Array(8).fill(255);
const m=api.createMachine(keys,new Uint8Array(2).fill(255));
api.setHomeRom(m,fs.readFileSync(path.join(base,'roms/ts2068-0.rom')));
api.setExRom(m,fs.readFileSync(path.join(base,'roms/ts2068-1.rom')));
assert.equal(api.insertDock(m,fs.readFileSync('build/ts2068-cpm.dck')),null);
const frames=n=>{for(let i=0;i<n;i++)api.runFrame(m);};frames(300);
const symbols=Object.fromEntries([...fs.readFileSync('build/bios.bin.sym','utf8').matchAll(/^(\w+): EQU 0x([\da-f]+)/gmi)].map(x=>[x[1],parseInt(x[2],16)]));
const disk=fs.readFileSync('build/drive-a.img');
const saved={...m.cpu};
function call(label,lba){
    m.cpu.pc=symbols[label];m.cpu.h=lba>>8;m.cpu.l=lba&255;m.cpu.c=0;m.cpu.sp=0xfefe;
    m.bus.write(0xfefe,0);m.bus.write(0xfeff,0xf7);
    let count=0;while(m.cpu.pc!==0xf700&&count++<10000)runZ80(m.cpu,m.bus,1,m);
    assert(count<10000,`hung ${label} ${lba}`);
    assert.equal(m.portF4,15);assert.equal(m.portFF,62);
    return m.cpu.a;
}
const bounce=symbols.bounce;
for(let lba=0;lba<384;lba++){
    assert.equal(call('block_read',lba),0);
    assert.deepEqual(Buffer.from(Array.from({length:128},(_,i)=>m.bus.read(bounce+i))),disk.subarray(lba*128,lba*128+128),`read LBA ${lba}`);
}
for(const lba of [0,63,64,127,128,191,192,255,256,319,320,383]){
    const pattern=Buffer.from(Array.from({length:128},(_,i)=>(lba+i*17)&255));
    pattern.forEach((v,i)=>m.bus.write(bounce+i,v));assert.equal(call('block_write',lba),0);
    assert.equal(call('block_read',lba),0);
    assert.deepEqual(Buffer.from(Array.from({length:128},(_,i)=>m.bus.read(bounce+i))),pattern);
    disk.subarray(lba*128,lba*128+128).forEach((v,i)=>m.bus.write(bounce+i,v));
    assert.equal(call('block_write',lba),0);
}
assert.equal(call('block_read',384),1);assert.equal(call('block_write',65535),1);
Object.assign(m.cpu,saved);
m.frameStart=m.tstates;
// Observe bytes written by the Z80 console routine in chronological order.
let transcript='';const write=m.bus.write;
m.bus.write=(a,v)=>{if(a>=0xf800&&a<0xfe00)transcript+=String.fromCharCode(v);write(a,v);};
const keymap=['\0ZXCV','ASDFG','QWERT','12345','09876','POIUY','\rLKJH',' \0MNB'];
const symbolsKey={'.':'M','=':'L'};
function type(s){for(let c of s){if(symbolsKey[c]){keys[7]&=~2;c=symbolsKey[c];}let found=false;for(let r=0;r<8&&!found;r++){let b=keymap[r].indexOf(c);if(b>=0){keys[r]&=~(1<<b);frames(4);keys.fill(255);frames(4);found=true;}}assert(found,c);}}
function command(s,wait=400){type(s+'\r');frames(wait);}
command('STAT');
const freeKiB=JSON.parse(fs.readFileSync('build/manifest.json')).disk_free_bytes/1024;
assert(transcript.includes(`Space: ${freeKiB}k`),transcript);
command('PIP COPY.COM=HELLO.COM');command('COPY');assert.match(transcript,/HELLO from a \.COM/);
command('ERA COPY.COM');
command('SUBMIT DEMO',1800);
fs.writeFileSync('build/tsrun-utilities-transcript.txt',transcript);
console.log(transcript);
assert.match(transcript,/Assembled on the TS2068!/);
assert.doesNotMatch(transcript,/DISK FULL|NO SPACE|Bdos Err|READ ERROR|WRITE ERROR/);
fs.writeFileSync('build/tsrun-utilities-drive.img',Buffer.concat(m.exCart.slice(1,7).map(p=>Buffer.from(p))));
fs.writeFileSync('build/tsrun-utilities-screen.bin',m.ram);
console.log('All 384 sectors, six bank boundaries, PIP copy and SUBMIT/ASM/LOAD execution PASS');
