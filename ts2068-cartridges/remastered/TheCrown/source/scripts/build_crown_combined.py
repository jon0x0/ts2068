"""Build the stock-ROM 64KB Crown cartridge with its full eight-pose ECM intro."""
from pathlib import Path
import json
import subprocess
import sys
import re
import struct
import hashlib
from PIL import Image
from package_leap_cartridge import load_symbols
from clean_crown_intro import build_sequence
import native_crown_init

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/crown-combined'
RUNTIME=ROOT/'build/combined-runtime'
NODE=Path(__import__('os').environ.get('CROWN_NODE') or __import__('shutil').which('node') or 'node')
CODEC=ROOT/'tools/tsvideocodec'
sys.path.insert(0,str(CODEC))
from svd_stream import encode_hybrid_plane
from svd_ecm import ECMFrame

def run(*args,cwd=ROOT):
    subprocess.run(list(map(str,args)),cwd=cwd,check=True)

def wslpath(p):
    return '/mnt/'+p.drive[0].lower()+p.as_posix()[2:]

OUT.mkdir(parents=True,exist_ok=True)
source=(ROOT/'build/crown/converted.leap.bas').read_text()
# Restore the stock game's real joystick input in the final cartridge.
assert source.count('QV34 = 255\nQV35$ = INKEY$()') == 1
source=source.replace('QV34 = 255\nQV35$ = INKEY$()',
                      'QV34 = USR(63512)\nQV35$ = INKEY$()')
