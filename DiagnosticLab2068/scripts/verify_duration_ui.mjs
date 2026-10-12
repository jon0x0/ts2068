// Execute each changed packed screen loader and compare every display byte.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {pathToFileURL,fileURLToPath} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=path.resolve(root,'../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
const cart=fs.readFileSync(path.join(root,'build/diagnostic-v02.dck'));
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)]));
const cases=[];
for(const name of ['fullinfo','rammenu','startupfull','soak','soakstop','beeper','aylisten','keyboard','rampass','pass','cpuinfo']){
 const m=api.createMachine(new Uint8Array(8).fill(31),new Uint8Array(2).fill(255));
 m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));
 assert.equal(api.insertDock(m,cart),null);api.resetMachine(m);m.portF4=1;m.portFF=0x40;m.cpu.pc=sym['load_'+name];m.cpu.sp=0xbeef;m.cpu.iff1=false;
 const read=m.bus.read,stop={};let reached=false;
 m.bus.read=a=>{if(a===m.cpu.pc&&a===sym[name+'_ready']){reached=true;throw stop;}return read(a);};
 try{for(let i=0;i<100;i++)api.runFrame(m);}catch(e){if(e!==stop)throw e;}
 assert.ok(reached,name);assert.equal(m.cpu.sp,0xbeef);
 const actual=m.ram.slice(0x4000,0x5b00),expected=fs.readFileSync(path.join(root,'build','suite-'+name+'.bin'));
 assert.deepEqual(Buffer.from(actual),expected,name+' exact packed screen');
 fs.writeFileSync(path.join(root,'build','duration-'+name+'-screen.bin'),actual);
 cases.push({name,result:'PASS',display_bytes:6912,stack_unchanged:true});
}
fs.writeFileSync(path.join(root,'build/duration-ui-verification.json'),JSON.stringify({image_sha256:createHash('sha256').update(cart).digest('hex'),result:'PASS',cases,limitations:['Model display memory comparisons; actual visibility still requires working video RAM/output']},null,2)+'\n');
console.log('Eleven UI screens: actual packed ROM loaders PASS');

