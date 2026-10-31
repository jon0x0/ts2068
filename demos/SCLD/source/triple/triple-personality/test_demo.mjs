import fs from 'node:fs';
import {createMachine,insertDock,resetMachine,runFrame} from './tsrun/machine.js';
const root=new URL('.',import.meta.url);
const source=new Uint8Array(fs.readFileSync(new URL('initial-ram.bin',root)));
const events=JSON.parse(fs.readFileSync(new URL('mode-events.json',root)));
const row=y=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2);
const m=createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(31));
const err=insertDock(m,new Uint8Array(fs.readFileSync(new URL('triple-personality-mosaic.dck',root))));
if(err)throw Error(err);resetMachine(m);
const writes=[],original=m.bus.ioWrite;
m.bus.ioWrite=(p,v)=>{if((p&255)===255)writes.push({time:m.tstates-m.frameStart,value:v});original(p,v);};
for(let f=0;f<4;f++)runFrame(m);
let checkedPixels=0,modeChanges=0;const pixelsByMode={H:0,E:0,N:0};
for(let f=0;f<300;f++){
 writes.length=0;runFrame(m);
 if(writes.length!==events.length)throw Error('Mode write count '+writes.length);
 let previous=0;
 for(let i=0;i<events.length;i++){
  for(const k of ['time','value'])if(writes[i][k]!==events[i][k])throw Error(`Mode write ${i} ${k}: ${writes[i][k]} != ${events[i][k]}`);
  if(writes[i].value!==previous)modeChanges++;previous=writes[i].value;
 }
 for(let y=0;y<240;y++)for(let x=0;x<640;x++){
  let expected=4;
  if(y>=24&&y<216){
   const sy=y-24,order=(Math.floor(sy/32)&1)?['N','E','H']:['H','E','N'];
   if(x<64||x>=576)expected=order[0]==='H'?1:4;
   else{
    const sx=x-64,xx=sx>>>1,c=xx>>>3,panel=Math.min(9,Math.floor(c/3)),mode=order[panel%3],o=row(sy);
    if(mode==='H'){
     const bits=source[0x4000+((sx>>>3)&1)*8192+o+(sx>>>4)];expected=(bits&(128>>>(sx&7)))?6:1;
    }else{
     const bits=source[0x4000+o+c],a=source[mode==='E'?0x6000+o+c:0x5800+Math.floor(sy/8)*32+c];
     expected=((bits&(128>>>(xx&7)))?a&7:(a>>>3)&7)+((a&64)?8:0);
    }
    if(f===0)pixelsByMode[mode]++;
   }
  }
  if(m.pixels[y*640+x]!==expected)throw Error(`Pixel ${x},${y} frame ${f}: ${m.pixels[y*640+x]} != ${expected}`);
  checkedPixels++;
 }
}
fs.writeFileSync(new URL('captured-pixels.json',root),JSON.stringify(Array.from(m.pixels)));
const report={frames:300,checkedVisiblePixels:checkedPixels,pixelMismatches:0,modeWritesPerFrame:events.length,actualModeChangesPerFrame:modeChanges/300,horizontalBoundariesPerFrame:9*192,regionsPerLine:10,allThreeModesOnEveryActiveLine:true,pixelsByMode,orderReversesEvery:32,allPortWritesTimed:true,hardwareVerified:false,tsrunCommit:'41dbe3e41c692a1806f2cb900c5a0faa1549ae77'};
fs.writeFileSync(new URL('validation.json',root),JSON.stringify(report,null,2));console.log(report);
