import fs from 'node:fs';
import {createMachine,insertDock,resetMachine,runFrame} from './tsrun/machine.js';
const root=new URL('.',import.meta.url),m=createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(31));
insertDock(m,new Uint8Array(fs.readFileSync(new URL('timex-ecm-highres-reveal.dck',root))));resetMachine(m);
const colors=[[0,0,0],[0,0,205],[205,0,0],[205,0,205],[0,205,0],[0,205,205],[205,205,0],[205,205,205],[0,0,0],[0,0,255],[255,0,0],[255,0,255],[0,255,0],[0,255,255],[255,255,0],[255,255,255]];
const out=new URL('prover-frames/',root);fs.mkdirSync(out,{recursive:true});
const captured=new Set();
for(let i=0;i<1800;i++){
 const split=m.ram[0x7c00],phase=m.ram[0x7c02],pic=m.ram[0x7c06],hi=m.ram[0x7c08],dir=m.ram[0x7c09];runFrame(m);
 const capturePhase=(phase&1)?phase:split===(dir?0:192)?(phase+3)%4:null;
 const name=capturePhase+'-'+pic+'-'+hi+'-'+dir+'-'+String(split).padStart(3,'0');
 if(i<2||capturePhase===null||split%2||captured.has(name))continue;captured.add(name);
 const rgb=Buffer.alloc(640*240*3);
 for(let p=0;p<m.pixels.length;p++)for(let c=0;c<3;c++)rgb[p*3+c]=colors[m.pixels[p]][c];
 fs.writeFileSync(new URL(name+'.ppm',out),Buffer.concat([Buffer.from('P6\n640 240\n255\n'),rgb]));
}
console.log('Captured',captured.size,'frames for the four-screen preview');
