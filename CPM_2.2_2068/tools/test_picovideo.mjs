// PicoVideo 4.2 register/framebuffer contract, with the native TSRun Z80.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const api=await import(pathToFileURL(path.resolve('../../TSRun/machine.js')));
const {runZ80}=await import(pathToFileURL(path.resolve('../../TSRun/z80.js')));
const dir=process.argv[2]||'build';
const symbols=Object.fromEntries([...fs.readFileSync(dir+'/bios.bin.sym','utf8').matchAll(/^(\w+): EQU 0x([\da-f]+)/gmi)].map(x=>[x[1],parseInt(x[2],16)]));
function machine(version){
 const keys=new Uint8Array(8).fill(255),m=api.createMachine(keys,new Uint8Array(2).fill(255));
 api.setHomeRom(m,fs.readFileSync('../../TSRun/roms/ts2068-0.rom'));api.setExRom(m,fs.readFileSync('../../TSRun/roms/ts2068-1.rom'));
 assert.equal(api.insertDock(m,fs.readFileSync(dir+'/ts2068-cpm.dck')),null);
 const regs=new Uint8Array(256);regs[127]=version;let selector=17;
 const rd=m.bus.ioRead,wr=m.bus.ioWrite;
 m.bus.ioRead=p=>p===0xbf3b?selector:p===0xff3b?regs[selector]:rd(p);
 m.bus.ioWrite=(p,v)=>{if(p===0xbf3b)selector=v;else if(p===0xff3b)regs[selector]=v;else wr(p,v);};
 const frames=n=>{for(let i=0;i<n;i++)api.runFrame(m);};
 function call(name,c=0){m.cpu.pc=symbols[name];m.cpu.c=c;m.cpu.sp=0xfefe;m.bus.write(0xfefe,0);m.bus.write(0xfeff,0xf7);const clock={tstates:0};let count=0;while(m.cpu.pc!==0xf700&&count++<1000000)runZ80(m.cpu,m.bus,1,clock);assert(count<1000000,name);}
 function utility(arg,name='COLUMNS'){m.bus.write(5,0xc3);m.bus.write(6,6);m.bus.write(7,0xd8);const data=fs.readFileSync('build/'+name+'.COM');for(let i=0;i<data.length;i++)m.bus.write(0x100+i,data[i]);m.bus.write(0x80,arg.length);for(let i=0;i<arg.length;i++)m.bus.write(0x81+i,arg.charCodeAt(i));symbols.utility=0x100;call('utility');}
 function put(text){for(const byte of Buffer.from(text))call('conout',byte);}
 return {m,regs,frames,call,put,utility,selector:()=>selector};
}
for(const version of [0xff,0x10,0x41,0x50]){
 const t=machine(version);t.frames(300);assert.equal(t.m.bus.read(0xeff5),0);assert.equal(t.m.bus.read(symbols.columns),64);
 assert.equal(t.regs[64],0);assert.equal(t.selector(),17);
 t.call('cls');t.put('A');
 const cartridge=fs.readFileSync(dir+'/ts2068-cpm.dck');
 const font=cartridge.subarray(9+4*8192+256,9+4*8192+256+768);
 for(let line=0;line<8;line++)assert.equal(t.m.ram[0x4000+line*256],font[('A'.charCodeAt(0)-32)*8+line]);
}
const t=machine(0x42);t.frames(300);
assert.equal(t.m.bus.read(0xeff5),1);assert.equal(t.m.bus.read(symbols.columns),80);
assert.equal(t.regs[64],1);assert.equal(t.regs[65],5);assert.equal(t.regs[67],0);
assert.equal(t.selector(),17);
if(JSON.parse(fs.readFileSync(dir+'/manifest.json')).profile!=='oliger')assert.match(Buffer.from(t.m.ram.subarray(0x4000,0x4780)).toString('ascii'),/HELLO from a \.COM/);
t.call('cls');t.put('X'.repeat(80));assert.equal(t.m.bus.read(symbols.row),1);assert.equal(t.m.bus.read(symbols.col),0);
assert.equal(Buffer.from(t.m.ram.subarray(0x4000,0x4050)).toString(),'X'.repeat(80));
t.put('Y');assert.equal(t.m.ram[0x4050],89);assert.equal(t.m.portF4,15);
t.call('cls');t.put('A\r\n');t.put('B\r\n');for(let i=0;i<23;i++)t.put('C\r\n');
assert.equal(t.m.ram[0x4000],67);assert.equal(t.m.bus.read(symbols.row),23);
assert(t.m.ram.subarray(0x4780,0x4f00).every(x=>x===7),'attributes changed during scrolling');
if(symbols.escape_state!==undefined){
 t.call('cls');t.put('STATUS');t.put('\x1b='+String.fromCharCode(33,32));
 for(let i=0;i<24;i++)t.put('BODY\r\n');
 assert.equal(Buffer.from(t.m.ram.subarray(0x4000,0x4006)).toString(),'STATUS');
 t.put('\x1b='+String.fromCharCode(55,111));t.put('Z');assert.equal(t.m.ram[0x477f],32,'last-column wrap should scroll body');
}
t.utility('64');assert.equal(t.m.bus.read(symbols.columns),64);assert.equal(t.m.bus.read(0xeff5),0);assert.equal(t.regs[64],1);assert.equal(t.regs[65],6);assert.equal(t.m.bus.read(0xeff7),1);
t.utility('80');assert.equal(t.m.bus.read(symbols.columns),80);assert.equal(t.m.bus.read(0xeff5),1);assert.equal(t.regs[64],1);assert.equal(t.selector(),17);
t.utility('65');assert.equal(t.m.bus.read(symbols.columns),80);
const fallback=machine(0xff);fallback.frames(300);fallback.utility('80');assert.equal(fallback.m.bus.read(symbols.columns),64);assert.equal(fallback.m.bus.read(0xeff5),0);
console.log('COLUMNS switching, invalid argument and unsupported renderer PASS');
console.log('PicoVideo 4.2: detection, 80-column boot, wrapping, scrolling, attributes and 64-column fallback PASS');

