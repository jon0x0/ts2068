import fs from 'node:fs';
import {createMachine,insertDock,resetMachine,runFrame} from './tsrun/machine.js';
const root=new URL('.',import.meta.url);
const source=new Uint8Array(fs.readFileSync(new URL('initial-ram.bin',root)));
const m=createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(31));
const err=insertDock(m,new Uint8Array(fs.readFileSync(new URL('split-personality.dck',root))));
if(err)throw Error(err);resetMachine(m);
const row=y=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2);
function paperIndex(y,c){const a=source[0x6000+row(y)+c];return ((a>>>3)&7)+((a&64)?8:0);}
const swatches=Array.from({length:16},(_,c)=>paperIndex(150,c));
if(swatches.some((n,c)=>n!==c))throw Error('Missing palette swatch');
const scanlines=Array.from({length:16},(_,y)=>paperIndex(y+158,0));
if(scanlines.some((n,y)=>n!==y))throw Error('One-pixel vertical color sequence altered');
for(let y=176;y<192;y++)for(let c=0;c<16;c++){
 if(source[0x4000+row(y)+c]!==((y&1)?0x55:0xaa))throw Error('ECM one-pixel checker altered');
}
const writes=[];const original=m.bus.ioWrite;
m.bus.ioWrite=(p,v)=>{if((p&255)===255)writes.push({time:m.tstates-m.frameStart,value:v});original(p,v);};
runFrame(m);runFrame(m);
let checkedPixels=0;const phases=new Set();
for(let f=0;f<180;f++){
 const oldFlash=m.flashFrame;writes.length=0;runFrame(m);
 if(writes.length!==480)throw Error('Expected 480 mode writes, got '+writes.length);
 for(let n=0;n<240;n++){
  const a=writes[n*2],b=writes[n*2+1];
  if(a.time!==(16+n)*224+8||a.value!==2)throw Error('Left phase drift '+JSON.stringify(a));
  if(b.time!==(16+n)*224+96||b.value!==0x36)throw Error('Midpoint drift '+JSON.stringify(b));
  phases.add(a.time%224);phases.add(b.time%224);
 }
 for(let y=0;y<240;y++)for(let x=0;x<640;x++){
  let expected=x<320?4:1;
  if(y>=24&&y<216&&x>=64&&x<576){
   const sy=y-24,sx=x-64,o=row(sy);
   if(x<320){
    const xx=sx>>>1,k=o+(xx>>>3),a=source[0x6000+k],bits=source[0x4000+k];
    let ink=a&7,paper=(a>>>3)&7;if((a&128)&&(oldFlash&16))[ink,paper]=[paper,ink];
    expected=((bits&(128>>>(xx&7)))?ink:paper)+((a&64)?8:0);
   }else{
    const bits=source[0x4000+((sx>>>3)&1)*8192+o+(sx>>>4)];
    expected=(bits&(128>>>(sx&7)))?6:1;
   }
  }
  if(m.pixels[y*640+x]!==expected)throw Error(`Pixel mismatch frame ${f} x ${x} y ${y}: ${m.pixels[y*640+x]} != ${expected}`);
  checkedPixels++;
 }
}
const palette=[[0,0,0],[0,0,205],[205,0,0],[205,0,205],[0,205,0],[0,205,205],[205,205,0],[205,205,205],[0,0,0],[0,0,255],[255,0,0],[255,0,255],[0,255,0],[0,255,255],[255,255,0],[255,255,255]];
const rgb=Buffer.alloc(640*240*3);
for(let i=0;i<m.pixels.length;i++)for(let c=0;c<3;c++)rgb[i*3+c]=palette[m.pixels[i]][c];
fs.writeFileSync(new URL('preview.ppm',root),Buffer.concat([Buffer.from('P6\n640 240\n255\n'),rgb]));
const result={frames:180,checkedPixels,modeWrites:180*480,exactModePhases:[...phases],paletteSwatches:swatches,onePixelVerticalColorSequence:scanlines,ecmOnePixelChecker:true,leftMode:'ECM 2',rightMode:'512-mode 6; yellow ink / blue paper',leftBorder:'green',rightBorder:'blue',pixelMismatches:0,tsrunCommit:'41dbe3e41c692a1806f2cb900c5a0faa1549ae77'};
fs.writeFileSync(new URL('validation.json',root),JSON.stringify(result,null,2));console.log(result);
