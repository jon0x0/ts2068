import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {root,up,api}from './r21_test_machine.mjs';
const info=JSON.parse(fs.readFileSync(path.join(root,'build/art_assets/terrain_groups.json')));const masks=Array.from({length:428},(_,x)=>info.runs.filter(v=>v[0]<=x).at(-1)[1]);const results=[];
for(const target of ['sram','rom']){
 const cart=fs.readFileSync(path.join(root,target==='rom'?'build/readonly_ecm/RType_ECM_ROM_candidate.dck':'build/ecm_native/RType_level1_ECM_TSPico_RAM_r21.dck'));const joy=new Uint8Array(2).fill(255),m=api.createMachine(new Uint8Array(8).fill(31),joy);m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));api.insertDock(m,cart);api.resetMachine(m);
 let last=-1,initial=0,stream=0,variants=0;let pending=null;const contexts=new Map(),read=m.bus.read;
 const renderer=fs.readFileSync(path.join(root,'build',target==='rom'?'readonly_ecm':'ecm_native','renderer.bin'));const init=target==='rom'?fs.readFileSync(path.join(root,'build/readonly_ecm/initial_terrain.bin')):renderer;const ret=(target==='rom'?0x1160:0x1400)+init.indexOf(Buffer.from([0xcd,0x20,0x09]))+3;
 m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;
  if(a===0x920){const source=m.cpu.h<<8|m.cpu.l,attr=m.cpu.a;if((attr&128)&&source>=0xd900&&source<0xe600&&read(0x7a9c)===0){const de=m.cpu.d<<8|m.cpu.e,row=(de>>5)&31,x=((read(0x7a84)-8)&255)*4+(de&31),expected=((masks[x]??0)>>row&1)*8;pending={expected,source,attr,row,x};}}
  if(a===ret&&pending){assert.equal(m.cpu.a&8,pending.expected,target+' initial '+JSON.stringify(pending));initial++;variants+=!!pending.expected;const s=contexts.get(pending.source)??new Set();s.add(pending.expected);contexts.set(pending.source,s);pending=null;}
  if(a===0x89fe){const attr=m.cpu.a;if(attr&128){const row=(m.cpu.xl)-128>>2;const x=read(0x7a84)*4+read(0x7a83)-1;const expected=((masks[x]??0)>>row&1)*8;assert.equal(attr&8,expected,target+' streaming row'+row+' col'+x);stream++;variants+=!!expected;}}
 }return read(a);};
 for(let f=0;f<4000;f++){joy[0]=f>=800&&f<830?239:255;api.runFrame(m);}
 assert(initial>100);assert(stream>100);assert(variants>50);const reused=[...contexts.values()].filter(s=>s.size>1).length;
 results.push({target,bin_sha256:crypto.createHash('sha256').update(cart.subarray(9)).digest('hex'),initial_cells:initial,stream_cells:stream,cool_cells:variants,reused_source_cells_with_distinct_palettes:reused,passed:true});console.log(results.at(-1));
}
fs.writeFileSync(path.join(root,'build/diagnostics/instance_groups_r21.json'),JSON.stringify(results,null,2));
