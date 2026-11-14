import fs from 'node:fs';import assert from 'node:assert/strict';import {stockFixture}from './stock_fixture.mjs';
const n=Number(process.argv[2]||4),f=stockFixture(n),{m,call,out}=f,j=JSON.parse(fs.readFileSync(out+'/combined_frames.json'));const palette=j.hardware_palette||j.palette;let cases=0;
for(let pi=0;pi<palette.length;pi++)for(const flip of [false,true]){
 m.ram[0x780a]=pi&255;m.ram[0x810a]=32|((pi>>8)<<2)|(flip?128:0);
 for(let y=0;y<8;y++){call(0xe00,{a:7,d:0x40+y,e:10,yl:y});assert.equal(m.cpu.a,palette[pi][flip?7-y:y],'single '+pi+'/'+y);cases++;}
 call(0xe40,{a:7,d:0x40,e:10,b:0x12,c:0x34,h:0x58,l:10});for(let y=0;y<8;y++)assert.equal(m.ram[0x600a+y*256],palette[pi][flip?7-y:y],'bulk '+pi+'/'+y);assert.equal(m.cpu.d,0x40);assert.equal(m.cpu.e,10);assert.equal(m.cpu.h,0x58);assert.equal(m.cpu.l,10);assert.equal(m.cpu.b,0x12);assert.equal(m.cpu.c,0x34);cases++;
}
m.ram[0x810a]=0;for(let a=0;a<128;a++){call(0xe00,{a,d:0x40,e:10,yl:0});assert.equal(m.cpu.a,a&63);}
for(let pi=0;pi<16;pi++){for(let y=0;y<8;y++){call(0xe00,{a:128|pi,d:0x40+y,e:10,yl:y});assert.equal(m.cpu.a,(n===2?m.bus.read(JSON.parse(fs.readFileSync(out+'/l2_row_palette_contract.json')).palette+pi*8+y):m.ram[0xfbd0+pi*8+y]));}call(0xe40,{a:128|pi,d:0x40,e:10});for(let y=0;y<8;y++)assert.equal(m.ram[0x600a+y*256],(n===2?m.bus.read(JSON.parse(fs.readFileSync(out+'/l2_row_palette_contract.json')).palette+pi*8+y):m.ram[0xfbd0+pi*8+y]));}
if(n===2){const r=JSON.parse(fs.readFileSync(out+'/l2_row_palette_contract.json'));assert(r.patterns===17);}
const report={passed:true,level:n,cases,paletteRows:palette.length,romWrites:f.romWrites,scope:'Actual global single/bulk refresh preserves all dictionary8x1pairs/bothverticalorientations and registers; plain attributes never interpreted as dictionary indices'};fs.writeFileSync(out+'/global_colour_validation.json',JSON.stringify(report,null,2));console.log(report);
