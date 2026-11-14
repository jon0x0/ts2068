import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import crypto from'node:crypto';import{root,api,call}from'./r22_test_machine.mjs';const results=[];
for(let level=1;level<=8;level++){
 const folder=path.join(root,'build/fullgame','level'+String(level).padStart(2,'0')),raw=fs.readFileSync(path.join(folder,'game.bin')),cart=Buffer.concat([Buffer.from([0,2,3,3,3,2,2,2,2]),raw]),runtime=fs.readFileSync(path.join(folder,'runtime_region.bin')),m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));api.insertDock(m,cart);
 for(const[src,dest]of[[7,2],[1,3],[2,4],[3,5],[5,6],[6,7]])m.ram.set(raw.subarray(src*8192,(src+1)*8192),dest*8192);
 for(const b of[1,2,3])m.dock[b].set(runtime.subarray(b*8192,(b+1)*8192));m.dock[3][0x1aa4]=3;m.portF4=0x19;m.portFF=2;m.ram.fill(0,0xfd92,0xfd95);m.ram.fill(0,0xfbc0,0xfbca);
 const source=JSON.parse(fs.readFileSync(path.join(root,'build/fullgame/audio','music_probe_'+(level-1)+'.json'))),expected=new Uint8Array(14);let maxStack=0;
 for(let tick=0;tick<source.frames.length*2+1;tick++){
  const frame=tick===0?source.init:source.frames[(tick-1)%source.frames.length];for(const[r,v]of frame)expected[r]=v;call(m,0x9c00);assert.deepEqual(m.ram.slice(0xfd84,0xfd92),expected,'Level'+level+' music tick'+tick);const used=(m.ram[0xfd80]|m.ram[0xfd81]<<8)-0xfd50;assert(used>=0&&used<=44,'Music grammar stack overflow');maxStack=Math.max(maxStack,used);
 }
 results.push({level,entry:level-1,ticks:source.frames.length*2+1,max_pending_stack_bytes:maxStack,sha256:crypto.createHash('sha256').update(raw).digest('hex'),exact_source_registers:true,passed:true});console.log(results.at(-1));
}
fs.writeFileSync(path.join(root,'build/fullgame/audio/native_validation.json'),JSON.stringify(results,null,2));
