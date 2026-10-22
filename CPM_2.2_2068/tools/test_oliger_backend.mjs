// Functional WD register model: validates Z80 translation/errors, not FDC timing.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const base=path.resolve(process.argv[2]||'../../TSRun');
const api=await import(pathToFileURL(path.join(base,'machine.js')));
const {runZ80}=await import(pathToFileURL(path.join(base,'z80.js')));
const m=api.createMachine(new Uint8Array(8).fill(255),new Uint8Array(2).fill(255));
api.setHomeRom(m,fs.readFileSync(path.join(base,'roms/ts2068-0.rom')));
api.setExRom(m,fs.readFileSync(path.join(base,'roms/ts2068-1.rom')));
assert.equal(api.insertDock(m,fs.readFileSync('build/ts2068-cpm.dck')),null);
const disk=Buffer.from(fs.readFileSync('build/drive-a.img'));
const sides=JSON.parse(fs.readFileSync('build/manifest.json')).sides||1;
const records=disk.length/128;
let head=0,status=0,track=0,sector=1,index=0,offset=0,writing=false,protectedDisk=false,missing=false,short=false;
let reads=0,writes=0,crc=false;
const rd=m.bus.ioRead,wr=m.bus.ioWrite;
m.bus.ioRead=p=>{
  switch(p&255){
    case 0x8f:return status;
    case 0x9f:return track;
    case 0xaf:return sector;
    case 0xbf:{const v=disk[offset+index++];if(index===(short?64:256))status=short?4:crc?8:0;return v;}
    default:return rd(p);
  }
};
m.bus.ioWrite=(p,v)=>{
  switch(p&255){
    case 0xb7:assert([1,129].includes(v));head=v>>7;break;
    case 0x9f:track=v;break;
    case 0xaf:sector=v;break;
    case 0xbf:if(writing){disk[offset+index++]=v;if(index===256){status=0;writing=false;}}else index=v;break;
    case 0x8f:
      if(v===0){track=0;status=0;}
      else if(v===0x10){track=index;status=0;}
      else if(v===0xd0){status=0;writing=false;}
      else if(v===0x80||v===0xa0){
        assert(sector>=1&&sector<=16);offset=((track*sides+head)*16+sector-1)*256;index=0;
        writing=v===0xa0;status=missing?16:writing&&protectedDisk?64:3;
        if(writing)writes++;else reads++;
      } else assert.fail(`command ${v.toString(16)}`);
      break;
    default:wr(p,v);
  }
};
for(let i=0;i<300;i++)api.runFrame(m);
const symbols=Object.fromEntries([...fs.readFileSync('build/bios.bin.sym','utf8').matchAll(/^(\w+): EQU 0x([\da-f]+)/gmi)].map(x=>[x[1],parseInt(x[2],16)]));
function call(name,lba,drive=0){
 m.cpu.pc=symbols[name];m.cpu.h=lba>>8;m.cpu.l=lba&255;m.cpu.c=drive;m.cpu.sp=0xfefe;
 m.bus.write(0xfefe,0);m.bus.write(0xfeff,0xf7);
 let n=0;while(m.cpu.pc!==0xf700&&n++<30000)runZ80(m.cpu,m.bus,1,m);
 assert(n<30000,`hung ${name} ${lba}`);return m.cpu.a;
}
const bounce=symbols.bounce;
// Exercise the utility with real CP/M BDOS on the Oliger mapping as well.
const color=fs.readFileSync('build/COLOR.COM');symbols.color_start=0x100;
for(let scheme=0;scheme<8;scheme++){
 color.forEach((v,i)=>m.bus.write(0x100+i,v));
 m.bus.write(0x80,2);m.bus.write(0x81,32);m.bus.write(0x82,48+scheme);m.bus.write(0x83,13);
 call('color_start',0);
 assert.equal(m.portFF,6+(scheme<<3));assert.equal(m.portF4,15);
 assert.equal(call('block_read',0),0);assert.equal(m.portFF,6+(scheme<<3));
}
m.bus.ioWrite(0xff,62);
console.log('COLOR: all eight schemes through native CP/M BDOS on Oliger PASS');
call('ol_invalidate',0);
const beforeSequential=reads;
for(let lba=0;lba<records;lba++){
 assert.equal(call('block_read',lba),0,`LBA ${lba}`);
 assert.deepEqual(Buffer.from(Array.from({length:128},(_,i)=>m.bus.read(bounce+i))),disk.subarray(lba*128,lba*128+128));
}
const sequentialReads=reads-beforeSequential;
assert.equal(sequentialReads,records/2,'sequential records must share each physical read');
console.log(`${records} sequential CP/M reads: ${sequentialReads} WD reads, previously ${records} (50% fewer)`);
// Only the immediate partner may hit. Repeated records, intervening requests,
// HOME, and explicit media reinitialization must fetch from the controller.
function readCount(sequence){const start=reads;for(const lba of sequence)assert.equal(call('block_read',lba),0);return reads-start;}
call('ol_invalidate',0);assert.equal(readCount([0,1]),1);
assert.equal(readCount([0]),1,'partner is consumed after one use');
call('ol_invalidate',0);assert.equal(readCount([1,0]),1,'reverse-order partner');
call('ol_invalidate',0);assert.equal(readCount([0,0]),2,'same-half repeat must refetch');
call('ol_invalidate',0);assert.equal(readCount([0,2,1]),3,'intervening sector invalidates');
call('ol_invalidate',0);assert.equal(readCount([0]),1);call('home',0);assert.equal(readCount([1]),1);
call('ol_invalidate',0);assert.equal(readCount([0]),1);call('oliger_init',0);assert.equal(readCount([1]),1);
call('ol_invalidate',0);assert.equal(readCount([0]),1);
m.bus.write(symbols.keyqueue,65);m.bus.write(symbols.qtail,0);m.bus.write(symbols.qhead,1);
assert.equal(call('conin',0),65);assert.equal(readCount([1]),1,'console input discards pending media data');
for(const lba of [0,1,30,31,32,33,63,64,639,640,records-2,records-1]){
 const before=Buffer.from(disk);const pattern=Buffer.from(Array.from({length:128},(_,i)=>(i*17+lba)&255));
 const oldReads=reads,oldWrites=writes;
 pattern.forEach((v,i)=>m.bus.write(bounce+i,v));assert.equal(call('block_write',lba),0);
 assert.equal(reads-oldReads,1,'write always refreshes physical sector');
 assert.equal(writes-oldWrites,1,'write reaches controller synchronously');
 before.set(pattern,lba*128);assert.deepEqual(disk,before,'write must preserve every other record');
}
const count=reads+writes;
for(const lba of [records,65535])assert.equal(call('block_write',lba),1);
assert.equal(call('block_read',0,1),1);assert.equal(reads+writes,count);
protectedDisk=true;assert.equal(call('block_write',0),1);protectedDisk=false;
missing=true;assert.equal(call('block_read',0),1);missing=false;
short=true;assert.equal(call('block_read',0),1);
short=false;crc=true;assert.equal(call('block_read',0),1);crc=false;
const afterCrc=reads;assert.equal(call('block_read',1),0);assert.equal(reads,afterCrc+1,'CRC failure must not populate cache');
console.log('Z80 Oliger: all records, half-sector preservation, boundaries and errors PASS');
// FORMAT uses the real BIOS directory-write mode and catches write protection.
function format(){
 const program=fs.readFileSync('build/FORMAT.COM');program.forEach((v,i)=>m.bus.write(0x100+i,v));
 m.bus.write(0x80,2);m.bus.write(0x81,32);m.bus.write(0x82,65);m.bus.write(0x83,13);
 m.bus.write(symbols.keyqueue,89);m.bus.write(symbols.qtail,0);m.bus.write(symbols.qhead,1);
 m.cpu.pc=0x100;m.cpu.sp=0xfefe;let text='',steps=0;
 while(m.cpu.pc!==0&&steps++<2000000){if(m.cpu.pc===symbols.conout)text+=String.fromCharCode(m.cpu.c);runZ80(m.cpu,m.bus,1,m);}
 assert(steps<2000000,'FORMAT hung');return text;
}
const originalFormatDisk=Buffer.from(disk);
protectedDisk=true;assert.match(format(),/Format failed/);assert.deepEqual(disk,originalFormatDisk);
protectedDisk=false;assert.match(format(),/Disk initialized and directory verified/);
assert.deepEqual(disk.subarray(0,4096),Buffer.alloc(4096,0xe5));
assert.deepEqual(disk.subarray(4096),originalFormatDisk.subarray(4096));
console.log('FORMAT on Oliger: write-protection refusal, directory initialization/readback, payload preservation PASS');
