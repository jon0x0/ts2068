import fs from'node:fs';import path from'node:path';import{root,up,api}from'./r22_test_machine.mjs';
const out=path.join(root,'build/fullgame/true_black_r31'),results=[];
for(let level=1;level<=8;level++){
 const joy=new Uint8Array(2).fill(255),m=api.createMachine(new Uint8Array(8).fill(31),joy);m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));api.insertDock(m,fs.readFileSync(path.join(out,`Level_${level}_true_black_r31.dck`)));api.resetMachine(m);
 let updates=0;const read=m.bus.read,write=m.bus.write,producers=new Map();m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc){if(a===0x8634)m.ram[0x91f2]=201;if(a===0x8b06&&read(0x7aa4)>0)updates++;}return read(a);};m.bus.write=(a,v)=>{if(a>=0x6000&&a<0x7800&&!(m.portF4&8)&&(v&64)&&(!(v&7)||!(v&56))){const key=m.cpu.pc.toString(16);producers.set(key,(producers.get(key)||0)+1);}write(a,v);};
 const samples=[];
 for(let f=0;f<4500;f++){joy[0]=f>=800&&f<830?239:255;api.runFrame(m);if([200,700,1000,1300,2000,3000,4000].includes(f)){
  let bad=0,bright=0;for(let y=0;y<192;y++)for(let x=0;x<32;x++){const o=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x,a=m.ram[0x6000+o],p=m.ram[0x4000+o];if(a&64){bright++;if((!(a&56)&&p!==255)||(!(a&7)&&p!==0))bad++;}}
  samples.push({frame:f,bad,bright});if(f===2000&&level===1)fs.writeFileSync(path.join(out,'level1_live.home.bin'),m.ram);
 }}
 const r={level,updates,samples,producers:[...producers.entries()].sort((a,b)=>b[1]-a[1]).slice(0,12)};results.push(r);console.log(JSON.stringify(r));
}
fs.writeFileSync(path.join(out,'live_validation.json'),JSON.stringify(results,null,2));
