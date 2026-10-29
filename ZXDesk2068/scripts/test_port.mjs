// Integration tests against a caller-supplied TSRun checkout and its native ROMs.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const tsrun = path.resolve(process.argv[2] || '../TSRun');
const name = process.argv[3] || 'zxdesk2068';
const api = await import(pathToFileURL(path.join(tsrun, 'machine.js')));
const {runZ80} = await import(pathToFileURL(path.join(tsrun, 'z80.js')));
const sym = Object.fromEntries(fs.readFileSync(`build/${name}.sym`, 'utf8').trim().split(/\r?\n/).map(l => {
    const [name,, value] = l.trim().split(/\s+/); return [name, parseInt(value, 16)];
}));
const keys = new Uint8Array(8).fill(0x1f);
const sticks = new Uint8Array([255, 255]);
const m = api.createMachine(keys, sticks);
api.setHomeRom(m, fs.readFileSync(path.join(tsrun, 'roms/ts2068-0.rom')));
api.setExRom(m, fs.readFileSync(path.join(tsrun, 'roms/ts2068-1.rom')));
api.resetMachine(m);
const ports = [];
const out = m.bus.ioWrite;
m.bus.ioWrite = (p, v) => { ports.push([p, v]); out(p, v); };
assert.equal(api.insertTape(m, fs.readFileSync(`build/${name}.tap`)), null);
assert.equal(api.autoloadTape(m), true);
let bootFrames = 0;
for (; bootFrames < 20000; bootFrames++) {
    api.runFrame(m);
    if (m.cpu.im === 2 && m.ram[sym.StBackend] === 1 && m.ram[sym.IrqCnt] > 10) break;
}
assert.ok(bootFrames < 20000, `native tape did not boot: PC=${m.cpu.pc.toString(16)}`);
for (let n = 0; n < 180; n++) api.runFrame(m);
assert.equal(m.portF4, 0);
assert.equal(m.portFF, (sym.SCRCOLS === 64) ? 6 : 0);
assert.equal(m.ram[sym.Is128], 0);
assert.equal(m.ram[sym.MouseOn], 0);
assert.equal(m.ram[sym.StBackend], 1);
assert.ok(!ports.some(([p]) => p === 0x7ffd), 'Spectrum paging port used');
assert.ok(m.ram.slice(0x4000, 0x5800).some(v => v !== 0), 'blank desktop');
if (sym.SCRCOLS === 32) fs.writeFileSync('build/desktop.scr', m.ram.slice(0x4000, 0x5b00));
if ((sym.SCRCOLS === 64)) fs.writeFileSync('build/desktop-512.hires', Buffer.concat([m.ram.slice(0x4000,0x5800),m.ram.slice(0x6000,0x7800)]));
console.log(`PASS native ROM tape boot (${bootFrames} frames), HOME mapping, IM2, desktop, no 7FFD`);
// Exercise the real event loop: plain letters must type, not move the pointer.
const beforeTypingX = m.ram[sym.PtrX];
keys[1] = 0x1e; // A
for (let n = 0; n < 3; n++) api.runFrame(m);
keys.fill(0x1f);
for (let n = 0; n < 3; n++) api.runFrame(m);
assert.equal(m.ram[sym.NoteBuf], 'A'.charCodeAt(0));
assert.equal(m.ram[sym.PtrX], beforeTypingX);
console.log('PASS notepad typing through native keyboard and event loop');