# Two contacts form one diagonal move/creature turn, using the original
# collision and redraw routines. At room edges fall back to cardinal input;
# do not pass diagonally through an adjacent wall or a locked-door glyph.
diagonal='''QV1 = QV7
QV4 = QV8
IF QV34 < 128 THEN
IF FN QZFLOOR(QV34/4)-2*FN QZFLOOR(QV34/8) THEN
QV1 = QV1-1
ENDIF
IF FN QZFLOOR(QV34/8)-2*FN QZFLOOR(QV34/16) THEN
QV1 = QV1+1
ENDIF
IF QV34-2*FN QZFLOOR(QV34/2) THEN
QV4 = QV4-1
ENDIF
IF FN QZFLOOR(QV34/2)-2*FN QZFLOOR(QV34/4) THEN
QV4 = QV4+1
ENDIF
IF (QV1 <> QV7) AND (QV4 <> QV8) THEN
IF (QV1 >= QV2) AND (QV1 <= QV3) AND (QV4 >= QV6) AND (QV4 <= QV5) THEN
IF POINT(QV1*8+3,175-((21-QV8)*8+4)) OR POINT(QV7*8+3,175-((21-QV4)*8+4)) THEN
QV1 = QV7
QV4 = QV8
GOTO QL1401
ENDIF
QV10 = 2
IF QV1 < QV7 THEN
QV10 = 4
ENDIF
IF QZSP >= 64 THEN
PRINT "GOSUB STACK OVERFLOW"
END
ENDIF
QZSP = QZSP+1
QZSTACK(QZSP) = 7
GOTO QL540
ENDIF
ENDIF
ENDIF
QV1 = QV7
QV4 = QV8
'''
source=source.replace('QV34 = (255 - QV34)\n', 'QV34 = (255 - QV34)\n'+diagonal,1)
# Startup uses black until the native ready prompt announces completion.
assert source.count('BORDER 1\nQV23 = 1')==1
source=source.replace('BORDER 1\nQV23 = 1','BORDER 0\nQV23 = 1')
old_help='QZPAOVER = PEEK(33030)\nOVER 1\nAT 0,12\nPRINT "_________"\nOVER QZPAOVER'
assert source.count(old_help)==1,'Help heading overlay changed'
source=source.replace(old_help,'LINE 96,9 TO 167,9')
# Draw below the first text row without modifying either heading glyphs.
old_inventory='PRINT "INVENTORY"\nOVER 1\nAT 0,12\nPRINT "_________"\nOVER 0'
assert source.count(old_inventory)==1,'Inventory heading overlay changed'
source=source.replace(old_inventory,'PRINT "INVENTORY"\nLINE 96,9 TO 167,9')
collision='IF POINT(((QV1 * 8) + 3),175-((((21 - QV4) * 8) + 4))) THEN'
assert source.count(collision)==1
# The X font's collision sample is blank on some levels. Test the whole
# middle bitmap row at the known lock coordinate, cleared only by use-key.
lock_guard='''IF (QV9 = 40) AND (QV1 = QA39((QV23-1)*3+1)) AND (QV4 = QA39((QV23-1)*3+2)) THEN
IF PEEK(17152 + FN QZFLOOR(QV4/8)*2048 + (QV4-FN QZFLOOR(QV4/8)*8)*32 + QV1) <> 0 THEN
QV1 = QV7
QV4 = QV8
GOTO QZRETURN
ENDIF
ENDIF
'''
source=source.replace('QL540:\n','QL540:\n'+lock_guard,1)
assert source.count('QR6:\nQL1450:')==1
source=source.replace('QR6:\nQL1450:','''QR6:
IF (QV35$ = "a") OR (QV35$ = "f") OR ((QA12(QV9) <> 0) AND (ABS(QV7-QV13) < 2) AND (ABS(QV8-QV14) < 2)) THEN
PAUSE 30
ENDIF
QL1450:''')
source=re.sub(r'PEEK\((33026|33028|33030|33099)\)',lambda m:'PEEK(%d)'%(int(m[1])-0x2500),source)
source='QZINTRO = USR(63491)\n'+source
source=re.sub(r'^(DIM .+)$',r'\1\nQZINTRO = USR(63488)',source,flags=re.M)
begin,end=source.index('QL3500:\n'),source.index('QR36:\n')
section=re.sub(r'^(NEXT .+)$',r'QZINTRO = USR(63488)\n\1',source[begin:end],flags=re.M)
source=source[:begin]+section+source[end:]
source=source.replace('PROC QZREAD(QZARG):\n','PROC QZREAD(QZARG):\nQZINTRO = USR(63488)\n',1)
source=source.replace('QR36:\n','QR36:\nQZINTRO = USR(63494)\nCLS\n',1)
old_exit='IF (QV35$ = "n") THEN\nEND\nENDIF'
assert source.count(old_exit)==1,'Play-again exit branch changed'
source=source.replace(old_exit,'IF (QV35$ = "n") THEN\nQZINTRO = USR(63497)\nENDIF',1)
source=native_crown_init.adapt(source)
(OUT/'startup.leap.bas').write_text(source)
conversion=json.loads((ROOT/'build/crown/converted.leap.conversion.json').read_text())
conversion['packed_data']=str(ROOT/'build/crown/converted.leap.data.bin')
(OUT/'startup.leap.conversion.json').write_text(json.dumps(conversion,indent=2)+'\n')
run(NODE,'scripts/leap_headless.mjs','compile',ROOT/'build/wide-host',OUT/'startup.leap.bas',OUT/'bytecode.json')
export=json.loads((OUT/'bytecode.json').read_text())
export['base']=0x8000
(OUT/'bytecode.json').write_text(json.dumps(export,indent=2)+'\n')
code=bytes.fromhex(export['code'])
assert len(code)<=0x3E00,(len(code),'code overlaps DATA cache')
assets=Path(export['packedData']).read_bytes()
init_tables=native_crown_init.tables(assets,export['symbols'])
# Static setup DATA is now in native tables. Keep the indexed offsets and
# glyphs, but compress the unused original setup records as zeros.
optimized=bytearray(assets)
for base,end in ((0,6698),(6867,6902),(13938,6570)):
    count=struct.unpack_from('<H',assets,base)[0]
    rows=[struct.unpack_from('<HH',assets,base+2+4*i) for i in range(count)]
    first=next(off for line,off in rows if line>=9200)
    optimized[base+first:base+end]=bytes(end-first)
assets=bytes(optimized)
(OUT/'native-packed-data.bin').write_bytes(assets)
export['packedData']=str(OUT/'native-packed-data.bin')
(OUT/'bytecode.json').write_text(json.dumps(export,indent=2)+'\n')
seq=build_sequence()
frames=[ECMFrame((seq/f'frame_{i:05d}.pix').read_bytes(),(seq/f'frame_{i:05d}.atr').read_bytes()) for i in range(8)]
raws={'game-code':code,'key-bitmap':frames[0].bitmap,'key-attributes':frames[0].attributes}
raws.update(init_tables)
raws.update({f'data-{i//512:02d}':assets[i:i+512] for i in range(0,len(assets),512)})
for name,raw in raws.items(): (OUT/(name+'.raw')).write_bytes(raw)
# Compress and independently round-trip every resource with the upstream tools.
commands=[]
for name in raws:
    if (OUT/(name+'.check')).exists() and (OUT/(name+'.zx0')).exists() and (OUT/(name+'.check')).read_bytes()==raws[name]:
        continue
    a=wslpath(OUT/(name+'.raw')); b=wslpath(OUT/(name+'.zx0')); c=wslpath(OUT/(name+'.check'))
    commands.append(f'"{wslpath(ROOT/"tools/ZX0/zx0")}" -f "{a}" "{b}" >/dev/null && "{wslpath(ROOT/"tools/ZX0/dzx0")}" -f "{b}" "{c}" >/dev/null')
