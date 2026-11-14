import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api}from'./r22_test_machine.mjs';import{out,symbols,demandFixture}from'./boss_motion_fixture_r61.mjs';const rows=[];
for(const[kind,expected,options]of[['checksum','E2',{corrupt:true}],['alias','E2',{alias:true}],['timeout','E0',{timeout:true}],['missing','03',{missing:true}]]){
 const{m,controller:c}=demandFixture(options);let frame=0;
 for(;frame<25000&&!c.fatalSeen;frame++){m.keyMatrix.fill(31);if(kind==='missing'&&frame>8&&m.ram[0xd610]===1)m.keyMatrix[3]&=~2;api.runFrame(m);}
 assert(c.fatalSeen,kind+' no safe halt '+JSON.stringify({frame,pc:m.cpu.pc,mounts:c.mounts}));const message=Buffer.from(m.ram.slice(symbols.error_text,symbols.error_text+23)).toString();assert(message.includes(expected),kind+message);assert(!c.booted,'Unverified startup launched');assert.equal(m.ram[0xfd4a],0);fs.writeFileSync(path.join(out,`error_${kind}.home.bin`),m.ram);rows.push({kind,expected,message,operation:m.ram[0xd609],page:m.ram[0xd600],frame,passed:true});console.log(rows.at(-1));
}
fs.writeFileSync(path.join(out,'failure_validation.json'),JSON.stringify(rows,null,2));
