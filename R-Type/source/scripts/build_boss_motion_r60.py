"""r60: terrain-safe shared boss phases, native-size arcade walkers, fewer L5 spheres."""
from pathlib import Path
import json,subprocess,re,hashlib,numpy as np
from boss_motion_assets_r60 import decode,phases,pack,unpack,SELECT,PALETTE
from build_rocket_fix import code
from native_lifetimes_r60 import protected_native,publisher,patch_calls
import build_l5_effects_fast as l5
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'build/fullgame/l5_effects_fast_r59';OUT=ROOT/'build/fullgame/boss_motion_r60'
SELECT={1:[21,22,23,24,25,201,202,203,204],**SELECT,3:list(range(101,107))}
ART_OVERRIDES={}
PLANS={1:0xd1c9,2:0xc4f2,3:0xdc71,4:0xc9c7,6:0xe740,7:0xceb1,8:0xf380}
def main():
 l5.OUT=OUT;l5.main();records=[];compat=[]
 def asm(name,source):
  p=OUT/(name+'.asm');p.write_text(source);r=subprocess.run([str(ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert r.returncode==0 and 'warning:'not in r.stderr.lower(),r.stdout+r.stderr;sy={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};return p.with_suffix('.bin').read_bytes(),sy
 def cache_defs(**kw):return ''.join(f'{k} EQU ${v:04X}\n'for k,v in kw.items())
 dummy=dict(PLAN_READ=0xa450,PLAN_EMPTY=0xa470,PLAN_VISIBLE=0xa480,SYNTH_ENTRY=0xa400,PRELOAD_TABLE=0x2400,MOTION_PTR=0x2800,MOTION_BYTES=0x400,WARMUP_ENTRY=0xa100)
 cache,cs=asm('generic_cache',cache_defs(**dummy)+(ROOT/'src/boss_cell_plans_r60.asm').read_text())
 for n,ids in SELECT.items():
  original=(BASE/f'level{n:02d}_region.bin').read_bytes();b=bytearray(original);payload=bytearray();addresses={};raw_assets={};spec=[];maxplan=0
  if n==4:
   for target in range(64):
    p,q=target>>3,target&7;codes=[]
    for source in range(64):
     v=[int((p==0 and c!=0)or(((PALETTE[c]-PALETTE[q])**2).sum()<((PALETTE[c]-PALETTE[p])**2).sum()))for c in [source>>3,source&7]];codes.append(3 if v==[1,1]else 0 if v==[0,0]else 1 if v==[0,1]else 2)
    payload.extend(sum(codes[j+k]<<(k*2)for k in range(4))for j in range(0,64,4))
  def add(raw):
   packed=pack(raw);assert unpack(packed)==bytes(raw)
   if packed not in addresses:addresses[packed]=0x2400+len(payload);payload.extend(packed)
   return addresses[packed]
  for ident in ids:
   im=np.load(ART_OVERRIDES.get(ident,ROOT/f'build/graphics/enemy_upgrades_r60/{ident}.npy'))if n==1 else decode(n,ident)[0];h,w=im.shape;raws=phases(im);ptrs=[]
   for phase,raw in enumerate(raws):(OUT/f'L{n}_sprite{ident}_phase{phase}.bin').write_bytes(raw)
   for phase in range(4):
    raw=raws[0 if n in[1,4]else phase];ptr=add(raw);raw_assets[ptr]=raw;ptrs.append(ptr)
   maxplan=max(maxplan,(w//8+1)*(h//8+1)*9);spec.append(dict(id=ident,size=[w,h],phase_ptrs=ptrs))
  raw_bytes=sum(map(len,raw_assets.values()));preloaded=raw_bytes<=0x1800;raw_ptrs={};destination=0xc000
  if preloaded:
   for ptr,raw in raw_assets.items():raw_ptrs[ptr]=destination;destination+=len(raw)
  table=bytearray()
  for sprite in spec:
   sprite['render_ptrs']=[raw_ptrs[p]for p in sprite['phase_ptrs']]if preloaded else sprite['phase_ptrs'];w,h=sprite['size'];table.extend(bytes([sprite['id'],w//8,h//8])+b''.join(p.to_bytes(2,'little')for p in sprite['render_ptrs']))
  table.append(0);assert len(table)<=0x80
  start=PLANS[n];finish=start+maxplan;native=bytes(0xc000)+original[0xa000:0xe000];backup=native[start:finish];backup_ptr=add(backup)if start>=0xe000 else 0
  preload_table=0x2400+len(payload)
  if preloaded:
   payload.append(len(raw_assets))
   for ptr in raw_assets:payload.extend(ptr.to_bytes(2,'little')+raw_ptrs[ptr].to_bytes(2,'little'))
  defines=cache_defs(MULTIPART_KEYS=int(n==4),PRELOADED=int(preloaded),PRELOAD_ENTRY=cs['preload'],RESTORE_PACKED=cs['restore_packed'],NO_SMOOTH=int(n==1),SYNTH_MODE=2 if n==4 else 0,PLAN_BYTES=maxplan,PREPARE_CELLS=cs['prepare_cells'],DECOMPRESS=cs['decompress'],PLAN_START=start,BACKUP_PTR=backup_ptr)
  motion,ms=asm(f'L{n}_motion',defines+(ROOT/'src/boss_phase_motion_r60.asm').read_text())
  shader_start=0xa000+len(motion);shader=(ROOT/'src/bellmite_interruptible.asm').read_text().replace('ORG $88EB',f'ORG ${shader_start:04X}').replace('LD DE,$EFA1',f'LD DE,${start:04X}',1).replace('LD DE,$F5A1',f'LD DE,${finish:04X}',1)
  a=shader.index('        ; Unowned core cells');z=shader.index('ours:',a);shader=shader[:a]+shader[z:]
  a=shader.index('        LD IX,0\n');z=shader.index('        LD A,($5C81)',a);shader=shader[:a]+shader[z:]
  a=shader.index('owner_done:');z=shader.index('visible_source:',a);shader=shader[:a]+'owner_done:\n'+shader[z:]
  a=shader.index('        CALL $01C8');z=shader.index('start_copy:',a);shader=shader[:a]+f'        LD A,$69\n        OUT ($F4),A\n        CALL ${cs["select_cache"]:04X}\n        LD (cache),HL\n        LD (reverse_y),A\n'+shader[z:]
  a=shader.index('        LD A,$1F',shader.index('start_copy:'));z=shader.index('        EI',a);shader=shader[:a]+'        LD A,$6F\n        LD HL,(cache)\n        OUT ($F4),A\n'+shader[z:]
  shader=shader.replace('LD A,$19','LD A,$29').replace('        CALL $097B ; restore normal vector and title source byte','        LD A,$84\n        LD I,A')
  a=shader.index('reject_core:');z=shader.index('reject:',a);shader=shader[:a]+shader[z:];shader=shader.replace('core_src: DW 0\n','').replace('caller: DB 0\n','').replace('ASSERT $ <= $8BF0','ASSERT $ <= $A4AE')
  paint,ss=asm(f'L{n}_compositor',shader)
  helper_start=shader_start+len(paint)
  helper=f'''        ORG ${helper_start:04X}
plan_read:
        LD A,$29
        OUT ($F4),A
        INC HL
        LD E,(HL)
        INC HL
        LD D,(HL)
        INC HL
        LD C,(HL)
        EX DE,HL
        LD A,$69
        OUT ($F4),A
        RET
plan_empty:
        DI
        LD A,$2F
        OUT ($F4),A
        LD (IX),54
        INC IX
        LD A,$6F
        OUT ($F4),A
        EI
        RET
plan_visible:
        DI
        LD A,$2F
        OUT ($F4),A
        LD (IX),0
        LD (IX+1),L
        LD (IX+2),H
        LD (IX+3),C
        LD DE,9
        ADD IX,DE
        LD A,$6F
        OUT ($F4),A
        EI
        RET
'''
  synth_extra=b'';synth_high=b''
  if n==4:
   text=(ROOT/'src/boss_l4_preshift_r60.asm').read_text();a=text.index('synth_row:');cut=text.index('        LD A,(height)',a);mid=text.index('coverage:');end=text.index('mapped:');equ=text[text.index('phase_x EQU'):];equ=equ[:equ.index('synth_phase EQU')]+equ[equ.index('synth_phase EQU'):]
   # Mapped is the stable bank6 helper; main body resides above its mode fields.
   synth_source=f'        ORG $DF50\nsynth_body:\n'+text[cut:mid]+'        ASSERT $ <= $E000\n'+equ+f'coverage EQU $1111\nmerge EQU $2222\nmapped EQU ${cs["mapped"]:04X}\n'
   entry=text[a:cut]+'        JP $DF50\n'+text[mid:end]
   # Assemble a combined prefix to resolve the small entry/coverage helper addresses.
   helpers,hs=asm('L4_plan_helpers',helper+entry+equ+f'synth_unshifted EQU $3333\nmapped EQU ${cs["mapped"]:04X}\n        ASSERT $ <= $A4AE\n')
   synth_source=synth_source.replace('$1111',f'${hs["coverage"]:04X}').replace('$2222',f'${hs["merge"]:04X}');synth_high,sy=asm('L4_synth_high',synth_source)
   helpers,hs=asm('L4_plan_helpers',helper+entry+equ+f'synth_unshifted EQU ${sy["synth_unshifted"]:04X}\nmapped EQU ${cs["mapped"]:04X}\n        ASSERT $ <= $A4AE\n')
  else:helpers,hs=asm(f'L{n}_plan_helpers',helper+'        ASSERT $ <= $A4AE\n')
  image=motion+paint+helpers;assert len(image)<=0x4ae
  motion_ptr=(0x2400+len(payload)+15)&~15;assert motion_ptr+len(image)<= (0x3000 if n==1 else 0x3fe0),(n,len(payload),len(image))
  final_defs=cache_defs(PLAN_READ=hs['plan_read'],PLAN_EMPTY=hs['plan_empty'],PLAN_VISIBLE=hs['plan_visible'],SYNTH_ENTRY=hs.get('synth_row',0),PRELOAD_TABLE=preload_table,MOTION_PTR=motion_ptr,MOTION_BYTES=len(image),WARMUP_ENTRY=ms['warmup'])
  cache,check=asm(f'L{n}_cache',final_defs+(ROOT/'src/boss_cell_plans_r60.asm').read_text());assert all(check[k]==cs[k]for k in ['prepare_cells','select_cache','decompress','preload','install_motion','mapped'])
  b[0x2400:0x3fe0]=bytes(7136);b[0x2400:0x2400+len(payload)]=payload;b[motion_ptr:motion_ptr+len(image)]=image;b[0xdc50:0xe000]=bytes(944);b[0xdc50:0xdc50+len(cache)]=cache
  if n==4:b[0xdf50:0xdf50+len(synth_high)]=synth_high
  b[0xe000:0xe400]=bytes(1024);tags=json.loads((BASE/'global_tags.json').read_text());old=(ROOT/f'build/fullgame/shot_sequence_r57/level{n:02d}_region.bin').read_bytes()
  for ptr in map(int,tags):b[0xe000+(ptr-0xa600)//8]=old[0x2000+(ptr&8191)]
  b[0xe2d0:0xe350]=bytes([255])*128;b[0xe350:0xe350+len(table)]=table
  gate=(OUT/'phase_gate.asm').read_text();gate=re.sub(r'RESTORE_ENTRY EQU \$[0-9A-Fa-f]+',f'RESTORE_ENTRY EQU ${ms["restore_sources"]:04X}',gate).replace('LD A,$59','LD A,$69').replace('        LD A,$19\n        OUT ($F4),A\n        CALL $88EB','        CALL $09FC\n        NOP\n        NOP\n        NOP\n        NOP');v,_=asm(f'L{n}_gate',gate);b[0xd00:0xd00+len(v)]=v
  warm=(OUT/'warmup.asm').read_text();warm=re.sub(r'WARMUP_ENTRY EQU \$[0-9A-Fa-f]+',f'WARMUP_ENTRY EQU ${cs["install_motion"]:04X}',warm).replace('LD A,$59','LD A,$49');v,_=asm(f'L{n}_warmup',warm);b[0xdc0:0xdc0+len(v)]=v
  b[0x19fc:0x19ff]=bytes.fromhex('c3 27 0d');b[0xee1:0xeec]=bytes.fromhex('f3 32 e4 5b 3e 69 d3 f4 c3 00 a0');b[0x14f4:0x14f8]=bytes.fromhex('f3 c3 2f 0d');b[0xd2f:0xd40]=(BASE/'level05_region.bin').read_bytes()[0xd2f:0xd40]
  b[0x9fc:0xa06]=bytes.fromhex('3e 29 d3 f4 c3')+shader_start.to_bytes(2,'little')+bytes(3)
  for at,file in [(0x1a6e,'boss_copy_fast'),(0xf57,'boss_copy_reverse'),(0xfc3,'boss_copy_flash')]:
   v,_=asm(f'L{n}_{file}',cache_defs(FLASH=ss['flash'],REVERSE_Y=ss['reverse_y'])+(ROOT/f'src/{file}.asm').read_text());b[at:at+len(v)]=v
  visibility=(ROOT/'src/l5_plan_visibility.asm').read_text();a=visibility.index('        CP $80');z=visibility.index('metadata_ready:',a);visibility=visibility[:a]+'        LD A,(DE)\n'+visibility[z:];v,_=asm(f'L{n}_visibility',cache_defs(SCREEN_X=cs['screen_x'],SCREEN_Y=cs['screen_y'])+visibility);b[0x80:0x80+len(v)]=v
  publisher(b);compat.append(dict(level=n,changes=protected_native(b)));(OUT/f'level{n:02d}_region.bin').write_bytes(b)
  if n==1:
   boot=bytearray((BASE/'boot_region.bin').read_bytes())
   for at,(x,y)in enumerate(zip(original,b)):
    if x!=y:boot[at]=y
   boot[0x2000:0x4000]=b[0x2000:0x4000];oldboot=(BASE/'boot_region.bin').read_bytes();workspace=bytearray(oldboot[0x2000:0x4000]);patch_calls(workspace,[(0x1000,0x1800)]);packed=pack(workspace);assert len(packed)<=0xbe0;boot[0x3400:0x3400+len(packed)]=packed
   tail=bytearray(oldboot[0xdc50:0xe000]);tail[0xb8:0xbf]=bytes.fromhex('cd fc 09 00 00 00 00');patch_calls(tail,[(0,len(tail))]);boot[0x3000:0x33b0]=tail
   for ptr in map(int,tags):
    at=ptr-0xa000+0x6000;tag=boot[at]
    for y in range(8):
     if not(tag&56)and boot[at+1+y]==255:boot[at+1+y]=0xaa if y&1 else 0x55
   low,_=asm('boot_native_tail',cache_defs(DECOMPRESS=cs['decompress'],INSTALL=cs['install_motion'])+'''        ORG $00D4
        LD A,$5B
        OUT ($F4),A
        LD HL,$3400
        LD DE,$6000
        CALL DECOMPRESS
        LD HL,$3000
        LD DE,$FC50
        LD BC,$03B0
        LDIR
        CALL INSTALL
        LD A,$11
        OUT ($F4),A
        JP $8170
        ASSERT $ <= $00F7
''');boot[0xd4:0xd4+len(low)]=low;at=bytes(boot).find(bytes.fromhex('3e 1a d3 f4'),0x8000,0x8170);assert at>=0;boot[at:at+7]=bytes.fromhex('3e 11 d3 f4 c3 d4 00');boot[0xdba7:0xdbab]=bytes.fromhex('f5 c3 01 0d');protected_native(boot);(OUT/'boot_region.bin').write_bytes(boot)
  records.append(dict(level=n,plan_start=start,plan_end=finish,backup_ptr=backup_ptr,backup=backup.hex(),preloaded=preloaded,raw_cache_bytes=raw_bytes if preloaded else 0,motion_ptr=motion_ptr,motion_image_bytes=len(image),phase_bytes=len(payload),sprites=spec,cache_symbols=check,shader_start=shader_start));print('L',n,'phase',len(payload),'code',len(image),'raw',raw_bytes,'preload',preloaded,flush=True)
 # L5 retains its tested r59 data layout and renderer; only its sphere activation and shared publisher change.
 b=bytearray((OUT/'level05_region.bin').read_bytes())
 # Sphere actors originate in the native event stream, not the E641 homing-SFX table.
 mem=bytes(0xc000)+bytes(b[0xa000:0xe000]);start=int.from_bytes(mem[0xc4b4:0xc4b6],'little');at=start;events=[];sphere=0
 while mem[at]!=255:
  event=mem[at:at+5]
  if event[0]==73 and event[2]==35:
   keep=sphere%2==0;sphere+=1
  else:keep=True
  if keep:events.append(event)
  at+=5
 assert sphere==24
 physical=start-0x2000;stream=b''.join(events)+bytes([255]);b[physical:at-0x2000+1]=stream+bytes([255])*(at-start+1-len(stream))
 publisher(b);b[0x9fc:0xa06]=bytes.fromhex('3e 19 d3 f4 c3 eb 88')+bytes(3);b[0xd0f:0xd16]=bytes.fromhex('cd fc 09 00 00 00 00')if False else b[0xd0f:0xd16];protected_native(b);(OUT/'level05_region.bin').write_bytes(b)
 for name,n in [('boot',0)]+[(f'level{i:02d}',i)for i in range(1,9)]:
  data=(OUT/f'{name}_region.bin').read_bytes();tap='RTBOOT.TAP'if n==0 else f'LEVEL{n:02d}.TAP';(OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{p:02X}',data[p*8192:(p+1)*8192],p)for p in range(8)))
 (OUT/'generic_manifest.json').write_text(json.dumps(records,indent=2));(OUT/'native_compatibility.json').write_text(json.dumps(compat,indent=2))
if __name__=='__main__':main()
