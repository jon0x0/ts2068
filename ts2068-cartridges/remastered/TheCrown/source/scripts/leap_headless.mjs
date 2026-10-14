// Execute the assembled Leap compiler/VM on TSRun's real Z80 and memory bus.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createMachine, setHomeRom, setExRom, insertDock, setVideoOn} from '../tools/tsrun/machine.js';
import {runZ80, irqZ80} from '../tools/tsrun/z80.js';

const [mode, cfg, input, output] = process.argv.slice(2);
const S = {};
for (const file of ['test_basic.sym', 'exrom.sym']) {
  const text = fs.readFileSync(path.join(cfg, 'build', file), 'utf8');
  for (const line of text.split(/\r?\n/)) {
    const match = line.match(/^(\S+):\s+EQU\s+0x([0-9a-f]+)/i);
    if (match) S[match[1]] ??= parseInt(match[2], 16);
  }
}
function sym(name) { if (!(name in S)) throw Error(`Missing symbol ${name}`); return S[name]; }
const doneAddress=sym('VM_CODE_BASE')===0x6000?0x5BFE:0xF6FE;
const m = createMachine(new Uint8Array(8).fill(255), new Uint8Array(2).fill(255));
setVideoOn(m, false);
function word(a) { return m.bus.read(a) | (m.bus.read(a+1) << 8); }
function putword(a, v) { m.bus.write(a, v&255); m.bus.write(a+1, v>>8); }
function bytes(a, n) { return Buffer.from(Array.from({length:n}, (_,i)=>m.bus.read(a+i))); }
let nextIrq = 58688;
let sourceStream=null, sourceIndex=0;
function returnFromHook() { const pc=word(m.cpu.sp); m.cpu.sp=(m.cpu.sp+2)&65535; m.cpu.pc=pc; }
function streamRecord() {
  const text=sourceStream[sourceIndex];
  m.cpu.h=0; m.cpu.l=0;
  if(text!==undefined) {
    putword(0xF000,text.length+1);
    for(let i=0;i<text.length;i++) m.ram[0xF002+i]=text.charCodeAt(i);
    m.ram[0xF002+text.length]=13;
    m.cpu.h=0xF0; m.cpu.l=0;
  }
  returnFromHook();
}
function until(stops, max=200_000_000, predicate=null) {
  const start=m.tstates;
  while (!stops.has(m.cpu.pc)) {
    if(predicate&&predicate()) return m.cpu.pc;
    if(sourceStream&&m.cpu.pc===sym('MEM_LINE_FIRST')) {sourceIndex=0;streamRecord();continue;}
    if(sourceStream&&m.cpu.pc===sym('MEM_LINE_NEXT')) {sourceIndex++;streamRecord();continue;}
    if (m.tstates-start>max) throw Error(`Timeout PC=${m.cpu.pc.toString(16)} IP=${word(sym('VM_IP')).toString(16)} VMERR=${m.ram[sym('VM_ERROR_CODE')]} F4=${m.portF4.toString(16)} FF=${m.portFF.toString(16)}`);
    runZ80(m.cpu,m.bus,4,m); // HALT needs four cycles to advance to the next interrupt.
    if (m.tstates>=nextIrq) {
      if (!(m.portFF&64)) m.tstates+=irqZ80(m.cpu,m.bus);
      nextIrq=m.tstates+58688;
    }
  }
  return m.cpu.pc;
}
function invoke(name, stops) {
  putword(0xFEFC, 0xFEF0);
  m.cpu.sp=0xFEFC;
  m.cpu.pc=sym(name);
  return until(new Set([...stops,0xFEF0]));
}
function screen() {
  const savedCpu={...m.cpu};
  const savedStack=Buffer.from(m.ram.subarray(0xFD00,0xFF00));
  const glyphs=new Map();
  for(let c=32;c<128;c++) {
    m.cpu.a=c;
    invoke('GFX_CHAR_TO_FONT_OFFSET',[]);
    if(!(m.cpu.f&1)) glyphs.set(bytes((m.cpu.h<<8)|m.cpu.l,8).toString('hex'),String.fromCharCode(c));
  }
  glyphs.set('0000000000000000',' ');
  const rows=[];
  for(let row=0;row<22;row++) {
    let text=''; const y=row*8;
    for(let col=0;col<32;col++) {
      const a=0x4000+((y&0xC0)<<5)+((y&0x38)<<2)+col;
      const key=Buffer.from(Array.from({length:8},(_,k)=>m.ram[a+256*k])).toString('hex');
      text+=glyphs.get(key)??'?';
    }
    rows.push(text.trimEnd());
  }
  while(rows.length&&!rows.at(-1)) rows.pop();
  Object.assign(m.cpu,savedCpu);
  m.ram.set(savedStack,0xFD00);
  return rows.join('\n');
}
function crc32(data) {
  let crc=0xFFFFFFFF;
  for(const byte of data) {
    crc^=byte;
    for(let i=0;i<8;i++) crc=(crc>>>1)^((crc&1)?0xEDB88320:0);
  }
  return (crc^0xFFFFFFFF)>>>0;
}
function loadBytecode(file, home, exrom) {
  const data=fs.readFileSync(file);
  if(data.length<49||data.subarray(0,4).toString()!=='LBC1') throw Error('Invalid LBC header');
  const base=data.readUInt16LE(4), size=data.readUInt16LE(6);
  if(base!==sym('VM_CODE_BASE')||size===0||base+size>sym('V2_CODE_LIMIT')||data.length!==49+size) throw Error('Invalid LBC address/size');
  const identity=crypto.createHash('sha256').update(home).update(exrom).digest();
  if(!identity.equals(data.subarray(13,45))) throw Error('LBC requires a different Leap ROM build');
  const code=data.subarray(49);
  if(crc32(Buffer.concat([data.subarray(0,45),code]))!==data.readUInt32LE(45)) throw Error('LBC checksum mismatch');
  if(data[8]>251||data[9]>251) throw Error('Invalid LBC scalar counts');
  for(let i=0;i<size;i++) m.bus.write(base+i,code[i]);
  for(let i=0;i<5;i++) m.bus.write(sym('SYM_COUNTS')+i,data[8+i]);
  putword(sym('SYM_END_V'),sym('PROG_AREA_START')-sym('SESS_GAP')-1);
  putword(sym('PAS_END'),sym('ARR2_BASE'));
  return size;
}
if(mode==='compile') {
  setHomeRom(m,fs.readFileSync(path.join(cfg,'v2_home.bin')));
  setExRom(m,fs.readFileSync(path.join(cfg,'v2_exrom.bin')));
  until(new Set([sym('V2_COMMAND_LOOP')]));
  const lines=fs.readFileSync(input,'utf8').replace(/^\uFEFF/,'').split(/\r?\n/).filter(l=>l.trim());
  let p=sym('PROG_AREA_START');
  const sourceBytes=lines.reduce((n,l)=>n+l.length+3,0);
  if(sourceBytes>=sym('V2_SOURCE_END')-p) sourceStream=lines;
  for(const l of lines) {
    if(Buffer.byteLength(l,'latin1')>127 || /[^\x00-\x7f]/.test(l)) throw Error('Source must be ASCII, at most 127 bytes per line');
    if(sourceStream) continue;
    putword(p,l.length+1); p+=2;
    for(const c of l) m.bus.write(p++,c.charCodeAt(0));
    m.bus.write(p++,13);
  }
  putword(sym('PROG_END'),p); putword(sym('ARRAYS_END'),p);
  const stop=invoke('V2_COMPILE_STORED',[]);
  const error=m.bus.read(sym('COMPILE_ERROR_CODE'));
  if(error || stop!==0xFEF0) throw Error(`Compile error ${error}, PC=${stop.toString(16)}, line=${word(sym('LEX_LINE'))}, streamed=${sourceIndex}, emit=${word(sym('EMIT_PTR')).toString(16)}, symbols=${word(sym('SYM_END_V')).toString(16)}`);
  const start=sym('VM_CODE_BASE'), end=word(sym('EMIT_PTR'));
  const code=bytes(start,end-start), counts=bytes(sym('SYM_COUNTS'),5);
  const reportFile=input.replace(/\.bas$/i,'.conversion.json');
  const conversion=fs.existsSync(reportFile)?JSON.parse(fs.readFileSync(reportFile,'utf8')):null;
  const symbols=[];
  let sp=word(sym('SYM_BASE_V')), se=word(sym('SYM_END_V'));
  while(sp<se) {
    const length=m.ram[sp], kind=m.ram[sp+1], nameLen=m.ram[sp+2], index=m.ram[sp+3];
    if(!length) break;
    const name=bytes(sp+4,nameLen).toString('ascii'), extra=sp+4+nameLen;
    symbols.push({name,kind,index,offset:kind===4?word(extra):null}); sp+=length;
  }
  fs.writeFileSync(output,JSON.stringify({format:'leap-bytecode-v1',base:start,code:code.toString('hex'),counts:[...counts],sourceLines:lines.length,
    packedData:conversion?.packed_data??null,levels:conversion?.levels??[],symbols,sourceNames:conversion?.names??[]},null,2)+'\n');
  console.log(`Compiled ${lines.length} BASIC lines to ${code.length} bytes; counts ${[...counts]}`);
} else if(mode==='bytecode') {
  const home=fs.readFileSync(path.join(cfg,'v2_home.bin'));
  const exrom=fs.readFileSync(path.join(cfg,'v2_exrom.bin'));
  setHomeRom(m,home); setExRom(m,exrom);
  until(new Set([sym('V2_COMMAND_LOOP')]));
  const size=loadBytecode(input,home,exrom);
  invoke('VM_INIT',[]);
  m.ram[sym('CURRENT_PAPER')]=7;
  invoke('GFX_CLS',[]);
  putword(sym('VM_IP'),sym('VM_CODE_BASE'));
  invoke('VM_RUN',[]);
  const report={status:'TSRun headless load of saved bytecode into fresh RAM runtime',codeBytes:size,sourceLoaded:false,vmError:m.ram[sym('VM_ERROR_CODE')],arenaFree:word(sym('VARS_START'))-word(sym('ARRAYS_END')),output:screen()};
  fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));
  if(report.vmError) throw Error(`VM error ${report.vmError}`);
} else if(mode==='cartridge'||mode==='game'||mode==='startup') {
  const romdir=path.dirname(input);
  setHomeRom(m,fs.readFileSync(path.join(romdir,'stock-home.rom')));
  setExRom(m,fs.readFileSync(path.join(romdir,'stock-exrom.rom')));
  const err=insertDock(m,fs.readFileSync(input)); if(err) throw Error(err);
  // Full reset through the stock ROM: this exercises AROS detection and OS handoff.
  let writesToRom=0, fetches=0;
  const write=m.bus.write, read=m.bus.read;
  m.bus.write=(a,v)=>{if((m.portF4&(1<<(a>>13)))&&!(m.portFF&128)&&m.dock[a>>13]) writesToRom++;write(a,v);};
  m.bus.read=a=>{if(a>=0x6000&&a<0x7F00&&(m.portF4&8)&&!(m.portFF&128)) fetches++;return read(a);};
  if(mode==='startup') {
    const intro={};
    for(const line of fs.readFileSync(path.join(romdir,'intro.sym'),'utf8').split(/\r?\n/)) {
      const match=line.match(/^(\S+):\s+EQU\s+0x([0-9a-f]+)/i);
      if(match) intro[match[1]]=parseInt(match[2],16);
    }
    const program=JSON.parse(fs.readFileSync(path.join(romdir,'bytecode.json'),'utf8'));
    const label=name=>program.base+program.symbols.find(s=>s.kind===4&&s.name.toUpperCase()===name.toUpperCase()).offset;
    const gameReady=()=>m.cpu.pc===sym('VM_RUN.loop')&&[label('QL1400'),label('QL1401')].includes(word(sym('VM_IP')));
    let refreshWhileInitializing=0, minimumSp=0xFFFF;
    const seedArg=process.argv.find(a=>a.startsWith('--seed='));
    const nativeSeed=seedArg?Number(seedArg.split('=')[1]):null;
    let nativeChecks=null;
    const manifest=JSON.parse(fs.readFileSync(path.join(romdir,'manifest.json'),'utf8'));
    const fullIntro=manifest.startup_intro?.display_size?.[0]===256;
    const expectedFrames=fullIntro?Array.from({length:8},(_,i)=>{
      const prefix=path.join(manifest.animation_sequence??'build/intro-eight-locked/codec/sequence',`frame_${String(i).padStart(5,'0')}`);
      return Buffer.concat([fs.readFileSync(prefix+'.pix'),fs.readFileSync(prefix+'.atr')]);
    }):null;
    const expectedCode=Buffer.from(program.code,'hex');
    const smallPrompt=fullIntro&&fs.existsSync(path.join(romdir,'prompt.pixels'));
    const promptRows=smallPrompt?[...fs.readFileSync(path.join(romdir,'prompt_rows.inc'),'utf8').matchAll(/\$([0-9A-F]{4})/g)].map(m=>parseInt(m[1],16)):[];
    const promptOffsets=new Set(promptRows.flatMap(a=>Array.from({length:5},(_,i)=>a+i-0x4000)));
    const expectedAssets=fullIntro?fs.readFileSync(program.packedData):null;
    let frameChecks=0, dataChecks=0, tickStart=0, lastDraw=-1;
    const decodeTimes=[];
    let pairStart=0,maximumPairMs=0,pairedBlocks=0;
    function probeIntro() {
      if(fullIntro) {
        if(m.cpu.pc===intro.native_dungeon&&nativeSeed!==null) putword(sym('RND_STATE'),nativeSeed);
        if(m.cpu.pc===intro.release&&m.ram[0xFAC3]===1&&(m.ram[sym('PORT_FE_SHADOW')]&7)!==0) throw Error('Ready intro border is not black');
        if(m.cpu.pc===intro.blackout_ready||m.cpu.pc===intro.bitmap_decoded) {
          if(m.portFF!==2||m.ram.subarray(0x6000,0x7800).some(v=>v!==0)) throw Error('Intro bitmap exposed before ECM attributes are ready');
          if(m.cpu.pc===intro.blackout_ready&&m.ram.subarray(0x5800,0x5B00).some(v=>v!==0)) throw Error('Standard attributes were not blacked out');
        }
        if(m.cpu.pc===intro.start) {
          if(!Buffer.from(m.ram.subarray(program.base,program.base+expectedCode.length)).equals(expectedCode)) throw Error('Expanded bytecode differs');
        }
        if(m.cpu.pc===intro.tick) tickStart=m.tstates;
        if(m.cpu.pc===intro['tick.direct_blocks']||m.cpu.pc===intro['tick.buffered_blocks']) pairStart=m.tstates;
        if(m.cpu.pc===intro['tick.direct_pair_done']||m.cpu.pc===intro['tick.buffered_pair_done']) {
          maximumPairMs=Math.max(maximumPairMs,(m.tstates-pairStart)*1000/3_528_000);
          pairedBlocks++;
        }
        if(m.cpu.pc===intro.key_decoded||(m.cpu.pc===intro.frame_decoded&&m.ram[0xFAC6]!==lastDraw)) {
          lastDraw=m.ram[0xFAC6];
          const phase=m.ram[0xFAC1];
          const actual=Buffer.concat([Buffer.from(m.ram.subarray(0x4000,0x5800)),Buffer.from(m.ram.subarray(0x6000,0x7800))]);
          const expected=expectedFrames[phase];
          for(let a=0;a<12288;a++) {
            const offset=a%6144;
            // Native ready prompt replaces one static text row (y=168..175).
            const promptRow=smallPrompt?promptOffsets.has(offset):(offset&0x1800)===0x1000&&(offset&0xE0)===0xA0;
            if(m.ram[0xFAC3]&&promptRow) continue;
            if(actual[a]!==expected[a]) throw Error(`Intro frame ${phase} mismatch at ${a.toString(16)}: ${actual[a]} != ${expected[a]}`);
          }
          frameChecks++;
          if(m.cpu.pc===intro.frame_decoded) decodeTimes.push({phase,ms:(m.tstates-tickStart)*1000/3_528_000});
        }
        if(m.cpu.pc===intro['data_byte.cached']) {
          const block=m.ram[0xFAD0], expected=expectedAssets.subarray(block*512,(block+1)*512);
          if(!Buffer.from(m.ram.subarray(0xBE00,0xBE00+expected.length)).equals(expected)) throw Error(`Expanded DATA block ${block} differs`);
          dataChecks++;
        }
      }
      return false;
    }
    const heldKeyTest=process.argv.includes('--held-key');
    const joyArg=process.argv.indexOf('--startup-joystick');
    const startupJoystick=joyArg<0?0:Number(process.argv[joyArg+1]);
    if(!Number.isInteger(startupJoystick)||startupJoystick<0||startupJoystick>255)throw Error('Invalid startup joystick mask');
    const startupInput=down=>{if(startupJoystick)m.joystick[0]=down?255^startupJoystick:255;else m.keyMatrix[7]=down?0xFE:0xFF;};
    until(new Set([heldKeyTest?intro.release:intro.wait_key]),400_000_000,()=>{
      probeIntro();
      if(heldKeyTest&&m.ram[0xFAC0]===1) startupInput(true);
      if(m.ram[0xFAC0]===1&&m.ram[0xFAC3]===0) refreshWhileInitializing=Math.max(refreshWhileInitializing,m.ram[0xFAC6]);
      if(m.cpu.pc>=0xF800&&m.cpu.pc<0xFAC0) minimumSp=Math.min(minimumSp,m.cpu.sp);
      return false;
    });
    if(m.ram[sym('VM_ERROR_CODE')]) throw Error('Startup VM error '+m.ram[sym('VM_ERROR_CODE')]);
    const initializationMs=m.tstates*1000/3_528_000;
    const readyScreen=screen();
    if(intro.native_dungeon) {
      function arrayPayload(slot,kind) {
        const descriptor=word(word(sym(kind?'RT_STRARRPTR_PTR':'RT_ARRPTR_PTR'))+2*slot);
        const width=kind?m.ram[descriptor+3]:2;
        return {address:descriptor+(kind?4:3)+width,width};
      }
      for(const name of ['init-items','init-level-1']) {
        const blob=fs.readFileSync(path.join(romdir,name+'.raw'));
        for(let p=0;blob[p]!==255;) {
          const slot=blob[p],kind=blob[p+1],size=blob.readUInt16LE(p+2);p+=4;
          const {address}=arrayPayload(slot,kind);
          if(!Buffer.from(m.ram.subarray(address,address+size)).equals(blob.subarray(p,p+size))) throw Error(`Native fixed table differs: ${name} slot ${slot}`);
          p+=size;
        }
      }
      const slot=program.symbols.find(s=>s.name==='QA40'&&s.kind===2).index;
      const {address}=arrayPayload(slot,0);
      const dungeon=Buffer.from(m.ram.subarray(address,address+480));
      for(let room=0;room<120;room++) {
        const kind=dungeon.readUInt16LE(room*4),amount=dungeon.readUInt16LE(room*4+2);
        if(kind>25||amount>7||(kind===0&&amount!==0)) throw Error('Native dungeon item out of range');
      }
      if(dungeon.readUInt16LE(476)!==15||dungeon.readUInt16LE(478)!==1) throw Error('Crown missing from final room');
      for(let level=0;level<3;level++) {
        const kinds=Array.from({length:40},(_,i)=>dungeon.readUInt16LE((level*40+i)*4));
        if(!kinds.includes(11+level)||!kinds.includes(20+level)) throw Error('Native dungeon lacks guaranteed key/special item');
      }
      nativeChecks={seed:nativeSeed,dungeonHash:crypto.createHash('sha256').update(dungeon).digest('hex'),fixedTables:true,itemRanges:true,guaranteedKeys:true};
    }
    if(smallPrompt) {
      const expected=fs.readFileSync(path.join(romdir,'prompt.pixels'));
      const actual=Buffer.from(promptRows.flatMap(a=>Array.from({length:5},(_,i)=>m.ram[a+i])));
      if(!actual.equals(expected)||promptRows.some(a=>Array.from({length:5},(_,i)=>m.ram[a+0x2000+i]).some(v=>v!==2))) throw Error('Small red readiness prompt differs');
    } else if(!readyScreen.includes('press a key to continue')) throw Error('Readiness prompt absent: '+readyScreen);
    if(!refreshWhileInitializing) throw Error('No animation update during initialization');
    fs.writeFileSync(path.join(romdir,'startup-ready.ecm'),Buffer.concat([Buffer.from(m.ram.subarray(0x4000,0x5800)),Buffer.from(m.ram.subarray(0x6000,0x7800))]));
    const refresh=m.ram[0xFAC6], end=m.tstates+3*3_528_000;
    until(new Set([doneAddress]),12_000_000,()=>{probeIntro();return m.tstates>=end;});
    if(m.ram[0xFAC6]===refresh) throw Error('Animation stopped while waiting for a key');
    if(heldKeyTest) {
      if(m.ram[0xFAC0]!==1) throw Error('Held initialization key bypassed readiness gate');
      startupInput(false);
      until(new Set([intro.wait_key]),10_000_000);
    }
    startupInput(true);
    until(new Set([intro.release_after]),10_000_000);
    startupInput(false);
    until(new Set([doneAddress]),200_000_000,gameReady);
    if(!gameReady()||m.ram[0xFAC0]||m.portFF!==0||m.ram[sym('VM_ERROR_CODE')]) throw Error('Startup handoff failed');
    const report={nativeChecks,initializationMs,refreshWhileInitializing,minimumSp,readyScreen,frameChecks,dataChecks,decodeTimes,maximumPairMs,pairedBlocks,
      keyGate:true,heldKeyTest,startupJoystick,animationContinuesWhileReady:true,gameEntered:true,videoMode:m.portFF,
      vmError:m.ram[sym('VM_ERROR_CODE')],gameScreen:screen()};
    fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(fullIntro?{...report,decodeTimes:`${decodeTimes.length} measured frame updates; see report file`}:report,null,2));
    process.exit(0);
  }
  if(mode==='game') {
    const program=JSON.parse(fs.readFileSync(path.join(romdir,'bytecode.json'),'utf8'));
    const resolve=(name,kind='scalar')=>{
      const converted=program.sourceNames.find(n=>n.original===name&&n.kind===kind)?.leap??name;
      const symbol=program.symbols.find(s=>s.name.toUpperCase()===converted.toUpperCase()&&s.kind===(kind==='array'?2:0));
      if(!symbol) throw Error(`Missing game variable ${name}`); return symbol;
    };
    const scalarAddress=name=>word(sym('RT_SYMTAB_PTR'))+3*resolve(name).index;
    const value=name=>{const a=scalarAddress(name);return (word(a+1)<<16)>>16;};
    const setValue=(name,v)=>{const a=scalarAddress(name);m.ram[a]=0;putword(a+1,v);};
    const arrayAddress=(name,index)=>word(word(sym('RT_ARRPTR_PTR'))+2*resolve(name,'array').index)+3+2*index;
    const setArray=(name,index,v)=>putword(arrayAddress(name,index),v);
    const arrayValue=(name,index)=>word(arrayAddress(name,index));
    const label=name=>program.base+program.symbols.find(s=>s.kind===4&&s.name.toUpperCase()===name.toUpperCase()).offset;
    const atLabel=name=>m.cpu.pc===sym('VM_RUN.loop')&&word(sym('VM_IP'))===label(name);
    const ready=()=>atLabel('QL1400')||atLabel('QL1401');
    const manifest=JSON.parse(fs.readFileSync(path.join(romdir,'manifest.json'),'utf8'));
    if(manifest.startup_intro) {
      const intro={};
      for(const line of fs.readFileSync(path.join(romdir,'intro.sym'),'utf8').split(/\r?\n/)) {
        const match=line.match(/^(\S+):\s+EQU\s+0x([0-9a-f]+)/i);
        if(match) intro[match[1]]=parseInt(match[2],16);
      }
      until(new Set([intro.wait_key]),400_000_000);
      m.keyMatrix[7]=0xFE;
      until(new Set([intro.release_after]),10_000_000);
      m.keyMatrix[7]=0xFF;
    }
    until(new Set([doneAddress]),400_000_000,ready);
    const snapshots=[];
    function snapshot(stage) {
      const fields=Object.fromEntries(['LV','RM','MX','MY','HP','DF'].map(n=>[n,value(n)]));
      fields.stage=stage;fields.screen=screen();fields.free=word(sym('VARS_START'))-word(sym('ARRAYS_END'));
      snapshots.push(fields);
      fs.writeFileSync(path.join(romdir,stage+'.screen.bin'),Buffer.from(m.ram.subarray(0x4000,0x5B00)));
      if(m.ram[sym('VM_ERROR_CODE')]) throw Error(`Game VM error ${m.ram[sym('VM_ERROR_CODE')]}`);
    }
    snapshot('level1');
    const savedFreshState=manifest.startup_intro?.display_size?.[0]===256&&m.ram[0xFAE5]?Buffer.from(m.ram.subarray(word(0xFAE6),word(0xFAEC))):null;
    if(value('LV')!==1||value('RM')!==1||value('HP')!==20) throw Error('Initial game state differs: '+JSON.stringify(snapshots[0]));
    for(let i=1;i<=40;i++) setArray('M',i,0);
    const key=char=>{m.ram[sym('KBD_LASTK')]=char.charCodeAt(0);m.ram[sym('KBD_KEYHIT')]=1;};
    function press(char) {
      key(char); runZ80(m.cpu,m.bus,1,m);
      until(new Set([doneAddress]),150_000_000,()=>atLabel('QL1401')&&!m.ram[sym('KBD_KEYHIT')]);
    }
    if(program.symbols.some(s=>s.name==='QZINTRO') && fs.readFileSync(path.join(romdir,'startup.leap.bas'),'utf8').includes('USR(63512)')) {
      const directions=[[1,0,-1],[2,0,1],[4,-1,0],[8,1,0],[5,-1,-1],[9,1,-1],[6,-1,1],[10,1,1]];
      const bitmapAddress=(x,y)=>0x4000+((y&24)<<8)+((y&7)<<5)+x;
      const empty=(x,y)=>Array.from({length:8},(_,i)=>m.ram[bitmapAddress(x,y)+256*i]).every(v=>v===0);
      const origin={x:value('MX'),y:value('MY')};
      let open=null;
      for(let yy=value('NB')+1;yy<value('SB')&&!open;yy++)for(let xx=value('WB')+1;xx<value('EB')&&!open;xx++) {
        if(Array.from({length:9},(_,i)=>empty(xx+i%3-1,yy+Math.floor(i/3)-1)).every(Boolean))open={x:xx,y:yy};
      }
      if(!open)throw Error('No open joystick test square');
      const erase=()=>{const a=bitmapAddress(value('MX'),value('MY'));for(let i=0;i<8;i++)m.ram[a+256*i]=0;};
      function joy(mask) {
        putword(sym('RND_STATE'),0x8000);m.joystick[0]=255^mask;
        runZ80(m.cpu,m.bus,1,m);
        until(new Set([doneAddress]),150_000_000,()=>atLabel('QL1460'));
        runZ80(m.cpu,m.bus,1,m);
        until(new Set([doneAddress]),150_000_000,()=>atLabel('QL1401'));
        m.joystick[0]=255;
      }
      const checked=[];
      for(const [mask,dx,dy] of directions) {
        erase();setValue('MX',open.x);setValue('MY',open.y);setValue('NMX',open.x);setValue('NMY',open.y);
        joy(mask);
        if(value('MX')!==open.x+dx||value('MY')!==open.y+dy)throw Error('Joystick direction failed: '+JSON.stringify({mask,x:value('MX'),y:value('MY'),open}));
        checked.push(mask);
      }
      erase();setValue('MX',open.x);setValue('MY',open.y);setValue('NMX',open.x);setValue('NMY',open.y);
      const wall=bitmapAddress(open.x+1,open.y)+256*3, oldWall=m.ram[wall];
      m.ram[wall]=255;
      joy(9);
      m.ram[wall]=oldWall;
      if(value('MX')!==open.x||value('MY')!==open.y)throw Error('Diagonal cut through adjacent wall');
      joy(128);
      if(!screen().includes("Can't attack"))throw Error('Joystick fire did not select sword attack');
      erase();setValue('MX',origin.x);setValue('MY',origin.y);setValue('NMX',origin.x);setValue('NMY',origin.y);
      fs.writeFileSync(path.join(romdir,'joystick-verification.json'),JSON.stringify({port:'0x01F6',ayRegister:14,directions:checked,diagonals:true,cornerCollision:true,fire:'sword attack',physicalHardwareTested:false},null,2)+'\n');
    }
    const y=value('MY');putword(sym('RND_STATE'),0x8000);press('q');snapshot('move');
    if(value('MY')!==y-1) throw Error('Keyboard movement failed');
    function cell(x,y) {
      const a=0x4000+((y&24)<<8)+((y&7)<<5)+x;
      return {glyph:Buffer.from(Array.from({length:8},(_,i)=>m.ram[a+256*i])),attr:m.ram[0x5800+y*32+x]};
    }
    function checkPlayer() {
      const c=cell(value('MX'),value('MY'));
      const expected=fs.readFileSync(path.join(process.cwd(),'assets/crown',`charset-${value('LV')+1}.bin`)).subarray((value('DF')-1)*8,value('DF')*8);
      if(!c.glyph.equals(expected)||(c.attr&7)===((c.attr>>3)&7)) throw Error(`Invisible/malformed player: ${JSON.stringify({x:value('MX'),y:value('MY'),attr:c.attr,glyph:c.glyph.toString('hex'),expected:expected.toString('hex')})}`);
    }
    checkPlayer();
    if(cell(value('MX'),y).glyph.some(v=>v)||(cell(value('MX'),y).attr&56)!==56) throw Error('Player left a bitmap/attribute trail');
    for(const char of 'zqzqzqzqzqzqzqzqzqzq') {
      // Keep the isolated movement test free of random monster spawns.
      putword(sym('RND_STATE'),0x8000);
      const old={x:value('MX'),y:value('MY')};press(char);checkPlayer();
      if((old.x!==value('MX')||old.y!==value('MY'))&&cell(old.x,old.y).glyph.some(v=>v)) throw Error('Repeated movement leaves a bitmap trail');
    }
    key('h');runZ80(m.cpu,m.bus,1,m);
    until(new Set([doneAddress]),150_000_000,()=>atLabel('QL2660')&&!m.ram[sym('KBD_KEYHIT')]);
    function checkMenuUnderline() {
      // Nine character widths at x=96..167, pixel y=9, below the title row.
      const address=0x4000+((9&0xC0)<<5)+((9&7)<<8)+((9&0x38)<<2)+12;
      if(!m.ram.subarray(address,address+9).every(v=>v===255)) throw Error('Graphical menu underline missing');
    }
    snapshot('help');
    if(!screen().split('\n')[0].includes('Help Menu')) throw Error('Help heading glyphs corrupted');
    checkMenuUnderline();
    press(' ');checkPlayer();
    key('i');runZ80(m.cpu,m.bus,1,m);
    until(new Set([doneAddress]),150_000_000,()=>atLabel('QL2660')&&!m.ram[sym('KBD_KEYHIT')]);
    snapshot('inventory');
    if(!screen().split('\n')[0].includes('INVENTORY')) throw Error('Inventory heading glyphs corrupted');
    checkMenuUnderline();
    press(' ');checkPlayer();
    press('d');snapshot('potion');
    if(!value('CX')) {setValue('CX',value('MX'));setValue('CY',value('MY')-4);}
    setArray('M',1,1);setValue('CHP',1000);setValue('HP',1000);
    for(const char of 'zqzqzqzq') {
      const old={x:value('CX'),y:value('CY')};press(char);checkPlayer();
      const monster=cell(value('CX'),value('CY'));
      if((monster.attr&7)!==2||!monster.glyph.equals(fs.readFileSync(path.join(process.cwd(),'assets/crown/charset-2.bin')).subarray(32,40))) throw Error('Creature bitmap/colour differs');
      if((old.x!==value('CX')||old.y!==value('CY'))&&(old.x!==value('MX')||old.y!==value('MY'))&&(cell(old.x,old.y).glyph.some(v=>v)||(cell(old.x,old.y).attr&56)!==56)) throw Error('Creature left a bitmap/attribute trail');
    }
    setValue('CX',value('MX'));setValue('CY',value('MY')-1);setValue('CHP',1000);
    const combatStart=m.tstates;press('a');
    const combatTurnMs=(m.tstates-combatStart)*1000/3_528_000;
    if(combatTurnMs<480) throw Error(`Combat turn delay absent: ${combatTurnMs} ms`);
    snapshot('creature-redraw');setArray('M',1,0);setValue('HP',20);
    const lockChecks=[];
    function checkLock() {
      const level=value('LV');
      setArray('E',1,40);setValue('MY',value('NB'));setValue('NMY',value('MY'));setValue('DF',1);
      press('q');
      if(value('RM')!==40) throw Error('Lock-room entry failed');
      const x=arrayValue('D',(level-1)*3+1),y=arrayValue('D',(level-1)*3+2),item=arrayValue('D',(level-1)*3+3);
      setValue('MX',x);setValue('NMX',x);setValue('MY',y+1);setValue('NMY',y+1);setValue('DF',1);setArray('I',item,0);
      const locked=cell(x,y).glyph;
      if(!locked.some(v=>v)) throw Error('Locked door absent');
      press('q');
      if(value('MY')!==y+1) throw Error(`Door traversable without using key: level=${level}, glyph=${locked.toString('hex')}, position=${value('MY')}, expected=${y+1}`);
      function useKey() {
        key('u');runZ80(m.cpu,m.bus,1,m);
        until(new Set([doneAddress]),20_000_000,()=>atLabel('QZW4')&&!m.ram[sym('KBD_KEYHIT')]);
        press('k');
      }
      useKey();
      if(!screen().includes('No key')||!cell(x,y).glyph.equals(locked)) throw Error('No-key lock rejection failed');
      const wrong=item===11?12:11;setArray('I',wrong,1);
      useKey();
      if(!cell(x,y).glyph.equals(locked)) throw Error('Wrong key opens door');
      setArray('I',item,1);
      press('q');
      if(value('MY')!==y+1) throw Error('Possessing key opens door without explicit use');
      useKey();
      if(cell(x,y).glyph.some(v=>v)) throw Error('Correct key did not clear locked door');
      press('q');
      if(value('MY')!==y) throw Error('Unlocked doorway not traversable');
      lockChecks.push({level,requiredInventoryItem:item,noKeyBlocked:true,wrongKeyBlocked:true,explicitUseRequired:true,correctKeyUnlocks:true,unlockedDoorTraversable:true});
    }
    checkLock();
    for(const level of [2,3]) {
      setArray('E',1,100*level+1);setValue('MY',value('NB'));setValue('NMY',value('MY'));setValue('DF',1);
      press('q');snapshot('level'+level);
      if(value('LV')!==level||value('RM')!==1) throw Error(`Level ${level} transition failed`);
      const original=fs.readFileSync(path.join(process.cwd(),'assets/crown',`charset-${level+1}.bin`));
      if(!Buffer.from(m.ram.subarray(61824,61992)).equals(original)) throw Error(`Level ${level} glyphs differ from TAP`);
      checkLock();
    }
    let warmIntro=null;
    if(manifest.startup_intro?.display_size?.[0]===256) {
      const intro=Object.fromEntries([...fs.readFileSync(path.join(romdir,'intro.sym'),'utf8').matchAll(/^(\S+):\s+EQU\s+0x([0-9a-f]+)/gmi)].map(m=>[m[1],parseInt(m[2],16)]));
      if(intro.restart_intro) {
        if(!Buffer.from(m.ram.subarray(word(0xFAE6),word(0xFAEC))).equals(savedFreshState)) throw Error('Gameplay overwrote the reserved fresh-game snapshot');
        // Enter the real end-of-game question from a safe bytecode boundary.
        putword(sym('VM_IP'),label('QL3020'));
        runZ80(m.cpu,m.bus,1,m);
        until(new Set([doneAddress]),20_000_000,()=>atLabel('QZW2')&&!m.ram[sym('KBD_KEYHIT')]);
        if(!screen().includes('Play again (y/n)?')) throw Error('Play-again question absent');
        m.keyMatrix[7]=0xF7; // Physical N key.
        until(new Set([intro.restart_intro]),20_000_000);
        const start=m.tstates;
        m.keyMatrix[7]=0xFF;
        until(new Set([intro.wait_key]),30_000_000);
        if(m.ram[0xFAC0]!==1||m.ram[0xFAC3]!==1||m.portFF!==2) throw Error('N did not return to ready animation');
        const returnMs=(m.tstates-start)*1000/3_528_000;
        const refresh=m.ram[0xFAC6], end=m.tstates+3_528_000;
        until(new Set([doneAddress]),5_000_000,()=>m.tstates>=end);
        if(m.ram[0xFAC6]===refresh) throw Error('Returned intro does not animate');
        m.keyMatrix[7]=0xFE;
        until(new Set([intro.release_after]),10_000_000);
        m.keyMatrix[7]=0xFF;
        until(new Set([doneAddress]),50_000_000,ready);
        if(value('LV')!==1||value('HP')!==20||value('RM')!==1||m.portFF!==0) throw Error('Warm fresh-game state differs');
        if(!Buffer.from(m.ram.subarray(61824,61992)).equals(fs.readFileSync('assets/crown/charset-2.bin'))) throw Error('Warm restart did not restore first-level glyphs');
        runZ80(m.cpu,m.bus,1,m);
        until(new Set([doneAddress]),20_000_000,()=>atLabel('QL1401')&&!m.ram[sym('KBD_KEYHIT')]);
        checkPlayer();
        warmIntro={physicalNKey:true,animationReady:true,returnMs,fullInitializationRepeated:false,freshLevel:1,freshHP:20,level1CharsetRestored:true,snapshotBytes:word(0xFAEC)-word(0xFAE6)};
        snapshot('warm-new-game');
        if(intro.native_dungeon) {
          const itemSlot=program.symbols.find(s=>s.name==='QA40'&&s.kind===2).index;
          const itemAddress=word(word(sym('RT_ARRPTR_PTR'))+2*itemSlot)+5;
          const before=Buffer.from(m.ram.subarray(itemAddress,itemAddress+480));
          putword(sym('VM_IP'),label('QL3020'));runZ80(m.cpu,m.bus,1,m);
          until(new Set([doneAddress]),20_000_000,()=>atLabel('QZW2')&&!m.ram[sym('KBD_KEYHIT')]);
          putword(sym('RND_STATE'),12345);press('y');
          if(before.equals(Buffer.from(m.ram.subarray(itemAddress,itemAddress+480)))) throw Error('Replay Y did not randomize dungeon');
          if(value('LV')!==1||value('HP')!==20||value('RM')!==1) throw Error('Replay Y initial state differs');
          warmIntro.replayYRandomizesDungeon=true;
          checkPlayer();
        }

      }
    }
    const report={status:'Scripted Crown cartridge gameplay',redrawChecks:{repeatedPlayerMoves:20,creatureTurns:8,playerGlyphAndContrast:true,oldPlayerBitmapCleared:true,oldCreatureBitmapAndPaperCleared:true},snapshots,warmIntro,writesToRom,bytecodeReads:fetches,vmError:m.ram[sym('VM_ERROR_CODE')]};
    report.lockChecks=lockChecks;
    report.combatTurnMs=combatTurnMs;
    fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report,null,2));
    if(writesToRom||report.vmError) throw Error('Game banking/runtime check failed');
    process.exit(0);
  }
  until(new Set([doneAddress]),400_000_000);
  const report={status:'TSRun headless cartridge execution',vmError:m.ram[sym('VM_ERROR_CODE')],hsr:m.portF4,decr:m.portFF,sp:m.cpu.sp,bytecodeFetches:fetches,writesToRom,arenaFree:word(sym('VARS_START'))-word(sym('ARRAYS_END')),output:screen()};
  if(report.vmError||writesToRom||!fetches) throw Error(JSON.stringify(report));
  fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));
} else throw Error('Mode must be compile, bytecode or cartridge');