if commands:
    compression_script=OUT/'compress-resources.sh'
    compression_script.write_text('set -e\n'+'\n'.join(commands)+'\n', encoding='utf-8', newline='\n')
    run('wsl','--exec','bash',wslpath(compression_script))
resources={name:(OUT/(name+'.zx0')).read_bytes() for name in raws}
assert all((OUT/(name+'.check')).read_bytes()==raw for name,raw in raws.items())
for i in range(1,9):
    previous,current=frames[i-1],frames[i%8]
    payload=b''.join(encode_hybrid_plane(before[offset:offset+512],after[offset:offset+512])
                     for offset in range(0,6144,512)
                     for before,after in ((previous.bitmap,current.bitmap),(previous.attributes,current.attributes)))
    resources[f'frame-{i%8}']=payload
stats={'code_raw':len(code),'code_zx0':len(resources['game-code']),
       'assets_raw':len(assets),'assets_zx0':sum(len(v) for k,v in resources.items() if k.startswith('data-')),
       'animation_bytes':sum(len(v) for k,v in resources.items() if k.startswith(('key-','frame-'))),
       'resource_bytes':sum(map(len,resources.values()))}
(OUT/'compression.json').write_text(json.dumps(stats,indent=2)+'\n')
print(json.dumps(stats,indent=2),flush=True)
if '--measure' in sys.argv: sys.exit(0)
# The assembly/packing stages below use byte offsets in the physical ROM as
# stream pointers. Reads restore the HOME mapping before touching the stack.
S=load_symbols(RUNTIME/'build/test_basic.sym')
E=load_symbols(RUNTIME/'build/exrom.sym')
main=(RUNTIME/'v2_home.bin').read_bytes()
service=(RUNTIME/'v2_exrom.bin').read_bytes()
native_base=(E['EXROM_RUNTIME_END']+15)&~15
equs=''.join(f'{k} EQU ${v:04X}\n' for k,v in (S | {k:v for k,v in E.items() if k not in S}).items() if '.' not in k)
# Generated resource directory is patched after measuring the native program.
directory='asset_table:\n'+'    DW 0\n'*len([k for k in resources if k.startswith('data-')])
directory+='ni_item_resource:\n    DW 0\nni_level_resources:\n'+'    DW 0\n'*3
directory+='ni_glyph_resources:\n'+'    DW 0\n'*3
directory+='frame_table:\n'+'    DW 0\n'*8
config=f'''    DEVICE NOSLOT64K
    ORG ${native_base:04X}
KEY_PIX EQU 0
KEY_ATR EQU 0
CODE_SRC EQU 0
RESUME_IP EQU ${0x8000+next(s['offset'] for s in export['symbols'] if s['name']=='QR36'):04X}
CODE_BYTES EQU {len(code)}
COUNT_BYTES: ; symbol-counts are embedded below in boot initialization
'''
font={'p':['110','101','110','100','100'],'r':['110','101','110','101','101'],
      'e':['111','100','110','100','111'],'s':['111','100','111','001','111'],
      'a':['010','101','111','101','101'],'n':['101','111','111','111','101'],
      'y':['101','101','010','010','010'],'k':['101','101','110','101','101'],
      ' ':['000']*5}
prompt=bytearray()
prompt_rows=[]
for text,y in [('press',179),('any key',185)]:
    for row in range(5):
        width=4*len(text)-1
        letters=''.join(font[c][row]+'0' for c in text)[:width]
        bits=letters.center(40,'0')
        prompt.extend(int(bits[i:i+8],2) for i in range(0,40,8))
        yy=y+row
        prompt_rows.append(0x4000+((yy&0xC0)<<5)+((yy&7)<<8)+((yy&0x38)<<2)+27)
