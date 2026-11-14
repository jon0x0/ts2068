import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api}from'./r22_test_machine.mjs';import{out,symbols,demandFixture}from'./selected_art_fixture.mjs';
const results=[];
for(const [kind,expected,options]of[['checksum','E2',{corrupt:true}],['alias','E2',{alias:true}],['timeout','E0',{timeout:true}],['missing','03',{missing:true}]]){
 const{m,joy,controller:c}=demandFixture(options);let forced=false;
 for(let frame=0;frame<6000&&!c.fatalSeen;frame++){
  joy[0]=c.booted&&frame%180<90?239:255;api.runFrame(m);
  if(kind==='missing'&&c.booted&&!forced&&frame>1800){m.portF4=9;m.cpu.pc=0x0a08;forced=true;}
 }
 assert(c.fatalSeen,kind+' failed to halt safely');const message=Buffer.from(m.ram.slice(symbols.error_text,symbols.error_text+23)).toString();assert(message.includes(expected),message);results.push({kind,expected,message,page:m.ram[0xd600],operation:m.ram[0xd609],mounts:c.mounts,passed:true});console.log(results.at(-1));if(kind==='missing')fs.writeFileSync(path.join(out,'missing_file.home.bin'),m.ram);
}
fs.writeFileSync(path.join(out,'failure_validation.json'),JSON.stringify(results,null,2));
