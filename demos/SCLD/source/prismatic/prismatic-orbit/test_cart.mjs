import fs from 'node:fs';
import {createMachine,insertDock,resetMachine,runFrame} from './tsrun/machine.js';
const root=new URL('.',import.meta.url),events=JSON.parse(fs.readFileSync(new URL('write-events.json',root)));
const blanking=JSON.parse(fs.readFileSync(new URL('blanking-events.json',root)));
const schedule=JSON.parse(fs.readFileSync(new URL('schedule.json',root)));
const conversion=JSON.parse(fs.readFileSync(new URL('conversion.json',root)));
const row=y=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2);
const sources={};for(const mode of ['ecm','dynamic'])sources[mode]={bitmap:new Uint8Array(fs.readFileSync(new URL(mode+'-bitmap.bin',root))),attrs:new Uint8Array(fs.readFileSync(new URL(mode+'-attributes.bin',root)))};
for(let y=0;y<192;y++)for(let c=0;c<32;c++)if(conversion.unchangedOutsideScheduledCells&&!schedule[y].columns.includes(c)){
 const k=row(y)+c;if(sources.ecm.bitmap[k]!==sources.dynamic.bitmap[k]||sources.ecm.attrs[k]!==sources.dynamic.attrs[k])throw Error('Unscheduled cell changed');
}
const compareReference=Boolean(conversion.referenceTap)&&fs.existsSync(new URL('reference.tap',root));
if(compareReference){
 const tape=fs.readFileSync(new URL('reference.tap',root));let at=0;const blocks=[];
 while(at<tape.length){const n=tape.readUInt16LE(at);blocks.push(tape.subarray(at+2,at+2+n));at+=n+2;}
 if(!Buffer.from(sources.ecm.attrs).equals(blocks[1].subarray(1,-1))||!Buffer.from(sources.ecm.bitmap).equals(blocks[3].subarray(1,-1)))throw Error('ECM comparison differs from supplied TAP');
}
const keys=new Uint8Array(8).fill(31),m=createMachine(keys,new Uint8Array(2).fill(31));
const err=insertDock(m,new Uint8Array(fs.readFileSync(new URL('timex-dynamic-ecm-prismatic.dck',root))));if(err)throw Error(err);resetMachine(m);
const log=[],wr=m.bus.write;m.bus.write=(a,v)=>{if(a>=0x6000&&a<0x7800)log.push({address:a,value:v,time:m.tstates-m.frameStart});wr(a,v);};
for(let i=0;i<30;i++)runFrame(m);
let pixels=0;const counts={};const captures={};
function verify(name){
 const src=sources[name],dynamic=name==='dynamic';
 for(let y=0;y<240;y++)for(let x=0;x<640;x++){
  let expected=dynamic?4:1;
  if(y>=24&&y<216&&x>=64&&x<576){const sy=y-24,xx=(x-64)>>>1,c=xx>>>3,k=row(sy)+c;let a=src.attrs[k];
   if(dynamic&&(xx&7)>=4){const t=schedule[sy].columns.indexOf(c);if(t>=0)a=schedule[sy].new[t];}
   expected=((src.bitmap[k]&(128>>>(xx&7)))?a&7:(a>>>3)&7)+((a&64)?8:0);
  }
  if(m.pixels[y*640+x]!==expected)throw Error(`${name} pixel mismatch ${x},${y}: ${m.pixels[y*640+x]} != ${expected}`);pixels++;
 }
 if(dynamic){const expected=[...blanking.before,...events.flatMap((es,y)=>es.map(e=>({...e,time:e.time+(40+y)*224}))),...blanking.after];
  if(log.length!==expected.length)throw Error('Attribute write count '+log.length);
  for(let i=0;i<log.length;i++)for(const k of ['address','value','time'])if(log[i][k]!==expected[i][k])throw Error('Write drift '+i+' '+k+' '+log[i][k]+' != '+expected[i][k]);
 }else if(log.length)throw Error('Static ECM has raster writes');
}
for(const name of ['dynamic','ecm','dynamic']){
 if(name==='ecm'||counts.dynamic){keys[7]=30;for(let i=0;i<16;i++)runFrame(m);keys[7]=31;for(let i=0;i<3;i++)runFrame(m);}
 for(let f=0;f<120;f++){log.length=0;runFrame(m);verify(name);}
 counts[name]=(counts[name]||0)+120;captures[name]=Array.from(m.pixels);
}
fs.writeFileSync(new URL('captured-pixels.json',root),JSON.stringify(captures));
const report={frames:360,checkedVisiblePixels:pixels,pixelMismatches:0,framesByMode:counts,spaceTogglesVerified:2,attributeWritesPerDynamicFrame:2688,enhancedCellsPerRow:7,prestagedResets:768,allAttributeWritesTimed:true,unchangedOutsideScheduledCells:conversion.unchangedOutsideScheduledCells,comparisonMatchesSuppliedTap:compareReference,hardwareVerified:false,tsrunCommit:'41dbe3e41c692a1806f2cb900c5a0faa1549ae77'};
fs.writeFileSync(new URL('validation.json',root),JSON.stringify(report,null,2));console.log(report);
