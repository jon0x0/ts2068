import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {z,root}from './r22_test_machine.mjs';
export function runtimeControls(m,kind,level){
 const savedRead=m.bus.read,savedWrite=m.bus.write,ram=Buffer.from(m.ram),dock=m.dock.map(v=>Buffer.from(v)),cpu={...m.cpu};
 const layout=JSON.parse(fs.readFileSync(path.join(root,`build/cartridges/integration_work/level${String(level).padStart(2,'0')}/player_ram_layout.json`))),flags=kind==='tap'?0x5bc0:layout.clock_flags[0];
 const baselineMap=kind==='tap'?9:3,clock=kind==='tap'?0x9501:0x0d90;let spawnCount=0,last=-1;
 function invoke(pc,regs={}){m.portF4=baselineMap;m.portFF=2;Object.assign(m.cpu,{pc,sp:0xffe0,iff1:false,iff2:false,halted:false,eiDelay:false,...regs});m.ram.set([0,0xf0],0xffe0);let steps=0;while(m.cpu.pc!==0xf000&&steps++<2000000)z.runZ80(m.cpu,m.bus,1,m);assert(steps<2000000,kind+' control-call hang');assert.equal(m.portF4,baselineMap);}
 function restore(){m.ram.set(ram);m.dock.forEach((v,i)=>v.set(dock[i]));m.keyMatrix.fill(31);m.joystick.fill(255);m.portF4=baselineMap;m.portFF=2;}
 function init(){restore();if(kind==='tap')m.dock[7].fill(0,0x1680,0x1880);else m.ram.fill(0,0x5b00,0x5d00);m.ram[flags+2]=0;m.ram[flags+3]=0;m.ram[flags+13]=0;m.bus.write(0x7aa1,8);m.bus.write(0x7aa2,10);m.bus.write(0x7aa4,3);m.bus.write(0x7a98,255);invoke(kind==='tap'?0xfb37:0x2409,{a:3});}
 const pos=()=>kind==='tap'?[m.dock[7][0x1680],m.dock[7][0x1681]]:[m.ram[0x5b00],m.ram[0x5b01]];
 try{
  init();const movement=[];for(const[mask,count]of [[8,7],[0,1],[1,3],[0,1],[2,3],[0,1],[4,7]])for(let i=0;i<count;i++){m.joystick[0]=255^mask;invoke(0x8b06);invoke(kind==='tap'?0xfb37:0x2400,{a:0});movement.push(pos());}
  init();m.ram.fill(0,0x5eb4,0x5ee4);const rawRead=m.bus.read;m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x9d5c)spawnCount++;}return rawRead(a);};const taps=[];
  for(let i=0;i<6;i++){const before=spawnCount;for(let tick=0;tick<20;tick++){m.joystick[0]=tick<3?127:255;invoke(kind==='tap'?0xfb00:0x1003);}taps.push(spawnCount-before);}m.bus.read=rawRead;
  const collisions=[];for(const which of ['shown','future','empty','terrain','reused']){
   init();m.ram.fill(0,0x5eb4,0x5ee4);m.ram[0x8501]=3;m.ram[0x8506]=0x12;m.ram[0x8507]=0x34;m.bus.write(0x7aa4,2);for(let i=0;i<640;i++)m.bus.write(0x7e00+i,0);
   const owners=kind==='tap'?m.dock[7]:m.ram,base=kind==='tap'?0x1880:layout.allocations.published_owner_map[0];owners.fill(0,base,base+640);
   invoke(clock,{a:2});m.ram.set([0x18,8,6],0x5eb4);if(which==='shown'||which==='reused')owners[base+6*32+9]=0x81;if(which==='future')m.bus.write(0x7e00+6*32+9,0x81);if(which==='terrain')owners[base+6*32+9]=0xfb;
   invoke(clock,{a:1});const pending=kind==='tap'?m.dock[2][0x1fb0]:m.ram[layout.allocations.projectile_state[0]+0x30];if(which==='reused')m.ram[0x8506]^=1;invoke(0x9da5);collisions.push({which,pending,hp:m.ram[0x8501]});
  }
  assert.deepEqual(taps,[1,1,1,1,1,1],kind+' normal short shots');assert.deepEqual(collisions.map(v=>v.hp),[2,3,3,3,3]);return{passed:true,movement,taps,collisions,scope:'Direct execution of actual initialized runtime input/player/IRQ/shot/native-damage paths, IRQ disabled during individual component calls; not hardware response timing'};
 }finally{m.bus.read=savedRead;m.bus.write=savedWrite;restore();Object.assign(m.cpu,cpu);}
}
