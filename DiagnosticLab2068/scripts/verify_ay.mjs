import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {pathToFileURL,fileURLToPath} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js'))),cpuapi=await import(pathToFileURL(path.join(up,'z80.js')));
const cart=fs.readFileSync(path.join(root,'build/diagnostic-v02.dck'));
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)]));
Object.assign(sym,Object.fromEntries([...fs.readFileSync(path.join(root,'build/cpu-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)])));
const evidence=[];
function machine({irq=false,readFault=null,writeFault=null,ioFault=null}={}){
 const keys=new Uint8Array(8).fill(31),joy=new Uint8Array(2).fill(255),m=api.createMachine(keys,joy);
 m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));
 assert.equal(api.insertDock(m,cart),null);api.resetMachine(m);m.portF4=1;m.portFF=0x40;m.cpu.pc=sym.menu_draw;m.cpu.sp=0xbeef;m.cpu.iff1=false;m.ram.fill(0);
 const seen=new Set(),ports=[],r=m.bus.read,w=m.bus.write,io=m.bus.ioWrite,ir=m.bus.ioRead;
 m.bus.read=a=>{if(a===m.cpu.pc){seen.add(a);assert.ok(a<0x2000 || (a>=0x4000&&a<0x5fd0&&(m.portF4&4)) || (a>=0x8000&&a<0x8200) || (a>=0xc000&&a<0xc100),'opcode outside declared anchors');if(!irq)assert.equal(m.cpu.sp,0xbeef);}
 let v=r(a);return readFault?readFault(m,a,v):v;};
 m.bus.write=(a,v)=>{assert.ok(a>=0x4000 || (a>=0x2000 && (m.portF4&2)),`unexpected low-memory write ${a.toString(16)} pc ${m.cpu.pc.toString(16)}`);w(a,writeFault?writeFault(m,a,v):v);};
 m.bus.ioWrite=(p,v)=>{ports.push([p,v]);io(p,v);};m.bus.ioRead=p=>ioFault?ioFault(m,p,ir(p)):ir(p);
 return {m,keys,joy,seen,ports};
}
function frames(t,n){for(let i=0;i<n;i++)api.runFrame(t.m);}
function until(t,label,budget=2000){const a=sym[label];assert.ok(a!==undefined,label);for(let i=0;i<budget&&!t.seen.has(a);i++)api.runFrame(t.m);assert.ok(t.seen.has(a),`did not reach ${label}; pc=${t.m.cpu.pc.toString(16)}`);}
function enter(t,label){t.seen.clear();t.m.cpu.pc=sym[label];until(t,label.endsWith('_ready')?label:label.replace('load_','')+'_ready');frames(t,2);}
function record(name,details={}){evidence.push({name,result:'PASS',...details});console.log(name+': PASS');}
const captures=[];
{const t=machine();const r=t.m.bus.read;
 t.m.bus.read=a=>{if(a===t.m.cpu.pc&&a===sym.ay_listen_delay){const step=t.m.cpu.i;if(!captures.some(s=>s.step===step)){
  const expected=JSON.parse(fs.readFileSync(path.join(root,'build/manifest-v02.json'))).ay_playback.steps[step];
  assert.ok(step<24);assert.deepEqual([...t.m.ay.regs].slice(0,14),expected.registers);
  const at=0x58c0+(expected.highlight_row&15)*32+(expected.highlight_column&24);
  assert.deepEqual([...t.m.ram.slice(at,at+8)],new Array(8).fill(0x46));assert.equal(t.m.ram[0x5aa1+step],0x46);
  assert.equal(t.m.portF4,1);assert.equal(t.m.cpu.sp,0xbeef);assert.equal(t.m.ay.regs[7]&0xc0,0);
  captures.push({step,name:expected.name,registers:[...t.m.ay.regs].slice(0,14),highlight:at.toString(16)});
  if(step===6)fs.writeFileSync(path.join(root,'build/ay-listen-active-v02.bin'),t.m.ram.slice(0x4000,0x5b00));
 }}return r(a);};
 t.m.cpu.pc=sym.ay_test;until(t,'menu_ready',6000);assert.equal(captures.length,24);assert.equal(t.m.ay.regs[8]|t.m.ay.regs[9]|t.m.ay.regs[10],0);assert.equal(t.m.ay.regs[7],63);
 for(let c=0;c<3;c++){const notes=captures.slice(c*4,c*4+4).map(x=>x.registers[c*2]|x.registers[c*2+1]<<8);assert.deepEqual(notes,[1000,500,250,125]);}
 assert.deepEqual(captures.slice(12,15).map(s=>s.registers[8]),[3,8,15]);assert.deepEqual(captures.slice(15,18).map(s=>s.registers[6]),[31,8,1]);assert.deepEqual(captures.slice(18,22).map(s=>s.registers[13]),[9,13,10,8]);
 record('all24 AY steps: channel periods, volumes, noise, envelopes, chord, silence and visual highlights');
}
for(const step of [0,4,8,12,15,18,22,23]){
 const t=machine();let reached=false;const r=t.m.bus.read;t.m.bus.read=a=>{if(a===t.m.cpu.pc&&a===sym.ay_listen_delay&&t.m.cpu.i===step)reached=true;return r(a);};
 t.m.cpu.pc=sym.ay_test;for(let f=0;f<6000&&!reached;f++)api.runFrame(t.m);assert.ok(reached);t.keys[2]&=~1;t.seen.clear();until(t,'menu_ready',300);assert.equal(t.m.ay.regs[8]|t.m.ay.regs[9]|t.m.ay.regs[10],0);assert.equal(t.m.ay.regs[7],63);assert.equal(t.m.portF4,1);record('Q stops AY step'+step+' and mutes');
}
{const t=machine({readFault:(m,a,v)=>m.portF4===5&&a>=0x4400&&a<0x4580?255:v});t.m.cpu.pc=sym.ay_test;until(t,'menu_ready',6000);assert.equal(t.m.ay.regs[8]|t.m.ay.regs[9]|t.m.ay.regs[10],0);assert.equal(t.m.cpu.sp,0xbeef);record('corrupt AY table remains bounded and joystick port input-safe');}
{const t=machine({writeFault:(m,a,v)=>0});t.m.cpu.pc=sym.ay_test;until(t,'menu_ready',6000);assert.equal(t.m.ay.regs[8]|t.m.ay.regs[9]|t.m.ay.regs[10],0);assert.equal(t.m.cpu.sp,0xbeef);record('AY sequence completes with all HOME display writes lost');}
fs.writeFileSync(path.join(root,'build/ay-verification.json'),JSON.stringify({image_sha256:createHash('sha256').update(cart).digest('hex'),result:'PASS',configuration:'TSRun stock TS2068 ROM execution; actual AY register writes and HOME highlight attributes',cases:evidence,steps:captures,limitations:['No physical sound measurement or analog output certification','Original ROM-only/active fetch dependencies remain']},null,2)+'\n');
