// Actual assembled graphic-keyboard routine: all matrix contacts, shared CAPS,
// derived BREAK, exact attribute extents and recovery without HOME writes.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=process.cwd(),up=path.resolve(root,'../TSRun'),api=await import(pathToFileURL(path.join(up,'machine.js')));
const cart=fs.readFileSync('build/diagnostic-v02.dck'),sym=Object.fromEntries([...fs.readFileSync('build/symbols.txt','utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(m=>[m[1],parseInt(m[2],16)]));
const layout=JSON.parse(fs.readFileSync('build/keyboard-art-layout.json','utf8')),cases=[];
const matrix=[['CS','Z','X','C','V'],[...'ASDFG'],[...'QWERT'],[...'12345'],[...'09876'],[...'POIUY'],['EN','L','K','J','H'],['SPACE','SY','M','N','B']];
function machine(lost=false,history=false){
 const keys=new Uint8Array(8).fill(31),m=api.createMachine(keys,new Uint8Array(2).fill(255));m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));assert.equal(api.insertDock(m,cart),null);api.resetMachine(m);m.portF4=1;m.portFF=64;m.cpu.pc=sym.load_keyboard;m.cpu.sp=0xbeef;
 const r=m.bus.read,w=m.bus.write,seen=new Set();m.bus.read=a=>{if(a===m.cpu.pc){assert.ok(a<0x2000||(a>=0xe000&&a<0xe600&&(m.portF4&128)),'keyboard opcode outside fixed ROM anchors');assert.equal(m.cpu.sp,0xbeef);seen.add(a);}return history&&a>=0x5b00&&a<=0x5b28?255:r(a);};
 m.bus.write=(a,v)=>{assert.ok(a>=0x4000&&a<0x8000,'write escaped HOME display/data');assert.equal(m.portF4&(1<<(a>>13)),0,'DOCK source overlays destination');if(!lost)w(a,v);};return {m,keys,seen};
}
function frames(t,n){for(let i=0;i<n;i++)api.runFrame(t.m);}
function until(t,label,budget=1000){for(let i=0;i<budget&&!t.seen.has(sym[label]);i++)api.runFrame(t.m);assert.ok(t.seen.has(sym[label]),label);}
function cells(name){return layout.keys.filter(k=>k.name===name).flatMap(k=>{const[x,y,w,h]=k.target;return Array.from({length:w*h},(_,i)=>(y+Math.floor(i/w))*32+x+i%w);});}
function record(name){cases.push({name,result:'PASS'});console.log(name+': PASS');}
for(let row=0;row<8;row++)for(let bit=0;bit<5;bit++){
 const name=matrix[row][bit],t=machine();until(t,'keyboard_scan');frames(t,2);const initial=t.m.ram.slice(0x5800,0x5b00),expected=initial.slice();
 t.keys[row]&=~(1<<bit);frames(t,3);assert.equal(t.m.ram[0x5b00+row*5+bit],1);for(const c of cells(name))expected[c]=0x60;assert.deepEqual(t.m.ram.slice(0x5800,0x5b00),expected,name+' changed wrong cells');
 t.keys.fill(31);frames(t,3);for(const c of cells(name))expected[c]=0x68;assert.deepEqual(t.m.ram.slice(0x5800,0x5b00),expected,name+' release changed neighbor');record(name+' matrix row'+row+'/bit'+bit+' exact full-key highlight and release');
}
{const t=machine();until(t,'keyboard_scan');frames(t,2);t.keys[0]&=~1;t.keys[7]&=~1;frames(t,2);assert.equal(t.m.ram[0x5b28],1);for(const name of ['CS','SPACE','BR'])for(const c of cells(name))assert.equal(t.m.ram[0x5800+c],0x60);t.keys.fill(31);frames(t,2);for(const c of cells('BR'))assert.equal(t.m.ram[0x5800+c],0x68);t.keys[6]&=~1;t.keys[7]&=~1;frames(t,2);for(const c of cells('BR'))assert.equal(t.m.ram[0x5800+c],0x68,'ENTER+SPACE is not physical BREAK');until(t,'menu_ready',500);record('BREAK requires CAPS+SPACE; ENTER+SPACE exit leaves BREAK history accurate');}
for(const [lost,history] of [[true,false],[false,true]]){const t=machine(lost,history);until(t,'keyboard_scan');t.keys[6]&=~1;t.keys[7]&=~1;until(t,'menu_ready',1000);record(lost?'keyboard exit survives all HOME writes lost':'corrupt history changes only bounded colors, exit survives');}
{const t=machine();until(t,'keyboard_scan');frames(t,2);t.keys[1]&=~1;frames(t,2);t.keys.fill(31);frames(t,2);t.keys[2]&=~2;t.keys[0]&=~1;frames(t,2);fs.writeFileSync('build/keyboard-active-v02.bin',t.m.ram.slice(0x4000,0x5b00));record('actual artwork capture: W/shared CAPS held, A released, other keys unseen');}
fs.writeFileSync('build/keyboard-verification.json',JSON.stringify({result:'PASS',image_sha256:createHash('sha256').update(cart).digest('hex'),source_image_sha256:layout.source_sha256,cases,limitations:['Post-entry TSRun matrix/write/history models','Physical contacts, readability and signal timing require target testing']},null,2)+'\n');