// Call real assembled routines with the native memory/port model.
function call(name, regs = {}) {
    const stack = sym.STACKTOP - 16;
    Object.assign(m.cpu, {pc: sym[name], sp: stack, halted: false, iff1: false, iff2: false}, regs);
    m.ram[stack] = 0; m.ram[stack+1] = 0x5b;
    for (let n = 0; n < 2000000; n++) {
        if (m.cpu.pc === 0x5b00) return;
        runZ80(m.cpu, m.bus, 1, m);
    }
    throw new Error(`routine ${name} did not return: PC=${m.cpu.pc.toString(16)}, SP=${m.cpu.sp.toString(16)}`);
}
const word = a => m.ram[a] | m.ram[a + 1] << 8;
const bc = () => m.cpu.b << 8 | m.cpu.c;
const carry = () => m.cpu.f & 1;
for (const [contact, dir] of [[0,4], [1,8], [2,1], [3,2]]) {
    sticks[0] = 255 ^ (1 << contact);
    call('TsReadJoy', {b: 0x55, c: 0});
    assert.equal(m.cpu.c, dir); assert.equal(m.cpu.b, 0x55);
}
sticks[0] = 255; sticks[1] = 127;
m.ram[sym.Buttons] = 255;
call('TsReadJoy', {c: 1});
assert.equal(m.cpu.c, 1); assert.equal(m.ram[sym.Buttons], 253);
sticks[1] = 255;
call('TsReadJoy', {c: 0}); assert.equal(m.cpu.c, 0);
// Native matrix input: P moves right while idle input does not drift.
const px = m.ram[sym.PtrX];
keys[0] = 0x1e; keys[7] = 0x1d; keys[5] = 0x1e;
call('ReadInput'); keys.fill(0x1f);
assert.ok(m.ram[sym.PtrX] > px);
const idleX = m.ram[sym.PtrX]; call('ReadInput');
assert.equal(m.ram[sym.PtrX], idleX);
console.log('PASS both native joystick ports, directions, fire, keyboard pointer and idle');
call('ClkInit');
for (let n = 0; n < 60; n++) { m.ram[sym.IrqCnt]++; if (!m.ram[sym.IrqCnt]) m.ram[sym.IrqCnt+1]++; call('ClkTick'); }
assert.equal(m.ram[sym.ClkS], 1);
console.log('PASS 60-interrupt clock second');
call('WndOpen', {a:sym.APP_CLOCK}); assert.equal(carry(),0);
call('WndOpen', {a:sym.APP_CAL}); assert.equal(carry(),0);
console.log('PASS clock and calendar window creation');
if (sym.SCRCOLS === 64) {
    const setPointer = (x,y) => {
        call('PtrRestore');
        m.ram[sym.PtrX]=x&255;m.ram[sym.PtrX+1]=x>>8;m.ram[sym.PtrY]=y;
        call('PtrSaveBg');call('PtrDraw');
    };
    const screen = () => Buffer.concat([m.ram.slice(0x4000,0x5800),m.ram.slice(0x6000,0x7800)]);
    setPointer((m.ram[sym.WinX]+3)*8,m.ram[sym.WinY]+3);
    call('HdlBtnDown');assert.equal(m.ram[sym.Dragging],1);
    setPointer(39*8,m.ram[sym.WinY]+3);
    call('HdlPtrMove');assert.equal(m.ram[sym.WinX],36);
    call('WinRedraw');call('HdlBtnUp');
    call('WndHitTest',{b:39,c:m.ram[sym.WinY]+3});assert.equal(m.cpu.a,sym.CTL_TITLEBAR);
    const oldW=m.ram[sym.WinW], oldH=m.ram[sym.WinH];
    call('RszStart');setPointer((36+oldW+2-1)*8,m.ram[sym.WinY]+oldH-1);
    call('RszMove');call('HdlBtnUp');assert.equal(m.ram[sym.WinW],oldW+2);
    call('WndRepaintAll');call('PtrSaveBg');call('PtrDraw');
    const before=screen();call('MenuOpenDrop',{a:2});assert.equal(m.ram[sym.MenuOpen],2);
    call('MenuClose');
    const afterMenu=screen();
    const diffs=[];
    for(let y=0;y<192;y++)for(let x=0;x<64;x++) {
        const a=(x&1)*6144+((y&192)<<5)+((y&7)<<8)+((y&56)<<2)+(x>>1);
        if(afterMenu[a]!==before[a])diffs.push([x,y,before[a],afterMenu[a]]);
    }
    assert.equal(diffs.length,0,`menu restoration: ${JSON.stringify(diffs.slice(0,20))}`);
    fs.writeFileSync('build/desktop-512-windows.hires',screen());
    console.log('PASS right-half title hit, drag, resize, repaint and menu restoration');
}
call('StInit');
for (const id of [2,3,4,8]) { call('StSelect', {a:id}); assert.equal(carry(),1); assert.equal(m.ram[sym.StBackend],1); }
m.ram.set(Buffer.from('ROUNDTRIP\0'), 0x5b10);
m.ram.set([1, 23, 45, 67, 89], 0x5b40);
call('StOpen', {h:0x5b,l:0x10,b:14}); assert.equal(carry(),0);
const handle = m.cpu.a;
call('StWrite', {a:handle,h:0x5b,l:0x40,b:0,c:5}); assert.equal(carry(),0); assert.equal(bc(),5);
call('StClose', {a:handle});
call('StOpen', {h:0x5b,l:0x10,b:1}); assert.equal(carry(),0);
call('StRead', {a:m.cpu.a,h:0x5b,l:0x60,b:0,c:16}); assert.equal(carry(),0); assert.equal(bc(),5);
assert.deepEqual([...m.ram.slice(0x5b60,0x5b65)], [1,23,45,67,89]);
call('StDir', {a:0}); assert.equal(carry(),0); assert.equal(m.cpu.d << 8 | m.cpu.e,5);
call('StDelete', {h:0x5b,l:0x10}); assert.equal(carry(),0);
call('StDir', {a:0}); assert.equal(carry(),1);
console.log('PASS RAM file round-trip, short read, directory, delete and unsupported backend rejection');
if ((sym.SCRCOLS === 64)) {
    const put = (n,v) => { m.ram[sym[n]]=v&255; m.ram[sym[n]+1]=v>>8; };
    const byte = (n,v) => { m.ram[sym[n]]=v; };
    const addr = (x,y) => 0x4000 + ((x&1)<<13) + ((y&192)<<5) + ((y&7)<<8) + ((y&56)<<2) + (x>>1);
    const screen = () => Buffer.concat([m.ram.slice(0x4000,0x5800),m.ram.slice(0x6000,0x7800)]);
    const offset = a => a < 0x6000 ? a-0x4000 : a-0x4800;
    function pattern() { for(let y=0;y<192;y++) for(let x=0;x<64;x++) m.ram[addr(x,y)]=(x*17+y*13)&255; }
    for(let y=0;y<192;y++) for(let x=0;x<64;x++) {
        call('AddrAt',{a:y,c:x}); assert.equal(m.cpu.h<<8|m.cpu.l,addr(x,y));
    }
    console.log('PASS all 12,288 high-resolution byte addresses');
    for(const [x,y,w,h] of [[0,0,64,1],[1,7,17,9],[31,63,6,3],[32,127,32,9],[62,190,2,2],[3,8,1,1],[0,0,0,2],[0,0,2,0]]) {
        pattern(); const expected=screen();
        for(let dy=0;dy<h;dy++) for(let dx=0;dx<w;dx++) expected[offset(addr(x+dx,y+dy))]=dx&1?0xa5:0x3c;
        for(const [n,v] of Object.entries({FrX:x,FrY:y,FrW:w,FrH:h})) byte(n,v);
        put('FrPat',0xa53c); call('DevFillRect'); assert.deepEqual(screen(),expected,`fill ${x},${y},${w},${h}`);
    }
    pattern(); let expected=screen();
    byte('FrX',31);byte('FrY',61);byte('FrW',7);byte('FrH',11);
    call('DevFillDesk');
    for(let y=61;y<72;y++) for(let x=31;x<38;x++) expected[offset(addr(x,y))]=y%4===0?m.ram[sym.LatA1]:y%4===2?m.ram[sym.LatB1]:0;
    assert.deepEqual(screen(),expected);
    for(const [x,y,w,h] of [[0,0,64,8],[1,7,17,9],[31,63,6,3],[32,127,32,9],[62,190,2,2]]) {
        pattern(); const before=screen(); const linear=[];
        for(let dy=0;dy<h;dy++) for(let dx=0;dx<w;dx++) linear.push(m.ram[addr(x+dx,y+dy)]);
        for(const [n,v] of Object.entries({RcX:x,RcY:y,RcW:w,RcH:h})) byte(n,v);
        put('RcBuf',0xd000); call('RectGrab'); assert.deepEqual([...m.ram.slice(0xd000,0xd000+w*h)],linear);
        for(let dy=0;dy<h;dy++) for(let dx=0;dx<w;dx++) m.ram[addr(x+dx,y+dy)]=0;
        call('RectBlit');assert.deepEqual(screen(),before);
    }
    console.log('PASS fill, lattice, grab and blit across both planes and all row boundaries');
    for(const inverse of [0,1]) {
        pattern(); const text='ABCDEFGHIJKLMNOPQRSTUVWXYZ012345';
        expected=screen();m.ram.set(Buffer.from(text+'\0'),0x5b10);
        byte('PxRow',61);byte('PrintInv',inverse);
        call('PrintStrPx2',{h:0x5b,l:0x10,c:31});
        for(let i=0;i<text.length;i++)for(let r=0;r<8;r++)expected[offset(addr(31+i,61+r))]=m.homeRom[0x3c00+text.charCodeAt(i)*8+r]^(inverse?255:0);
        assert.deepEqual(screen(),expected,'font blit across planes and row boundary');
    }
    byte('PrintInv',0);
    pattern();expected=screen();
    for(const [n,v] of Object.entries({WinX:29,WinY:60,WinW:16,WinH:12,ClX:31,ClY:63,ClW:9,ClH:5})) byte(n,v);
    put('WinBufP',0xd000);for(let i=0;i<192;i++)m.ram[0xd000+i]=i^0x55;
    call('BlitClip');
    for(let y=63;y<68;y++)for(let x=31;x<40;x++)expected[offset(addr(x,y))]=((y-60)*16+x-29)^0x55;
    assert.deepEqual(screen(),expected);
    for(const x of [0,7,8,15,16,247,248,255,256,263,495,503]) for(const y of [0,7,63,127,172]) {
        pattern();const before=screen();put('PtrX',x);byte('PtrY',y);
        call('PtrSaveBg');call('PtrDraw');assert.notDeepEqual(screen(),before);
        call('PtrRestore');assert.deepEqual(screen(),before,`pointer restore ${x},${y}`);
    }
    for(const [x,delta,result] of [[255,1,256],[256,-1,255],[0,-1,0],[503,1,503],[500,10,503],[4,-10,0]]) {
        put('PtrX',x);call('HiresMoveX',{a:delta&255});assert.equal(word(sym.PtrX),result);
    }
    put('PtrX',400);call('SsBuild');assert.equal(Buffer.from(m.ram.slice(sym.StatRow+2,sym.StatRow+5)).toString(),'400');
    put('PtrX',256);put('EvLastX',0);byte('EvLastY',m.ram[sym.PtrY]);byte('EvHead',0);byte('EvTail',0);
    byte('EvLastBtn',m.ram[sym.Buttons]);call('EvPoll');assert.equal(m.ram[sym.EvHead],1);
    call('EvNext');assert.equal(m.cpu.a,sym.EV_PTRMOVE);assert.equal(m.cpu.b,32);
    console.log('PASS clipped blits, pointer save/restore, 9-bit motion/clamping, status and high-byte move events');
}


