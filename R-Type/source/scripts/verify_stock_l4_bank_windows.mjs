import fs from 'node:fs';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {stockFixture} from './stock_fixture.mjs';
const f=stockFixture(4),{m,call,out}=f;
const layout=JSON.parse(fs.readFileSync(out+'/shared_cache_layout.json'));
const c=JSON.parse(fs.readFileSync(out+'/l4_procedural_contract.json'));
const sy=Object.fromEntries([...fs.readFileSync(out+'/stock_l4_procedural.sym','utf8').matchAll(/(\w+): EQU 0x([0-9a-f]+)/ig)].map(x=>[x[1],parseInt(x[2],16)]));
const negative=process.argv.includes('--negative');if(negative){for(const name of ['get_desc','palette_token']){const at=sy[name]&8191;assert.equal(m.dock[1][at],0xf3);m.dock[1][at]=0;}}
let inside=false,fetches=0,mappedFetches=0,enabledFetches=0,entries=0,last=-1;
const rd=m.bus.read;
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===sy.construct){inside=true;entries++;}if(inside){fetches++;if(m.cpu.iff1)enabledFetches++;if(m.portF4!==3){mappedFetches++;assert(!m.cpu.iff1,'Interrupts enabled during constructor ROM mapping: PC '+a.toString(16)+' F4 '+m.portF4.toString(16));}}if(a===sy.CACHED_FRAME)inside=false;}return rd(a);};
for(const iff of [false,true])for(const frame of c.frames){m.ram.fill(0,0x7e00,0x8080);m.ram[layout.symbols.CTX+16]=iff?4:0;call(0x2006,{a:frame,b:2,c:2,iff1:iff,iff2:iff});assert.equal(m.portF4,3);assert.equal(m.cpu.iff1,false);}
assert(entries>=96);assert(mappedFetches>1000&&enabledFetches>1000);
assert(!negative,'Negative control was not detected');
const probe=spawnSync(process.execPath,['scripts/verify_stock_l4_bank_windows.mjs','--negative'],{encoding:'utf8'});assert(probe.status!==0&&/Interrupts enabled during constructor ROM mapping/.test(probe.stderr),probe.stdout+probe.stderr);
const r={passed:true,negativeControlDetected:true,level:4,cases:c.frames.length*2,entries,fetches,mappedFetches,enabledFetches,romWrites:f.romWrites,scope:'Every constructor phase with saved caller IFF off/on: all mapped-source instruction windows stay DI; ordinary RAM construction resumes interrupts; complements actual256-vector return probes, not hardware timing'};
fs.writeFileSync(out+'/l4_bank_windows_validation.json',JSON.stringify(r,null,2));console.log(r);
