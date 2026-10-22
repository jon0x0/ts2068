// Save on the TS2068, remove power, and reload the exact disk without a PC repack.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {SramPicoModel,tapBlocks} from './tspico_sram_model.mjs';
const api=await import(pathToFileURL(path.resolve('../../TSRun/machine.js')));
const single=process.argv.includes('--single'),dir='build/profiles/tspico-dual';
const media=single?'build/dual-fixtures/stock160':dir;
const cart=fs.readFileSync(dir+'/ts2068-cpm.dck'),disk=fs.readFileSync(media+'/drive-a.img'),tap=fs.readFileSync(media+'/CPM320.TAP');
const count=disk.length/8192;
const seed=Object.fromEntries(Array.from({length:single?4:8},(_,i)=>[`/CPM/CPM3200${i}.TAP`,fs.readFileSync(media+`/CPM3200${i}.TAP`)]));
const map=['\0ZXCV','ASDFG','QWERT','12345','09876','POIUY','\rLKJH',' \0MNB'];
function machine(options={},volumes=seed){
 const keys=new Uint8Array(8).fill(255),m=api.createMachine(keys,new Uint8Array(2).fill(255));
 api.setHomeRom(m,fs.readFileSync('../../TSRun/roms/ts2068-0.rom'));api.setExRom(m,fs.readFileSync('../../TSRun/roms/ts2068-1.rom'));
 assert.equal(api.insertDock(m,cart),null);const pico=new SramPicoModel(m,cart,tap,{volumes,...options});
 const rd=m.bus.ioRead,wr=m.bus.ioWrite;m.bus.ioRead=p=>[14,15].includes(p&255)?pico.read(p):rd(p);
 m.bus.ioWrite=(p,v)=>[14,15].includes(p&255)?pico.write(p,v):wr(p,v);
 let text='';const write=m.bus.write;m.bus.write=(a,v)=>{if(a>=0xf800&&a<0xfe00)text+=String.fromCharCode(v);write(a,v);};
 function frames(n){for(let i=0;i<n;i++)api.runFrame(m);}
 function until(needle,max=800){for(let i=0;i<max&&!text.includes(needle);i++)frames(100);assert(text.includes(needle),JSON.stringify({needle,pc:m.cpu.pc.toString(16),tail:text.replaceAll('\0','').slice(-1200),cmd:pico.commands.slice(-6)}));}
 function type(s){for(let c of s){if(c==='.'||c==='='){keys[7]&=~2;c=c==='.'?'M':'L';}let found=false;for(let r=0;r<8;r++){const bit=map[r].indexOf(c);if(bit>=0){keys[r]&=~(1<<bit);frames(4);keys.fill(255);frames(4);found=true;break;}}assert(found,c);}}
 function boot(choice){if(options.service){until('L: reload saved RAMDisk');type(choice||'R');}until('HELLO from a .COM');}
 return {m,pico,frames,until,type,boot,log:()=>text};
}

for(const options of [{},{verbose:true},{missingSaveDirectory:true},{missingStatus:5},{modern:true}]){
 if(process.argv.includes('--errors-only'))continue;
 const t=machine(options);t.boot();
 assert.equal(t.m.bus.read(0xeff6),0,'empty SAVE must use factory preload');
 if(!options.modern)assert(!t.pico.commands.some(x=>/CPMSTATE|CPM00\.TAP/.test(x)),'absent saves must not be opened');
 for(let i=0;i<t.pico.commands.length;i++){
  const command=t.pico.commands[i].toUpperCase();
  if(command.endsWith('.TAP'))assert.equal(t.pico.commandHeaders[i][1],1,'named mount must be LOAD');
  if(command.startsWith('TPI:CD '))assert.equal(t.pico.commandHeaders[i][1],0,'CD must be SAVE');
 }
 console.log('Empty SAVE / absent SAVE directory and named LOAD selection PASS '+JSON.stringify(options));
}
for(const verbose of [false,true]){
 const t=machine({verbose,rejectCommand:'TPI:CPMSTATE.TAP',getinfoText:'FW Rev.: TEST; uPython: 1.20.0\rDefault ROM version: 1.00\r'},{...seed,'/CPM/SAVE/CPMSTATE.TAP':tap});t.until('failed. Do not boot.');
 assert.match(t.log(),/GETINFO \(read-only\)/);
 assert.match(t.log(),/FW Rev.: TEST/);
 assert(t.pico.commands.includes('tpi:getinfo'));
 assert(!t.log().includes('HELLO from a .COM'));
 assert.match(t.log(),/error=05/);
 assert.match(t.log(),/Header: 42 01 FF 00 00 00 00 10 00 AC/);
 assert.match(t.log(),verbose?/Function=81 status=05/:/Function=05 status=05/);
 assert.match(t.log(),/Command \(LOAD=01 \/ SAVE=00\): 01\r\ntpi:CPMSTATE.TAP/);
 if(verbose)assert.match(t.log(),/Reply: \r81 - Unrecognized command: TPI:CPMSTATE.TAP/);
 else assert.match(t.log(),/Reply: \r\n/);
 assert(!t.pico.commands.some(x=>x.includes('CPM32000')),'unknown command must not load factory disk');
 fs.writeFileSync('build/discovery-error05-'+verbose+'.txt',t.log());
 console.log('Error 05 remains fatal; exact command, direction and '+(verbose?'text':'plain')+' reply PASS');
}

// A present modern save with invalid metadata must not fall back to preload.
const brokenTap=Buffer.from(tap);
brokenTap[24]^=1;brokenTap[24+128]^=1; // alter magic, keep transport checksum valid
const malformed=machine({modern:true},{...seed,'/CPM/SAVE/CPMRAM.TAP':brokenTap});
malformed.until('failed. Do not boot.');
assert(!malformed.log().includes('HELLO from a .COM'));
assert(!malformed.pico.commands.some(x=>x.includes('CPM32000')));
console.log('Malformed modern saved image refuses factory fallback PASS');

const tooMany={...seed};
for(let i=0;i<80;i++)tooMany['/CPM/SAVE/F'+String(i).padStart(3,'0')+'.TAP']=tap;
const overflow=machine({},tooMany);overflow.until('failed. Do not boot.');
assert.match(overflow.log(),/stage=09/);
assert(!overflow.log().includes('HELLO from a .COM'));
assert(!overflow.pico.commands.some(x=>x.includes('CPM32000')));
console.log('Incomplete/oversized listing refuses factory fallback PASS');
