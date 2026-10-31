import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createMachine,insertDock,resetMachine,runFrame} from './tsrun/machine.js';
const root=path.dirname(fileURLToPath(import.meta.url));
const dck=new Uint8Array(fs.readFileSync(path.join(root,'timex-ecm-highres-reveal.dck')));
const source=new Uint8Array(fs.readFileSync(path.join(root,'initial-ram.bin')));
const title2=new Uint8Array(fs.readFileSync(path.join(root,'second-title.bin')));
const frog=dck.subarray(9+0x1000,9+0x4000);
const font=new Uint8Array(fs.readFileSync(path.join(root,'timex-font-8x8.bin')));
const keys=new Uint8Array(8).fill(31);
const m=createMachine(keys,new Uint8Array(2).fill(31));
const err=insertDock(m,dck);if(err)throw Error(err);resetMachine(m);
const palette=[[0,0,0],[0,0,205],[205,0,0],[205,0,205],[0,205,0],[0,205,205],[205,205,0],[205,205,205],[0,0,0],[0,0,255],[255,0,0],[255,0,255],[0,255,0],[0,255,255],[255,255,0],[255,255,255]];
const row=y=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2);
function hiBit(id,x,y){const k=((x>>>3)&1)*8192+row(y)+(x>>>4);return !!((id?title2[k]:source[0x8000+k])&(128>>>(x&7)));}
let checkerPixels=0,whiteBarPixels=0;
for(const id of [0,1]){
 for(let y=96;y<192;y++)for(let x=0;x<512;x++)if(x<30||x>=482||y<126||y>=162){
  const white=x>=30&&x<482&&y>=174&&y<186;
  if(hiBit(id,x,y)!==(white||!!((x+y)&1)))throw Error('Checkerboard or white reference altered');
  if(white)whiteBarPixels++;else checkerPixels++;
 }
 if(id===0){
  const ruler='1234567890'.repeat(6)+'1234';
  for(let c=0;c<64;c++)for(let v=0;v<8;v++)for(let u=0;u<8;u++){
   if(hiBit(id,c*8+u,60+v)!==!!(font[(ruler.charCodeAt(c)-32)*8+v]&(128>>u)))throw Error('Timex 64-column glyph altered');
  }
 }
}
let frames=0,pixels=0,maxMismatch=0;
const seen=new Set(),captures=new Set(),combinations=new Set();
const capturesDir=path.join(root,'cycle-frames');fs.mkdirSync(capturesDir,{recursive:true});
function capture(name){
 const rgb=Buffer.alloc(640*240*3);
 for(let i=0;i<m.pixels.length;i++)for(let j=0;j<3;j++)rgb[i*3+j]=palette[m.pixels[i]][j];
 fs.writeFileSync(path.join(capturesDir,name+'.ppm'),Buffer.concat([Buffer.from('P6\n640 240\n255\n'),rgb]));
}
function check(){
 const split=m.ram[0x7c00],flash=(m.flashFrame&16)!==0;
 const top=m.ram[0x7c04],bottom=m.ram[0x7c05],pic=m.ram[0x7c06],hi=m.ram[0x7c08],phase=m.ram[0x7c02];
 runFrame(m);seen.add(split);combinations.add(top+'/'+bottom);
 let bad=0;
 for(let y=0;y<192;y++)for(let x=0;x<512;x++){
  const o=row(y);let expected;
  if((y<split?top:bottom)===0x3e){const k=((x>>>3)&1)*8192+o+(x>>>4),b=hi?title2[k]:source[0x8000+k];expected=b&(128>>>(x&7))?7:0;}
  else {const xx=x>>>1,k=o+(xx>>>3),b=pic?frog[k]:source[0xc000+k],a=pic?frog[6144+k]:source[0xe000+k];let ink=a&7,paper=(a>>>3)&7;if(flash&&(a&128))[ink,paper]=[paper,ink];expected=((b&(128>>>(xx&7)))?ink:paper)+((a&64)?8:0);}
  if(m.pixels[(y+24)*640+64+x]!==expected)bad++;
 }
 frames++;pixels+=512*192;maxMismatch=Math.max(maxMismatch,bad);
 if(bad)throw Error('Frame '+frames+' split '+split+': '+bad+' mismatched pixels');
 const name=phase+'-'+pic+'-'+hi+'-'+m.ram[0x7c09]+'-'+String(split).padStart(3,'0');
 if((phase&1)&&split%2===0&&!captures.has(name)){capture(name);captures.add(name);}
}
runFrame(m);runFrame(m);
let titleVisits=0,pictureVisits=0,priorState=m.ram[0x7c02];
const titleIds=new Set(),pictureIds=new Set(),sequence=[],directions=[];
for(let i=0;i<3600;i++){
 check();const state=m.ram[0x7c02];
 if(state!==priorState&&(state===0||state===2)){
  if(m.ram[0x7c01]!==240)throw Error('Endpoint hold is not 240 frames');
  if(m.ram[0x7c00]!== (m.ram[0x7c09]?0:192))throw Error('Wipe did not reach endpoint');
  directions.push(m.ram[0x7c09]?'up':'down');
  if(state===2){titleVisits++;titleIds.add(m.ram[0x7c08]);sequence.push('title'+m.ram[0x7c08]);}
  else {pictureVisits++;pictureIds.add(m.ram[0x7c06]);sequence.push('ecm'+m.ram[0x7c06]);}
 }
 priorState=state;
}
if(titleVisits<4||pictureVisits<4||titleIds.size!==2||pictureIds.size!==2)throw Error('Four-image loop did not repeat');
if(sequence.slice(0,8).join(',')!=='title0,ecm1,title1,ecm0,title0,ecm1,title1,ecm0')throw Error('Wrong image order');
if(new Set(directions).size!==2)throw Error('Random wipes did not cover both directions');
for(const target of [1,3]){
 let budget=1000;while(!(m.ram[0x7c02]===target&&m.ram[0x7c00]===96)&&budget-->0)check();
 if(budget<=0)throw Error('Did not reach manual test position');
 keys[2]=30;for(let i=0;i<32;i++)check();keys.fill(31);
 if(m.ram[0x7c00]!==64)throw Error('Q did not raise boundary');
 keys[1]=30;for(let i=0;i<32;i++)check();keys.fill(31);
 if(m.ram[0x7c00]!==96)throw Error('A did not lower boundary');
 keys[3]=23;check();keys.fill(31);
 if(m.ram[0x7c07]!==0)throw Error('R did not resume');
}
// Space edge toggles pause/resume without repeating while held.
keys[7]=30;check();const paused=m.ram[0x7c07];for(let i=0;i<4;i++)check();
if(m.ram[0x7c07]!==paused)throw Error('Space repeated while held');keys.fill(31);check();
const result={frames,pixels,splitPositions:seen.size,maxMismatch,continuousLoop:true,titleVisits,pictureVisits,sequence,directions,pauseFrames:240,modeCombinations:[...combinations],checkerPixels,whiteBarPixels,checkerFrameThickness:30,timex64ColumnGlyphs:true,twoTitles:true,twoECMPictures:true,manualBothOrientations:true,spaceEdge:true,tsrunCommit:'41dbe3e41c692a1806f2cb900c5a0faa1549ae77'};
fs.writeFileSync(path.join(root,'validation.json'),JSON.stringify(result,null,2));console.log(result);
