import fs from 'node:fs';import assert from 'node:assert/strict';import {stockFixture} from './stock_fixture.mjs';
const level=Number(process.argv[2]||1),f=stockFixture(level),{m,call,out}=f,l=JSON.parse(fs.readFileSync(out+'/player_ram_layout.json')),owner=l.allocations.published_owner_map[0],bolts=l.allocations.projectile_state[0];
const home=Buffer.from(m.ram),cases=[];
for(const kind of ['shown_enemy','future_enemy','empty','terrain','reused_actor']){
 m.ram.set(home);m.ram.fill(0,0x7e00,0x8080);m.ram.fill(0,owner,owner+640);m.ram.fill(0,0x5eb4,0x5ee4);
 m.ram[0x8501]=3;m.ram[0x8506]=0x12;m.ram[0x8507]=0x34;m.ram[0x7aa4]=2;m.ram[0x7aa1]=4;m.ram[0x7aa2]=10;call(0x1b26);
 m.ram.set([0x18,8,6],0x5eb4);
 if(['shown_enemy','reused_actor'].includes(kind))m.ram[owner+6*32+9]=0x81;
 if(kind==='future_enemy')m.ram[0x7e00+6*32+9]=0x81;
 if(kind==='terrain')m.ram[owner+6*32+9]=0xfb;
 call(0x1b23);const pending=m.ram[bolts+0x30];assert.equal(pending,['shown_enemy','reused_actor'].includes(kind)?0x81:kind==='terrain'?0xfb:0,kind);
 if(kind==='reused_actor')m.ram[0x8506]^=1;
 call(0x9da5);const hp=m.ram[0x8501];assert.equal(hp,kind==='shown_enemy'?2:3,kind+' health');cases.push({kind,pending,hp});
}
const report={passed:true,level,cases,romWrites:f.romWrites,scope:'Actual stock displayed-frame projectile lookup and native damage handoff, same shown/future/empty/terrain/reuse cases as TAP r145. Seeded collision cells, not live walker encounter.'};fs.writeFileSync(out+'/visible_collision_validation.json',JSON.stringify(report,null,2));console.log(report);
