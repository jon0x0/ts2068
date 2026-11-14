import fs from'node:fs';import path from'node:path';import assert from'node:assert/strict';import{root,up,api}from'./r22_test_machine.mjs';
export const out=path.join(root,'build/fullgame/l5_cold_start_r98');
export const symbols=Object.fromEntries([...fs.readFileSync(path.join(out,'demand_loader.sym'),'utf8').matchAll(/(\w+): EQU 0x([0-9a-f]+)/ig)].map(v=>[v[1],parseInt(v[2],16)]));
function tape(file){const b=fs.readFileSync(file),blocks=[];for(let p=0;p<b.length;){const n=b.readUInt16LE(p),v=b.subarray(p+2,p+2+n);assert.equal(v.reduce((a,c)=>a^c,0),0);blocks.push({flag:v[0],data:v.subarray(1,-1),checksum:v.at(-1)});p+=n+2;}return blocks;}
const globalTags=new Set(Object.keys(JSON.parse(fs.readFileSync(path.join(out,'global_tags.json'),'utf8'))).map(Number));
export function demandFixture(options={}){
 const joy=new Uint8Array(2).fill(255),m=api.createMachine(new Uint8Array(8).fill(31),joy),store=new Uint8Array(524288).fill(0xa5);m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));api.insertDock(m,Buffer.concat([Buffer.from([0,...Array(8).fill(3)]),Buffer.alloc(65536)]));m.ram.set(fs.readFileSync(path.join(out,'launcher.bin')),0x8000);Object.assign(m.cpu,{pc:0x8000,sp:0xfff0,iff1:false,iff2:false});m.portF4=0;m.portFF=0;
 const expectedCode=Array.from({length:8},(_,i)=>fs.readFileSync(path.join(out,`level${String(i+1).padStart(2,'0')}_region.bin`)).subarray(0,8192));
 
 const c={region:0,pending:null,primes:0,commands:[],mounts:[],blocks:0,booted:false,cwd:'/sd/TAP/GAMES/SHOOTERS/rtype',snapshots:[]},fifo=[],queued=[];let packet=[],phase='header',header=null,currentTape=[],tapIndex=0,currentFile='',lastTx=-10000;
 const map=r=>{c.region=r;for(let b=0;b<8;b++)m.dock[b]=store.subarray(r*65536+((options.alias&&b===2)?1:b)*8192,r*65536+((options.alias&&b===2)?1:b)*8192+8192);};map(0);
 const read=m.bus.read,write=m.bus.write,ioRead=m.bus.ioRead,ioWrite=m.bus.ioWrite;
 m.bus.read=a=>{
 if(m.stepAdded===0&&a===m.cpu.pc){if(a===0x004c&&(m.portF4&1)){const ptr=m.cpu.h*256+m.cpu.l;assert(globalTags.has(ptr),'Unknown global colour source '+JSON.stringify({ptr:ptr.toString(16),map:m.portF4,sp:m.cpu.sp,boot:c.booted,region:c.region,return:m.bus.read(m.cpu.sp)+256*m.bus.read(m.cpu.sp+1)}));}if(a===0x8b06&&!(m.portF4&16)&&read(0x7aa4)>0){if(!Buffer.from(m.dock[0]).equals(expectedCode[c.region])){let ds=[];for(let i=0;i<8192;i++)if(m.dock[0][i]!==expectedCode[c.region][i])ds.push([i,expectedCode[c.region][i],m.dock[0][i]]);throw Error('CODE DIFF '+JSON.stringify({region:c.region,pc:m.cpu.pc,sp:m.cpu.sp,diffs:ds.slice(0,20)}));}c.codeAuditChecks=(c.codeAuditChecks||0)+1;}
  if(a===0x8b06 && !(m.portF4&16) && read(0x7aa4)>0){for(let i=0;i<256;i++)assert.equal(m.ram[0x5d00+i],parseInt(i.toString(2).padStart(8,'0').split('').reverse().join(''),2),'Live reverse table '+i);c.reverseChecks=(c.reverseChecks||0)+1;}
  if(a===symbols.fatal_halt)c.fatalSeen=true;
  if(c.booted&&a===0x0a08){c.coreBefore=Buffer.from(m.ram.slice(0x8400,0xc000));if(c.region===1&&c.coreBefore.subarray(0x42d,0x430).equals(Buffer.from([0xc3,0xd8,1])))c.coreBefore.set([0x3c,0x87,0x87],0x42d);c.metaBefore=Buffer.from(m.dock[3].slice(0,0x1e00));c.metaBefore[0x119c]=c.metaBefore[0x119c]>=56?49:c.metaBefore[0x119c]+1;}
  if(c.booted&&a===symbols.runtime_entry){c.commonBefore=Buffer.from(m.ram.slice(0x8000,0xc000));c.nativeSP=m.cpu.sp;}
  if(a===0x5e00&&m.ram[0x5e0b]===0x21&&m.ram[0x5e0d]===0x5e){if(c.commonBefore){if(!c.commonBefore.equals(Buffer.from(m.ram.slice(0x8000,0xc000)))){fs.writeFileSync(path.join(out,'expected_common.bin'),c.commonBefore);fs.writeFileSync(path.join(out,'actual_common.bin'),m.ram.slice(0x8000,0xc000));fs.writeFileSync(path.join(out,'bad_cache.store.bin'),store);throw Error('Cache common restore failed '+JSON.stringify({region:c.region,holder:m.ram[0xd60d],backup:m.ram[0xd60e],target:m.ram[0xd60c]}));}assert.equal(m.cpu.sp,c.nativeSP);c.commonBefore=null;}c.tailEntered=true;}
  if(c.tailEntered&&a===0x5e28){assert(c.coreBefore.equals(Buffer.from(m.ram.slice(0x8400,0xc000))),'Native core changed before level init');assert(c.metaBefore.equals(Buffer.from(m.dock[3].slice(0,0x1e00))),'Cached score/workspace changed');c.coreChecks=(c.coreChecks||0)+1;c.tailEntered=false;}


 }
if(c.pending!==null&&(m.portF4&1)&&a<8192){c.primes++;if(c.primes>=8&&m.tstates>=(c.readyAt||0)){c.maxPriming=Math.max(c.maxPriming||0,c.primes);map(c.pending);c.pending=null;}}if(a===symbols.cold_launch&&m.cpu.pc===a&&m.stepAdded===0&&!c.initialLoadedSnapshot)c.initialLoadedSnapshot=Buffer.from(store.subarray(0,65536));if(a===0x8634&&m.cpu.pc===a&&m.stepAdded===0)c.booted=true;return read(a);};
 m.bus.write=(a,v)=>{if((m.portFF&7)===1&&a>=0x7800&&a<0x7b00&&!(m.portF4&8)&&v!==0)throw Error('Visible secondary attribute write '+a.toString(16)+' pc '+m.cpu.pc.toString(16)+' '+JSON.stringify({map:m.portF4,hl:m.cpu.h*256+m.cpu.l,de:m.cpu.d*256+m.cpu.e,bc:m.cpu.b*256+m.cpu.c,region:c.region,code:Array.from(m.ram.slice(0x7b00,0x7b12))}));if(c.pending!==null&&(m.portF4&(1<<(a>>>13))))throw Error('External write before8 selector reads');write(a,v);};
 const send=(bytes,delay=0)=>{if(delay)queued.push({at:m.tstates+delay,bytes});else fifo.push(...bytes);};
 m.bus.ioRead=p=>{if((p&255)!==14)return ioRead(p);while(queued.length&&queued[0].at<=m.tstates)fifo.push(...queued.shift().bytes);return fifo.shift()??255;};
 m.bus.ioWrite=(p,v)=>{if((p&255)===255&&(v&7)===1){assert(m.ram.slice(0x7800,0x7b00).every(v=>v===0),'Secondary revealed with dirty attributes');c.hiddenChecks=(c.hiddenChecks||0)+1;}
  if((p&255)!==14){ioWrite(p,v);return;}assert(m.tstates-lastTx>=300,'Unpaced TX');lastTx=m.tstates;
  if(phase==='expected_flag'){
   assert.equal(v,header[0]);const b=currentTape[tapIndex++];assert(b,'Read past end of '+currentFile);assert.equal(b.flag,v);assert.equal(b.data.length,header[7]|header[8]<<8);let payload=Buffer.from(b.data);
   if(options.corrupt&&currentFile==='START01.TAP'&&tapIndex===4)payload[17]^=1;
   fifo.push(b.flag,...payload,b.checksum);c.blocks++;phase='residual';return;
  }
  if(phase==='residual'){if(!options.corrupt)assert.equal(v,0,'Host TAP checksum');assert.equal(fifo.length,0);send([64,1],options.delay?50000:0);phase='header';return;}
  packet.push(v);
  if(phase==='header'&&packet.length===10){assert.equal(packet.reduce((a,b)=>a^b,0),0);header=packet;packet=[];assert.equal(fifo.length+queued.length,0,'Previous reply not drained');if(!(options.timeout&&currentFile==='START01.TAP'&&tapIndex===4))send([1,64],options.delay?100000:0);phase=header[0]===66?'body':'expected_flag';return;}
  if(phase==='body'&&packet.length===(header[7]|header[8]<<8)+4){
   assert.equal(packet.reduce((a,b)=>a^b,0),0);const text=Buffer.from(packet.slice(3,-1)).toString();c.commands.push(text);let status=1;
   if(text==='tpi:memdock'){assert.equal(header[3],1);assert.equal(header[5]&1,0);c.pending=header[5]/2;c.readyAt=m.tstates+(options.selectorDelay||0);assert(c.pending>=0&&c.pending<8,'Cache slot range');c.primes=0;}
   else if(/^tpi:(RTBOOT|RTCORE|START0[1-8]|LEVEL0[1-8]|RTPRELD)\.TAP$/.test(text)){
    currentFile=text.slice(4);c.mounts.push(currentFile);if(options.missing&&(currentFile==='LEVEL02.TAP'||currentFile==='START02.TAP'))status=3;else{currentTape=tape(path.join(out,'rtype',currentFile));tapIndex=0;}
    c.snapshots.push({file:currentFile,home:Buffer.from(m.ram)});
   }else throw Error('Unexpected command / directory change: '+text);
   send([1,64,...(c.commands.length%3?[status]:[129,status,79,75,0])],options.delay?75000:0);packet=[];phase='header';
  }
 };
 return{m,joy,controller:c,store,get fifoCount(){return fifo.length+queued.length;}};
}





