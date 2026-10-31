import fs from 'node:fs';
import {createMachine,insertDock,resetMachine,runFrame} from './tsrun/machine.js';
const root=new URL('.',import.meta.url),row=y=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2);
const palette=[[0,0,0],[0,0,205],[205,0,0],[205,0,205],[0,205,0],[0,205,205],[205,205,0],[205,205,205],[0,0,0],[0,0,255],[255,0,0],[255,0,255],[0,255,0],[0,255,255],[255,255,0],[255,255,255]];
function ppm(name,pixels){const data=Buffer.alloc(640*240*3);for(let i=0;i<pixels.length;i++)for(let c=0;c<3;c++)data[i*3+c]=palette[pixels[i]][c];fs.writeFileSync(new URL(name+'.ppm',root),Buffer.concat([Buffer.from('P6\n640 240\n255\n'),data]));}
for(const name of ['timex-color-atlas','attribute-race-lab']){
 const m=createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(31));
 const err=insertDock(m,new Uint8Array(fs.readFileSync(new URL(name+'.dck',root))));if(err)throw Error(err);resetMachine(m);
 const src=new Uint8Array(fs.readFileSync(new URL(name+'-ram.bin',root)));
 const params=JSON.parse(fs.readFileSync(new URL('race-params.json',root)));
 const outs=[];const orig=m.bus.ioWrite;m.bus.ioWrite=(p,v)=>{outs.push({p:p&255,v,t:m.tstates-m.frameStart});orig(p,v);};
 runFrame(m);runFrame(m);let checked=0,uniqueCounts=new Set();
 const latched=new Uint8Array(640*240);
 for(let f=0;f<120;f++){
  outs.length=0;runFrame(m);
  if(name==='timex-color-atlas'){
   const ff=outs.filter(o=>o.p===255);
   if(ff.length!==480)throw Error('FF count '+ff.length);
   for(let y=0;y<240;y++){
    if(ff[y*2].t!==(16+y)*224-10 ||ff[y*2+1].t!==(16+y)*224+96)throw Error('Atlas timing '+JSON.stringify(ff.slice(0,4)));
   }
  }
  for(let y=0;y<240;y++)for(let x=0;x<640;x++){
   const sy=y-24,sx=x-64;let expected=0,hardware=0;
   if(name==='timex-color-atlas'){
    const band=Math.max(0,Math.min(7,Math.floor(sy/24)));expected=x<320?band:band^7;
    if(sy>=0&&sy<192&&sx>=0&&sx<512){
     if(x<320){const xx=sx>>>1,k=row(sy)+(xx>>>3),a=src[0x6000+k],b=src[0x4000+k];expected=((b&(128>>>(xx&7)))?(a&7):((a>>>3)&7))+((a&64)?8:0);}
     else {const b=src[0x4000+((sx>>>3)&1)*8192+row(sy)+(sx>>>4)];expected=b&(128>>>(sx&7))?band:band^7;}
    }hardware=expected;
   }else if(sy>=0&&sy<192&&sx>=0&&sx<512){
    const xx=sx>>>1,c=xx>>>3,k=row(sy)+c,bit=src[0x4000+k]&(128>>>(xx&7));let a=src[0x6000+k];
    const target=params.targets.indexOf(c);hardware=(bit?a&7:(a>>>3)&7)+((a&64)?8:0);
    if(target>=0 && (xx&7)>=4)a=params.new[sy][target];
    expected=(bit?a&7:(a>>>3)&7)+((a&64)?8:0);
   }
   if(m.pixels[y*640+x]!==expected)throw Error(`${name} frame ${f} pixel ${x},${y} got ${m.pixels[y*640+x]} expected ${expected}`);
   latched[y*640+x]=hardware;checked++;
  }
 }
 if(name==='attribute-race-lab')for(let y=164;y<177;y++)for(const c of params.targets){
  const s=new Set();for(let b=0;b<8;b++)s.add(m.pixels[(y+24)*640+64+(c*8+b)*2]);
  if(s.size!==4)throw Error('Expected 4 distinct colors '+y+','+c);uniqueCounts.add(s.size);
 }
 ppm(name,m.pixels);if(name==='attribute-race-lab')ppm('attribute-race-latched-model',latched);
 let enhancedImageCells=0;
 if(name==='attribute-race-lab')for(let y=96;y<164;y++)for(const c of params.targets){const s=new Set();for(let b=0;b<8;b++)s.add(m.pixels[(y+24)*640+64+(c*8+b)*2]);if(s.size>2)enhancedImageCells++;}
 if(name==='attribute-race-lab'&&enhancedImageCells===0)throw Error('No improvement in image cells');
 const report={frames:120,checkedPixels:checked,pixelMismatches:0,colorsPerTargetCell:[...uniqueCounts],enhancedImageCells,hardwareVerified:false,tsrunCommit:'41dbe3e41c692a1806f2cb900c5a0faa1549ae77'};
 fs.writeFileSync(new URL(name+'-validation.json',root),JSON.stringify(report,null,2));console.log(name,report);
}
