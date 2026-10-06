import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536);
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const assets=JSON.parse(fs.readFileSync(path.join(root,'build/mining-assets.json'))),cpu=createZ80(),clock={tstates:0,stepAdded:0};let mapping=16,maxBuild=0,maxDecode=0,maxDraw=0,maxOverlap=0;
const bus={read:a=>mapping&(1<<(a>>13))?rom[a]:ram[a],write(a,v){assert.equal(mapping&(1<<(a>>13)),0,'ROM write');ram[a]=v;},ioRead:()=>255,ioWrite(p,v){assert.equal(p&255,0xf4);mapping=v;}};
function invoke(op){mapping=16;ram[0x78df]=16;cpu.pc=sym.assembly_cache_call;cpu.a=op;cpu.b=ram[0x5bd8];if(op===2){cpu.h=88;cpu.l=12;cpu.d=52;cpu.e=7;cpu.xh=0;cpu.xl=0;}cpu.sp=0x7ffd;ram[0x7ffd]=0;ram[0x7ffe]=1;cpu.halted=false;const t=clock.tstates;for(let n=0;cpu.pc!==0x100;n++){assert.ok(n<200000,'bounded cache call');runZ80(cpu,bus,1,clock);}assert.equal(cpu.sp,0x7fff);assert.equal(mapping,16);const elapsed=clock.tstates-t;if(op===2)maxDecode=Math.max(maxDecode,elapsed);else if(op===1)maxDraw=Math.max(maxDraw,elapsed);else if(op===3)maxOverlap=Math.max(maxOverlap,elapsed);else maxBuild=Math.max(maxBuild,elapsed);}
function expected(raw,phase){const out=Uint8Array.from(raw);for(let y=0;y<52;y++){
 for(let p=0;p<phase;p++){let mc=1,bc=0;for(let x=0;x<7;x++){const i=(y*7+x)*3,m=out[i],b=out[i+1];out[i]=(m>>1)|(mc<<7);out[i+1]=(b>>1)|(bc<<7);mc=m&1;bc=b&1;}}
 let previous=7;for(let x=0;x<7;x++){const i=(y*7+x)*3;if(out[i]===255)out[i+2]=7;else{if(out[i+2]===1)out[i+2]=previous;previous=out[i+2];}}
}return out;}
ram.fill(0,0xbe00,0xbe34);ram.fill(32,0xbe40,0xbe74);ram[0x5bd3]=0x80;let phases=0,front=0,composited=0,culled=0;
for(let stage=1;stage<=20;stage++){
 const raw=assets.find(a=>a.kind==='assembly'&&a.index===stage-1).data;ram.set(raw,0xd800);ram[0x5bd7]=stage;
 const old=ram.slice(ram[0x5bd3]<<8,(ram[0x5bd3]<<8)+4096);
 for(let tick=0;tick<52;tick++){invoke(0);if(tick<51){assert.equal(ram[0x5bd0],front,'no partial presentation');assert.deepEqual(ram.slice(ram[0x5bd3]<<8,(ram[0x5bd3]<<8)+4096),old,'front cache immutable while building');}}
 assert.equal(ram[0x5bd0],stage);front=stage;
 for(let phase=0;phase<8;phase++){for(let y=0;y<52;y++)for(let x=0;x<7;x++){const sy=y+88,o=((sy&192)<<5)|((sy&7)<<8)|((sy&56)<<2)|(x+12);ram[0xa000+o]=0;ram[0xc000+o]=7;}assert.ok(ram[(ram[0x5bd3]<<8)+4095]<=100);ram[0x5bd8]=phase;do{invoke(2);}while(!(cpu.f&64));invoke(3);do{invoke(1);}while(!(cpu.f&64));const ref=expected(raw,phase);for(let y=0;y<52;y++)for(let x=0;x<7;x++){const sy=y+88,o=((sy&192)<<5)|((sy&7)<<8)|((sy&56)<<2)|(x+12),i=(y*7+x)*3;assert.equal(ram[0xa000+o],ref[i+1],`bitmap stage ${stage} phase ${phase} ${x},${y}`);assert.equal(ram[0xc000+o],ref[i+2],`color stage ${stage} phase ${phase} ${x},${y}`);}
 // An overlapping foreground footprint forces masked composition, including holes.
 ram.fill(0,0xb800,0xb81c);ram.set([12,88,7,52],0xb800);
 for(let y=0;y<52;y++)for(let x=0;x<7;x++){const sy=y+88,o=((sy&192)<<5)|((sy&7)<<8)|((sy&56)<<2)|(x+12);ram[0xa000+o]=(x*31+y*7+85)&255;ram[0xc000+o]=0x46;}
 do{invoke(2);}while(!(cpu.f&64));invoke(3);assert.equal(ram[0xb802],7,'partial overlap must remain visible');do{invoke(1);}while(!(cpu.f&64));
 for(let y=0;y<52;y++)for(let x=0;x<7;x++){const sy=y+88,o=((sy&192)<<5)|((sy&7)<<8)|((sy&56)<<2)|(x+12),i=(y*7+x)*3;assert.equal(ram[(ram[0x5bd3]<<8)+3276+8*ram[(ram[0x5bd3]<<8)+2912+y*7+x]+phase],ref[i],'exact selected-phase mask');assert.equal(ram[0xa000+o],(((x*31+y*7+85)&255)&ref[i])|ref[i+1],'masked bitmap');assert.equal(ram[0xc000+o],ref[i]===255?0x46:ref[i+2],'transparent color preserved');}
 composited++;
 // Narrow dirty spans must leave every other cell untouched, including
 // the remaining portion of a sprite row and its attribute cells.
 ram.fill(32,0xbe00,0xbe34);ram.fill(0,0xbe40,0xbe74);
 const dirtyRow=10+(phase&3);ram[0xbe00+dirtyRow]=14;ram[0xbe40+dirtyRow]=16;
 for(let y=0;y<52;y++)for(let x=0;x<7;x++){const sy=y+88,o=((sy&192)<<5)|((sy&7)<<8)|((sy&56)<<2)|(x+12);ram[0xa000+o]=85;ram[0xc000+o]=0x46;}
 invoke(2);invoke(3);do{invoke(1);}while(!(cpu.f&64));
 for(let y=0;y<52;y++)for(let x=0;x<7;x++){const sy=y+88,o=((sy&192)<<5)|((sy&7)<<8)|((sy&56)<<2)|(x+12),i=(y*7+x)*3,dirty=y===dirtyRow&&x>=2&&x<4;assert.equal(ram[0xa000+o],dirty?(85&ref[i])|ref[i+1]:85,'narrow dirty bitmap');assert.equal(ram[0xc000+o],dirty&&ref[i]!==255?ref[i+2]:0x46,'narrow dirty attribute');}
 ram.fill(0,0xbe00,0xbe34);ram.fill(32,0xbe40,0xbe74);
 // Find a fully opaque player-sized rectangle, then exercise geometry+mask culling.
 let hidden=null;for(let y=0;y<=40&&!hidden;y++)for(let x=0;x<=4&&!hidden;x++){let solid=true;for(let yy=0;yy<12;yy++)for(let xx=0;xx<3;xx++)solid&&=ref[((y+yy)*7+x+xx)*3]===0;if(solid)hidden=[x+12,y+88,3,12];}
 if(hidden){ram.fill(0,0xb800,0xb81c);ram.set(hidden,0xb80c);do{invoke(2);}while(!(cpu.f&64));invoke(3);assert.equal(ram[0xb80e],0,'fully hidden player skips drawing');culled++;}
 ram.fill(0,0xb800,0xb81c);phases++;}
 const saved=ram.slice(0x8000,0xa000);invoke(0);assert.deepEqual(ram.slice(0x8000,0xa000),saved,'unchanged stage reuses cached data');
}
// A superseding piece abandons only the incomplete back set.
const preserved=ram.slice(ram[0x5bd3]<<8,(ram[0x5bd3]<<8)+4096);
ram.set(assets.find(a=>a.kind==='assembly'&&a.index===2).data,0xd800);ram[0x5bd7]=3;
for(let i=0;i<11;i++)invoke(0);
ram.set(assets.find(a=>a.kind==='assembly'&&a.index===9).data,0xd800);ram[0x5bd7]=10;
for(let i=0;i<51;i++){invoke(0);assert.equal(ram[0x5bd0],20);assert.deepEqual(ram.slice(ram[0x5bd3]<<8,(ram[0x5bd3]<<8)+4096),preserved);}
invoke(0);assert.equal(ram[0x5bd0],10);
assert.ok(maxBuild<58688&&maxDecode<58688&&maxDraw<58688&&maxOverlap<58688,'each banked DI interval fits one refresh');
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),stages:20,phases,composited,culled,atomicSwaps:21,supersedingPiece:true,buildCallsPerStage:52,pictureUpdatesPerStage:26,maxBuildTstates:maxBuild,maxDecodeTstates:maxDecode,maxDrawTstates:maxDraw,maxOverlapTstates:maxOverlap,romWrites:0,bankAndStackRestored:true};
fs.writeFileSync(path.join(root,'build/assembly-cache-verification.json'),JSON.stringify(report,null,2));console.log(report);