(OUT/'prompt.pixels').write_bytes(prompt)
(OUT/'prompt_rows.inc').write_text('    DW '+','.join(f'${a:04X}' for a in prompt_rows)+'\n')
native=(ROOT/'assets/intro/combined_native.asm').read_text()
native+=native_crown_init.equs(export['symbols'])+(ROOT/'assets/intro/native_initializer.asm').read_text()
native=native.replace('; COUNTS_PLACEHOLDER','    DB '+','.join(map(str,export['counts'])))
zx=(ROOT/'tools/ZX0/z80/dzx0_standard.asm').read_text()
zx=zx.replace('        ldir                            ; copy literals','        call zx_literals')
zx=zx.replace('        ld      c, (hl)                 ; obtain offset LSB\n        inc     hl', '        push af\n        call stream_get\n        ld c,a\n        pop af')
zx=zx.replace('        ld      a, (hl)                 ; load another group of 8 bits\n        inc     hl','        call stream_get')
zx+='''
zx_literals:
    push af
.loop:
    call stream_get
    ld (de),a
    inc de
    dec bc
    ld a,b
    or c
    jr nz,.loop
    pop af
    ret
'''
(OUT/'native.asm').write_text(equs+config+native+'\n'+zx+'\n'+directory+'\nnative_end:\n    ASSERT $ <= $3FF0\n    SAVEBIN "native.bin",'+f'${native_base:04X},native_end-${native_base:04X}\n')
assembler=wslpath(ROOT/'tools/sjasmplus/sjasmplus')
run('wsl','--exec','bash','-c','cd "$1" && "$2" --sym=intro.sym native.asm','crown-build',wslpath(OUT),assembler)
N=load_symbols(OUT/'intro.sym')
image=bytearray([255])*65536
image[:S['HOME_RUNTIME_END']]=main[:S['HOME_RUNTIME_END']]
image[0x3ff0:0x3ffa]=main[0x3ff0:0x3ffa]
image[0x2800:E['EXROM_RUNTIME_END']]=service[:E['EXROM_RUNTIME_END']-0x2800]
assert S['HOME_RUNTIME_END']<=0x2800
# Boot is in chunk 4. All resources can cross physical bank boundaries.
free=[(S['HOME_RUNTIME_END'],0x2800),(N['native_end'],0x3ff0),(0x4000,0x8000),(0x8080,0x10000)]
spans=[]
addresses={}
# Largest changes decode directly from safe banks with no byte-reader calls.
# Each direct stream stays within one bank; other streams use a RAM buffer.
bank_ranges=[(0x8080,0xA000),(0xA000,0xC000),(0xC000,0xE000)]
buffered_name='frame-4'
fast_names=sorted((f'frame-{i}' for i in range(1,8) if f'frame-{i}'!=buffered_name),key=lambda n:len(resources[n]),reverse=True)
groups=[[],[],[]]
remaining=[b-a for a,b in bank_ranges]
def assign_fast(index):
    if index==len(fast_names): return True
    name=fast_names[index];size=len(resources[name])
    for bank in range(3):
        if remaining[bank]<size: continue
        remaining[bank]-=size;groups[bank].append(name)
        if assign_fast(index+1): return True
        groups[bank].pop();remaining[bank]+=size
    return False
assert assign_fast(0),'Direct-animation streams exceed the three safe banks'
fast_banks=[(start,end,names) for (start,end),names in zip(bank_ranges,groups)]
free=free[:3]
for start,end,names in fast_banks:
    for name in names:
        data=resources[name]
        assert start+len(data)<=end
        addresses[name]=start;image[start:start+len(data)]=data
        spans.append((name,start,len(data)));start+=len(data)
    free.append((start,end))
free.append((0xE000,0x10000))
# Keep the key planes and the remaining substantial buffered delta away from
# chunk 7, whose stack/cache overlap requires the slower far-byte reader.
start,end=free[2]
for name in ('key-bitmap','key-attributes',buffered_name):
    data=resources[name]
    assert start+len(data)<=end
    addresses[name]=start;image[start:start+len(data)]=data
    spans.append((name,start,len(data)));start+=len(data)
free[2]=(start,end)
for name,data in sorted(resources.items(),key=lambda pair:len(pair[1]),reverse=True):
    if name in addresses: continue
    # Keep each stream contiguous; a stream may cross the chunk-4 boot hole
    # only by starting above it. Avoid arbitrary per-resource padding.
    for i,(start,end) in sorted(enumerate(free),key=lambda pair:pair[1][1]-pair[1][0]):
        if end-start>=len(data):
            addresses[name]=start;image[start:start+len(data)]=data
            free[i]=(start+len(data),end);spans.append((name,start,len(data)));break
    else: raise ValueError(f'64KB overflow placing {name} ({len(data)} bytes); remaining {free}')