const colors=[0,2,0x10,0x12,0x80,0x82,0x90,0x92];
for(let n=0;n<8;n++){
 t.utility(String(n),'COLOR');
 assert.equal(t.regs[7],colors[n]);assert.equal(t.regs[8],colors[n^7]);
 assert.equal(t.m.border,0);assert.equal(t.regs[0],colors[n^7],'border must match paper');
}
const selected=t.selector();t.utility('','VIDEO');assert.equal(t.selector(),selected);
assert.match(Buffer.from(t.m.ram.subarray(0xf800,0xfe00)).toString(),/7F=42/);
t.utility('64');t.m.bus.write(0xeff7,0);t.utility('80');
assert.equal(t.m.bus.read(0xeff7),1,'slow COLUMNS probe must recover a missed boot detection');
assert.equal(t.m.bus.read(symbols.columns),80);
console.log('COLOR paper/border palette, read-only VIDEO diagnostic and COLUMNS slow retry PASS');

t.utility('64');
for(let n=0;n<8;n++){
 t.utility(String(n),'COLOR');
 assert.equal(t.regs[65],6);assert.equal(t.m.bus.read(0xeff5),0);
 assert.equal(t.regs[n],colors[n]);assert.equal(t.regs[n|1],colors[n]);
 assert.equal(t.regs[8+(n^7)],colors[n^7]);
 assert.equal(t.regs[t.m.border],colors[n^7]);
}
console.log('64-column PicoVideo palette covers original and corrected ink calculation, with matching border PASS');

for(const width of [64,80]){
 t.utility(String(width));
 for(let border=0;border<8;border++){
  t.utility('0 '+border,'COLOR');
  assert.equal(t.regs[t.m.border],colors[border]);
  assert.equal(t.regs[width===80?7:1],colors[0],'border must not replace text ink');
  assert.equal(t.regs[width===80?8:15],colors[7],'border must not replace paper');
 }
 t.utility('0','COLOR');assert.equal(t.regs[t.m.border],colors[7]);
}
console.log('Optional border color, palette isolation and default restoration in 64/80 columns PASS');
