import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{api,root,z}from'./r16_test_machine.mjs';import{demandFixture}from'./boss_motion_fixture_r129.mjs';const out=path.join(root,'build/fullgame/l2_pre_copy_r129'),ct=JSON.parse(fs.readFileSync(path.join(out,'L2_actor_contract.json')));const{m,joy,controller:c}=demandFixture();let boot=-1,u=0,last=-1;const rd=m.bus.read;m.bus.read=a=>{if(a===m.cpu.pc&&m.stepAdded===0&&last!==m.tstates){last=m.tstates;if(a===0x94f1&&rd(0x7aa4)>0)u++;}return rd(a);};for(let f=0;f<8000&&u<11;f++){m.keyMatrix.fill(31);joy.fill(255);if(c.booted&&boot<0)boot=f;if(boot<0&&f>8&&m.ram[0xd610]===1)m.keyMatrix[3]&=~2;if(boot>=0&&f-boot>=800&&f-boot<840)joy[0]=127;api.runFrame(m);}assert(u>=11&&c.region===1);for(let i=0;i<256;i++)assert.equal(m.dock[6][0x1800+i]+256*m.dock[6][0x1801+i],0x5b5b);fs.writeFileSync(path.join(out,'actual_im2_validation.json'),JSON.stringify({passed:true,targets:256,target:'5B5B',scope:'Actual cold-gameplay RAM; emulator fixed FF, not hardware probes'}));m.bus.read=rd;const tc=JSON.parse(fs.readFileSync(path.join(out,'integration_contract.json'))),input=JSON.parse(fs.readFileSync(path.join(out,'tile_inputs.json'))),region=fs.readFileSync(path.join(out,'level02_region.bin'));const results=[];

for(let k=0;k<18;k++)m.dock[6].set(Buffer.from(input.tiles[34+k],'hex'),0xb00+k*144);
const manifest=JSON.parse(fs.readFileSync(path.join(root,'build/graphics/l2_integrated_r67/manifest.json'))).tiles;
const flag=(a,v)=>{const bank=a<0x8000?m.dock[3]:m.ram,off=a<0x8000?a-0x6000:a;if(v!==undefined)bank[off]=v;return bank[off];};
function run(){m.portF4=0x2b;m.ram[0xfff0]=0xf0;m.ram[0xfff1]=0x5c;Object.assign(m.cpu,{pc:0xb002,sp:0xfff0,iff1:false,iff2:false});let steps=0;while(m.cpu.pc!==0x5cf0&&steps++<500000)z.runZ80(m.cpu,m.bus,1,m);assert(steps<500000);assert.equal(m.portF4,9);assert(Buffer.from(m.dock[4].slice(0,0x2b3)).equals(region.subarray(0x8000,0x82b3)));return steps;}

const cells=[];for(let t=0;t<18;t++)for(let c=0;c<16;c++){const y=manifest[t].ty*4+(c>>2),x=manifest[t].tx*4+(c&3),a=0x7e00+y*32+x;flag(a,99);cells.push({t,c,y,x,a});}
function verifyPlanes(){let rows=0;for(const q of cells){const raw=Buffer.from(input.tiles[34+q.t],'hex'),tag=raw[q.c*9];if(tag===7){assert.equal(flag(q.a),99,'Empty cells retain actor ownership');continue;}const pi=tag<32?tag+96:tag-144;for(let line=0;line<8;line++){const y=q.y*8+line,off=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|q.x,bits=raw[q.c*9+1+line],attr=tag===7?0:region[0x2000+pi*8+line];assert.equal(m.dock[3][off],bits,'Background bitmap');assert.equal(m.dock[2][off],attr,'Background colour');assert.equal(m.ram[0x4000+off],bits,'Visible bitmap');assert.equal(m.ram[0x6000+off],attr,'Visible colour');rows++;}assert.equal(flag(q.a),0,'Owner must return to background');}return rows;}

// Empty native front metadata recreates the reported custom-boss/native-star mismatch.
m.dock[3].fill(0,0x1b00,0x1d80);m.dock[3][0x1a8e]=1;run();
const protectedOffsets=new Set();for(const q of cells){const raw=Buffer.from(input.tiles[34+q.t],'hex');if(raw[q.c*9]===7||q.x>=31)continue;for(let line=0;line<8;line++){const y=q.y*8+line;protectedOffsets.add(((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|q.x);}}
let writesInside=0,writesOutside=0,cases=0;const origWrite=m.bus.write;
m.bus.write=(a,v)=>{if(a>=0x4000&&a<0x5800&&!(m.portF4&4)){if(protectedOffsets.has(a-0x4000))writesInside++;else writesOutside++;}origWrite(a,v);};
// Exercise the actual native single-star entry over all21 records,4 speed modes,
//32 horizontal positions and4 animation clock phases, including wrap cleanup.
for(let record=0;record<21;record++)for(let speed=0;speed<4;speed++)for(let x=0;x<32;x++)for(let phase=0;phase<4;phase++){
 const ix=0x8084+record*4,h=m.ram[ix+1],l=m.ram[ix];if(!l)continue;
 m.ram[0x80d8]=speed;m.ram[0x80d9]=x;m.dock[3][0x1a9d]=phase;m.portF4=9;m.ram[0xfff0]=0xf0;m.ram[0xfff1]=0x5c;
 Object.assign(m.cpu,{pc:0xbe97,sp:0xfff0,iff1:false,iff2:false,xh:ix>>8,xl:ix&255,h,l,d:0x80,e:0xd8});let steps=0;
 while(m.cpu.pc!==0x5cf0&&steps++<3000)z.runZ80(m.cpu,m.bus,1,m);assert(steps<3000);assert.equal(m.portF4,9);cases++;
}
const report={passed:writesInside===0,cases,writesInside,writesOutside,protectedScanlineCells:protectedOffsets.size,scope:'Actual native star code, all21 records x4speeds x32positions x4phases; includes native erase/draw/wrap; direct fixture, not hardware.'};
fs.writeFileSync(path.join(out,'star_negative_control_r130.json'),JSON.stringify(report,null,2));console.log(report);assert.equal(writesInside,0,'Native stars must never write protected boss cells');assert(writesOutside>100,'Stars must remain active outside boss');
