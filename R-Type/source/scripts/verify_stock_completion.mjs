import fs from 'node:fs';import assert from 'node:assert/strict';import{stockFixture}from './stock_fixture.mjs';
const n=Number(process.argv[2]||1),f=stockFixture(n),{m,call,out}=f;
const sy=Object.fromEntries([...fs.readFileSync(out+'/stock_completion.sym','utf8').matchAll(/(\w+): EQU 0x([0-9a-f]+)/ig)].map(x=>[x[1],parseInt(x[2],16)]));
const picture=fs.readFileSync(out+'/completion_bitmap.bin');let shown=false,replayed=false;const rd=m.bus.read;
m.keyMatrix.fill(31);m.joystick.fill(255);m.ay.regs[8]=12;m.ay.regs[9]=9;m.ay.regs[10]=10;
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc){if(a===sy.press&&!shown){shown=true;assert(Buffer.from(m.ram.slice(0x4000,0x5800)).equals(picture));for(let i=0;i<6144;i++)assert.equal(m.ram[0x6000+i],picture[i]?7:0);assert.deepEqual(Array.from(m.ay.regs.slice(8,11)),[0,0,0]);m.joystick[0]=127;}if(shown&&a===0x8634&&m.portF4===3){replayed=true;throw Error('REPLAYED');}}return rd(a);};
try{call(0xc2a3);}catch(e){if(!replayed)throw e;}m.bus.read=rd;
assert(shown&&replayed);assert.equal(m.ram[0xfc63],0);assert.equal(m.ram[0xb79c],48+n);
const r={passed:true,level:n,normalSizeCompletionScreen:true,normalBlackEmptyCells:true,audioMuted:true,nativeCompletionEntry:true,joystickReplayReloadsCartridge:true,romWrites:f.romWrites,scope:'Actual native completion entry and full ROM bootstrap replay; boss victory prerequisite separately tested'};fs.writeFileSync(out+'/completion_validation.json',JSON.stringify(r,null,2));console.log(r);
