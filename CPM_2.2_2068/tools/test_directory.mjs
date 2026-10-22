// TSRun Z80 + actual Python directory service, operating on real temporary files.
import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {PicoModel} from './tspico_model.mjs';
const base=path.resolve(process.argv.slice(2).find(a=>!a.startsWith('--'))||'../../TSRun');
const api=await import(pathToFileURL(path.join(base,'machine.js')));
const native=process.argv.includes('--native');
const dual=process.argv.includes('--dual');
const build=dual?'build/profiles/tspico-dual':native?'build/profiles/tspico-dir':'build';
const manifest=JSON.parse(fs.readFileSync(build+'/manifest.json'));
const sd=fs.mkdtempSync(path.resolve('build/directory-integration-'));
const dir=path.join(sd,'CPM/FILES');fs.mkdirSync(dir,{recursive:true});
for(const entry of manifest.files)fs.copyFileSync(path.join(dual?'build/profiles/tspico-ram/files':native?build+'/files':'build/sdcard/CPM/FILES',entry.name),path.join(dir,entry.name));
if(dual)fs.copyFileSync('build/profiles/tspico-dir/files/CPMDISK.COM',path.join(dir,'CPMDISK.COM'));
if(process.argv.includes('--large'))fs.writeFileSync(path.join(dir,'BIG.BIN'),Buffer.alloc(180000,0x17));
const keys=new Uint8Array(8).fill(255);
const m=api.createMachine(keys,new Uint8Array(2).fill(255));
api.setHomeRom(m,fs.readFileSync(path.join(base,'roms/ts2068-0.rom')));
api.setExRom(m,fs.readFileSync(path.join(base,'roms/ts2068-1.rom')));
assert.equal(api.insertDock(m,fs.readFileSync(build+'/ts2068-cpm.dck')),null);
// Simulate SRAM-provided DOCK without the emulator's extra EXROM disk pages.
m.exCart.fill(null);m.exCartRam.fill(false);m.dockRam.fill(true);
const pico=new PicoModel(fs.readFileSync(build+'/drive-a.img'));
let maxRead=0;
pico.rpc=(command,par1,par2)=>{
  if(command.toLowerCase()==='tpi:.cpmrd')maxRead=Math.max(maxRead,par1);
  const r=spawnSync(process.env.PYTHON||'python',['tools/directory_rpc.py',JSON.stringify({sd,command,par1,par2,directory_kb:native?320:256})],{encoding:'utf8'});
  assert.equal(r.status,0,String(r.error||r.stderr));return JSON.parse(r.stdout);
};
const rd=m.bus.ioRead,wr=m.bus.ioWrite;
m.bus.ioRead=p=>[14,15].includes(p&255)?pico.read(p):rd(p);
m.bus.ioWrite=(p,v)=>{if([14,15].includes(p&255))pico.write(p,v);else wr(p,v);};
const syms=Object.fromEntries([...fs.readFileSync(build+'/bios.bin.sym','utf8').matchAll(/^(\w+): EQU 0x([\da-f]+)/gmi)].map(x=>[x[1],parseInt(x[2],16)]));
let text='';const write=m.bus.write;
m.bus.write=(a,v)=>{if(a>=0xf800&&a<0xfe00&&(dual||(m.cpu.pc>=syms.conout&&m.cpu.pc<syms.logok)))text+=String.fromCharCode(v);write(a,v);};
function frames(n){for(let i=0;i<n;i++)api.runFrame(m);}
const keymap=['\0ZXCV','ASDFG','QWERT','12345','09876','POIUY','\rLKJH',' \0MNB'];
const sym={'.':'M','=':'L','*':'B'};
function type(s){for(let c of s){if(sym[c]){keys[7]&=~2;c=sym[c];}let found=false;for(let r=0;r<8&&!found;r++){let b=keymap[r].indexOf(c);if(b>=0){keys[r]&=~(1<<b);frames(4);keys.fill(255);frames(4);found=true;}}assert(found,c);}}
function command(s,n=600){type(s+'\r');frames(n);fs.writeFileSync('build/directory-transcript.txt',text);}
frames(500);
if(dual){assert(text.includes('ENTER: persistent SD'),text.slice(-1000));type('\r');frames(500);}
assert(text.includes('TSPico directory '+(native?'320K':'256K')),text.slice(-600));assert.match(text,/HELLO from a \.COM/);
console.log('Directory-backed boot PASS');
if(dual){
 command('PIP COPY.COM=HELLO.COM');assert(fs.existsSync(path.join(dir,'COPY.COM')),text.slice(-1000));
 command('COPY');assert.equal((text.match(/HELLO from a \.COM/g)||[]).length,2);
 const prepared=spawnSync(process.env.PYTHON||'python',['tools/prepare_dual_geometry_test.py',path.join(sd,'CPM')],{encoding:'utf8'});assert.equal(prepared.status,0,prepared.stderr);
 command('CPMDISK MOUNT DISK160.DSK');command('HELLO');
 command('CPMDISK DIR');command('COPY');
 assert.equal((text.match(/HELLO from a \.COM/g)||[]).length,4,text.slice(-2000));
 assert.doesNotMatch(text,/Bdos Err|READ ERROR|WRITE ERROR/);
 fs.writeFileSync('build/dual-native-files-transcript.txt',text);
 console.log('Unified cartridge + actual Python native FILES: boot, create/execute, 160KB DSK mount, return to directory PASS');
 process.exit(0);
}
if(process.argv.includes('--dual-only')){
 const prepared=spawnSync(process.env.PYTHON||'python',['tools/prepare_dual_geometry_test.py',path.join(sd,'CPM')],{encoding:'utf8'});
 assert.equal(prepared.status,0,prepared.stderr);
 for(const [kb,extension] of [[160,'DSK'],[320,'TAP'],[160,'TAP'],[320,'DSK']]){
  const start=text.length;
  command(`CPMDISK MOUNT DISK${kb}.${extension}`,500);
  assert(text.slice(start).includes('Disk operation completed.'),text.slice(start));
  assert.equal(m.bus.read(syms.disk_tracks),kb===160?80:160);
  const ptr=m.bus.read(syms.dph+10)|(m.bus.read(syms.dph+11)<<8);
  assert.equal(m.bus.read(ptr+2),kb===160?3:4);
  command('HELLO',150);assert.match(text.slice(start),/HELLO from a \.COM/);
  command('PIP COPY.COM=HELLO.COM',300);command('COPY',150);
  assert.equal((text.slice(start).match(/HELLO from a \.COM/g)||[]).length,2,text.slice(start));
  console.log(`${kb}KB ${extension}: mount, geometry, execute, write, execute copied file PASS`);
 }
 command('CPMDISK SAVE ROUND.DSK',300);assert(fs.existsSync(path.join(sd,'CPM/ROUND.DSK')),text.slice(-1500));
 command('CPMDISK DIR',300);assert.equal(m.bus.read(syms.disk_tracks),160);
 command('HELLO',150);assert.match(text.slice(-700),/HELLO from a \.COM/);
 fs.writeFileSync('build/dual-geometry-transcript.txt',text);
 fs.writeFileSync('build/dual-geometry-test-location.txt',sd+'\n');
 console.log('Return to native directory and DSK export PASS');
 process.exit(0);
}
if(process.argv.includes('--boot-only')){
  assert(maxRead>1024,'did not exercise the upper half of the 256KB volume');
  console.log('Boot HELLO with a 180000-byte native file present, max LBA',maxRead,'PASS');
  process.exit(0);
}
command('DIR');command('STAT');
command('PIP COPY.COM=HELLO.COM');assert(fs.existsSync(path.join(dir,'COPY.COM')),text);
command('COPY');assert.equal((text.match(/HELLO from a \.COM/g)||[]).length,2);
command('REN RENAMED.COM=COPY.COM');assert(fs.existsSync(path.join(dir,'RENAMED.COM')),text);assert(!fs.existsSync(path.join(dir,'COPY.COM')));
command('ERA RENAMED.COM');assert(!fs.existsSync(path.join(dir,'RENAMED.COM')));
console.log('Native SD create/copy/rename/delete PASS');
command('SUBMIT DEMO',3000);assert.match(text,/Assembled on the TS2068!/);
for(const name of ['HI.HEX','HI.PRN','HI.COM'])assert(fs.existsSync(path.join(dir,name)),name+' missing\n'+text);
assert.equal(fs.readFileSync(path.join(dir,'HI.COM'))[0],0x11);
assert(!fs.existsSync(path.join(dir,'$$$.SUB')),'submit scratch was not removed');
assert.doesNotMatch(text,/Bdos Err|DISK FULL|READ ERROR|WRITE ERROR/);
fs.writeFileSync('build/directory-screen.bin',m.ram);
fs.writeFileSync('build/directory-test-location.txt',sd+'\n');
console.log('SUBMIT/ASM/LOAD create ordinary SD files and run HI.COM PASS');
console.log('Directory service commands:',pico.commands.length,'; test files:',dir);
if(native){
 command('CPMDISK SAVE TEST.TAP',1200);assert(fs.existsSync(path.join(sd,'CPM/TEST.TAP')),text.slice(-1200));
 command('CPMDISK MOUNT TEST.TAP',1200);assert(text.slice(-1200).includes('Disk operation completed.'),text.slice(-1200));
 command('DIR');command('HI');assert(text.slice(-2000).includes('Assembled on the TS2068!'));
 command('PIP TAPCOPY.COM=HELLO.COM');
 assert(!fs.existsSync(path.join(dir,'TAPCOPY.COM')),'TAP changes must stay inside TAP');
 command('CPMDISK DIR');command('DIR');
 assert(!fs.existsSync(path.join(dir,'TAPCOPY.COM')));
 command('PIP NEWFILE.COM=HELLO.COM');assert(fs.existsSync(path.join(dir,'NEWFILE.COM')));
 fs.writeFileSync('build/directory-native-transcript.txt',text);
 console.log('CPMDISK: directory -> TAP export/mount/write -> directory, native file persistence PASS');
}
