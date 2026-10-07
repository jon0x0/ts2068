import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {createHash} from 'node:crypto';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),up=process.env.TSRUN_ROOT ? path.resolve(process.env.TSRUN_ROOT) : path.resolve(root,'../../../TSRun');
const api=await import(pathToFileURL(path.join(up,'machine.js')));
const sym=Object.fromEntries([...fs.readFileSync(path.join(root,'build/mining-symbols.txt'),'utf8').matchAll(/^(\w+): EQU 0x([0-9A-F]+)/gm)].map(x=>[x[1],parseInt(x[2],16)]));
const cart=fs.readFileSync(path.join(root,'build/sinistar-mining.dck')),keys=new Uint8Array(8).fill(31),joy=new Uint8Array(2).fill(255),m=api.createMachine(keys,joy);
m.homeRom.set(fs.readFileSync(path.join(up,'roms/ts2068-0.rom')));m.exRom.set(fs.readFileSync(path.join(up,'roms/ts2068-1.rom')));assert.equal(api.insertDock(m,cart),null);api.resetMachine(m);
const get=n=>m.ram[sym[n]],set=(n,v)=>m.ram[sym[n]]=v,word=(a,v)=>{m.ram[a]=v&255;m.ram[a+1]=v>>8;};
let romWrites=0,titleEntries=0,pictures=0,stage='title',helpPage=0,boots=0,fullSinistarPictures=0;const captured=new Set(),phases=new Set(),carrierSides=new Set();let lastCarrier=-1;
function capture(name){fs.writeFileSync(path.join(root,`build/frontend-${name}.bin`),Buffer.concat([Buffer.from(m.ram.slice(0x4000,0x5800)),Buffer.from(m.ram.slice(0x6000,0x7800))]));}
const protectedPages=new Map();let protectedChecks=0;
function verifyProtectedText(){if(!get('front_demo'))return;const phase=m.ram[0x7bf8];if(phase>2)return;const data=[];for(let y=24;y<63;y++)for(let x=0;x<32;x++){const o=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x;data.push(m.ram[0x4000+o],m.ram[0x6000+o]);}if(protectedPages.has(phase))assert.deepEqual(data,protectedPages.get(phase),'objects must not overwrite protected instructions');else protectedPages.set(phase,data);protectedChecks++;}
let aySelect=0,attractAudibleWrites=0,mutedAudibleWrites=0;const ayVolumes=new Uint8Array(3);const io=m.bus.ioWrite;
m.bus.ioWrite=(p,v)=>{if((p&255)===0xf5)aySelect=v&15;if((p&255)===0xf6&&aySelect>=8&&aySelect<=10){ayVolumes[aySelect-8]=v;if(v&31){if(get('front_demo'))attractAudibleWrites++;if(m.ram[0x5e6e])mutedAudibleWrites++;}}io(p,v);};
const read=m.bus.read,write=m.bus.write;
m.bus.write=(a,v)=>{if(a>=0x4000&&(m.portF4&(1<<(a>>13))))romWrites++;write(a,v);};
m.bus.read=a=>{
 if(a===m.cpu.pc){
  if(a===sym.front_orbit&&get('front_demo')===2&&get('worker_mission')===6&&get('assembly_count')!==lastCarrier){lastCarrier=get('assembly_count');carrierSides.add(`${(get('worker_x')-m.ram[sym.face_x+1]+256)%256},${(get('worker_y')-m.ram[sym.face_y+1]+256)%256}`);}
  if(a===sym.start_resume){stage='play';boots++;}
  if(a===sym.title_wait){titleEntries++;stage='title';}
  if(a===sym.front_table)stage='scores';
  if(a===sym.front_help)stage=`help-${++helpPage}`;
  if(a===sym.front_wait&&!captured.has(stage)){capture(stage);captured.add(stage);}
  if(a===sym.publication_done){verifyProtectedText();pictures++;if(get("front_demo")&&m.ram[0x7bf8]<3&&!phases.has(m.ram[0x7bf8])){capture(`demo-${m.ram[0x7bf8]}`);phases.add(m.ram[0x7bf8]);}if(get('front_demo')&&get('assembly_count')===20&&m.ram[sym.rects+22]===7&&m.ram[sym.rects+23]===52){fullSinistarPictures++;if(fullSinistarPictures===10)capture('full-sinistar');}}
 }
 return read(a);
};
function run(n){for(let i=0;i<n;i++)api.runFrame(m);}
function until(fn,budget=4000){for(let i=0;i<budget&&!fn();i++)run(1);assert.ok(fn(),`timeout pc=${m.cpu.pc.toString(16)} stage=${stage}`);}
until(()=>captured.has('title'),300);assert.deepEqual(Buffer.from(m.ram.slice(0x4000,0x5800)),fs.readFileSync(path.join(root,'build/title-bitmap.bin')),'original title bitmap unchanged');
const initial=Buffer.concat([fs.readFileSync(path.join(root,'build/frontend-seeds.bin')),fs.readFileSync(path.join(root,'build/frontend-seeds.bin'))]);
assert.equal(initial.readUInt16LE(0)*5,39045);assert.equal(initial.readUInt16LE(5)*5,38780);assert.equal(initial.readUInt16LE(10)*5,38415);assert.deepEqual([...initial.slice(2,5)],[19,1,13]);
for(let i=150;i<300;i+=5)initial.writeUInt16LE(initial.readUInt16LE(i)-4000,i);
assert.deepEqual(Buffer.from(m.ram.slice(sym.front_scores,sym.front_scores+300)),initial,'both thirty-entry arcade seeds');
until(()=>get('front_demo')===1&&stage==='play',1600);
const max={hits:0,crystals_taken:0,assembly_count:0,bs_fired:0,bs_hits:0};let sawSinistar=false;
const originalTitles=titleEntries;
for(let i=0;i<3300&&titleEntries===originalTitles;i++){
 run(1);for(const n of Object.keys(max))max[n]=Math.max(max[n],get(n));
 if(get('assembly_count')>=20&&get('front_demo')){sawSinistar=true;if(!captured.has('sinistar')){capture('sinistar');captured.add('sinistar');}}
}
assert.ok(titleEntries>originalTitles,'attract returns to title');assert.ok(max.hits>0&&max.crystals_taken>=2&&max.assembly_count===20&&max.bs_hits>=1,JSON.stringify(max));assert.equal(phases.size,3);assert.ok(sawSinistar);assert.ok(fullSinistarPictures>=10,'Sinistar fully visible in published gameplay');assert.equal(attractAudibleWrites,0,'arcade attract is silent');assert.equal(carrierSides.size,4,'four worker entry sides');
assert.deepEqual(Buffer.from(m.ram.slice(sym.front_scores,sym.front_scores+300)),initial,'attract cannot alter either score table');
function startGame(){const n=boots;joy[0]=127;until(()=>boots>n,300);joy[0]=255;run(15);assert.equal(get('front_demo'),0);assert.equal(get('game_status'),0);assert.equal(get('front_finished'),0);}
startGame();
const beforeX=m.ram[sym.px]+256*m.ram[sym.px+1];joy[0]=247;run(20);joy[0]=255;assert.notEqual(m.ram[sym.px]+256*m.ram[sym.px+1],beforeX,'native joystick movement');joy[0]=127;run(5);joy[0]=255;assert.equal(get('bullet_alive'),1,'native joystick fire');
function press(row,bit){keys[row]&=~(1<<bit);run(5);keys[row]|=1<<bit;run(5);}
function endGame(workers,crystals,parts,total){set('crystals_taken',crystals);m.ram[0x5c24]=workers;set('bs_hits',parts);set('game_status',parts===13?1:2);until(()=>get('front_finished')===1 && (m.ram[sym.front_score]+256*m.ram[sym.front_score+1])===total/5,40);assert.equal(m.ram[sym.front_score]+256*m.ram[sym.front_score+1],total/5);if(parts===13){run(5);capture('victory');}until(()=>m.cpu.pc>=sym.front_name_release&&m.cpu.pc<sym.front_name_next,400);}
// S switches once per press, even when held, and drops queued sounds.
set('speech_pending',3);run(12);assert.ok(ayVolumes.some(v=>v&31),'live speech audible');
keys[1]&=~2;run(60);assert.equal(m.ram[0x5e6e],1);assert.deepEqual([...ayVolumes],[0,0,0]);
keys[1]|=2;run(3);set('speech_pending',3);run(5);assert.equal(get('speech_pending'),0);assert.deepEqual([...ayVolumes],[0,0,0]);
press(1,1);assert.equal(m.ram[0x5e6e],0);set('speech_pending',3);run(12);assert.ok(ayVolumes.some(v=>v&31),'unmuting permits new speech');
assert.equal(mutedAudibleWrites,0);assert.equal(attractAudibleWrites,0);
endGame(100,100,13,56000);capture('initials');
press(5,1);press(5,0);press(5,0);press(6,0);
joy[0]=254;run(5);joy[0]=255;run(5);joy[0]=127;run(5);joy[0]=255;run(5);press(7,0);
until(()=>stage==='title',100);
for(const base of [sym.front_scores,sym.front_today_scores])assert.deepEqual([...m.ram.slice(base+2,base+5)],[2,3,3],'BCC in both tables, confirmed letters carry forward');
startGame();endGame(100,75,0,30000);press(7,0);press(7,0);press(7,0);until(()=>stage==='title',100);startGame();
endGame(100,200,13,76000);press(7,0);press(7,0);press(7,0);until(()=>stage==='title',100);
const scoreAt=a=>(m.ram[a]+256*m.ram[a+1])*5;
assert.equal(scoreAt(sym.front_scores),76000);assert.equal(scoreAt(sym.front_scores+5),56000);assert.equal(scoreAt(sym.front_today_scores),76000);assert.equal(scoreAt(sym.front_today_scores+5),56000);assert.equal(scoreAt(sym.front_today_scores+10),30000);
for(const base of [sym.front_scores,sym.front_today_scores])assert.deepEqual([...m.ram.slice(base+7,base+10)],[2,3,3],'initials move with scores');
assert.equal(romWrites,0);
const report={dck_sha256:createHash('sha256').update(cart).digest('hex'),protectedTextChecks:protectedChecks,titleBitmapExact:true,arcadeSeedEntries:60,attract:max,carrierEntrySides:carrierSides.size,attractSilent:true,soundToggleNative:true,holdDoesNotRepeat:true,mutedAudibleWrites,attractSinistarVisible:sawSinistar,fullSinistarPictures,instructionPhases:phases.size,attractReturnsToTitle:true,demoExcludedFromScores:true,initials:'BCC',keyboardOPEnterSpace:true,joystickMoveFireEntry:true,scoresSurviveNewGame:true,ranking:[76000,56000,30000],romWrites};
fs.writeFileSync(path.join(root,'build/frontend-verification.json'),JSON.stringify(report,null,2));console.log(report);
