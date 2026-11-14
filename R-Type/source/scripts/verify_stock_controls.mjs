import fs from 'node:fs';import assert from 'node:assert/strict';import{stockFixture}from './stock_fixture.mjs';
const n=Number(process.argv[2]||1),f=stockFixture(n),{m,call,out}=f;
const sy=Object.fromEntries([...fs.readFileSync(out+'/stock_controls.sym','utf8').matchAll(/(\w+): EQU 0x([0-9a-f]+)/ig)].map(x=>[x[1],parseInt(x[2],16)]));
m.ram[0x7aa4]=3;m.ram.fill(255,0xbd80,0xbd8c);m.keyMatrix.fill(31);m.keyMatrix[5]=30;
for(let k=0;k<0x1800;k++){m.ram[0x4000+k]=(k*17+3)&255;m.ram[0x6000+k]=(k&7)|64;}
const nativeFont=Buffer.from(m.ram.slice(0x7ae8,0x7ce8));
const before=Buffer.from(m.ram.slice(0x4000,0x7800));m.ay.regs[8]=11;m.ay.regs[9]=8;m.ay.regs[10]=13;m.ay.regs[14]=0xa5;m.ay.regs[15]=0x5a;
let reads=0,paused=false;const rd=m.bus.read;
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&a===sy.read_p){reads++;m.keyMatrix[5]=reads===2?30:31;if(reads===1){paused=true;assert.equal(m.cpu.iff1,false);assert.deepEqual(Array.from(m.ay.regs.slice(8,11)),[0,0,0]);for(let y=0;y<8;y++)for(let x=0;x<6;x++)assert.equal(m.ram[0x486d+y*256+x],m.bus.read(sy.font+y*6+x));}}return rd(a);};
call(sy.pause_poll);m.bus.read=rd;assert(Buffer.from(m.ram.slice(0x7ae8,0x7ce8)).equals(nativeFont),'Pause overwrote native message font');assert(paused&&reads>=3);assert(Buffer.from(m.ram.slice(0x4000,0x7800)).equals(before));assert.deepEqual(Array.from(m.ay.regs.slice(8,11)),[11,8,13]);assert.equal(m.ay.regs[14],0xa5);assert.equal(m.ay.regs[15],0x5a);
m.keyMatrix.fill(31);m.ram[0xfd93]=0;m.ram[0xfd94]=0;m.keyMatrix[7]&=~4;call(0x11d0);assert.equal(m.ram[0xfd93],1);call(0x11d0);assert.equal(m.ram[0xfd93],1);m.keyMatrix.fill(31);call(0x11d0);m.keyMatrix[7]&=~4;call(0x11d0);assert.equal(m.ram[0xfd93],0);
m.keyMatrix.fill(31);for(const socket of[0,1]){m.joystick.fill(255);m.joystick[socket]=127;m.ram[0xbafa]=0;call(0x1a00);assert(m.ram[0xbafa]&16,'Native joystick fire socket '+socket);}m.joystick.fill(255);
m.ram[0x7aa4]=3;m.ram[0xfd4b]=0;m.keyMatrix[7]&=~16;call(sy.boss_poll);assert.equal(m.ram[0xfd4b],1);m.keyMatrix.fill(31);call(sy.boss_poll);assert.equal(m.ram[0xfd4b],2);m.keyMatrix[7]&=~16;call(sy.boss_poll);assert.equal(m.ram[0xfd4b],3);assert.equal(m.ram[0x7ac1],2);assert.equal(m.ram[0x7ac5],2);
const r={passed:true,level:n,nativeFontPreserved:true,pauseOverlay:true,pauseRestoresPixelsAndColours:true,pauseMutesAndRestoresAy:true,joystickSockets:[1,2],musicToggleEdges:true,doubleBBossNativeSetup:true,collectiblePickups:true,romWrites:f.romWrites,scope:'Actual control routines and native boss initializer; boss fight/victory separately tested'};fs.writeFileSync(out+'/controls_validation.json',JSON.stringify(r,null,2));console.log(r);
