import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api,z,root,rev}from'./r22_test_machine.mjs';
const out=path.join(root,'build/diagnostics/boss_relocatable'),referenceStage=fs.readFileSync(path.join(root,'build/fullgame/material_game_r49/level05_region.bin')),variants=['compiled_game_r48','material_game_r49'];let cases=0,totalOld=0,totalNew=0;
function fixture(folder,owner,flash,attr){const base=path.join(root,'build/fullgame',folder),boot=fs.readFileSync(path.join(base,'boot_region.bin')),stage=fs.readFileSync(path.join(base,'level05_region.bin')),m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));api.insertDock(m,Buffer.concat([Buffer.from([0,...Array(8).fill(3)]),stage]));m.ram.set(boot.subarray(0x4000,0x8000),0x8000);m.ram.set(stage.subarray(0xa000,0xe000),0xc000);m.ram.set(boot.subarray(0xd87c,0xe000),0xf87c);m.ram.set(stage.subarray(0xfb00,0xfd00),0x5b00);for(let i=0;i<256;i++)m.ram[0x5d00+i]=rev(i);m.portF4=9;m.portFF=2;m.dock[2].fill(attr,0,6144);for(let i=0;i<6144;i++)m.dock[3][i]=(i&1)?0x55:0xaa;m.dock[3].fill(owner,0x1e00,0x2000);m.ram.fill(owner,0x8000,0x8080);m.dock[3][0x1a9c]=0x90;m.ram[0x8eb1]=flash;m.ram[0x5c81]=flash;m.ram[0x8ebf]=0x60;return m;}
function call(m,entry,ptr,w,h,x,y){Object.assign(m.cpu,{pc:entry,sp:0xffe0,h:ptr>>8,l:ptr&255,d:h,e:w,b:y,c:x,iff1:false,iff2:false});m.ram[0xffe0]=0xf0;m.ram[0xffe1]=0xbf;let n=0,start=m.tstates;while(m.cpu.pc!==0xbff0&&n++<2000000)z.runZ80(m.cpu,m.bus,1,m);assert(n<2000000,'Hang '+m.cpu.pc.toString(16));assert.equal(m.portF4,9);assert.equal(m.cpu.sp,0xffe2);return m.tstates-start;}

fs.mkdirSync(out,{recursive:true});const metrics=[];
for(let frame=200;frame<208;frame++){
 const commands=JSON.parse(fs.readFileSync(path.join(root,`build/diagnostics/delta_benchmark/sample_${frame}.commands.json`),'utf8'));
 const m=fixture('material_game_r49',0,0,0);m.dock[2].fill(0,0,6144);m.dock[3].fill(0,0,6144);m.dock[3][0x1a82]=0;let cycles=0;
 for(const c of commands){m.dock[3][0x1a9c]=0x90;cycles+=call(m,c.entry,c.pointer,c.width,c.height,c.x,c.y);}
 fs.writeFileSync(path.join(out,`frame_${frame}.bin`),Buffer.concat([Buffer.from(m.dock[3].slice(0,6144)),Buffer.from(m.dock[2].slice(0,6144))]));metrics.push({frame,commands:commands.length,native_composition_cycles:cycles});
}
fs.writeFileSync(path.join(out,'source_metrics.json'),JSON.stringify(metrics,null,2));console.log(metrics);
