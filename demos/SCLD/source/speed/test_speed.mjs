import fs from 'node:fs';
import {createMachine,insertDock,resetMachine,runFrame} from './tsrun/machine.js';
import {createZ80,runZ80} from './tsrun/z80.js';
const root=new URL('.',import.meta.url),params=JSON.parse(fs.readFileSync(new URL('speed-params.json',root)));
const src=new Uint8Array(fs.readFileSync(new URL('attribute-speed-lab-ram.bin',root)));
const row=y=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2);
const m=createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(31));
const err=insertDock(m,new Uint8Array(fs.readFileSync(new URL('attribute-speed-lab.dck',root))));if(err)throw Error(err);resetMachine(m);
const writes=[],write=m.bus.write;m.bus.write=(addr,v)=>{if(addr>=0x6000&&addr<0x7800)writes.push({addr,v,t:m.tstates-m.frameStart});write(addr,v);};
runFrame(m);runFrame(m);let checked=0,maxColors=0;const histogram={},phases=new Set();
for(let f=0;f<120;f++){
 writes.length=0;runFrame(m);
 if(writes.length!==192*9)throw Error('Unexpected attribute write count '+writes.length);
 for(let y=0;y<192;y++){
  const s=params.rows[y];phases.add(s.phase);
  for(let g=0;g<3;g++)for(let i=0;i<3;i++){
   const w=writes[y*9+g*3+i],t=(40+y)*224+s.writeTimes[g][i];
   if(w.t!==t||w.addr!==0x6000+row(y)+params.targets[g]||w.v!==s.values[i])throw Error('Write phase drift '+JSON.stringify({y,g,i,w,t}));
  }
  for(let c=0;c<32;c++){
   const colors=new Set(),g=params.targets.indexOf(c),k=row(y)+c,bitmap=src[0x4000+k];
   for(let b=0;b<8;b++){
    let a=src[0x6000+k];
    if(g>=0){a=s.values[2];for(let i=0;i<3;i++)if(s.writeTimes[g][i]<=32+(c*8+b)/2)a=s.values[i];}
    const expected=((bitmap&(128>>>b))?a&7:(a>>>3)&7)+((a&64)?8:0);
    colors.add(expected);
    for(let repeat=0;repeat<2;repeat++){const got=m.pixels[(y+24)*640+64+c*16+b*2+repeat];if(got!==expected)throw Error(`Pixel mismatch ${y},${c},${b}: ${got} != ${expected}`);checked++;}
   }
   if(f===0&&g>=0&&y>=32&&y<177){histogram[colors.size]=(histogram[colors.size]||0)+1;maxColors=Math.max(maxColors,colors.size);}
  }
 }
}
// Independently exercise multi-write CPU instructions. The unmodified core
// timestamps their two callbacks at instruction start; they address different bytes.
const burstTests=[];
for(const [name,opcode,budget] of [['PUSH BC',0xc5,11],['EX (SP),HL',0xe3,19]]){
 const cpu=createZ80(),ram=new Uint8Array(65536),log=[];
 cpu.sp=0x6102;cpu.b=0x51;cpu.c=0x74;cpu.h=0x51;cpu.l=0x74;ram[0]=opcode;
 const bus={read:a=>ram[a&65535],write:(a,v)=>{log.push({address:a,value:v});ram[a&65535]=v;},ioRead:()=>255,ioWrite:()=>{}};
 const clock={tstates:0,stepAdded:0};runZ80(cpu,bus,budget,clock);
 if(log.length!==2||log[0].address===log[1].address)throw Error('Unexpected burst behavior');
 burstTests.push({name,tstates:clock.tstates,writes:log,sameAddress:false});
}
const palette=[[0,0,0],[0,0,205],[205,0,0],[205,0,205],[0,205,0],[0,205,205],[205,205,0],[205,205,205],[0,0,0],[0,0,255],[255,0,0],[255,0,255],[0,255,0],[0,255,255],[255,255,0],[255,255,255]];
const rgb=Buffer.alloc(640*240*3);for(let i=0;i<m.pixels.length;i++)for(let c=0;c<3;c++)rgb[i*3+c]=palette[m.pixels[i]][c];
fs.writeFileSync(new URL('preview.ppm',root),Buffer.concat([Buffer.from('P6\n640 240\n255\n'),rgb]));
const result={frames:120,checkedActivePixels:checked,pixelMismatches:0,sameAddressWriteIntervalTstates:7,phases:[...phases].sort(),maxColorsPer8x1Cell:maxColors,targetCellHistogram:histogram,burstTests,hardwareVerified:false};
fs.writeFileSync(new URL('validation.json',root),JSON.stringify(result,null,2));console.log(result);
