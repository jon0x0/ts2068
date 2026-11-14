import fs from'node:fs';import path from'node:path';import{root,api}from'./r22_test_machine.mjs';import{demandFixture}from'./demand_disk_fixture.mjs';
const out=path.join(root,'build/diagnostics/l2_emergence');fs.mkdirSync(out,{recursive:true});const{m,joy,controller:c}=demandFixture();let boot=-1,frame=0,last=-1,rows=[],seen=new Set(),pending=null;const read=m.bus.read;
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x8634)m.ram[0x91f2]=201;if([0x8cfd,0x8dd3,0x8d65,0x8e29].includes(a)&&read(0x719c)===50){const id=read(0x7a9c),p=m.cpu.h*256+m.cpu.l,w=m.cpu.e,h=m.cpu.d;if(id>111){const key=[id,p,w,h].join('_');if(!seen.has(key)){seen.add(key);const r={frame,id,level_id:id-111,p,w,h,y:m.cpu.b,x:m.cpu.c,variant:a};rows.push(r);if(rows.length<100){pending=r;console.log(r);}}}}}return read(a);};
for(frame=0;frame<10000;frame++){
 if(c.booted&&boot<0)boot=frame;const t=frame-boot;m.keyMatrix.fill(31);if(boot>=0&&t>=600&&t<700)m.keyMatrix[3]=29;joy[0]=boot>=0&&t>=800&&frame%120<70?239:255;api.runFrame(m);
 if(pending){const r=pending;fs.writeFileSync(path.join(out,`id${r.level_id}_f${frame}_p${r.p.toString(16)}.home.bin`),m.ram);pending=null;}
 if(c.fatalSeen)throw Error('Loader failure');
}
fs.writeFileSync(path.join(out,'draw_sources.json'),JSON.stringify(rows,null,2));console.log('Unique emergence source variants',rows.length);
