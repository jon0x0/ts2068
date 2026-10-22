// Test the exact browser disk adapter against TSRun's native Z80 and CP/M BIOS.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {attachOliger,decodeDsk,decodeTap,decodeTapSet,encodeTap,encodeTapSet,storedZip} from '../web/tsrun/oliger.mjs';
const api=await import(pathToFileURL(path.resolve('../../TSRun/machine.js')));
const matrix=['\0ZXCV','ASDFG','QWERT','12345','09876','POIUY','\rLKJH',' \0MNB'];
function boot(cart,data){
 const keys=new Uint8Array(8).fill(255),m=api.createMachine(keys,new Uint8Array(2).fill(255));
 api.setHomeRom(m,fs.readFileSync('../../TSRun/roms/ts2068-0.rom'));api.setExRom(m,fs.readFileSync('../../TSRun/roms/ts2068-1.rom'));
 assert.equal(api.insertDock(m,cart),null);const device=attachOliger(m,data);let log='';const write=m.bus.write;
 m.bus.write=(a,v)=>{if(a>=0xf800&&a<0xfe00)log+=String.fromCharCode(v);write(a,v);};
 const frames=n=>{for(let i=0;i<n;i++)api.runFrame(m);};
 const type=text=>{for(let c of text){keys.fill(255);if('.='.includes(c)){keys[7]&=~2;c=c==='.'?'M':'L';}for(let r=0;r<8;r++){let bit=matrix[r].indexOf(c);if(bit>=0){keys[r]&=~(1<<bit);break;}}frames(4);keys.fill(255);frames(4);}};
 frames(300);assert(log.includes('HELLO from a .COM'));assert(log.includes('A>'));assert.equal(m.portF4,15);
 return {m,device,frames,type,log:()=>log};
}

for(const kind of ['dsk','tap']){
 const cart=fs.readFileSync('build/infocom-cpm.dck'),data=fs.readFileSync('build/software-example/zork2.'+kind),t=boot(cart,data);
 t.type('ZORK2\r');t.frames(1800);assert.match(t.log(),/ZORK II/);assert.match(t.log(),/Version 48/);
 const before=t.log().length;t.type('LOOK\r');t.frames(500);assert.match(t.log().slice(before),/LOOK[\r\n]+Inside the Barrow/);
 t.type('SAVE\r');t.frames(200);t.type('\r');t.frames(200);t.type('\r');t.frames(600);
 assert(Buffer.from(t.device.raw.subarray(0,4096)).map(v=>v&127).includes(Buffer.from('ZORK2   SAV')),'save file missing');
 t.type('QUIT\r');t.frames(300);t.type('Y\r');t.frames(800);assert.match(t.log().slice(-1000),/A>/);
 fs.writeFileSync('build/software-example/zork2-'+kind+'-run.txt',t.log());
 console.log('Zork II '+kind+': prepared interpreter/story, cold boot, LOOK and SAVE PASS');
}
