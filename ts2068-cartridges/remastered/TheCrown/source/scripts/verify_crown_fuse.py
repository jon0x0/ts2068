"""Check HOME bitmap/attribute samples during scripted Crown gameplay in Fuse."""
import json,re,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
combined='--combined' in sys.argv
out=ROOT/('build/crown-combined' if combined else 'build/crown')
syms={}
for name in ('test_basic','exrom'):
    variant='combined-runtime' if combined else 'wide-cartridge'
    for n,v in re.findall(r'^(\S+): EQU 0x([\da-fA-F]+)',(ROOT/f'build/{variant}/build/{name}.sym').read_text(),re.M):
        syms.setdefault(n,int(v,16))
p=json.loads((out/'bytecode.json').read_text())
target=p['base']+next(s['offset'] for s in p['symbols'] if s['name']=='QL1401')
ip=syms['VM_IP']; loop=syms['VM_RUN.loop']
commands=['set $stage 0']
watch='--watch' in sys.argv
if watch:
    commands += ['breakpoint write 0x8103','commands 1','print 0x20000','print z80:pc','print z80:af','print [0x8103]',f'print [{ip}]+256*[{ip+1}]','continue','end']
    commands += ['breakpoint 0x200c if z80:bc>31','commands 2','print 0x30000','print z80:hl','print z80:bc','print z80:af','print [0xb811]+256*[0xb812]','print [0xb818]','print [0xb6a0]',f'print [{ip}]+256*[{ip+1}]','continue','end']
    commands += ['breakpoint 0x1550','commands 3','print 0x40000','print z80:sp','print [z80:sp]+256*[z80:sp+1]','print [0xb6a6]+256*[0xb6a7]',f'print [{ip}]+256*[{ip+1}]','continue','end']
for stage,key in enumerate(('q','z',None)):
    commands += [f'breakpoint {loop} if ([{ip}]+256*[{ip+1}])=={target} && $stage=={stage} && [{syms["KBD_KEYHIT"]}]==0',f'commands {stage+1+3*watch}',f'print {0x10000+stage}']
    commands += [f'print [{syms[n]}]' for n in ('CURRENT_INK','CURRENT_PAPER','CURRENT_OVER','CURRENT_INVERSE','VM_ERROR_CODE')]
    commands += ['out 0xf4 0x0b']
    # Pack four bytes per expression to keep the Windows command line short.
    commands += [f'print [{a}]+256*[{a+1}]+65536*[{a+2}]+16777216*[{a+3}]' for a in range(0x4000,0x5B00,4)]
    commands += ['out 0xf4 0x4f',f'set $stage {stage+1}']
    if key:
        commands += [f'set {syms["KBD_LASTK"]} {ord(key)}',f'set {syms["KBD_KEYHIT"]} 1','continue','end']
    else: commands += ['exit 0','end']
# Capture attributes in rows 14-18 and the initial/moved player glyphs.
# Four bytes per expression keep the command below the Windows argv limit.
compact=[]
for line in commands:
    if line.startswith('print [') and '+16777216*' in line:
        a=int(re.search(r'\[(\d+)\]',line)[1])
        if not (0x5800+14*32<=a<0x5800+19*32 or any(a==0x4000+((y&24)<<8)+((y&7)<<5)+16+i*256 for y in (15,16) for i in range(8))): continue
    compact.append(line)
text='\n'.join(compact)
if combined:
    intro={n:int(v,16) for n,v in re.findall(r'^(\S+): EQU 0x([\da-fA-F]+)',(out/'intro.sym').read_text(),re.M)}
    # Gate input itself is verified through TSRun's physical keyboard matrix.
    # Fuse starts gameplay by jumping to the release-after branch at the gate.
    text=text.replace('out 0xf4 0x0b','out 0xf4 3').replace('out 0xf4 0x4f','out 0xf4 3')
    text += f'\nbreakpoint {intro["wait_key"]}\ncommands 4\nset z80:pc {intro["release_after"]}\ncontinue\nend'
(out/'fuse-game-commands.txt').write_text(text)
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW
argv=[__import__('os').environ.get('FUSE_EXE', 'fuse'),'--machine','ts2068','--rom-ts2068-0',str(out/'stock-home.rom'),'--rom-ts2068-1',str(out/'stock-exrom.rom'),'--dock',str(out/'program.dck'),'--speed','5000','--no-sound','--no-loading-sound','--debugger-command',text]
r=subprocess.run(argv,capture_output=True,text=True,timeout=45,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
(out/'fuse-game.log').write_text(r.stdout+r.stderr)
print('Fuse exit:',r.returncode)
if r.returncode or 'Invalid debugger command' in r.stdout+r.stderr:
    print((r.stdout+r.stderr)[:1200]);raise SystemExit(1)
if not watch:
    values=[int(v,16)&0xffffffff for v in re.findall(r'^0x([\da-fA-F]+)\s*$',r.stdout,re.M)]
    addresses=[]
    for a in range(0x4000,0x5B00,4):
        if 0x5800+14*32<=a<0x5800+19*32 or any(a==0x4000+((y&24)<<8)+((y&7)<<5)+16+i*256 for y in (15,16) for i in range(8)): addresses.append(a)
    snapshots=[];cursor=0;glyphs=(ROOT/'assets/crown/charset-2.bin').read_bytes()
    for stage,y,direction in ((0,16,1),(1,15,1),(2,16,3)):
        assert values[cursor]==0x10000+stage,'Missing Fuse checkpoint'
        state=values[cursor+1:cursor+6]
        assert state==[0,7,0,0,0],f'Corrupted drawing state: {state}'
        memory={}
        for a,v in zip(addresses,values[cursor+6:cursor+6+len(addresses)]):
            memory.update({a+i:(v>>(8*i))&255 for i in range(4)})
        def glyph(row):
            a=0x4000+((row&24)<<8)+((row&7)<<5)+16
            return bytes(memory[a+i*256] for i in range(8))
        assert glyph(y)==glyphs[(direction-1)*8:direction*8],'Player glyph differs in Fuse'
        assert memory[0x5800+y*32+16]==0x38,'Player colour/contrast differs in Fuse'
        if stage:
            old=31-y
            assert glyph(old)==bytes(8),'Old player glyph was not erased'
            assert memory[0x5800+old*32+16]==0x38,'Erasure left a black attribute block'
        snapshots.append({'stage':stage,'playerY':y,'ink':state[0],'paper':state[1],'vmError':state[4]})
        cursor+=6+len(addresses)
    assert cursor==len(values),'Unexpected Fuse output'
    report={'emulator':'Fuse 1.10.0','result':'Stock-ROM boot, visible player, up/down movement and bitmap/attribute erasure passed','snapshots':snapshots}
    (out/'fuse-gameplay.json').write_text(json.dumps(report,indent=2)+'\n')
    manifest=json.loads((out/'manifest.json').read_text())
    manifest['verification']='TSRun repeated player/creature redraw and three levels passed; Fuse stock-ROM boot, player visibility and up/down bitmap/attribute erasure passed; physical hardware untested'
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(report['result'])
raise SystemExit(r.returncode)
