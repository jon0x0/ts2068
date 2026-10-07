import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
const sym=Object.fromEntries([...['mining','incremental'].map(n=>fs.readFileSync(path.join(root,`build/${n}-symbols.txt`),'utf8')).join('\n').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const pieces=JSON.parse(fs.readFileSync(path.join(root,'build/damage-pieces.json')));
assert.deepEqual(pieces.map(p=>p.name),['S5R','S6R','S6L','S5L','S4L','S4R','S3R','S2R','S3L','S2L','S1R','S1L']);
const offset=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|(x>>3);
let romWrites=0,cases=0,maxTstates=0;const byHits={};
const bus={read:a=>0x14&(1<<(a>>13))?rom[a]:ram[a],write(a,v){if(0x14&(1<<(a>>13)))romWrites++;else ram[a]=v;},ioRead:()=>255,ioWrite(){throw Error('Damage renderer must not switch banks or write video ports');}};
for(let hits=0;hits<=13;hits++)for(let phase=0;phase<8;phase++)for(const [baseX,y] of [[96,90],[-30,90],[-7,55],[248,166],[96,-20]]){
 const x=baseX+phase;ram.fill(0);ram.fill(0xa5,0xa800,0xc000);ram.fill(7,0xe800,0x10000);
 ram[sym.bs_hits]=hits;ram[sym.rects+22]=7;ram[sym.face_x+1]=x&255;ram[sym.face_y+1]=y&255;ram[0x7cba]=+(x<0);ram[0x7cbb]=+(y<0);
 const expected=ram.slice(0xa800,0xc000);
 if(hits<13)for(const p of pieces.slice(0,hits))for(let yy=y+p.y;yy<y+p.y+p.height;yy++)for(let xx=x+p.x;xx<x+p.x+p.width;xx++)if(xx>=0&&xx<256&&yy>=64&&yy<176)expected[offset(xx,yy)-0x800]&=~(128>>(xx&7));
 cpu.pc=sym.damage_render;cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;cpu.halted=false;const start=clock.tstates;
 for(let n=0;cpu.pc!==0x100;n++){assert.ok(n<100000,'bounded removal');runZ80(cpu,bus,1,clock);}
 const cost=clock.tstates-start;maxTstates=Math.max(maxTstates,cost);byHits[hits]=Math.max(byHits[hits]||0,cost);assert.deepEqual(ram.slice(0xa800,0xc000),expected,`hit ${hits}, phase ${phase}, at ${x},${y}`);assert.ok(ram.slice(0x4000,0x5800).every(v=>v===0),'no direct screen writes');cases++;
}
assert.equal(romWrites,0);
const result={dck_sha256:createHash('sha256').update(cart).digest('hex'),cases,order:pieces.map(p=>p.name),faceFinalHit:13,maxTstates,maxMilliseconds:maxTstates/3528,byHits,romWrites};fs.writeFileSync(path.join(root,'build/damage-verification.json'),JSON.stringify(result,null,2));console.log(result);
