import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import crypto from 'node:crypto';import{fileURLToPath,pathToFileURL}from'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../../TSRun'),api=await import(pathToFileURL(path.join(up,'machine.js'))),out=path.join(root,'build/diagnostics/initial_terrain_r18');fs.mkdirSync(out,{recursive:true});const off=y=>((y&192)<<5)|((y&7)<<8)|((y&56)<<2),results=[];
for(const [target,file]of [['sram_r13','build/ecm_native/RType_level1_ECM_TSPico_RAM_r13.dck'],['rom_r13','build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r13.dck'],['sram_r18','build/ecm_native/RType_level1_ECM_TSPico_RAM_r18.dck'],['rom_r18','build/readonly_ecm/RType_ECM_ROM_candidate.dck']]){
 const cart=fs.readFileSync(path.join(root,file)),joy=new Uint8Array(2).fill(255),m=api.createMachine(new Uint8Array(8).fill(31),joy);m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));api.insertDock(m,cart);api.resetMachine(m);
 let last=-1,record=false,initials=0,solid=0,missing=0,categoryErrors=0,checked=0,bad=0,updates=0,previous=null,currentFrame=0;let coverage=new Uint8Array(6144),expected=new Map();const failures=[],motion=[],read=m.bus.read;
 m.bus.read=a=>{if(m.stepAdded===0&&m.tstates!==last&&a===m.cpu.pc){last=m.tstates;
  if(a===0xff17){record=true;coverage.fill(0);expected.clear();previous=null;}
  if(record&&a===0x8ea2){const h=m.cpu.h<<8|m.cpu.l,d=m.cpu.d<<8|m.cpu.e;if(h>=0xd911&&h<0xe571&&d>=0x7e00&&d<0x8080){const attr=read(h),row=(d-0x7e00)>>5,x=d&31;expected.set(d,!!(attr&128));if(attr&128)for(let y=0;y<8;y++)coverage[off(row*8+y)+x]=255;}}
  if(record&&a===0xff8b){record=false;initials++;for(const [d,isSolid]of expected)if(isSolid){solid++;if(target.startsWith('rom')&&!(read(d+0x300)&64))categoryErrors++;if(read(d)!==255){missing++;if(failures.length<30)failures.push({frame:currentFrame,address:d,id:read(d),row:(d-0x7e00)>>5,col:d&31,attribute:read(d-0x600)});}}fs.writeFileSync(path.join(out,target+'_initial_home.bin'),m.ram);fs.writeFileSync(path.join(out,target+'_initial_coverage.bin'),coverage);}
  if(a===0x8842&&!record&&read(0x7a8e)===0){for(let y=0;y<160;y++){const o=off(y);for(let x=0;x<31;x++)coverage[o+x]=(coverage[o+x]<<1|coverage[o+x+1]>>7)&255;coverage[o+31]=(coverage[o+31]<<1)&255;}}
  if(a===0x8a03&&!record){const d=m.cpu.d<<8|m.cpu.e,row=(d-0x7e00)>>5;if(row>=0&&row<20)for(let y=0;y<8;y++)coverage[off(row*8+y)+(d&31)]=(read(m.cpu.h<<8|m.cpu.l)&128)?255:0;}
  if(a===0x8b06&&read(0x7aa4)>0){updates++;const state={pixels:m.ram.slice(0x4000,0x5800),ids:Uint8Array.from({length:640},(_,i)=>read(0x7e00+i)),counter:read(0x7a89),coverage:coverage.slice()};
   if(previous&&state.counter===((previous.counter+1)&255)&&read(0x7a8e)===0){for(let row=8;row<20;row++)for(let x=2;x<30;x++){const i=row*32+x,actor=id=>id>0&&id<0xdc;if(actor(state.ids[i])||actor(previous.ids[i])||actor(previous.ids[i+1]))continue;for(let dy=0;dy<8;dy++){const o=off(row*8+dy)+x,mask=((previous.coverage[o]<<1|previous.coverage[o+1]>>7)&255)&state.coverage[o];if(!mask)continue;checked++;const e=(previous.pixels[o]<<1|previous.pixels[o+1]>>7)&255;if(((state.pixels[o]^e)&mask)!==0){bad++;if(motion.length<30)motion.push({frame:currentFrame,update:updates,row,x,dy,mask,expected:e,actual:state.pixels[o],id:state.ids[i]});}}}}
   if(updates>=30&&updates<62)fs.writeFileSync(path.join(out,target+'_'+updates+'.bin'),m.ram);previous=state;
  }
 }return read(a);};
 for(let f=0;f<2600;f++){currentFrame=f;joy[0]=f>=800&&f<830?0xef:255;api.runFrame(m);}
 const r={target,bin_sha256:crypto.createHash('sha256').update(cart.subarray(9)).digest('hex'),initials,solid,missing,categoryErrors,checked,bitmap_mismatches:bad,updates,failures,motion};results.push(r);console.log(JSON.stringify(r));
 if(target.endsWith('r18')){assert(solid>50);assert.equal(missing,0);assert.equal(categoryErrors,0);assert(checked>30000);assert.equal(bad,0);}else{assert(missing>50);assert(bad>0);}
}
fs.writeFileSync(path.join(out,'validation.json'),JSON.stringify(results,null,2));
