import {acceptTitle} from './accept_title.mjs';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck'));
const offset=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;
const cases=[];
for(const status of [1,2]) for(const input of ['keyboard','joystick']) {
 const keys=new Uint8Array(8).fill(31),joy=new Uint8Array(2).fill(255),m=api.createMachine(keys,joy);
 m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));api.insertDock(m,cart);api.resetMachine(m);acceptTitle(m,sym);
 const run=n=>{for(let i=0;i<n;i++)api.runFrame(m);};run(300);
 const press=()=>input==='keyboard'?keys[7]&=~1:joy[0]&=~128;
 const release=()=>{keys.fill(31);joy.fill(255);};
 press();m.ram[sym.game_status]=status;run(120);
 assert.equal(m.ram[sym.game_status],status,'held fire must not dismiss result');assert.equal(m.ram[0x5897],1);
 // Independently check the first glyph of each result and the restart prompt.
 const first=status===1?[0x88,0x88,0x50,0x20,0x20,0x20,0x20]:[0x70,0x88,0x80,0xb8,0x88,0x88,0x70];
 for(const [x,y,glyph] of [[11,24,first],[8,40,[0xf8,0x80,0x80,0xf0,0x80,0x80,0x80]]])for(let r=0;r<7;r++) {
  assert.equal(m.ram[0x4000+offset(x,y+r)],glyph[r]);assert.equal(m.ram[0x6000+offset(x,y+r)],71);
 }
 release();run(20);assert.equal(m.ram[0x5897],2);press();run(20);release();run(250);
 assert.equal(m.ram[sym.game_status],0);assert.equal(m.ram[sym.lives],3);assert.equal(m.ram[sym.bombs],3);assert.equal(m.ram[0x5897],0);
 cases.push({status,input,held_fire_safe:true,native_text:true,restart:true});
}
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),cases};console.log(report);fs.writeFileSync(path.join(root,'build/end-screen-verification.json'),JSON.stringify(report,null,2)+'\n');
