import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
function machine(build){
 const cart=fs.readFileSync(path.join(build,'sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536),cpu=createZ80(),clock={tstates:0,stepAdded:0};
 const sym=Object.fromEntries([...fs.readFileSync(path.join(build,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
 let mapping=0x50;const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){if((p&255)===0xf4)mapping=v;}};
 return {ram,sym,cart,cpu,clock,call(label,map=0x50){mapping=map;cpu.pc=sym[label];cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;for(let i=0;cpu.pc!==0x100;i++){assert.ok(i<100000);runZ80(cpu,bus,1,clock);}}};
}
const now=machine(path.join(root,'build')),assets=JSON.parse(fs.readFileSync(path.join(root,'build/mining-assets.json')));
const off=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;
let seed=49,cases=0;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed>>>24;};
for(let phase=0;phase<8;phase++)for(let height=1;height<=28;height++)for(const top of [false,true]){
 const x=(height+phase)%28,y=top?64:176-height,skip=top?28-height:0;
 now.ram.fill(0);const pix=Uint8Array.from({length:6144},rand),attr=Uint8Array.from({length:6144},()=>rand()&127);
 now.ram.set(pix,0xa000);now.ram.set(attr,0xc000);
 now.ram.set([x,y,5,height],now.sym.rects);now.ram[0x7cd0]=skip;now.ram[0x78e4]=1;
 const raw=assets.find(a=>a.kind==='rock'&&a.index===phase).data;
 for(let r=0;r<height;r++)for(let c=0;c<5;c++){
  const i=((r+skip)*5+c)*3,o=off(x+c,y+r);if(raw[i]===255)continue;
  pix[o]=(pix[o]&raw[i])|raw[i+1];attr[o]=raw[i+2];
 }
 now.cpu.h=1;now.cpu.l=phase;now.call('draw_rock',0x10);
 assert.deepEqual(now.ram.slice(0xa000,0xb800),pix,`bitmap ${phase}/${height}/${top}`);
 assert.deepEqual(now.ram.slice(0xc000,0xd800),attr,`attributes ${phase}/${height}/${top}`);cases++;
}
const report={dck_sha256:createHash('sha256').update(now.cart).digest('hex'),cases,allFinePhases:true,visibleHeights:[1,28],topAndBottom:true,randomBackgroundCompositing:true,exact:true};
fs.writeFileSync(path.join(root,'build/vertical-rock-verification.json'),JSON.stringify(report,null,2));console.log(report);
