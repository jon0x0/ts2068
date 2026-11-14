import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{root,api,call,off,rev}from'./r22_test_machine.mjs';
const folder=path.join(root,'build/fullgame/cached_levels_r34'),raw=fs.readFileSync(path.join(folder,'level02_region.bin')),boot=fs.readFileSync(path.join(folder,'boot_region.bin')),layout=JSON.parse(fs.readFileSync(path.join(root,'build/fullgame/foundation/manifest.json'))).levels[1],m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));api.insertDock(m,Buffer.concat([Buffer.from([0,...Array(8).fill(3)]),raw]));
for(const[s,d]of[[7,2],[1,3],[2,4],[3,5],[5,6],[6,7]])m.ram.set((s===2||s===3?boot:raw).subarray(s*8192,(s+1)*8192),d*8192);for(const b of[1,2,3])m.dock[b].set(raw.subarray(b*8192,(b+1)*8192));for(let i=0;i<256;i++)m.ram[0x5d00+i]=rev(i);const source=Buffer.from(m.ram),dictionary=raw.subarray(0xe000,0xe400),results=[];

const diag=path.join(root,'build/diagnostics/l2_spawn_r35');fs.mkdirSync(diag,{recursive:true});
const captured=fs.readFileSync(path.join(root,'build/diagnostics/l2_emergence/id19_f4251_pcbc7.home.bin'));
for(const fixed of[false,true]){
 m.ram.set(source);m.portF4=9;m.portFF=2;m.ram.fill(0,0x4000,0x5800);m.ram.fill(7,0x6000,0x7800);m.dock[3].fill(0,0x1e00);
 m.ram.set(captured.subarray(0x5d00,0x5e00),0x5d00);
 if(fixed)for(let i=0;i<256;i++)m.ram[0x5d00+i]=rev(i);
 m.bus.write(0x7a9c,130);m.ram[0x8eb1]=0;m.ram[0x8ebf]=0x40;m.ram[0x8f10]=0xd8;
 call(m,0x8d65,{b:12,c:14,d:5,e:5,h:0xcb,l:0xc7});
 fs.writeFileSync(path.join(diag,fixed?'fixed_pose.home.bin':'old_pose.home.bin'),m.ram);
}
console.log('Old and corrected mirrored descriptor32 captured');
