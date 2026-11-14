import fs from 'node:fs';import assert from 'node:assert/strict';
import{stockFixture}from './stock_fixture.mjs';import{z}from './r22_test_machine.mjs';
const level=Number(process.argv[2]||1),f=stockFixture(level),{m,call,out,cart}=f;
const layout=JSON.parse(fs.readFileSync(out+'/shared_cache_layout.json')),before=Buffer.from(m.ram.slice(0xc000,0xe000)),atlas=fs.readFileSync(out+'/../../../art_assets/title_delta_atlas.bin');
call(0x0c00);assert.equal(m.ram[0xfc63],1);
assert(Buffer.from(m.ram.slice(0xc700,0xdc00)).equals(atlas),'Generated suffix atlas differs from current logo');
m.ram[0xfc51]=0;m.ram[0xfc54]=255;m.ram[0xfc5a]=31;let steps=0;
for(let x=248;x>=0;x-=4){m.ram[0xfc50]=x;call(0x1ab0);steps++;}
m.ram[0xfc51]=1;
for(let x=0;x<212;x+=4){m.ram[0xfc50]=x;call(0x1ab0);steps++;}
for(let y=0;y<48;y++){
 const at=cart.readUInt16LE(9+0x1100+y*2);
 for(let x=0;x<32;x++){
  assert.equal(m.ram[at+x],cart[9+0x9000+y*32+x],'Final title pixels '+y+','+x);
  assert.equal(m.ram[at+0x2000+x],cart[9+0x9600+y*32+x],'Final title colour '+y+','+x);
 }
}
// Simulate8696 initializing the live checkpoint after title generation.
call(0x8696);
const liveHeader=Buffer.from(m.ram.slice(0xc4ae,0xc4b2));
liveHeader.copy(before,0x4ae);
assert(m.ram[0xc4af]||m.ram[0xc4b0],'Native initial enemy pointer must be nonzero');
const rd=m.bus.read;let restored=false;
m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&a===0x86c3){restored=true;throw Error('RESTORED');}return rd(a);};
try{call(layout.title_lifetime+3);}catch(e){if(!restored)throw e;}m.bus.read=rd;
assert(Buffer.from(m.ram.slice(0xc4ae,0xc4b2)).equals(liveHeader),'Title restoration reset live enemy checkpoint');assert(restored);assert.equal(m.ram[0xfc63],0);
assert(Buffer.from(m.ram.slice(0xc000,0xe000)).equals(before),'Native level source must be restored exactly before initialization');
const result={passed:true,level,generatedAtlasBytes:atlas.length,animationSteps:steps,finalPixelsAndColoursExact:true,nativeLevelPageRestored:true,liveEnemyHeaderPreserved:true,romWrites:f.romWrites,scope:'Exact generated atlas and final title, actual delta helper; level restoration intercepted immediately before native initializer, gameplay separately tested'};
fs.writeFileSync(out+'/title_validation.json',JSON.stringify(result,null,2));console.log(result);
