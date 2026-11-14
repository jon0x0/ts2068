import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{root,api,call,off,rev}from'./r22_test_machine.mjs';
const folder=path.join(root,'build/fullgame/transition_fix_r36'),raw=fs.readFileSync(path.join(folder,'level02_region.bin')),boot=fs.readFileSync(path.join(folder,'boot_region.bin')),layout=JSON.parse(fs.readFileSync(path.join(root,'build/fullgame/foundation/manifest.json'))).levels[1],m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));api.insertDock(m,Buffer.concat([Buffer.from([0,...Array(8).fill(3)]),raw]));
for(const[s,d]of[[7,2],[1,3],[2,4],[3,5],[5,6],[6,7]])m.ram.set((s===2||s===3?boot:raw).subarray(s*8192,(s+1)*8192),d*8192);for(const b of[1,2,3])m.dock[b].set(raw.subarray(b*8192,(b+1)*8192));for(let i=0;i<256;i++)m.ram[0x5d00+i]=rev(i);const source=Buffer.from(m.ram),dictionary=raw.subarray(0xe000,0xe400),results=[];

m.portF4=9;m.portFF=2;m.ram.fill(0xa5,0x7800,0x7b00);call(m,0x0f20,{d:0xca,e:0xfe});
assert.equal(m.cpu.d*256+m.cpu.e,0x7800,'Original fill routine returns DE at end of attribute plane');
assert.equal(m.portFF,0x41);assert.equal(m.portF4,9);assert(m.ram.slice(0x7800,0x7b00).every(v=>v===0));assert(m.ram.slice(0x4000,0x5800).every(v=>v===0));
console.log('Title fill endpoint, mapping and hidden attributes verified');
