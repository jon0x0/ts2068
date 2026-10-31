import fs from 'node:fs';
import {createMachine,insertDock,resetMachine,runFrame} from './tsrun/machine.js';
const root=new URL('.',import.meta.url),stages=JSON.parse(fs.readFileSync(new URL('stages.json',root)));
const source=new Uint8Array(fs.readFileSync(new URL('ecm-art.bin',root)));
const hires=new Uint8Array(fs.readFileSync(new URL('hires-art.bin',root)));
const m=createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(31));
const err=insertDock(m,new Uint8Array(fs.readFileSync(new URL('split-personality-evolution.dck',root))));if(err)throw Error(err);resetMachine(m);
const colors=[[0,0,0],[0,0,205],[205,0,0],[205,0,205],[0,205,0],[0,205,205],[205,205,0],[205,205,205],[0,0,0],[0,0,255],[255,0,0],[255,0,255],[0,255,0],[0,255,255],[255,255,0],[255,255,255]];
const row=y=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2);
let renderedIndex=null;
const io=m.bus.ioWrite,outs=[];m.bus.ioWrite=(p,v)=>{if((p&255)===255){outs.push({t:m.tstates-m.frameStart,v});if(m.cpu.pc===0x44)renderedIndex=((m.ram[0xfe01]|m.ram[0xfe02]<<8)-0x4000)/226;}io(p,v);};
fs.mkdirSync(new URL('frames/',root),{recursive:true});
for(const name of fs.readdirSync(new URL('frames/',root)))if(name.startsWith('anim-'))fs.unlinkSync(new URL('frames/'+name,root));
function capture(name){
 const data=Buffer.alloc(640*240*3);for(let i=0;i<m.pixels.length;i++)for(let c=0;c<3;c++)data[i*3+c]=colors[m.pixels[i]][c];
 fs.writeFileSync(new URL('frames/'+name+'.ppm',root),Buffer.concat([Buffer.from('P6\n640 240\n255\n'),data]));
}
runFrame(m);let pixels=0,fastFrames=0,loopRestarts=0,restartFrames=0,previousIndex=0;const seen=new Set();const captured=new Set();const samples=[];
for(let f=0;f<3300;f++){
 outs.length=0;renderedIndex=null;runFrame(m);
 const index=renderedIndex;
 if(index===null){
  restartFrames++;
  for(let y=0;y<192;y++)for(let x=0;x<512;x++)if(m.pixels[(y+24)*640+x+64]!==0)throw Error('Reset frame not clean black');
  for(let y=0;y<240;y++)for(let x=0;x<640;x++)if((y<24||y>=216||x<64||x>=576)&&m.pixels[y*640+x]!==4)throw Error('Reset border not steady green');
  if(loopRestarts===0)capture('anim-'+String(f).padStart(4,'0')+'-reset');
  continue;
 }
 if(!Number.isInteger(index)||!stages[index])throw Error('Bad source entry '+index);
 const s=stages[index];seen.add(s.stage);
 if(index<previousIndex)loopRestarts++;previousIndex=index;
 const active=outs.filter(o=>o.t>=8960&&o.t<51968);
 if(active.length!==384)throw Error('Mode write count '+f+' '+index+' '+active.length);
 for(let y=0;y<192;y++){
  const converted=s.stage===5&&y>=s.threshold;
  const left=converted?0x26:2,right=converted?2:0x36;
  if(active[y*2].t!==(40+y)*224+2||active[y*2].v!==left)throw Error('Left phase/mode drift frame '+f+' row '+y+' '+JSON.stringify(active[y*2]));
  if(active[y*2+1].t!==(40+y)*224+32+s.cols[y]*4||active[y*2+1].v!==right)throw Error('Boundary drift frame '+f+' row '+y);
  for(let x=0;x<512;x++){
   const mode=x<s.cols[y]*16?left:right;let expected;
   if((mode&7)===2){const xx=x>>>1,k=row(y)+(xx>>>3),a=source[0x6000+k],b=source[0x4000+k];expected=((b&(128>>>(xx&7)))?(a&7):((a>>>3)&7))+((a&64)?8:0);}
   else {const b=hires[0x4000+((x>>>3)&1)*8192+row(y)+(x>>>4)],ink=(mode>>>3)&7;expected=b&(128>>>(x&7))?ink:ink^7;}
   if(m.pixels[(y+24)*640+x+64]!==expected)throw Error(`Pixel mismatch frame ${f} stage ${s.stage} x ${x} y ${y}`);pixels++;
  }
 }
 const finalBorders=s.final&&outs.some(o=>o.t>=3500&&o.t<8960);
 if(finalBorders){
  fastFrames++;
  if(fastFrames===1)capture('final');
  for(let y=0;y<240;y++)for(let x=0;x<640;x++)if(y<24||y>=216||x<64||x>=576){
   const expected=y<120?(x<320?4:1):(x<320?3:2);
   if(m.pixels[y*640+x]!==expected)throw Error('Final border mismatch '+x+','+y);
  }
 }
 else {
  // All visible border pixels are checked on every ordinary animation frame,
  // including idle, kernel preparation and artwork transition frames.
  for(let y=0;y<240;y++)for(let x=0;x<640;x++)if(y<24||y>=216||x<64||x>=576){
   let expected=4;
   if(y>=24&&y<216){
    const sy=y-24,converted=s.stage===5&&sy>=s.threshold;
    expected=x<64?(converted?3:(s.stage===5&&sy>=96?2:4)):(converted?2:1);
   }
   if(m.pixels[y*640+x]!==expected)throw Error(`Animated border mismatch frame ${f} entry ${index} pixel ${x},${y}: ${m.pixels[y*640+x]} != ${expected}`);
  }
 }
 if(!captured.has(index)&&(index===0||index===17||index===34||index===51||index===59||index===67||index===75||index===83||index>=84&&index%4===0||s.final)){
  const name=String(index).padStart(3,'0');capture(name);captured.add(index);samples.push({file:name+'.ppm',stage:s.stage});
 }
 if(f%6===0&&loopRestarts===0)capture('anim-'+String(f).padStart(4,'0'));
}
if(seen.size!==6||fastFrames<50||loopRestarts<2)throw Error('Missing stage, stable final, or repeated loops');
const result={frames:3300,pixels,pixelMismatches:0,allVisibleBordersChecked:true,stableAnimatedTopAndBottomBorder:'green',independentEcmAndHiresArtwork:true,loopRestarts,restartFrames,finalHoldFrames:120,stages:[...seen],stableFinalFrames:fastFrames,exactPerScanlineTiming:true,finalBorderColors:{upperLeft:'green',upperRight:'blue',lowerLeft:'magenta',lowerRight:'red'},lowerLeftInk:'green (native complement of magenta)',samples};
fs.writeFileSync(new URL('validation.json',root),JSON.stringify(result,null,2));console.log(result);
