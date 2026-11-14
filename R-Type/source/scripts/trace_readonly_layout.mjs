import fs from 'node:fs';import path from 'node:path';import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
const keys=new Uint8Array(8).fill(31),joy=new Uint8Array(2).fill(255),m=api.createMachine(keys,joy);
m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));
api.insertDock(m,fs.readFileSync(path.join(root,'build/ecm_native/RType_level1_ECM_TSPico_RAM_r9.dck')));api.resetMachine(m);
const pcs=new Set(),unusedAccesses=[],workAccesses={},dirtyAccesses={};let lastT=-1,pc=0,armed=false,updates=0;
const read=m.bus.read,write=m.bus.write;
m.bus.read=a=>{if(m.stepAdded===0&&m.tstates!==lastT&&a===m.cpu.pc){lastT=m.tstates;pc=a;pcs.add(a);if(a===0x8634)armed=true;if(a===0x8649)updates++;}
 if(armed){if(a>=0x8100&&a<0x8380){const k=pc.toString(16);dirtyAccesses[k]??={reads:0,writes:0,values:[]};dirtyAccesses[k].reads++;}if(((a>=0x5b00&&a<0x5d00)&&!(m.portF4&4))||(a>=0x8f2e&&a<0x8fae)){if(unusedAccesses.length<100)unusedAccesses.push({op:'read',pc,address:a,map:m.portF4});}
 if((m.portF4&8)&&a>=0x6000&&a<0x7800){const k=pc.toString(16);workAccesses[k]??={reads:0,writes:0,examples:[]};workAccesses[k].reads++;if(workAccesses[k].examples.length<3)workAccesses[k].examples.push(a);}}
 return read(a);};
m.bus.write=(a,v)=>{if(armed){if(a>=0x8100&&a<0x8380){const k=pc.toString(16);dirtyAccesses[k]??={reads:0,writes:0,values:[]};dirtyAccesses[k].writes++;if(!dirtyAccesses[k].values.includes(v))dirtyAccesses[k].values.push(v);}if(((a>=0x5b00&&a<0x5d00)&&!(m.portF4&4))||(a>=0x8f2e&&a<0x8fae)){if(unusedAccesses.length<100)unusedAccesses.push({op:'write',pc,address:a,value:v,map:m.portF4});}
 if((m.portF4&8)&&a>=0x6000&&a<0x7800){const k=pc.toString(16);workAccesses[k]??={reads:0,writes:0,examples:[]};workAccesses[k].writes++;if(workAccesses[k].examples.length<3)workAccesses[k].examples.push(a);}}
 write(a,v);};
for(let f=0;f<8000;f++){joy[0]=f>=800&&f<830?0xef:255;api.runFrame(m);if(f%2000===1999)console.log('layout trace frames',f+1,'updates',updates);}
const out=path.join(root,'build/readonly_ecm');fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'runtime_layout_trace.json'),JSON.stringify({frames:8000,updates,pcs:[...pcs].sort((a,b)=>a-b),unusedAccesses,workAccesses,dirtyAccesses},null,2));
console.log('trace complete',pcs.size,'executed addresses,',unusedAccesses.length,'candidate reserved-space accesses');
