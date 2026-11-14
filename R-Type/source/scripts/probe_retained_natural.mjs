import fs from'node:fs';import path from'node:path';import{root,api}from'./r22_test_machine.mjs';import{demandFixture}from'./retained_fix_fixture.mjs';
const out=path.join(root,'build/diagnostics/retained_natural_r40');fs.mkdirSync(out,{recursive:true});const{m,joy,controller:c}=demandFixture();let boot=-1,frame=0,last=-1,updates=0,starts=0,deaths=0,nativeDeath=null,lastUpdate=0,savedStall=false;const read=m.bus.read;
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x8634){if(nativeDeath===null)nativeDeath=m.ram[0x91f2];}if(a===0x8721)starts++;if(a===0x91f2)deaths++;if(a===0x8b06&&read(0x7aa4)>0){updates++;lastUpdate=frame;}}return read(a);};
for(;frame<30000;frame++){
 if(c.booted&&boot<0)boot=frame;m.keyMatrix.fill(31);if(boot>=0&&frame-boot>=600&&frame-boot<700)m.keyMatrix[3]=27;
 joy[0]=255;joy[1]=255;
 if(boot>=0&&frame-boot>=800&&frame%180<90)m.keyMatrix[5]&=30; // keyboard0/Fire
 if(frame>5000&&m.dock[3][0x1aa4]>0){const phase=frame%800;if(phase<200)m.keyMatrix[5]&=29;else if(phase<400)m.keyMatrix[6]&=27;else if(phase<600)m.keyMatrix[2]&=30;else m.keyMatrix[2]&=29;}
 if(frame===12000&&nativeDeath!==null)m.ram[0x91f2]=nativeDeath;
 api.runFrame(m);
 if(frame>4000&&frame-lastUpdate>700&&!savedStall){savedStall=true;fs.writeFileSync(path.join(out,'possible_stall.home.bin'),m.ram);for(const b of[1,2,3])fs.writeFileSync(path.join(out,`possible_stall.dock${b}.bin`),m.dock[b]);console.log('Possible stall',frame,m.cpu.pc,m.cpu.sp);}
 if(frame%5000===0){fs.writeFileSync(path.join(out,`frame${frame}.home.bin`),m.ram);console.log({frame,updates,starts,deaths,pc:m.cpu.pc,sp:m.cpu.sp});}
}
fs.writeFileSync(path.join(out,'result.json'),JSON.stringify({frame,updates,starts,deaths,lastUpdate,savedStall},null,2));
