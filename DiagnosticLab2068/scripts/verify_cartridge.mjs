// Execute the actual assembled Z80 code with the sibling TSRun machine model.
// Fault injection begins at diagnostic entry, preserving the passive boot limit.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const up=process.env.TSRUN_ROOT || path.resolve(root,'../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
const cart=fs.readFileSync(path.join(root,'build/diagnostic-v01.dck'));
const symbols=Object.fromEntries([...fs.readFileSync(path.join(root,'build/symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)]));
assert.ok(symbols.entry && symbols.menu_ready && symbols.fault_report);
const evidence=[];
function scenario(name,{native=false,region=0,bit=0,kind=null,choice=0}={}) {
 const keys=new Uint8Array(8).fill(31),joy=new Uint8Array(2).fill(255);
 const m=api.createMachine(keys,joy);
 m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));
 m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));
 assert.equal(api.insertDock(m,cart),null);api.resetMachine(m);
 if(!native){m.portF4=1;m.portFF=0x40;m.cpu.pc=symbols.entry;m.cpu.sp=0xbeef;m.ram.fill(0xa7);}
 const read=m.bus.read,write=m.bus.write,io=m.bus.ioWrite;
 let armed=false,done=false,entrySp=0,frames=0,transientFired=false,awaitingRun=false,subsequentRun=false;
 const writes=new Uint8Array(65536),reads=new Uint8Array(65536),ports=[];
 m.bus.read=a=>{
  if(a===m.cpu.pc && a===symbols.entry && !armed){armed=true;entrySp=m.cpu.sp;}
  if(armed && a===m.cpu.pc){
   assert.ok(a<0x2000,'diagnostic opcode fetch must remain low ROM');
   assert.equal(m.cpu.sp,entrySp,'diagnostic must not use SP');
   if(a!==symbols.entry)assert.equal(m.cpu.iff1,false,'no diagnostic interrupts after entry DI');
   if(awaitingRun && a===symbols.ram_start)subsequentRun=true;
   if((!awaitingRun || subsequentRun) && (a===symbols.menu_ready || a===symbols.fault_report)) done=true;
  }
  let v=read(a);
  if(armed && a>=0x4000 && !(m.portF4&(1<<(a>>13)))){
   reads[a]=1;
   if(kind==='stuck-low' && a>=region && a<region+0x4000)v&=~(1<<bit);
   if(kind==='transient' && a===0xc123 && !transientFired){v^=0x20;transientFired=true;}
  }
  return v;
 };
 m.bus.write=(a,v)=>{
  if(armed){assert.ok(a>=0x4000,'no writes to ROM/low addresses');assert.equal(m.portF4&(1<<(a>>13)),0,'HOME write must not be overlaid');writes[a]=1;}
  if(armed&&kind==='write-loss'&&a===0x8123)v&=~4;
  write(a,v);
 };
 m.bus.ioWrite=(p,v)=>{if(armed){assert.ok([0xf4,0xff,0xfe].includes(p&255));ports.push([p&255,v]);}io(p,v);};
 if(choice){ // Enter normally, then select a specific menu path in a second run.
  while(!done && frames++<4000)api.runFrame(m);
  assert.ok(done&&m.cpu.pc>=symbols.menu_ready);
  done=false;awaitingRun=true;keys[3]&=~(1<<choice);
  api.runFrame(m);keys[3]=31;
 }
 while(!done && frames++<6000)api.runFrame(m);
 assert.ok(done,`${name}: bounded run timed out at ${m.cpu.pc.toString(16)}`);
 if(choice){assert.ok(subsequentRun,'menu selection must start another test');assert.equal(m.cpu.i,choice===1?24:30,'selected algorithm completed');}
 if(!choice) for(let a=0x4000;a<=0xffff;a++){assert.equal(writes[a],1,`not written ${a.toString(16)}`);assert.equal(reads[a],1,`not read ${a.toString(16)}`);}
 const masks=[m.cpu.h2,m.cpu.l2,m.cpu.d2];
 if(kind==='stuck-low')assert.deepEqual(masks,[0x4000,0x8000,0xc000].map(r=>r===region?1<<bit:0));
 else if(kind==='transient'){assert.deepEqual(masks,[0,0,0x20]);assert.equal((m.cpu.xh<<8)|m.cpu.xl,0xc123);assert.equal(m.cpu.b2,0);assert.equal(m.cpu.c2,0x20);}
 else if(kind==='write-loss')assert.deepEqual(masks,[0,4,0]);
 else assert.deepEqual(masks,[0,0,0]);
 if(kind){
  // Continue through fault output, proving corrupt video RAM does not hang reporter.
  const before=ports.length;
  for(let i=0;i<250;i++)api.runFrame(m);
  assert.ok(ports.slice(before).some(([p,v])=>p===0xfe&&(v&16)),'speaker pulses emitted');
  assert.equal(m.cpu.sp,entrySp);assert.equal(m.cpu.iff1,false);
 }
 if(name==='healthy native LROS')fs.writeFileSync(path.join(root,'build/menu-screen.bin'),m.ram.slice(0x4000,0x5b00));
 const record={name,entry_observed:armed,frames,error_masks:masks.map(v=>v.toString(16).padStart(2,'0')),first_address:((m.cpu.xh<<8)|m.cpu.xl).toString(16),stack_unchanged:true,rom_opcode_only:true,covered_all_home:!choice,kind};
 evidence.push(record);console.log(JSON.stringify(record));
}
scenario('healthy native LROS',{native:true});
scenario('healthy direct entry');
for(const region of [0x4000,0x8000,0xc000])for(let bit=0;bit<8;bit++)scenario(`stuck-low ${region.toString(16)} D${bit}`,{region,bit,kind:'stuck-low'});
scenario('single transient C123 D5',{kind:'transient'});
scenario('write loss 8123 D2',{kind:'write-loss'});
scenario('menu pattern selection',{choice:1});
scenario('menu March selection',{choice:2});
const result={image_sha256:createHash('sha256').update(cart).digest('hex'),configuration:`TSRun sibling ${up}; stock TS2068 HOME/EXROM; injected after entry`,result:'PASS',cases:evidence,limitations:['Post-entry injected faults; bad RAM during OS launch not covered','No physical electrical/timing/refresh validation','No bank-switch stress or overnight firmware yet'],engine_sha256:createHash('sha256').update(fs.readFileSync(path.join(up,'machine.js'))).digest('hex'),cpu_sha256:createHash('sha256').update(fs.readFileSync(path.join(up,'z80.js'))).digest('hex')};
fs.writeFileSync(path.join(root,'build/verification.json'),JSON.stringify(result,null,2)+'\n');
