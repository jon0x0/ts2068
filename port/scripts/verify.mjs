// Execute assembled Z80 against independent integer models of the cited 6809.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const upstream=path.resolve(root,'../../../TSRun');
const {createZ80,runZ80}=await import(pathToFileURL(path.join(upstream,'z80.js')));
const api=await import(pathToFileURL(path.join(upstream,'machine.js')));
const read=n=>fs.readFileSync(path.join(root,n));
const symbols=Object.fromEntries([...read('build/symbols.txt').toString().matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const memory=new Uint8Array(65536); memory.set(read('build/bank4.bin'),0x8000);
const cpu=createZ80(), clock={tstates:0,stepAdded:0};
let writes=0,cases=0;
const bus={read:a=>memory[a],write:(a,v)=>{assert.ok((a>=0x7f00&&a<0x8000)||(a>=0x7900&&a<0x7908),`Unexpected routine write ${a.toString(16)}`);memory[a]=v;writes++;},ioRead:()=>255,ioWrite:()=>{throw Error('Kernel routine performed I/O');}};
const signed=x=>(x<<16)>>16;
const put=(hi,lo,n)=>{cpu[hi]=(n>>8)&255;cpu[lo]=n&255;};
const hl=()=>signed(cpu.h*256+cpu.l);
const timing={};
function invoke(name){
 cpu.pc=symbols[name];cpu.sp=0x7ffd;cpu.halted=false;
 memory[0x7ffd]=0;memory[0x7ffe]=1; // sentinel return address $0100
 const start=clock.tstates;
 let steps=0;
 while(cpu.pc!==0x100){assert.ok(++steps<1000,`Nontermination ${name}`);runZ80(cpu,bus,1,clock);}
 assert.equal(cpu.sp,0x7fff);
 timing[name]=Math.max(timing[name]||0,clock.tstates-start);cases++;
}
// Hand-resolved original table: intentionally independent of build parser.
const table=[[32767,2047,5],[4000,4096,4],[1024,128,1],[600,320,5],[80,256,3],[64,192,4],[32,128,4],[16,96,3],[0,64,2]];
assert.deepEqual(JSON.parse(read('build/sinistar-speeds.json')),table);
for(let distance=-32767;distance<=32767;distance++){
 put('h','l',distance);put('xh','xl',symbols.sinistar_speeds);
 invoke('new_velocity');
 const magnitude=table.find(row=>Math.abs(distance)>=row[0])[1];
 const desired=distance<0?magnitude:-magnitude;
 const shift=table.find(row=>magnitude>=row[1])[2];
 assert.equal(hl(),desired,`distance ${distance}`);assert.equal(cpu.a,shift);
}
// Every 16-bit difference and shift; vary current to exercise addition wrap.
for(let bits=0;bits<65536;bits++)for(let shift=0;shift<8;shift++){
 const current=signed((bits*109+shift*7919)&65535);
 const diff=signed(bits),desired=signed(current+diff);
 put('h','l',desired);put('d','e',current);cpu.a=shift;
 invoke('smooth_velocity');
 const expected=diff===0?current:signed(current+((diff>>shift)|1));
 assert.equal(hl(),expected,`smooth ${desired},${current},${shift}`);
}
// Every signed angular difference and every radius; vary starting heading.
for(let delta=-128;delta<128;delta++)for(let radius=0;radius<256;radius++){
 const current=(delta*31+radius*17)&255;
 cpu.a=current;cpu.b=(current+delta)&255;cpu.c=radius;
 invoke('player_turn');
 assert.equal(cpu.a,(current+Math.floor((delta*radius+128)/256))&255,`turn ${delta},${radius}`);
}
const sines=[0,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,59,62,65,67,70,73,75,78,80,82,85,87,89,91,94,96,98,100,102,103,105,107,108,110,112,113,114,116,117,118,119,120,121,122,123,123,124,125,125,126,126,126,126,126];
for(let angle=0;angle<256;angle++){
 cpu.a=angle;invoke('player_sincos');
 const q=angle>>6,p=angle&63;
 const sine=(q&1)?sines[63-p]:sines[p];
 const cosine=(q&1)?sines[p]:sines[63-p];
 assert.equal(cpu.d,q>=2?sine^255:sine);
 assert.equal(cpu.e,q===1||q===2?cosine^255:cosine);
}
let accelerationCases=0;
for(const radius of [0,1,13,50,114,127,128,254,255])for(let bits=0;bits<65536;bits++){
 const current=signed(bits*29),diff=signed(bits),desired=signed(current+diff);
 put('h','l',desired);put('d','e',current);cpu.c=radius;
 invoke('player_accelerate');accelerationCases++;
 const product=signed(Math.floor(diff*radius/256));
 assert.equal(hl(),signed(current+Math.floor((product+4)/8)),`player acceleration ${diff},${radius}`);
}
let seed=0x20681982;
const random=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return seed>>>0;};
const signed8=x=>(x<<24)>>24;
let cameraCases=0,integrateCases=0,hardBranches=0;
for(let i=0;i<100000;i++){
 const pos=random()&65535,vel=signed(random()),scroll=signed(random()),unit=signed8(random()),axis=i&1;
 const predicted=((pos+vel+scroll)&65535)>>8;
 const hard=predicted<(axis?16:8)||predicted>=(axis?240:108);
 let base=hard?signed(-vel):scroll;if(hard)hardBranches++;
 let e=signed8((axis?123:56)-(pos>>8));if(axis)e>>=1;
 e=signed8(e-(unit>>3));let correction=signed(e*8-vel-base)>>5;
 const want=signed(base+correction+(correction>>1));
 memory[0x7900]=pos&255;memory[0x7901]=pos>>8;
 memory[0x7902]=vel&255;memory[0x7903]=(vel>>8)&255;
 memory[0x7904]=scroll&255;memory[0x7905]=(scroll>>8)&255;
 memory[0x7906]=unit&255;memory[0x7907]=axis;
 put('xh','xl',0x7900);invoke('camera_axis');cameraCases++;
 assert.equal(hl(),want,`camera case ${i}`);
 assert.equal(signed(memory[0x7904]+256*memory[0x7905]),want);
}
for(let i=0;i<100000;i++){
 const position=i<65536?((i&1)?0xffff00:0)+(i&255):random()&0xffffff;
 const speed=i<65536?signed(i):signed(random());
 memory[0x7900]=position&255;memory[0x7901]=(position>>8)&255;memory[0x7902]=(position>>16)&255;
 put('h','l',0x7900);put('d','e',speed);invoke('camera_integrate');integrateCases++;
 assert.equal(memory[0x7900]+256*memory[0x7901]+65536*memory[0x7902],(position+speed)&0xffffff);
}
let chaseCases=0;
for(let i=0;i<200000;i++){
 const desired=i<65536?signed(i):signed(random());
 const target=i<65536?signed(i*13+127):signed(random());
 const limit=i<65536?2047:random()&32767;
 let expected=desired;
 if((desired<0)===(target<0)){
  expected=signed(desired+target);
  if(desired>=0){if(expected>limit)expected=limit;}
  else if(signed(Math.abs(expected))>limit)expected=-limit;
 }
 put('h','l',desired);put('d','e',target);put('b','c',limit);
 invoke('chase_velocity');chaseCases++;
 assert.equal(hl(),expected,`CHASE ${desired},${target},${limit}`);
}
// Separate genuine TS2068 ROM boot and long-running IM2 validation.
const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));
m.homeRom.set(fs.readFileSync(path.join(upstream,'roms/ts2068-0.rom')));
m.exRom.set(fs.readFileSync(path.join(upstream,'roms/ts2068-1.rom')));
const dck=read('build/sinistar-port-kernel.dck');
assert.equal(api.insertDock(m,dck),null);api.resetMachine(m);
let romWrites=0,started=false,first=-1,last=-1,interrupts=0,balancedReturns=0;
const reader=m.bus.read;
m.bus.read=a=>{if(a===symbols.idle&&m.cpu.pc===a){assert.equal(m.cpu.sp,0x7fff);balancedReturns++;}return reader(a);};
const writer=m.bus.write;
m.bus.write=(a,v)=>{if(m.cpu.pc>=0x8000&&m.cpu.pc<0xa000&&(m.portF4&(1<<(a>>13))))romWrites++;writer(a,v);};
for(let f=0;f<1200;f++){
 api.runFrame(m);
 if(m.ram[0x7800]===0xee)throw Error(`Boot self-test failed at stage ${m.ram[0x7801]}`);
 if(m.ram[0x7800]!==0xa5)continue;
 assert.equal(m.portF4,16);assert.equal(m.portFF,2);
 // A frame boundary may fall inside IRQ entry; check exact balance at idle.
 assert.ok(m.cpu.sp>=0x7ffb&&m.cpu.sp<=0x7fff);
 const ticks=m.ram[0x7802]+256*m.ram[0x7803];
 if(started){assert.equal(ticks-last,1);interrupts++;}else{first=f;started=true;}
 last=ticks;
}
assert.ok(started&&interrupts>1000&&balancedReturns>1000);assert.equal(romWrites,0);
const report={dck_sha256:createHash('sha256').update(dck).digest('hex'),routine_cases:cases,table_distances:65535,acceleration_cases:524288,turn_cases:65536,sincos_cases:256,player_acceleration_cases:accelerationCases,camera_cases:cameraCases,camera_hard_branches:hardBranches,camera_integrate_cases:integrateCases,chase_cases:chaseCases,max_routine_tstates:timing,routine_writes:writes,boot_frame:first,consecutive_refresh_interrupts:interrupts,balanced_stack_returns:balancedReturns,rom_writes:romWrites,hardware_tested:false};
fs.writeFileSync(path.join(root,'build/verification.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
