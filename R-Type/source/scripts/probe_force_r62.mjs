import fs from'node:fs';import path from'node:path';import{api,z}from'./r22_test_machine.mjs';import{out,demandFixture}from'./boss_motion_fixture_r61.mjs';
const{m,joy,controller:c}=demandFixture();let boot=-1,last=-1,updates=0;const rr=m.bus.read;m.bus.read=a=>{if(a===m.cpu.pc&&m.stepAdded===0&&last!==m.tstates){last=m.tstates;if(a===0x8634)m.ram[0x91f2]=201;if(a===0x94f1&&rr(0x7aa4)>0)updates++;}return rr(a);};for(let f=0;f<10000&&updates<60;f++){if(c.booted&&boot<0)boot=f;joy[0]=boot>=0&&f-boot>=800&&f-boot<840?239:255;api.runFrame(m);}
function call(pc){Object.assign(m.cpu,{pc,sp:0xffe0,iff1:false,iff2:false});m.ram[0xffe0]=0;m.ram[0xffe1]=0xf0;let i=0;for(;m.cpu.pc!==0xf000&&i<1000000;i++)z.runZ80(m.cpu,m.bus,1,m);if(i===1000000)throw Error('loop '+m.cpu.pc.toString(16));}
const saved={ram:Buffer.from(m.ram),dock:m.dock.map(v=>Buffer.from(v))};const results=[];
for(const stamp of[false,true]){m.ram.set(saved.ram);m.dock.forEach((v,i)=>v.set(saved.dock[i]));m.portF4=9;const q=m.dock[3];let x=q[0x1aa1],y=q[0x1aa2];q[0x1aa8]=3;q[0x1aa9]=x;q[0x1aaa]=y;q[0x1abe]=1;q[0x1aa3]=0;q[0x1aab]=0;q[0x1aae]=0;q[0x1a98]=0;
if(stamp)for(let dx=0;dx<4;dx++)q[0x1e00+y*32+x+dx]=3;
const rows=[];for(let u=0;u<12;u++){call(0x95f6);rows.push({u,pod:q[0x1aa8],attach:q[0x1aa3],x:q[0x1aa9],y:q[0x1aaa],hits:q[0x1a95],ids:[...q.slice(0x1ad8,0x1ae0)]});}results.push({stamp,x,y,cells:[...q.slice(0x1e00+y*32+x,0x1e00+y*32+x+4)],rows});}
fs.writeFileSync(path.join(out,'force_probe.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));
