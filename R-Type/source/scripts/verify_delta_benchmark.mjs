import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {api,z,root}from './r22_test_machine.mjs';
const out=path.join(root,'build/diagnostics/delta_benchmark'),code=fs.readFileSync(path.join(out,'decoder.bin'));
const sym=Object.fromEntries([...fs.readFileSync(path.join(out,'decoder.sym'),'utf8').matchAll(/(\w+): EQU 0x([0-9a-f]+)/ig)].map(v=>[v[1],parseInt(v[2],16)]));
let rows=[];
for(let n=0;n<60;n++){
 const old=fs.readFileSync(path.join(out,`sample_${150+n}.home.bin`)),next=fs.readFileSync(path.join(out,`sample_${151+n}.home.bin`));
 for(const kind of ['raw','scan','xor','sparse']){
  const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));m.portF4=0;m.portFF=2;m.ram.set(code,0x8000);m.ram.set(old.subarray(0x4000,0x5800),0x4000);m.ram.set(old.subarray(0x6000,0x7800),0x6000);
  const payload=['raw','scan'].includes(kind)?Buffer.concat([next.subarray(0x4000,0x5800),next.subarray(0x6000,0x7800)]):fs.readFileSync(path.join(out,`${kind}_${String(n).padStart(2,'0')}.bin`));m.ram.set(payload,0xa000);
  Object.assign(m.cpu,{pc:sym[kind],sp:0xffe0,h:0xa0,l:0,iff1:false,iff2:false});m.ram[0xffe0]=0;m.ram[0xffe1]=0xf0;let count=0,writes=0;const write=m.bus.write;m.bus.write=(a,v)=>{if((a>=0x4000&&a<0x5800)||(a>=0x6000&&a<0x7800))writes++;write(a,v);};const start=m.tstates;
  while(m.cpu.pc!==0xf000&&count++<500000)z.runZ80(m.cpu,m.bus,1,m);
  assert(count<500000,'Decoder hang '+kind);assert(Buffer.from(m.ram.slice(0x4000,0x5800)).equals(next.subarray(0x4000,0x5800)),kind+' bitmap '+n);assert(Buffer.from(m.ram.slice(0x6000,0x7800)).equals(next.subarray(0x6000,0x7800)),kind+' attrs '+n);
  rows.push({pair:n,kind,tstates:m.tstates-start,writes,bytes:payload.length});
 }
}
let summary={};for(const k of ['raw','scan','xor','sparse']){const rs=rows.filter(r=>r.kind===k);summary[k]={mean_tstates:rs.reduce((a,r)=>a+r.tstates,0)/rs.length,min_tstates:Math.min(...rs.map(r=>r.tstates)),max_tstates:Math.max(...rs.map(r=>r.tstates)),mean_writes:rs.reduce((a,r)=>a+r.writes,0)/rs.length};}
fs.writeFileSync(path.join(out,'z80_decoder_validation.json'),JSON.stringify({passed:true,consecutive_pairs:60,cases:rows.length,decoder_only:true,encoding_composition_and_game_logic_excluded:true,summary,rows},null,2));console.log(summary);
