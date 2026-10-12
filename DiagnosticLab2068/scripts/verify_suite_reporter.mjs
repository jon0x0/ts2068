// Independently check chip/nibble-bit selection in the assembled ROM reporter.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=process.env.TSRUN_ROOT||path.resolve(root,'../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
const cart=fs.readFileSync(path.join(root,'build/diagnostic-v02.dck'));
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)]));
const cases=[];
for(let region=0;region<3;region++)for(let bit=0;bit<8;bit++){
 const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));
 assert.equal(api.insertDock(m,cart),null);m.portF4=1;m.portFF=64;m.cpu.pc=sym.fault_report;m.cpu.sp=0xbeef;
 m.cpu[['h2','l2','d2'][region]]=1<<bit;
 m.cpu.xh=0xc1;m.cpu.xl=0x23;m.cpu.e2=2;m.cpu.b2=255;m.cpu.c2=255^(1<<bit);
 const read=m.bus.read,io=m.bus.ioWrite;let captured=null,white=false;
 m.bus.read=a=>{if(a===m.cpu.pc&&a===sym.report_class&&!captured)captured=[m.cpu.d,m.cpu.e];return read(a);};
 m.bus.ioWrite=(p,v)=>{if((p&255)===254&&v===23)white=true;io(p,v);};
 for(let frame=0;frame<200&&!captured;frame++)api.runFrame(m);
 const expected=[region*2+(bit<4?1:2),(bit%4)+1];
 assert.deepEqual(captured,expected);assert.ok(white);assert.equal(m.cpu.sp,0xbeef);
 assert.equal((m.cpu.xh<<8)|m.cpu.xl,0xc123);assert.equal(m.cpu.e2,2);
 cases.push({region,bit,chip_code:captured[0],detail:captured[1],sync_output:true});
}
const result={image_sha256:createHash('sha256').update(cart).digest('hex'),result:'PASS',configuration:'TSRun ROM reporter entry with seeded register fault state; no HOME RAM prerequisite',cases};
fs.writeFileSync(path.join(root,'build/suite-reporter-verification.json'),JSON.stringify(result,null,2)+'\n');
console.log('Verified all 24 chip/bit report mappings, synchronization output and retained register fault state.');
