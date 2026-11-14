import fs from'node:fs';import assert from'node:assert/strict';import{api,z,root,off,rev}from'./r22_test_machine.mjs';import{demandFixture}from'./boss_motion_fixture_r145.mjs';
const level=Number(process.argv[2]||1);assert(level>=1&&level<=8);const out=root+'/build/cartridges/integration_work';fs.mkdirSync(out,{recursive:true});const foundation=JSON.parse(fs.readFileSync(root+'/build/fullgame/foundation/manifest.json')).levels[level-1], {m,joy,controller:c}=demandFixture();let boot=-1,u=0,last=-1;const rd=m.bus.read;m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x94f1&&rd(0x7aa4)>0)u++;}return rd(a)};for(let f=0;f<8000&&u<5;f++){m.keyMatrix.fill(31);joy.fill(255);if(c.booted&&boot<0)boot=f;if(f>=30&&(boot<0||f-boot<120)){if(level<=5)m.keyMatrix[3]&=~(1<<(level-1));else m.keyMatrix[4]&=~(1<<(10-level));}if(boot>=0&&f-boot>=300)joy[0]=127;api.runFrame(m);}assert(u>=5);assert.equal(c.region,level-1);console.log('selectors',level,'game',rd(0x7aa4),'mode',m.portFF,m.dock[1][0x1ff0],Array.from(m.ram.slice(0x9172,0x917a)),Array.from(m.ram.slice(0x8e85,0x8e8c)));
const meta=JSON.parse(fs.readFileSync(root+'/build/fullgame/visible_hits_r145/walker_runtime.json')).find(q=>q.level===level)||(level===2?{extension:Object.fromEntries([...fs.readFileSync(root+'/build/fullgame/visible_hits_r145/L2_actor_extension.sym','utf8').matchAll(/(\w+): EQU 0x([0-9a-f]+)/ig)].map(v=>[v[1],parseInt(v[2],16)]))}:null),home=Buffer.from(m.ram),banks=m.dock.map(v=>Buffer.from(v)),select=rd(0x9173)+256*rd(0x9174),palette=[],frames=[],variants=[],unique=new Map();
function run(pc,regs={},flip=0){m.portF4=9;m.portFF=2;Object.assign(m.cpu,{pc,sp:0xffe0,iff1:false,iff2:false,halted:false,eiDelay:false},regs);m.ram.set([0,0xf0,0,flip,0,0],0xffe0);let n=0;while(m.cpu.pc!==0xf000&&n++<1000000)z.runZ80(m.cpu,m.bus,1,m);assert(n<1000000,'hang '+m.cpu.pc.toString(16));}
if(meta){console.log('runtime extension',meta.extension.actor_phases.toString(16),Array.from(m.dock[5].slice(meta.extension.sprite_hook&8191,(meta.extension.sprite_hook&8191)+10)),Array.from(m.dock[1].slice(meta.extension.sprite_hook&8191,(meta.extension.sprite_hook&8191)+10)));}

const audit=JSON.parse(fs.readFileSync(out+`/L${level}_tap_motion_audit.json`)),chosen=audit.results.filter(v=>v.fractionalPixelsChange),uniqueFrames=new Map(),write=m.bus.write;let recording=false;const writes=new Map();
m.bus.write=(a,v)=>{if(recording&&a>=0x4000&&a<0x7800)writes.set(a,v);write(a,v);};
const normal=JSON.parse(fs.readFileSync(out+`/L${level}_written_stock_frames.json`));
for(const spec of chosen){
 const id=spec.id,animated=Math.max(...normal.variants.filter(v=>v.id===id).map(v=>v.phase))+1;
 const different=new Set(normal.variants.filter(v=>v.id===id&&v.flip===0).map(v=>v.frame)).size;
 const animCount=different>1?Math.min(animated,4):1;
 const lockX=level!==5&&spec.state[1][2]===16;
 for(let anim=0;anim<animCount;anim++)for(let py=0;py<4;py++)for(let px=0;px<(lockX?1:4);px++)for(let flip=0;flip<4;flip++){
  m.ram.set(home);for(let i=0;i<8;i++)m.dock[i].set(banks[i]);m.dock[3].fill(0,0,0x1800);m.dock[2].fill(0,0,0x1800);m.dock[3].fill(0,0x1e00,0x2000);m.ram.fill(0,0x8000,0x8380);m.ram.fill(7,0x5800,0x5b00);m.dock[3][0x119c]=48+level;m.dock[3][0x1a9c]=0x81;m.ram[0x8eb1]=0;m.ram[0x8ebf]=0x60;
  m.dock[7].fill(255,0x2d0,0x350);m.dock[7].set([1,level===4?id:0,px?6+px*2:255,py?6+py*2:255],0x2d0);
  if(level===5)m.dock[7].set([px?6+px*2:255,py?6+py*2:255],0x300);
  if(meta?.extension?.actor_phases)m.dock[5][(meta.extension.actor_phases+1)&8191]=anim;
  run(select,{a:id,b:2,c:2,yh:0x85,yl:1},flip);
  const originX=m.cpu.c,originY=m.cpu.b*8,w=m.cpu.e,h=m.cpu.d,drawFlip=m.ram[0xffe3]&3;
  assert(w>0&&w<=30&&h>0&&h<=24,JSON.stringify({id,px,py,w,h}));
  writes.clear();recording=true;run([0x8cfd,0x8d65,0x8dd3,0x8e29][drawFlip],{b:originY/8,c:originX});recording=false;
  const bits=[],rows=[];
  for(let cy=0;cy<h;cy++)for(let cx=0;cx<w;cx++){
   const bytes=[],attrs=[];
   for(let y=0;y<8;y++){const x=flip&1?w-1-cx:cx,sy=flip&2?h*8-1-(cy*8+y):cy*8+y,p=off(originY+sy)+originX+x;let bit=writes.get(0x6000+p)??0;if(flip&1)bit=rev(bit);bytes.push(bit);attrs.push(writes.get(0x4000+p)??0);}
   if(!bytes.some((b,y)=>((attrs[y]&7)&&b)||((attrs[y]&56)&&b!==255))){bits.push(54);rows.push(-1);continue;}
   const key=attrs.join(',');let pi=palette.findIndex(v=>v.join(',')===key);if(pi<0){pi=palette.length;palette.push(attrs);}bits.push(7,...bytes);rows.push(pi);
  }
  const key=JSON.stringify([w,h,bits,rows]);let frame=uniqueFrames.get(key);if(frame===undefined){frame=frames.length;uniqueFrames.set(key,frame);frames.push({w,h,bits,rows});}
  variants.push({id,anim,px,py,flip,lockX,frame});
 }
}
fs.writeFileSync(out+`/L${level}_tap_motion_frames.json`,JSON.stringify({level,source:'Actual r145 native selector/painter writes with actor8501 and controlled fractional motion state',palette,frames,variants}));console.log({level,frames:frames.length,palette:palette.length,variants:variants.length});
