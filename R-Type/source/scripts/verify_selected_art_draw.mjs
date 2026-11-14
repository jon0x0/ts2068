import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{root,api,call,off,rev}from'./r22_test_machine.mjs';
const out=path.join(root,'build/fullgame/selected_art_r43'),base=fs.readFileSync(path.join(root,'build/fullgame/level05/game.bin')),region=fs.readFileSync(path.join(out,'level05_region.bin')),native=fs.readFileSync(path.join(out,'native_level5.bin')),dictionary=fs.readFileSync(path.join(out,'enemy_palette.bin'));
const layout=JSON.parse(fs.readFileSync(path.join(root,'build/fullgame/foundation/manifest.json'))).levels[4];
const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));api.insertDock(m,Buffer.concat([Buffer.from([0,3,3,3,3,3,3,3,3]),region]));
for(const[s,d]of[[7,2],[1,3],[2,4],[3,5],[5,6],[6,7]])m.ram.set(base.subarray(s*8192,(s+1)*8192),d*8192);
m.ram.set(native.subarray(0xc000),0xc000);for(let i=0;i<256;i++)m.ram[0x5d00+i]=rev(i);m.portFF=2;
const source=Buffer.from(m.ram);let cases=0;const cycles=[];
for(let id=1;id<=layout.enemy_descriptors;id++){
 const at=layout.enemy_descriptors_start+(id-1)*4,w=source[at],h=source[at+1],ptr=source.readUInt16LE(at+2);if(!w||!h)continue;
 for(let flip=0;flip<4;flip++)for(const[x,y]of[[4,3],[0,0],[29,18]])for(const flash of[0,71]){
 m.ram.set(source);m.portF4=9;m.dock[3].fill(0,0x1e00);m.ram.fill(0xa5,0x4000,0x5800);m.ram.fill(0x47,0x6000,0x7800);m.bus.write(0x7a9c,id+111);m.ram[0x8eb1]=flash;m.ram[0x8ebf]=0x40;m.ram[0x8f10]=0xd8;
 const t=m.tstates;call(m,[0x8cfd,0x8dd3,0x8d65,0x8e29][flip],{b:y,c:x,d:h,e:w,h:ptr>>8,l:ptr&255,iff1:true,iff2:true});if(id===8&&!flash&&x===4)cycles.push({flip,tstates:m.tstates-t});
 assert(m.cpu.iff1);assert.equal(m.portF4,9);if(id===8&&!flip&&x===4&&!flash)fs.writeFileSync(path.join(out,'core_draw.home.bin'),m.ram);const pix=Buffer.alloc(6144,0xa5),atr=Buffer.alloc(6144,0x47);let p=ptr;
 for(let cy=0;cy<h;cy++)for(let cx=0;cx<w;cx++){const a=source[p];if(a===54){p++;continue;}const xx=x+((flip&2)?w-1-cx:cx),yy=y+((flip&1)?h-1-cy:cy);if(xx>=1&&xx<31&&yy<20)for(let sy=0;sy<8;sy++){const target=off(yy*8+((flip&1)?7-sy:sy))+xx;pix[target]=(flip&2)?rev(source[p+1+sy]):source[p+1+sy];atr[target]=(flash&63)||dictionary[(a&127)*8+sy];}p+=9;}
 assert(p<=0xf87c);assert.deepEqual(Buffer.from(m.ram.slice(0x4000,0x5800)),pix,`id${id} flip${flip} bitmap`);assert.deepEqual(Buffer.from(m.ram.slice(0x6000,0x7800)),atr,`id${id} flip${flip} attrs`);cases++;
 }
}
const result={cases,cycles,passed:true,scope:'All level-five descriptors, flips, edge clipping and flash palettes; enlarged source stays below AY code'};fs.writeFileSync(path.join(out,'draw_validation.json'),JSON.stringify(result,null,2));console.log(result);

