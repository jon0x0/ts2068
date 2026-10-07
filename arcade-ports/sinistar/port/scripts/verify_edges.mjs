import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck'));
const keys=new Uint8Array(8).fill(31),m=api.createMachine(keys,new Uint8Array(2).fill(255));
m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));assert.equal(api.insertDock(m,cart),null);api.resetMachine(m);
const get=n=>m.ram[sym[n]],set=(n,v)=>m.ram[sym[n]]=v;
function run(n){for(let i=0;i<n;i++)api.runFrame(m);}
run(200);
assert.deepEqual(Buffer.from(m.ram.slice(0x4000,0x5800)),fs.readFileSync(path.join(root,'build/title-bitmap.bin')));
assert.ok(m.ram.slice(0x6000,0x7800).every(x=>x===0x42));
assert.ok(m.cpu.pc>=sym.title_wait&&m.cpu.pc<sym.title_data);
keys[7]=30;
let active=false,seen=0;
const cases=[];
for(const y of [32,37,38,50,63,64,100,148,149,160,175,176,256,500])for(const x of [-40,-33,-32,-25,-8,-1,0,7,8,216,223,224,231,248,255,256,280])cases.push([x,y]);
const assets=JSON.parse(fs.readFileSync(path.join(root,'build/mining-assets.json')));
const off=(x,y)=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;
let coords;
const read=m.bus.read;
m.bus.read=a=>{
 if(a===m.cpu.pc){
  if(a===sym.start_resume)keys.fill(31);
  if(a===sym.frame_start&&seen<cases.length){
   active=true;set('game_status',1);set('rock_alive',1);set('worker_alive',0);set('crystal_alive',0);set('bullet_alive',0);set('bs_active',0);set('assembly_count',0);
   coords=cases[seen];const [x,y]=coords;set('rock_x',x&255);set('rock_y',y&255);m.ram[0x586e]=(x>>8)&1;m.ram[0x586f]=(y>>8)&1;
  }
  if(a===sym.publication_done&&active){
   const pixels=new Uint8Array(6144),attrs=new Uint8Array(6144).fill(7);
   const draw=(kind,index,x,y,w,h)=>{
    const raw=assets.find(a=>a.kind===kind&&a.index===index).data;
    for(let r=0;r<h;r++)for(let c=0;c<w;c++){
     const xx=Math.floor(x/8)+c,yy=y+r,i=(r*w+c)*3;
     if(xx<0||xx>=32||yy<64||yy>=176||raw[i]===255)continue;
     const n=off(xx,yy);pixels[n]=(pixels[n]&raw[i])|raw[i+1];attrs[n]=raw[i+2];
    }
   };
   draw('rock',coords[0]&7,...coords,5,28);
   const px=m.ram[sym.px+1],py=m.ram[sym.py+1];draw('ship',((get('angle')+4)&248)|(px&7),px,py,3,12);
   for(let y=64;y<176;y++)for(let x=0;x<32;x++){
    const n=off(x,y);assert.equal(m.ram[0x4000+n],pixels[n],`bitmap ${coords}: ${x},${y}`);assert.equal(m.ram[0x6000+n],attrs[n],`attribute ${coords}: ${x},${y}`);
   }
   seen++;active=false;
  }
 }
 return read(a);
};
for(let i=0;i<5000&&seen<cases.length;i++)run(1);
assert.equal(seen,cases.length);
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),native_title:true,fire_starts_game:true,clipped_positions:seen};
fs.writeFileSync(path.join(root,'build/edges-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(report);
