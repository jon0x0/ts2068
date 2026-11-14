import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{root,api}from'./r22_test_machine.mjs';import{fullgameFixture as fixedFixture}from'./restart_fixture.mjs';import{fullgameFixture as oldFixture}from'./true_black_fixture.mjs';
const results=[];
for(const level of[2,1,3,4,5,6,7,8])for(const negative of(level===2?[true,false]:[false])){
 const{m,joy,controller}=negative?oldFixture():fixedFixture();let updates=0,tape=0,last=-1,forced=false,forceFrame=-1,returned=false,restarted=false;const read=m.bus.read;
 m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&m.tstates!==last){last=m.tstates;if(a===0x8634)m.ram[0x91f2]=201;if(a===0x8b06&&read(0x7aa4)>0)updates++;if(a===0xfe03)tape++;}return read(a);};
 for(let f=0;f<6500;f++){
  m.keyMatrix[3]=31;m.keyMatrix[4]=31;if(f>=600&&f<700){if(level<=5)m.keyMatrix[3]=31^(1<<(level-1));else m.keyMatrix[4]=31^(1<<(10-level));}
  joy[0]=(f>=800&&f<830)||(returned&&f>=forceFrame+700&&f<forceFrame+730)?239:255;api.runFrame(m);
  if(!forced&&updates>=80){assert.equal(controller.region,level-1);m.portF4=9;m.cpu.pc=0x92a4;forced=true;forceFrame=f;updates=0;}
  if(negative&&tape)break;
  if(forced&&f>forceFrame+100&&controller.region===0)returned=true;
  if(!negative&&returned&&f>forceFrame+730&&updates>=80&&controller.region===level-1){restarted=true;break;}
 }
 if(negative)assert(tape>0,'Old build must reproduce obsolete tape entry');else{assert(forced&&returned&&restarted,'Restart failed level '+level+' '+JSON.stringify({forced,returned,restarted,region:controller.region,pc:m.cpu.pc,updates}));assert.equal(tape,0,'Tape loader on restart');assert.equal(m.portFF&7,2);}
 const r={level,negative_control:negative,tape_entries:tape,returned_to_level1:returned,restarted_selected_level:restarted,passed:true,diagnostic:'Force native exhausted-credits branch92A4 after80 updates; real number-key selection and Fire restart'};results.push(r);console.log(r);
}
fs.writeFileSync(path.join(root,'build/fullgame/restart_r32/gameover_validation.json'),JSON.stringify(results,null,2));