text=(OUT/'native.asm').read_text()
for key,name in [('KEY_PIX','key-bitmap'),('KEY_ATR','key-attributes'),('CODE_SRC','game-code')]:
    text=text.replace(f'{key} EQU 0',f'{key} EQU ${addresses[name]:04X}')
rows='asset_table:\n'+''.join(f'    DW ${addresses[k]:04X}\n' for k in raws if k.startswith('data-'))
rows+='ni_item_resource:\n'+f'    DW ${addresses["init-items"]:04X}\nni_level_resources:\n'+''.join(f'    DW ${addresses[f"init-level-{i}"]:04X}\n' for i in range(1,4))
rows+='ni_glyph_resources:\n'+''.join(f'    DW ${addresses[f"init-glyph-{i}"]:04X}\n' for i in range(1,4))
rows+='frame_table:\n'+''.join(f'    DW ${addresses[f"frame-{i}"]:04X}\n' for i in range(8))
text=text.replace(directory,rows)
text=text.replace('; COUNTS_PLACEHOLDER','    DB '+','.join(map(str,export['counts'])))
(OUT/'native.asm').write_text(text)
run('wsl','--exec','bash','-c','cd "$1" && "$2" --sym=intro.sym native.asm','crown-build',wslpath(OUT),assembler)
image[native_base:N['native_end']]=(OUT/'native.bin').read_bytes()
boot=f'''    DEVICE NOSLOT64K
    ORG $8000
    DB 2,2,8,$80,$EF,1,0,0
    di
    ld sp,$FF00
    xor a
    out ($FF),a
    ld hl,stub
    ld de,$F600
    ld bc,stub_end-stub
    ldir
    jp $F600
stub:
    DISP $F600
    ld a,3
    out ($F4),a
    jp ${N['boot_init']:04X}
    ENT
stub_end:
    ASSERT $ <= $8080
    SAVEBIN "boot.bin",$8000,$80
'''
(OUT/'boot.asm').write_text(boot)
run('wsl','--exec','bash','-c','cd "$1" && "$2" boot.asm','crown-build',wslpath(OUT),assembler)
image[0x8000:0x8080]=(OUT/'boot.bin').read_bytes()
from dck_format import build_dck,parse_dck,flat_image
dck=build_dck([2]*8,{i:bytes(image[i*8192:(i+1)*8192]) for i in range(8)})
assert flat_image(parse_dck(dck))==image and len(image)==65536
(OUT/'program.bin').write_bytes(image);(OUT/'program.dck').write_bytes(dck)
for name,start,length in spans:
    assert image[start:start+length]==resources[name],name
for name in ('stock-home.rom','stock-exrom.rom'):
    (OUT/name).write_bytes((ROOT/'build/crown'/name).read_bytes())
used=S['HOME_RUNTIME_END']+E['EXROM_RUNTIME_END']-0x2800+len((OUT/'native.bin').read_bytes())+10+128+sum(map(len,resources.values()))
manifest={'format':'TS2068 DOCK/AROS','physical_bytes':65536,'used_bytes':used,'free_bytes':65536-used,
          'leap_release':'v2.0.2-emu.1','leap_revision':'77f1baaf30424f2cec8cf31cae90513faa9c45c5',
          'runtime_variant':'combined-runtime','bytecode_base':0x8000,'code_bytes':len(code),
          'packed_asset_bytes':len(assets),'compression':stats,'stock_home_exrom':True,
          'startup_intro':{'frames':8,'mode':'ECM','display_size':[256,192],'fps':5,'ready_address':0xFAC3,'refresh_address':0xFAC6,'active_address':0xFAC0,
                           'ready_prompt':'PRESS\nANY KEY','prompt_position':[216,179],'prompt_font':'3x5, centered on two lines beside Brian Walker','background_init':'cooperative USR ticks'},
          'rom_resources':[{'name':n,'address':a,'bytes':b} for n,a,b in spans],
          'sha256':hashlib.sha256(image).hexdigest(),'status':'built; validation pending'}
