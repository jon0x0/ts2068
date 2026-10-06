import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const dir=path.resolve(root,process.argv[2]||'build');
const api=await import(pathToFileURL(path.resolve(root,'../../../TSRun/machine.js')));
const symbols=Object.fromEntries([...fs.readFileSync(path.join(dir,'mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const keys=new Uint8Array(8).fill(31),joy=new Uint8Array(2).fill(255),m=api.createMachine(keys,joy);
for(const [target,name] of [[m.homeRom,'ts2068-0'],[m.exRom,'ts2068-1']])target.set(fs.readFileSync(path.resolve(root,'../../../TSRun/roms/'+name+'.rom')));
const cart=fs.readFileSync(path.join(dir,'sinistar-mining.dck'));api.insertDock(m,cart);api.resetMachine(m);
const labels=['frame_start','composition_start','mr_piece_cached','mr_shift_ready','mr_after_piece','compile','ready','publish','publication_done'];
const times={},sums={},counts={},intervals={};let first=0,last=0,frames=0,setup=false,fastFrames=0;
const read=m.bus.read;m.bus.read=a=>{
 if(a===m.cpu.pc){
  if(a===symbols.game_step&&!setup){m.ram[symbols.game_mode]=0;m.ram[symbols.control_mode]=0;m.ram[symbols.bombs]=0;setup=true;}
  if(a===symbols.frame_start&&m.ram[symbols.awake_done]){
   // Identical moving, changing-phase workload independent of rendering rate.
   const phase=frames%160;
   m.ram[symbols.px]=0;m.ram[symbols.px+1]=232;m.ram[symbols.py]=0;m.ram[symbols.py+1]=152;m.ram[symbols.rock_x]=216;
   m.ram[symbols.face_x]=0;m.ram[symbols.face_x+1]=24+phase%64;
   m.ram[symbols.face_y]=0;m.ram[symbols.face_y+1]=72+Math.floor(phase/8)%40;
  }
  if(m.ram[symbols.awake_done])for(let i=0;i<labels.length;i++)if(a===symbols[labels[i]]){
   times[labels[i]]=m.tstates;
   if(i&&times[labels[i-1]]!==undefined){const n=labels[i-1]+' -> '+labels[i];sums[n]=(sums[n]||0)+m.tstates-times[labels[i-1]];counts[n]=(counts[n]||0)+1;}
   if(i===labels.length-1){if(!frames)first=m.tstates;else{const gap=Math.round((m.tstates-last)/58688);intervals[gap]=(intervals[gap]||0)+1;}last=m.tstates;frames++;if(symbols.fast_cells&&m.ram[0x78f6])fastFrames++;}
  }
 }
 return read(a);
};
for(let i=0;i<14000&&frames<500;i++)api.runFrame(m);
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),frames,fast_frames:fastFrames,refresh_intervals:intervals,tstates_per_picture:(last-first)/(frames-1),pictures_per_second:3528000*(frames-1)/(last-first),stages:Object.fromEntries(Object.entries(sums).map(([k,v])=>[k,Math.round(v/counts[k])]))};
console.log(report);fs.writeFileSync(path.join(root,'build/profile-'+(process.argv[3]||'current')+'.json'),JSON.stringify(report,null,2)+'\n');
