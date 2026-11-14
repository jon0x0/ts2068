import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{root,api,call,original}from'./r22_test_machine.mjs';
const out=path.join(root,'build/diagnostics/l3_photo'),raw=fs.readFileSync(path.join(root,'build/fullgame/transition_fix_r36/level03_region.bin')),results=[];
for(const name of fs.readdirSync(out).filter(v=>/^frame\d+\.home\.bin$/.test(v))){const home=fs.readFileSync(path.join(out,name)),captures=[];for(const baseline of[false,true]){
 const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));api.insertDock(m,Buffer.concat([Buffer.from([0,...Array(8).fill(3)]),raw]));m.ram.set(home);for(const b of[1,2,3])m.dock[b].set(fs.readFileSync(path.join(out,name.replace('.home.',`.dock${b}.`))));m.portF4=9;m.portFF=2;
 if(baseline){m.ram.set(original.subarray(0x8859-0x4000,0x885c-0x4000),0x8859);m.ram.set(original.subarray(0x8872-0x4000,0x8875-0x4000),0x8872);}
 call(m,0x8842);captures.push(Buffer.concat([Buffer.from(m.ram.slice(0x4000,0x5800)),Buffer.from(m.ram.slice(0x6000,0x7800)),...m.dock.slice(1,4).map(v=>Buffer.from(v))]));
 }
 const same=captures[0].equals(captures[1]);results.push({name,same});if(!same){fs.writeFileSync(path.join(out,name+'.optimized.bin'),captures[0]);fs.writeFileSync(path.join(out,name+'.baseline.bin'),captures[1]);console.log('Mismatch',name);}
}
fs.writeFileSync(path.join(out,'background_scan_comparison.json'),JSON.stringify(results,null,2));assert(results.every(v=>v.same));console.log(results.length,'actual scenes match native background scan');
