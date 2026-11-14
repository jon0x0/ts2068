import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api,root}from'./r22_test_machine.mjs';import{out,demandFixture}from'./clean_player_fixture.mjs';
const {m,joy,controller:c}=demandFixture();let boot=-1,main=0,last=-1,trigger=-1,death=-1,respawn=-1,frame=0;const read=m.bus.read;m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x94f1)main++;if(trigger>=0&&a===0x91f2&&death<0)death=frame;if(death>=0&&a===0x8bae)respawn=frame;}return read(a);};
for(;frame<8000;frame++){
 if(c.booted&&boot<0)boot=frame;const t=frame-boot;joy[0]=boot>=0&&t>=800&&t<840?239:255;m.keyMatrix.fill(31);
 if(main>=20&&m.ram[0x5bc2]&&trigger<0){trigger=frame;m.dock[3][0x1a98]=0;m.ram[0x5bc4]=1;}
 api.runFrame(m);
 if(respawn>=0&&m.ram[0x5bc2]&&m.dock[3][0x1aa4]===3&&m.ram[0x5bc4]===0)break;
}
assert(trigger>=0&&death>=trigger&&respawn>death,'Pixel hit did not enter real death/respawn '+JSON.stringify({trigger,death,respawn,pc:m.cpu.pc}));assert(frame<8000);const result={passed:true,trigger_frame:trigger,death_frame:death,respawn_frame:respawn,complete_frame:frame,no_death_bypass:true,pixel_hit_flag_consumed:true,hit_flag_cleared_after_respawn:true,mounts:c.mounts,scope:'Actual death and respawn reached from the separately pixel-tested hit flag'};fs.writeFileSync(path.join(out,'death_validation.json'),JSON.stringify(result,null,2));console.log(result);
