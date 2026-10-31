import fs from 'node:fs';
import {createMachine,insertDock,resetMachine,runFrame} from './tsrun/machine.js';
const root=new URL('.',import.meta.url),row=y=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2);
const palette=[[0,0,0],[0,0,205],[205,0,0],[205,0,205],[0,205,0],[0,205,205],[205,205,0],[205,205,205],[0,0,0],[0,0,255],[255,0,0],[255,0,255],[0,255,0],[0,255,255],[255,255,0],[255,255,255]];
const reports=[];
for(const name of ['timex-dynamic-ecm-probe','timex-dynamic-ecm-push','timex-dynamic-ecm-exchange'].flatMap(n=>[n,n+'-hardware'])){
 const hardware=name.endsWith('-hardware'),slug=hardware?name.slice(0,-9):name;
 const schedule=JSON.parse(fs.readFileSync(new URL(slug+'-schedule.json',root)));
 const src=new Uint8Array(fs.readFileSync(new URL(slug+'-ram.bin',root)));
 const m=createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(31));
 const err=insertDock(m,new Uint8Array(fs.readFileSync(new URL(name+'.dck',root))));if(err)throw Error(err);resetMachine(m);
 // Equivalent entry mapping/address to OUT 244,64: RANDOMIZE USR 49160.
 // The test exercises the actual DOCK copy bootstrap, not HOME preloading.
 if(hardware){m.bus.ioWrite(244,64);m.cpu.pc=0xc008;for(let f=0;f<30;f++)runFrame(m);if(m.cpu.im!==2)throw Error('Hardware bootstrap failed');}
 const log=[],wr=m.bus.write;m.bus.write=(a,v)=>{if(a>=0x6000&&a<0x7800)log.push({address:a,value:v,time:m.tstates-m.frameStart});wr(a,v);};
 runFrame(m);runFrame(m);let pixels=0;const histogram={single:{},burst:{},dense:{}};
 for(let f=0;f<120;f++){
  log.length=0;runFrame(m);const expectedEvents=schedule.flatMap(s=>s.events.map(e=>({...e,time:e.time+(40+s.y)*224})));
  if(log.length!==expectedEvents.length)throw Error('Write count '+slug);
  for(let i=0;i<log.length;i++)for(const k of ['address','value','time'])if(log[i][k]!==expectedEvents[i][k])throw Error(`Write drift ${slug} event ${i} ${k}: ${log[i][k]} != ${expectedEvents[i][k]}`);
  for(let y=0;y<240;y++)for(let x=0;x<640;x++){
   let expected=4;
   if(y>=24&&y<216&&x>=64&&x<576){
    const sy=y-24,xx=(x-64)>>>1,c=xx>>>3,k=row(sy)+c,s=schedule[sy];let a=src[0x6000+k];
    for(const e of s.events)if(e.address===0x6000+k&&e.time<=32+xx/2)a=e.value;
    expected=((src[0x4000+k]&(128>>>(xx&7)))?a&7:(a>>>3)&7)+((a&64)?8:0);
   }
   if(m.pixels[y*640+x]!==expected)throw Error(`Pixel mismatch ${slug} frame ${f} x ${x} y ${y}: ${m.pixels[y*640+x]} != ${expected}`);pixels++;
  }
  if(f===0)for(const s of schedule)for(const c of s.targets){
   const colors=new Set();for(let b=0;b<8;b++)colors.add(m.pixels[(s.y+24)*640+64+c*16+b*2]);
   const band=s.y<80?'single':s.y<130?'burst':'dense';histogram[band][colors.size]=(histogram[band][colors.size]||0)+1;
  }
 }
 const rgb=Buffer.alloc(640*240*3);for(let i=0;i<m.pixels.length;i++)for(let c=0;c<3;c++)rgb[i*3+c]=palette[m.pixels[i]][c];
 fs.writeFileSync(new URL(name+'.ppm',root),Buffer.concat([Buffer.from('P6\n640 240\n255\n'),rgb]));
 reports.push({cartridge:name+'.dck',dockCopyBootstrapTested:hardware,frames:120,checkedVisiblePixels:pixels,pixelMismatches:0,allAttributeWritesTimed:true,targetCellColorHistogram:histogram,hardwareVerified:false});
}
fs.writeFileSync(new URL('validation.json',root),JSON.stringify(reports,null,2));console.log(reports);
