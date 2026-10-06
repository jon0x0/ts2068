import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const {createZ80,runZ80}=await import(pathToFileURL(path.resolve(root,'../../../TSRun/z80.js')));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck')),rom=cart.subarray(9),ram=new Uint8Array(65536);
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const cpu=createZ80(),clock={tstates:0,stepAdded:0};let mapping=16,decisions=0,cases=0;
const bus={read(a){if(a===cpu.pc&&a===sym.fp_think)decisions++;return mapping&(1<<(a>>13))?rom[a]:ram[a];},write(a,v){assert.equal(mapping&(1<<(a>>13)),0,`ROM write ${a.toString(16)}`);ram[a]=v;},ioRead:()=>255,ioWrite(p,v){assert.equal(p&255,0xf4);mapping=v;}};
const set=(n,v)=>ram[sym[n]]=v,word=(n,v)=>{ram[sym[n]]=v&255;ram[sym[n]+1]=(v>>8)&255;},getword=n=>ram[sym[n]]+256*ram[sym[n]+1],signed=n=>(n<<16)>>16;
function invoke(n){cpu.pc=sym[n];cpu.sp=0x7ffd;cpu.halted=false;ram[0x7ffd]=0;ram[0x7ffe]=1;let steps=0;while(cpu.pc!==0x100){assert.ok(++steps<2000,n);runZ80(cpu,bus,1,clock);}assert.equal(cpu.sp,0x7fff);assert.equal(mapping,16);assert.equal(ram[0x78df],16);cases++;}
for(const x of [-32768,-2047,-255,-1,0,1,255,2047,32767])for(const y of [-2047,-1,0,1,2047])for(const stun of [0,1,2,254,255]){
 word('face_vx',x);word('face_vy',y);set('sini_stun',stun);invoke('sinistar_hit_response');assert.equal(signed(getword('face_vx')),x>>1);assert.equal(signed(getword('face_vy')),y>>1);assert.equal(ram[sym.sini_stun],(stun+2)&255);
}
const table=[[32767,2047,5],[4000,4096,4],[1024,128,1],[600,320,5],[80,256,3],[64,192,4],[32,128,4],[16,96,3],[0,64,2]];
function velocity(distance,current,target,double){const row=table.find(r=>Math.abs(distance)>=r[0]),shift=table.find(r=>row[1]>=r[1])[2];let desired=(distance<0?row[1]:-row[1])*(double?2:1);if((desired<0)===(target<0)){const sum=signed(desired+target);desired=desired>=0?(sum>2047?2047:sum):(signed(Math.abs(sum))>2047?-2047:sum);}const delta=signed(desired-current);return delta?signed(current+((delta>>shift)|1)):current;}
let ticks=0,stopped=0;
for(let phase=0;phase<8;phase++){
 set('game_mode',1);set('awake_done',1);set('bs_hits',0);set('sini_stun',0);set('sini_think_phase',phase);
 let x=450*256,y=490*256,vx=-255,vy=127,stun=0,p=phase;
 for(let t=0;t<192;t++){
  const px=40+t%150,py=70+t%70,pvx=(t%3-1)*127,pvy=(t%5-2)*90;
  word('px',px*256);word('py',py*256);word('pvx',pvx);word('pvy',pvy);
  word('face_x',x);word('face_y',y);word('face_vx',vx);word('face_vy',vy);
  ram[0x7c9a]=x>>16;ram[0x7c9b]=y>>16;
  if([3,4,17,95].includes(t)){invoke('sinistar_hit_response');vx>>=1;vy>>=1;stun=(stun+2)&255;}
  p=(p+1)&7;const before=decisions;
  const delta=(a,b)=>((a-b+256)&511)-256;
  if(p===0){if(stun)stun--;if(stun){vx=vy=0;stopped++;}else{vx=velocity(delta(x>>8,px)+18,vx,pvx,true);vy=velocity((delta(y>>8,py)+20)*2,vy,pvy,false);}}
  x=(x+vx)&131071;y=(y+vy)&131071;
  invoke('mining_pursuit_step');
  assert.equal(decisions-before,p===0&&!stun?1:0);assert.equal(getword('face_x')+65536*ram[0x7c9a],x);assert.equal(getword('face_y')+65536*ram[0x7c9b],y);assert.equal(signed(getword('face_vx')),vx);assert.equal(signed(getword('face_vy')),vy);assert.equal(ram[sym.sini_stun],stun);assert.equal(ram[sym.sini_think_phase],p);ticks++;
 }
}
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),signed_hit_cases:225,physics_ticks:ticks,stopped_decisions:stopped,decision_phases:8,bank_and_stack_restored:true};fs.writeFileSync(path.join(root,'build/pursuit-timing-verification.json'),JSON.stringify(report,null,2)+'\n');console.log(report);
