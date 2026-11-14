import fs from'node:fs';import assert from'node:assert/strict';import{api,z,root,off,rev}from'./r22_test_machine.mjs';import{demandFixture}from'./boss_motion_fixture_r145.mjs';
const level=Number(process.argv[2]||1);assert(level>=1&&level<=8);const out=root+'/build/cartridges/integration_work';fs.mkdirSync(out,{recursive:true});const foundation=JSON.parse(fs.readFileSync(root+'/build/fullgame/foundation/manifest.json')).levels[level-1], {m,joy,controller:c}=demandFixture();let boot=-1,u=0,last=-1;const rd=m.bus.read;m.bus.read=a=>{if(m.stepAdded===0&&a===m.cpu.pc&&last!==m.tstates){last=m.tstates;if(a===0x94f1&&rd(0x7aa4)>0)u++;}return rd(a)};for(let f=0;f<8000&&u<5;f++){m.keyMatrix.fill(31);joy.fill(255);if(c.booted&&boot<0)boot=f;if(f>=30&&(boot<0||f-boot<120)){if(level<=5)m.keyMatrix[3]&=~(1<<(level-1));else m.keyMatrix[4]&=~(1<<(10-level));}if(boot>=0&&f-boot>=300)joy[0]=127;api.runFrame(m);}assert(u>=5);assert.equal(c.region,level-1);console.log('selectors',level,'game',rd(0x7aa4),'mode',m.portFF,m.dock[1][0x1ff0],Array.from(m.ram.slice(0x9172,0x917a)),Array.from(m.ram.slice(0x8e85,0x8e8c)));
const meta=JSON.parse(fs.readFileSync(root+'/build/fullgame/visible_hits_r145/walker_runtime.json')).find(q=>q.level===level)||(level===2?{extension:Object.fromEntries([...fs.readFileSync(root+'/build/fullgame/visible_hits_r145/L2_actor_extension.sym','utf8').matchAll(/(\w+): EQU 0x([0-9a-f]+)/ig)].map(v=>[v[1],parseInt(v[2],16)]))}:null),home=Buffer.from(m.ram),banks=m.dock.map(v=>Buffer.from(v)),select=rd(0x9173)+256*rd(0x9174),palette=[],frames=[],variants=[],unique=new Map();
function run(pc,regs={},flip=0){m.portF4=9;m.portFF=2;Object.assign(m.cpu,{pc,sp:0xffe0,iff1:false,iff2:false,halted:false,eiDelay:false},regs);m.ram.set([0,0xf0,0,flip,0,0],0xffe0);let n=0;while(m.cpu.pc!==0xf000&&n++<1000000)z.runZ80(m.cpu,m.bus,1,m);assert(n<1000000,'hang '+m.cpu.pc.toString(16));}

const rawTiles=[];
for(let tile=0;tile<foundation.terrain_tiles;tile++){
 m.ram.set(home);for(let i=0;i<8;i++)m.dock[i].set(banks[i]);
 run(0x882d,{a:tile});const pointer=m.cpu.h*256+m.cpu.l;
 rawTiles.push({tile,pointer,bytes:Array.from({length:144},(_,i)=>m.bus.read(pointer+i))});
}
const themes=Array.from(home.slice(0xfbd0,0xfc50));
const original=fs.readFileSync(root+`/build/fullgame/level${String(level).padStart(2,'0')}/terrain_palette.bin`).subarray(0,128);
const sourceRegion=fs.readFileSync(root+`/build/fullgame/visible_hits_r145/level${String(level).padStart(2,'0')}_region.bin`);
const report={level,source:'r145 actual native882D getter; no manual painter/attribute preview',sourceRegionSha256:(await import('node:crypto')).createHash('sha256').update(sourceRegion).digest('hex'),palette:themes,rawTiles,paletteMatchesOlderBase:Buffer.from(themes).equals(original),sourcePaletteVisible:Array.from(new Set(themes))};
fs.writeFileSync(out+`/L${level}_native_terrain.json`,JSON.stringify(report));console.log({level,tiles:rawTiles.length,paletteMatchesOlderBase:report.paletteMatchesOlderBase,palette:report.sourcePaletteVisible});
