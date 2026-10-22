// Test the exact browser disk adapter against TSRun's native Z80 and CP/M BIOS.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {attachOliger,decodeDsk,decodeTap,decodeTapSet,encodeTap,encodeTapSet,storedZip} from '../web/tsrun/oliger.mjs';
const api=await import(pathToFileURL(path.resolve(process.env.TSRUN_PATH||'../../TSRun','machine.js')));
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
fs.mkdirSync('build/tsrun-tap-tests',{recursive:true});
for(const kb of [160,320])for(const format of ['dsk','tap']){
 const cart=fs.readFileSync(kb===320?'build/infocom-cpm.dck':'build/profiles/oliger/ts2068-cpm.dck');
 const disk=fs.readFileSync(kb===320?'build/infocom-cpm.dsk':'build/profiles/oliger/oliger-cpm.dsk');
 const input=format==='tap'?encodeTap(decodeDsk(disk).raw):disk;
 const t=boot(cart,input);assert.equal(t.device.sides,kb/160);
 t.type('PIP COPY.COM=HELLO.COM\r');t.frames(500);t.type('COPY\r');t.frames(200);
 assert.equal((t.log().match(/HELLO from a .COM/g)||[]).length,2);
 assert(t.device.dirty);const saved=t.device.exportDsk();assert.deepEqual(decodeDsk(saved).raw,t.device.raw);
 const tap=t.device.exportTap();assert.deepEqual(decodeTap(tap).raw,t.device.raw);
 const chunks=encodeTapSet(t.device.raw);assert.deepEqual(decodeTapSet(chunks.toReversed()).raw,t.device.raw);
 assert.throws(()=>decodeTapSet(chunks.slice(1)),'missing page accepted');
 const corrupt=tap.slice();corrupt[100]^=1;assert.throws(()=>decodeTap(corrupt));
 fs.writeFileSync(`build/tsrun-tap-tests/${kb}-${format}.tap`,tap);
 fs.writeFileSync(`build/tsrun-tap-tests/${kb}-${format}.zip`,storedZip(chunks));
 fs.writeFileSync(`build/tsrun-tap-tests/${kb}-${format}.img`,t.device.raw);
 const reopened=boot(cart,format==='tap'?tap:saved);reopened.type('COPY\r');reopened.frames(200);
 assert.equal((reopened.log().match(/HELLO from a .COM/g)||[]).length,2);
 // Reset keeps the in-memory disk; write protection refuses a sector write.
 const before=t.device.raw.slice();t.device.reset();api.resetMachine(t.m);t.frames(300);
 assert.deepEqual(t.device.raw,before);t.device.writeProtected=true;
 for(const [p,v] of [[0xb7,1],[0x9f,0],[0xaf,1],[0x8f,0xa0],[0xbf,42]])t.m.bus.ioWrite(p,v);
 assert.equal(t.m.bus.ioRead(0x8f),64);assert.deepEqual(t.device.raw,before);
 fs.writeFileSync(`build/tsrun-oliger-${kb}.txt`,t.log());
 console.log(`${kb}KB ${format}: ROM boot, CP/M copy/execute, DSK/TAP/chunk export, reload, reset and protection PASS`);
}
for(const bad of [new Uint8Array(10),fs.readFileSync('build/infocom-cpm.dsk').subarray(0,400)])assert.throws(()=>decodeDsk(bad));
for(const kb of [160,320]){
 const folder=kb===160?'build/dual-fixtures/stock160':'build/profiles/tspico-dual';
 const volumes=Array.from({length:kb/40},(_,i)=>({name:`CPM3200${i}.TAP`,data:fs.readFileSync(`${folder}/CPM3200${i}.TAP`)}));
 assert.deepEqual(decodeTapSet(volumes.toReversed()).raw,new Uint8Array(fs.readFileSync(`${folder}/drive-a.img`)));
 assert.throws(()=>decodeTapSet(volumes.slice(1)));
 const chunks=encodeTapSet(new Uint8Array(fs.readFileSync(`build/tsrun-tap-tests/${kb}-tap.img`)));
 const mixed=chunks.map(file=>({name:file.name,data:file.data.slice()}));mixed[0].data[24]^=1;mixed[0].data[mixed[0].data.length-1]^=1;
 assert.throws(()=>decodeTapSet(mixed),'valid TAP CRC concealed a mixed-generation page');
 console.log(`${kb}KB: preload volumes, missing volume and mixed saved-page checks PASS`);
}
