import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{root,api}from'./r22_test_machine.mjs';import{demandFixture}from'./cached_disk_fixture.mjs';
const out=path.join(root,'build/diagnostics/repeated_input_r34');fs.mkdirSync(out,{recursive:true});
const{m,joy,controller:c}=demandFixture();let frame=0,updates=0,last=-1,checks=0,gameovers=0,starts=0,history=[],lastInput=null;const read=m.bus.read;
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;
 if(a===0x92a4)gameovers++; if(a===0x8721){starts++;history.push({frame,starts,gameovers,mode:read(0x74fb),decoder:read(0x74fc)|read(0x74fd)<<8,bindings:Array.from({length:12},(_,i)=>read(0x7780+i))});}
 if(a===0x8b06&&read(0x7aa4)>0)updates++;
 if(a===0x1a6d){checks++;lastInput={frame,input:read(0x74fa),a:m.cpu.a,joy:[...joy],decoder:read(0x74fc)|read(0x74fd)<<8,bindings:Array.from({length:12},(_,i)=>read(0x7780+i))};if(read(0x74fa)&15){fs.writeFileSync(path.join(out,'failure.home.bin'),m.ram);fs.writeFileSync(path.join(out,'failure.dock3.bin'),m.dock[3]);throw Error('Phantom direction '+JSON.stringify(lastInput));}}
}return read(a);};
for(;frame<40000;frame++){
 m.keyMatrix.fill(31);joy[0]=c.booted&&frame%180<90?239:255;joy[1]=255;api.runFrame(m);
 assert(!c.fatalSeen,'Loader failed');
}
const result={frame,checks,gameovers,starts,history,lastInput,complete:frame===40000};fs.writeFileSync(path.join(out,'result.json'),JSON.stringify(result,null,2));console.log(result);
