import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import crypto from'node:crypto';import{root,api,z}from'./r22_test_machine.mjs';
const image=fs.readFileSync(path.join(root,'build/fullgame/RType_fullgame_candidate.ram512')),loader=fs.readFileSync(path.join(root,'build/fullgame/preloader.bin')),sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/fullgame/preloader.sym'),'utf8').matchAll(/(\w+): EQU 0x([0-9a-f]+)/ig)].map(v=>[v[1],parseInt(v[2],16)])),results=[];
function tape(file){const b=fs.readFileSync(file),blocks=[];for(let p=0;p<b.length;){const len=b.readUInt16LE(p),raw=b.subarray(p+2,p+2+len);assert.equal(raw.reduce((a,c)=>a^c,0),0);blocks.push({flag:raw[0],data:raw.subarray(1,-1),checksum:raw.at(-1)});p+=len+2;}return blocks;}
for(const alias of[false,true]){
 const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255)),store=new Uint8Array(524288);m.homeRom.set(fs.readFileSync(path.resolve(root,'../../TSRun/roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.resolve(root,'../../TSRun/roms/ts2068-1.rom')));api.insertDock(m,Buffer.concat([Buffer.from([0,...Array(8).fill(3)]),Buffer.alloc(65536)]));m.ram.set(loader,0x8000);Object.assign(m.cpu,{pc:0x8000,sp:0xfff0,iff1:false,iff2:false});m.portF4=0;m.portFF=0;
 let region=0,pending=null,primes=0,allPrimes=0,commands=0,mounts=0,blocksRead=0,packet=[],phase='header',header=null,currentTape=[],tapIndex=0,fifo=[],lastTx=-10000;const map=r=>{region=r;const actual=alias&&r===4?0:r;for(let b=0;b<8;b++)m.dock[b]=store.subarray(actual*65536+b*8192,actual*65536+(b+1)*8192);};map(0);const read=m.bus.read,write=m.bus.write,ioRead=m.bus.ioRead,ioWrite=m.bus.ioWrite;
 m.bus.read=a=>{if(pending!==null&&(m.portF4&1)&&a<8192){primes++;allPrimes++;if(primes===8){map(pending);pending=null;}}return read(a);};m.bus.write=(a,v)=>{if(pending!==null&&(m.portF4&(1<<(a>>>13))))throw Error('Write before selector priming');write(a,v);};
 m.bus.ioRead=p=>(p&255)===14?(fifo.shift()??255):ioRead(p);
 m.bus.ioWrite=(p,v)=>{if((p&255)!==14){ioWrite(p,v);return;}assert(m.tstates-lastTx>=300,'Unpaced TX');lastTx=m.tstates;
  if(phase==='expected_flag'){
   assert.equal(v,header[0]);const block=currentTape[tapIndex++];assert(block,'Read past volume end');assert.equal(block.flag,v);assert.equal(block.data.length,header[7]|header[8]<<8);fifo.push(block.flag,...block.data,block.checksum);blocksRead++;phase='residual';return;
  }
  if(phase==='residual'){assert.equal(v,0,'TAP checksum');assert.equal(fifo.length,0);fifo.push(64,1);phase='header';return;}
  packet.push(v);
  if(phase==='header'&&packet.length===10){assert.equal(packet.reduce((a,b)=>a^b,0),0);header=packet;packet=[];assert.equal(fifo.length,0,'Reply drained');fifo.push(1,64);phase=header[0]===66?'body':'expected_flag';return;}
  if(phase==='body'&&packet.length===(header[7]|header[8]<<8)+4){assert.equal(packet.reduce((a,b)=>a^b,0),0);const text=Buffer.from(packet.slice(3,-1)).toString();commands++;
   if(text==='tpi:memdock'){assert.equal(header[3],1);assert.equal(header[5]&1,0);pending=header[5]/2;assert(pending<8);primes=0;}
   else if(/^tpi:RTFG[0-9A-F]{2}\.TAP$/.test(text)){currentTape=tape(path.join(root,'build/fullgame/package/RTYPE',text.slice(4)));assert.equal(currentTape.length,8);tapIndex=0;mounts++;}
   else assert(['tpi:cd /','tpi:cd RTYPE'].includes(text),text);
   fifo.push(1,64,...(commands%3?[1]:[129,1,79,75,0]));packet=[];phase='header';
  }
 };
 let steps=0;while(m.cpu.pc!==sym.launch&&m.cpu.pc!==sym.fatal_halt&&steps++<100000000)z.runZ80(m.cpu,m.bus,1,m);assert(steps<100000000,'Preloader stalled at'+m.cpu.pc.toString(16));
 if(alias){assert.equal(m.cpu.pc,sym.fatal_halt,'Alias must be rejected');assert.equal(Buffer.from(m.ram.slice(sym.error_text+6,sym.error_text+8)).toString(),'E2');results.push({alias_negative_control:true,rejected:true,page:m.ram[0xd600],error:'E2',steps,passed:true});}
 else{assert.equal(m.cpu.pc,sym.launch,'Preloader failed');assert.deepEqual(Buffer.from(store),image,'All512KB byte-exact before game launch');assert.equal(mounts,16);assert.equal(blocksRead,128);assert.equal(region,0);assert.equal(fifo.length,0);fs.writeFileSync(path.join(root,'build/fullgame/preloader_screen.bin'),m.ram);results.push({alias_negative_control:false,pages:64,regions:8,mounts,code_blocks:blocksRead,priming_reads:allPrimes,byte_exact:true,steps,seconds_emulated:m.tstates/3528000,passed:true});}
 console.log(results.at(-1));
}
fs.writeFileSync(path.join(root,'build/fullgame/preloader_validation.json'),JSON.stringify({sha256:crypto.createHash('sha256').update(image).digest('hex'),loader_sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,'build/fullgame/preloader.bin'))).digest('hex'),scope:'Actual Z80 preloader, packet/SD-TAP model and access-delayed SRAM selector; not hardware evidence',results,passed:true},null,2));