(OUT/'ZX0-LICENSE.txt').write_bytes((ROOT/'tools/ZX0/LICENSE').read_bytes())
manifest['zx0_revision']='ecde3a2ae05061fe06469ed46df81a33b7de7d86'
manifest['animation_sequence']=str(seq)
manifest['animation_stability']=json.loads((seq.parent/'stability.json').read_text())
manifest['startup_intro']['ready_prompt_colour']='red ink (2) on black paper'
manifest['startup_intro']['black_attribute_staging']=True
manifest['ram_layout']={'display':'4000-57FF and 6000-77FF','system':'5B00-5D59','bytecode':'8000-BFFF (ends below BE00)',
                        'data_cache':'BE00-BFFF','vm_workspace':'C000-C9FF','arena':'CA00-F0FF','udg':'F180',
                        'stream_buffer':'F900-F9FF','intro_state':'FAC0-FAED','stack':'below FF00'}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'64KB combined cartridge: {used} used, {65536-used} free',flush=True)
for mode,name,extra in [('startup','startup-execution.json',()),('startup','startup-held-key.json',('--held-key',)),('game','gameplay.json',())]:
    run(NODE,'scripts/leap_headless.mjs',mode,RUNTIME,OUT/'program.dck',OUT/name,*extra)
run(sys.executable,'scripts/verify_combined_intro_fuse.py')
run(sys.executable,'scripts/verify_crown_fuse.py','--combined')
run(sys.executable,'scripts/verify_warm_intro_fuse.py')
startup=json.loads((OUT/'startup-execution.json').read_text())
manifest['status']='TSRun and Fuse verified combined cartridge'
manifest['play_again_no']='Return to full intro immediately using a saved fresh-game snapshot; no full initialization'
manifest['verification']='Stock-ROM boot, exact decoded frames and DATA, cooperative initialization, fresh/held-key gate, ECM prompt, normal-mode handoff and three-level gameplay passed; Fuse independently verified ECM samples, prompt and player redraws. Physical hardware untested.'
manifest['initialization_ms']=startup['initializationMs']
manifest['native_initializer']={'implementation':'Z80 array clearing, fixed DATA tables, randomized loot/creatures and character-set loading','previous_startup_ms':30900.412981859412,'startup_ms':startup['initializationMs'],'randomization':'Live Leap LFSR, integer ranges; no saved fixed dungeon','checks':startup.get('nativeChecks'),'scratch':'FAEE-FAF4','verification_report':'native-randomization.json'}
manifest['startup_intro']['update_format']='12 paired 512-byte bitmap/attribute blocks; no whole-plane colour delay'
manifest['startup_intro']['maximum_pair_ms']=startup['maximumPairMs']
gameplay=json.loads((OUT/'gameplay.json').read_text())
manifest['warm_return_ms']=gameplay['warmIntro']['returnMs']
manifest['verification']+=' Warm return from replay N and small two-line prompt also passed in both emulators.'
manifest['fresh_game_snapshot_bytes']=gameplay['warmIntro']['snapshotBytes']
manifest['startup_intro']['target_fps']=manifest['startup_intro'].pop('fps')
manifest['startup_intro']['decode_ms_by_phase']={i:round(sum(v['ms'] for v in startup['decodeTimes'] if v['phase']==i)/sum(v['phase']==i for v in startup['decodeTimes']),2) for i in range(8)}
manifest['startup_intro']['cadence_note']='Nominal 12-interrupt spacing. One substantial delta uses buffered reads; measured decoder times are recorded by phase. Cooperative callbacks can add delay during game initialization.'
manifest['animation_cpu_fraction_during_initialization']=sum(v['ms'] for v in startup['decodeTimes'][:startup['refreshWhileInitializing']])/startup['initializationMs']
preview=[]
for frame in frames:
    bitmap=bytearray(frame.bitmap);attrs=bytearray(frame.attributes)
    for row,address in enumerate(prompt_rows):
        offset=address-0x4000
        bitmap[offset:offset+5]=prompt[row*5:row*5+5]
        attrs[offset:offset+5]=bytes([2])*5
    preview.append(ECMFrame(bytes(bitmap),bytes(attrs)).render().resize((768,576),Image.Resampling.NEAREST))
palette=preview[0].quantize(colors=256)
indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in preview]
indexed[0].save(OUT/'intro-preview.gif',save_all=True,append_images=indexed[1:],duration=200,loop=0,optimize=False,disposal=1)
manifest['intro_preview']='intro-preview.gif'
capture=(OUT/'startup-ready.ecm').read_bytes()
ready_image=ECMFrame(capture[:6144],capture[6144:]).render()
ready_image.resize((768,576),Image.Resampling.NEAREST).save(OUT/'startup-ready.png')
ready_image.crop((160,170,256,192)).resize((768,176),Image.Resampling.NEAREST).save(OUT/'prompt-closeup.png')
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
