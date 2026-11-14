import fs from'node:fs';import path from'node:path';import{root,api}from'./r22_test_machine.mjs';import{fullgameFixture}from'./restart_fixture.mjs';
const out=path.join(root,'build/diagnostics/level3_late_waves');fs.mkdirSync(out,{recursive:true});
const{m,joy,controller,image}=fullgameFixture();let updates=0,starts=0,deaths=0,tape=0,last=-1,frame=0,minSP=65535,history=[];const read=m.bus.read;
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x8634&&frame<12000)m.ram[0x91f2]=201;if(a===0x8721)starts++;if(a===0x91f2)deaths++;if(a===0xfe03)tape++;if(a===0x8b06&&read(0x7aa4)>0)updates++;if(m.cpu.sp>=0xc000)minSP=Math.min(minSP,m.cpu.sp);}return read(a);};
for(frame=0;frame<25000;frame++){
 m.keyMatrix.fill(31);if(frame>=600&&frame<700)m.keyMatrix[3]=27;
 // Periodic fire pulses let title/continue screens progress naturally. Moving
 // the ship deliberately exercises real collisions, deaths and restoration.
 joy[0]=frame<800?255:(frame%180<120?239:255);
 if(frame>1500&&m.dock[3][0x1aa4]>0)joy[0]&=frame%800<200?254:frame%800<400?253:frame%800<600?251:247;
 if(frame===12000)m.ram[0x91f2]=image[0x51f2];api.runFrame(m);
 if(frame%1000===0){const r={frame,updates,starts,deaths,tape,region:controller.region,pc:m.cpu.pc,sp:m.cpu.sp,minSP,mode:m.portFF,level:m.dock[3][0x119c],musicSP:m.ram[0xfd80]|m.ram[0xfd81]<<8};history.push(r);console.log(JSON.stringify(r));if(frame%10000===0){fs.writeFileSync(path.join(out,`frame${frame}.home.bin`),m.ram);for(const b of[1,2,3])fs.writeFileSync(path.join(out,`frame${frame}.dock${b}.bin`),m.dock[b]);}}
}
fs.writeFileSync(path.join(out,'stress.json'),JSON.stringify({history,updates,starts,deaths,tape,frames:frame},null,2));
