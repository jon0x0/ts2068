import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{root,up,api}from'./r22_test_machine.mjs';
const out=path.join(root,'build/fullgame/preview_end_r29'),results=[];
for(const file of fs.readdirSync(out).filter(v=>v.endsWith('.dck'))){
 const joy=new Uint8Array(2).fill(255),m=api.createMachine(new Uint8Array(8).fill(31),joy);m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));api.insertDock(m,fs.readFileSync(path.join(out,file)));api.resetMachine(m);
 for(let f=0;f<1200;f++){joy[0]=f>=800&&f<850?239:255;api.runFrame(m);}
 let cassette=0,waitHits=0;const read=m.bus.read;m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc){if(a===0x8f1f)cassette++;if(a>=0xfe2e&&a<=0xfe32)waitHits++;}return read(a);};
 m.portF4=9;m.cpu.pc=0xfe03;
 for(let f=0;f<180;f++){m.keyMatrix.fill(f>=80&&f<100?0:31);api.runFrame(m);}
 assert.equal(cassette,0,file+' entered tape load');assert(waitHits>0,file+' did not remain in completion wait '+m.cpu.pc.toString(16));
 if(file==='Level_8_preview_r29.dck')fs.writeFileSync(path.join(out,'completion_screen.home.bin'),m.ram);
 results.push({file,cassette_calls:cassette,pc:m.cpu.pc,passed:true,diagnostic:'Forced resident loader entry after1200 frames; keys pressed during completion wait'});console.log(results.at(-1));
}
fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify(results,null,2));




