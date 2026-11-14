import fs from 'node:fs';
import assert from 'node:assert/strict';
import {stockFixture} from './stock_fixture.mjs';
import {z} from './r22_test_machine.mjs';
const level=Number(process.argv[2]||1),f=stockFixture(level),{m,out}=f;
const initial=Buffer.from(m.ram),cpu={...m.cpu},results=[];
for(let v=0;v<256;v++){
 m.ram.set(initial);m.portF4=3;m.portFF=2;
 Object.assign(m.cpu,cpu,{pc:0xf000,sp:0xffe0,iff1:true,iff2:true,eiDelay:false,halted:false,i:0x84,im:2});
 const target=m.bus.read(0x8400+v)+256*m.bus.read(0x8401+v);
 assert.equal(target,0x8383,'Invalid vector '+v);
 assert(z.irqZ80(m.cpu,m.bus)>0);
 // Emulator injects FF; explicitly choose each computed vector target.
 m.cpu.pc=target;let steps=0;
 while((m.cpu.pc!==0xf000||m.cpu.sp!==0xffe0)&&steps++<30000)z.runZ80(m.cpu,m.bus,1,m);
 assert(steps<30000,'IRQ did not return '+v);
 assert.equal(m.portF4,3);assert.equal(m.cpu.i,0x84);assert(m.cpu.iff1);
 results.push({vector:v,target,steps});
}
const result={passed:true,level,cases:results.length,romWrites:f.romWrites,scope:'Actual IRQ return probes for all 256 computed targets; explicit target injection in fixed-FF emulator, not hardware vector measurement',results};
fs.writeFileSync(out+'/stock_vector_validation.json',JSON.stringify(result,null,2));console.log({passed:true,level,vectors:results.length,romWrites:f.romWrites});
