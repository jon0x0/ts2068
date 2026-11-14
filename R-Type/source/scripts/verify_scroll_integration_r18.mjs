import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import crypto from 'node:crypto';import {fileURLToPath,pathToFileURL} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../TSRun'),api=await import(pathToFileURL(path.join(up,'machine.js'))),results=[];
const off=y=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2);
for(const target of ['r18','rom']){
 const dir=path.join(root,target==='rom'?'build/readonly_ecm':'build/ecm_native'),cart=fs.readFileSync(path.join(dir,target==='rom'?'RType_ECM_ROM_candidate.dck':'RType_level1_ECM_TSPico_RAM_r18.dck')),sym=fs.readFileSync(path.join(dir,'renderer.sym'),'utf8'),entry=parseInt(sym.match(/terrain_after_pixel_scroll: EQU 0x([0-9a-f]+)/i)[1],16),joy=new Uint8Array(2).fill(255),m=api.createMachine(new Uint8Array(8).fill(31),joy);
 m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));api.insertDock(m,cart);api.resetMachine(m);
 let last=-1,pending=null,spans=0,boundaries=0,spill=0;const phases=new Set(),read=m.bus.read;
 m.bus.read=a=>{
  if(m.stepAdded===0&&m.tstates!==last&&a===m.cpu.pc){last=m.tstates;
   if(pending&&a===0x8869){assert.deepEqual(m.ram.slice(0x6000,0x7800),pending.expected,`${target} frame${pending.frame} phase${pending.phase} row${pending.row}`);pending=null;spans++;}
   if(a===entry){assert(!pending);const c=m.cpu,phase=read(0x7a82),left=c.e&31,right=Math.min(30,c.c&31),row=((c.d<<8|c.e)-0x7e00)>>5,expected=Uint8Array.from(m.ram.slice(0x6000,0x7800)),mask=(255<<(phase+1))&255;phases.add(phase);
    assert(row>=0&&row<20&&right>=left);if(left>0&&read((c.d<<8)|c.e)<0xdc)spill++;
    for(let x=Math.max(1,left);x<=right;x++){
     const a=m.ram[0x5800+row*32+x],b=(x===30?read(0x7800+row*32+31):m.ram[0x5800+row*32+x+1]),decode=(a,y)=>(a&128)?fs.readFileSync(path.join(root,'build/art_assets/terrain_palette.bin'))[(a&127)*8+y]:a;
     if(x===left&&left>0&&read((c.d<<8)|c.e)<0xdc){for(let dy=0;dy<8;dy++)expected[off(row*8+dy)+x]=decode(b,dy);continue;}if(a===b&&phase!==0&&phase!==7)continue;if(a!==b)boundaries++;
     for(let dy=0;dy<8;dy++){const o=off(row*8+dy)+x;expected[o]=decode((m.ram[0x4000+o]&mask)?a:b,dy);}
    }
    pending={expected,phase,row,frame:m.frameCount};
   }
  }return read(a);
 };
 for(let f=0;f<8000;f++){joy[0]=f>=800&&f<830?0xef:255;api.runFrame(m);}
 assert(spans>100&&phases.size===8&&spill>0&&boundaries>0);results.push({target,bin_sha256:crypto.createHash('sha256').update(cart.subarray(9)).digest('hex'),frames:8000,spans,boundary_cells:boundaries,spill_spans:spill,phases:[...phases].sort(),passed:true});console.log(results.at(-1));
}
fs.writeFileSync(path.join(root,'build/diagnostics/terrain_motion/scroll_integration_r18.json'),JSON.stringify(results,null,2));
