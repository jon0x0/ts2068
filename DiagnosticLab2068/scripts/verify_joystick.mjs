import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const api=await import(pathToFileURL(path.resolve('../TSRun/machine.js')));
const bits=[0,1,2,3,7],targets=[0x5905,0x59c5,0x5961,0x5969,0x5a25];
for(const home of [false,true]){
 const base=home?'build/home/':'build/',file=home?'diagnostic-home-u16.bin':'diagnostic-v02.dck',image=fs.readFileSync(base+file);
 const sym=Object.fromEntries([...fs.readFileSync(base+'symbols.txt','utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)]));
 const cases=[];
 for(let player=0;player<2;player++)for(let combo=0;combo<32;combo++){
  const keys=new Uint8Array(8).fill(31),joy=new Uint8Array(2).fill(255),m=api.createMachine(keys,joy);
  if(home)m.homeRom.set(image);else assert.equal(api.insertDock(m,image),null);
  api.resetMachine(m);m.portF4=home?0:1;m.portFF=64;m.cpu.pc=sym.load_inputs;m.cpu.sp=0xbeef;m.cpu.iff1=false;
  let raw=255;bits.forEach((bit,n)=>{if(combo&(1<<n))raw&=~(1<<bit);});joy[player]=raw;
  const read=m.bus.read,write=m.bus.write;
  m.bus.read=a=>{if(a===m.cpu.pc){assert.equal(m.cpu.sp,0xbeef);assert.ok(home?a<0x4000:a<0x2000||(a>=0x3f00&&a<0x3fd0&&(m.portF4&2)),'ROM-only anchored fetch');}return read(a);};
  m.bus.write=(a,v)=>{assert.ok(a>=0x4000,'no ROM/code writes');write(a,v);};
  for(let i=0;i<30;i++)api.runFrame(m);
  for(let port=0;port<2;port++)for(let n=0;n<5;n++)for(let x=0;x<6;x++)assert.equal(m.ram[targets[n]+port*16+x],port===player&&(combo&(1<<n))?0x60:0x78,'independent control highlight');
  // Release keeps tested history, while subsequent transitions remain live.
  joy[player]=255;for(let i=0;i<2;i++)api.runFrame(m);
  for(let port=0;port<2;port++)for(let n=0;n<5;n++)assert.equal(m.ram[targets[n]+port*16],port===player&&(combo&(1<<n))?0x68:0x78);
  for(let edge=0;edge<8;edge++){
   joy[player]=edge%2?255:raw;for(let i=0;i<2;i++)api.runFrame(m);
   for(let n=0;n<5;n++)assert.equal(m.ram[targets[n]+player*16],combo&(1<<n)?(edge%2?0x68:0x60):0x78,'repeated momentary transitions remain live');
  }
  keys[1]&=~1;for(let i=0;i<30;i++)api.runFrame(m);assert.equal(m.portF4,home?0:1);
  cases.push({player:player+1,combo,raw,result:'PASS'});
 }
 for(const bad of [0x3f00,0x3f01,0x3f60]){
  const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));
  if(home)m.homeRom.set(image);else api.insertDock(m,image);api.resetMachine(m);m.portF4=home?0:1;m.portFF=64;m.cpu.pc=sym.load_inputs;m.cpu.iff1=false;
  const read=m.bus.read;let reported=false,transferred=false;
  m.bus.read=a=>{if(a===m.cpu.pc){if(a===sym.cartridge_alarm)reported=true;if(a===0x3f00)transferred=true;}return read(a)^(a===bad?1:0);};
  for(let i=0;i<200&&!reported;i++)api.runFrame(m);assert.ok(reported);assert.ok(!transferred,'bad helper must not execute');
  cases.push({name:'corrupt helper '+bad.toString(16)+' prevents code transfer',result:'PASS'});
 }
 // Both ports simultaneously: Up+Right+Fire versus Down+Left+Fire.
 const captureJoy=new Uint8Array([0xf9,0xf6]);
 const m=api.createMachine(new Uint8Array(8).fill(31),captureJoy);
 if(home)m.homeRom.set(image);else api.insertDock(m,image);api.resetMachine(m);m.portF4=home?0:1;m.portFF=64;m.cpu.pc=sym.load_inputs;m.cpu.iff1=false;
 for(let i=0;i<30;i++)api.runFrame(m);
 captureJoy.set([0x76,0x79]);for(let i=0;i<2;i++)api.runFrame(m);
 fs.writeFileSync(base+'joystick-active.screen',m.ram.slice(0x4000,0x5b00));
 fs.writeFileSync(base+'joystick-verification.json',JSON.stringify({image_sha256:createHash('sha256').update(image).digest('hex'),result:'PASS',cases,configuration:'TSRun active-low AY portA: all32 combinations per port; exact six-cell highlights, release, cancellation, stack/mapping and port isolation',limitations:['No automatic joystick presence/contact certification; physical wiring and user movement require observation']},null,2)+'\n');
 console.log((home?'HOME':'Cartridge')+' joystick64 combinations + releases/isolation/cancel PASS');
}

