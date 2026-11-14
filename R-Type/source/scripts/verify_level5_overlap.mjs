// Actual native cell renderer: overlapping arcade-derived round components.
import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';
import{root,api,call,rev,off}from'./r22_test_machine.mjs';
const out=path.join(root,'build/diagnostics/level5_overlap');fs.mkdirSync(out,{recursive:true});
const folder=path.join(root,'build/fullgame/level05'),raw=fs.readFileSync(path.join(folder,'game.bin')),runtime=fs.readFileSync(path.join(folder,'runtime_region.bin'));
const layout=JSON.parse(fs.readFileSync(path.join(root,'build/fullgame/foundation/manifest.json'))).levels[4];
const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));
api.insertDock(m,Buffer.concat([Buffer.from([0,2,3,3,3,2,2,2,2]),raw]));
for(const[s,d]of[[7,2],[1,3],[2,4],[3,5],[5,6],[6,7]])m.ram.set(raw.subarray(s*8192,(s+1)*8192),d*8192);
for(const b of[1,2,3])m.dock[b].set(runtime.subarray(b*8192,(b+1)*8192));
for(let i=0;i<256;i++)m.ram[0x5d00+i]=rev(i);
m.portFF=2;m.portF4=9;m.ram.fill(0,0x4000,0x5800);m.ram.fill(0,0x6000,0x7800);m.dock[3].fill(0,0x1e00);
const source=Buffer.from(m.ram),initialDock3=Buffer.from(m.dock[3]);
function draw(id,x,y){const at=layout.enemy_descriptors_start+(id-1)*4,w=source[at],h=source[at+1],ptr=source.readUInt16LE(at+2);m.portF4=9;m.bus.write(0x7a9c,id+111);m.ram[0x8eb1]=0;m.ram[0x8ebf]=0x40;m.ram[0x8f10]=0xd8;call(m,0x8cfd,{b:y,c:x,d:h,e:w,h:ptr>>8,l:ptr&255});return{width:w,height:h,pointer:ptr,x,y};}
const first=draw(9,8,7);const before=Buffer.from(m.ram);fs.writeFileSync(path.join(out,'first.home.bin'),before);
const second=draw(10,10,8);const after=Buffer.from(m.ram);fs.writeFileSync(path.join(out,'overlap.home.bin'),after);
m.ram.set(source);m.dock[3].set(initialDock3);draw(10,10,8);const alone=Buffer.from(m.ram);fs.writeFileSync(path.join(out,'second_alone.home.bin'),alone);
let lost=0,blocked=0;for(let y=0;y<192;y++)for(let x=0;x<256;x++){const at=0x4000+off(y)+(x>>3),bit=128>>(x&7);if((before[at]&bit)&&!(after[at]&bit))lost++;if((alone[at]&bit)&&!(after[at]&bit))blocked++;}
assert(blocked>0,'No whole-cell occlusion reproduced');
const report={status:'Controlled native-renderer overlap reproduction; exact reported gameplay still needs animation tracing',first,second,erasedEarlierPixels:lost,missingForegroundPixels:blocked,wholeCellPriority:true};
fs.writeFileSync(path.join(out,'result.json'),JSON.stringify(report,null,2));console.log(report);
