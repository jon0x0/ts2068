// Stop summaries keep counts in registers and never hide a recorded RAM fault.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const api=await import(pathToFileURL(path.resolve('../TSRun/machine.js')));
for(const home of [false,true]){
 const base=home?'build/home/':'build/',image=fs.readFileSync(base+(home?'diagnostic-home-u16.bin':'diagnostic-v02.dck'));
 const sym=Object.fromEntries([...fs.readFileSync(base+'symbols.txt','utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)]));
 const cases=[];
 function machine(){
  const keys=new Uint8Array(8).fill(31),m=api.createMachine(keys,new Uint8Array(2).fill(255));
  if(home)m.homeRom.set(image);else api.insertDock(m,image);
  api.resetMachine(m);m.portF4=home?0:1;m.portFF=64;m.cpu.sp=0xbeef;m.cpu.iff1=false;
  const seen=new Set(),read=m.bus.read;
  m.bus.read=a=>{if(a===m.cpu.pc){seen.add(a);assert.equal(m.cpu.sp,0xbeef);assert.ok(a<(home?0x4000:0x2000));}return read(a);};
  return {m,keys,seen};
 }
 function run(t,label,n=1000){for(let i=0;i<n&&!t.seen.has(sym[label]);i++)api.runFrame(t.m);assert.ok(t.seen.has(sym[label]),label);}
 for(const count of [0,1,0x1234,0xffff]){
  const t=machine();t.m.cpu.pc=sym.ram_cancel;t.m.cpu.a2=0x80;t.m.cpu.h2=t.m.cpu.l2=t.m.cpu.d2=0;t.m.cpu.b2=count>>8;t.m.cpu.c2=count&255;t.keys[1]=30;
  run(t,'fullsummary_poll');assert.ok(t.seen.has(sym.soakstop_ready));assert.ok(!t.seen.has(sym.menu_draw));
  assert.equal((t.m.cpu.b2<<8)|t.m.cpu.c2,count);
  const font=home?image.subarray(0x2000,0x2300):image.subarray(9+0x2200,9+0x2500);
  const hex=count.toString(16).toUpperCase().padStart(4,'0');
  for(let x=0;x<4;x++)for(let y=0;y<8;y++)assert.equal(t.m.ram[0x48cf+x+y*256],font[(hex.charCodeAt(x)-32)*8+y],'exact completed-pass count');
  for(let i=0;i<10;i++)api.runFrame(t.m);assert.ok(!t.seen.has(sym.menu_draw),'held stop quarantined');
  t.keys.fill(31);api.runFrame(t.m);t.keys[2]=30;run(t,'menu_ready');
  cases.push({name:'stopped count '+hex+' / held-key quarantine / new-key return',result:'PASS'});
 }
 {const t=machine();t.m.cpu.pc=sym.select_soak;run(t,'fill_1');t.keys[2]=30;run(t,'fullsummary_poll');assert.ok(t.seen.has(sym.soakstop_ready));assert.equal(t.m.cpu.c2,0);cases.push({name:'actual first-pass interruption before any completed pass',result:'PASS'});}
 {const t=machine();t.m.cpu.pc=sym.ram_cancel;t.m.cpu.a2=128;t.m.cpu.l2=4;run(t,'fault_report');assert.ok(!t.seen.has(sym.soakstop_ready));cases.push({name:'recorded RAM mismatch wins over stopped/no-failures message',result:'PASS'});}
 {const t=machine();t.m.cpu.pc=sym.ram_cancel;t.m.cpu.a2=128;t.m.bus.write=()=>{};run(t,'fullsummary_poll');t.keys[2]=30;run(t,'menu_ready');cases.push({name:'lost display writes cannot prevent stop acknowledgement',result:'PASS'});}
 fs.writeFileSync(base+'soak-verification.json',JSON.stringify({image_sha256:createHash('sha256').update(image).digest('hex'),result:'PASS',cases,limitations:['Model execution and display-memory checks; physical validation pending','16-bit completed-pass count wraps at65536; stopped run has no finite completion endpoint']},null,2)+'\n');
 console.log((home?'HOME':'Cartridge')+' soak stop summary/count/fault priority/acknowledgement PASS');
}
