import fs from 'node:fs';
import {createMachine,insertDock,resetMachine,runFrame} from './tsrun/machine.js';
const root=new URL('.',import.meta.url),m=createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(31));
const err=insertDock(m,new Uint8Array(fs.readFileSync(new URL('split-personality-evolution.dck',root))));if(err)throw Error(err);resetMachine(m);
const old=fs.existsSync(new URL('timing-calibration.json',root))?JSON.parse(fs.readFileSync(new URL('timing-calibration.json',root))):{};
const values={},observed={};const io=m.bus.ioWrite;
m.bus.ioWrite=(p,v)=>{
 if((p&255)===255&&m.cpu.pc===0x44){
  const path=m.ram[0xfe09],entry=(m.ram[0xfe01]|m.ram[0xfe02]<<8),next=(m.ram[0xfe04]|m.ram[0xfe05]<<8);
  const key=path===0?'idle':(path===1?'prep'+((next-0x4000)/226):'switch'+((entry-0x4000)/226));
  // Fast holding frame goes straight to the kernel from its top-border rows.
  if((m.ram[0xfe08]===1)&&m.ram[0xfe38]>0){io(p,v);return;}
  const t=m.tstates-m.frameStart;
  const delay=(old[key]??116)+8962-t;
  if(key in values&&values[key]!==delay)throw Error('Nonconstant path '+key+' '+values[key]+' '+delay);
  values[key]=delay;observed[key]=t;
 }
 io(p,v);
};
for(let f=0;f<1150;f++)runFrame(m);
fs.writeFileSync(new URL('timing-calibration.json',root),JSON.stringify({...old,...values},null,2));
console.log({paths:Object.keys(values).length,minDelay:Math.min(...Object.values(values)),maxDelay:Math.max(...Object.values(values)),observedFirst:Object.entries(observed).slice(0,5)});
