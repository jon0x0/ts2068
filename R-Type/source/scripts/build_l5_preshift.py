"""Experimental L5 sub-cell motion, derived from frozen r57. No reference edits."""
from pathlib import Path
import numpy as np,json,shutil,subprocess,hashlib,re
from build_rocket_fix import code
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'build/fullgame/shot_sequence_r57';OUT=ROOT/'build/fullgame/l5_preshift_r58'
PAL=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)])
def assets(b):
 core=np.zeros((80,80),np.uint8);p=0xcfa1
 for cy in range(10):
  for cx in range(10):
   tag=b[p];p+=1
   if tag==54:continue
   for y in range(8):
    a=b[0x2000+(tag&127)*8+y];bits=b[p+y]
    core[cy*8+y,cx*8:cx*8+8]=[(a&7)if bits&(128>>x)else(a>>3)&7 for x in range(8)]
   p+=8
 spheres=[]
 for cel in range(3):
  im=np.zeros((24,24),np.uint8)
  for cy in range(3):
   for cx in range(3):
    for y in range(8):
     q=0x8c00+(cel*16+cy*3+cx)*16+y*2;bits,a=b[q:q+2]
     im[cy*8+y,cx*8:cx*8+8]=[(a&7)if bits&(128>>x)else(a>>3)&7 for x in range(8)]
  spheres.append(im)
 def phases(im):
  h,w=im.shape;result=bytearray();reports=[]
  for shift in [0,2,4,6]:
   dst=np.zeros((h,w+8),np.uint8);dst[:,shift:shift+w]=im
   fitted=np.zeros_like(dst)
   # Column-major continuous rasters permit cheap vertical pointer relocation.
   for cx in range(w//8+1):
    for y in range(h):
     row=dst[y,cx*8:cx*8+8];colors=set(map(int,row));best=None
     if len(colors)<=2:
      cols=sorted(colors);paper=0 if 0 in cols else cols[0];ink=next((c for c in cols if c!=paper),paper);bits=sum((128>>x)for x,c in enumerate(row)if c==ink and ink!=paper)
     else:
      for paper in range(8):
       for ink in range(paper+1,8):
        if 0 in colors and paper!=0:continue
        costs=((PAL[row,None,:]-PAL[[paper,ink]][None,:,:])**2).sum(2);sel=costs.argmin(1)
        if paper==0:sel[row!=0]=1
        err=costs[np.arange(8),sel].sum()
        if best is None or err<best[0]:best=(err,paper,ink,sel)
      _,paper,ink,sel=best;bits=sum((128>>x)for x,c in enumerate(sel)if c)
     result.extend([bits,paper*8+ink]);fitted[y,cx*8:cx*8+8]=[ink if bits&(128>>x)else paper for x in range(8)]
   assert np.array_equal(fitted!=0,dst!=0),'Phase fitting changed silhouette'
   reports.append(dict(phase=shift,changed_colours=int(np.sum(fitted!=dst)),nonblack_pixels=int(np.sum(dst!=0))))
  return bytes(result),reports
 raw,cr=phases(core);sphere=bytearray();sr=[]
 for flip in [False]:
  for cel,im in enumerate(spheres):
   d,r=phases(im[:,::-1]if flip else im);sphere+=d;sr.append(dict(cel=cel,flip=flip,phases=r))
 assert len(raw)==7040 and len(sphere)==2304
 return raw,bytes(sphere),dict(core=cr,spheres=sr)
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 b=bytearray((SRC/'level05_region.bin').read_bytes());core,sphere,report=assets(b);print('Packed phase rows',len(core)+len(sphere),'expanded bytes')
 (OUT/'core_pairs.bin').write_bytes(core);(OUT/'sphere_pairs.bin').write_bytes(sphere)
 def asm(name,text):
  p=OUT/(name+'.asm');p.write_text(text);r=subprocess.run([str(ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],cwd=ROOT,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr;return p.with_suffix('.bin').read_bytes()
 cache=asm('cache',(ROOT/'src/l5_preshift_cache.asm').read_text())
 sym={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9a-f]+)',(OUT/'cache.sym').read_text(),re.I)}
 helper=asm('motion',f'INIT_CACHE EQU ${sym["init_cache"]:04X}\n'+(ROOT/'src/l5_preshift_motion.asm').read_text());motion_symbols={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9a-f]+)',(OUT/'motion.sym').read_text(),re.I)}
 shader=(ROOT/'src/bellmite_interruptible.asm').read_text();# Retain original source interval guards.
 # Keep the tested blend machinery. Phase entry is a separate helper below the old cache.
 shader=shader.replace('        ASSERT $ <= $8BF0', '        ASSERT $ <= $8BF0')
 # Replace source selection only; all cells use this source path, including the core.
 shader=shader.replace('        ; Unowned core cells use the original fast renderer/dictionary.','''        LD A,($5C82)
        OR A
        JR Z,ours
        CP $80
        JR C,reject_owner
        CP $DC
        JR C,ours
reject_owner:
        OR A
        RET
        ; Unowned core cells use the original fast renderer/dictionary.''')
 a=shader.index('        LD DE,$F3F1\n',shader.index('visible_source:'));z=shader.index('start_copy:',a)
 shader=shader[:a]+f'        CALL ${sym["select_cache"]:04X}\n        JR NC,phase_valid\n        LD DE,(meta)\n        LD A,(owner)\n        LD C,A\n        CALL $1AF6\n        JP return_ours\nphase_valid:\n        LD (cache),HL\n        LD (reverse_y),A\n        JP start_copy\n'+shader[z:]
 # phase_paint restores the exact original prologue register saves before ours.
 # Source prologue remains unchanged.
 shader=shader.replace('        ASSERT $ <= $8BF0','        ASSERT $ <= $8BF0')
 shader=shader.replace('LD A,$9F','LD A,$5F')
 shaderbin=asm('compositor',shader)
 shader_symbols={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9a-f]+)',(OUT/'compositor.sym').read_text(),re.I)}
 copies=[]
 for label,addr,file in [('forward',0x1a6e,'boss_copy_fast'),('reverse',0xf57,'boss_copy_reverse'),('flash',0xfc3,'boss_copy_flash')]:
  text=f'FLASH EQU ${shader_symbols["flash"]:04X}\nREVERSE_Y EQU ${shader_symbols["reverse_y"]:04X}\n'+(ROOT/f'src/{file}.asm').read_text();copies.append((addr,asm(file,text)))

 # Patches common native actor selector only; other levels branch to original selector.
 shims=[(0x1b14,bytes.fromhex('f5 3a 70 0d fe 35 c3 fc 09')),(0x9fc,bytes.fromhex('28 04 f1 c3 85 8e f1 c3 e1 0e')),(0xee1,bytes.fromhex('f3 32 e4 5b 3e 59 d3 f4 c3 50 dc')),(0x1af6,bytes.fromhex('3e 09 d3 f4 79 12 c3 f7 1f')),(0x1ff7,bytes.fromhex('3e 19 d3 f4 c9')),(0xe10,bytes.fromhex('fb d3 f4 f1 c9'))]
 gate='''        ORG $0D00
        RET
        POP AF
        LD A,(DE)
        AND A
        JP Z,$8F0B
        LD ($5C82),A
        LD A,($8EB1)
        LD ($5C81),A
        DI
        LD A,$19
        OUT ($F4),A
        CALL $88EB
        LD A,9
        OUT ($F4),A
        EI
        JP NC,fallback
        OR A
        RET
fallback:
        LD A,(DE)
        AND A
        JP $8EDA
        ASSERT $ == $0D27
        DI
        LD A,$59
        OUT ($F4),A
        JP RESTORE_ENTRY
        ASSERT $ == $0D2F
'''
 gate=asm('phase_gate',f'RESTORE_ENTRY EQU ${motion_symbols["restore_sources"]:04X}\n'+gate)
 warmup=asm('warmup',f'WARMUP_ENTRY EQU ${motion_symbols["warmup"]:04X}\n'+"""        ORG $0DC0
        CALL $86C3
        CALL $FCC8
        LD HL,$5D00
reverse_byte:
        LD A,L
        LD B,8
reverse_bit:
        RRCA
        RL D
        DJNZ reverse_bit
        LD (HL),D
        INC L
        JR NZ,reverse_byte
        DI
        LD A,$59
        OUT ($F4),A
        JP WARMUP_ENTRY
        ASSERT $ <= $0DDE
""")
 b[0xdc0:0xdc0+len(warmup)]=warmup
 b[0xd00:0xd2f]=gate;b[0x19fc:0x19ff]=bytes.fromhex('c3 27 0d')
 # Code starts after the native source-copy limit and the saved transition tail.
 # Source-shadow caches are expanded after HOME installation and restored on leave.
 # Palette dictionaries + nibble/5-bit indices fit all four phases in DOCK1.
 core_dict=sorted(set(core[1::2]));sphere_dict=sorted(set(sphere[1::2]));assert len(core_dict)<=16 and len(sphere_dict)<=32
 bits=core[::2]+sphere[::2];ci=[core_dict.index(v)for v in core[1::2]];si=[sphere_dict.index(v)for v in sphere[1::2]]
 packed_core=bytes(ci[i]|ci[i+1]<<4 for i in range(0,len(ci),2));word=0;n=0;packed_sphere=bytearray()
 for i in si:
  word|=i<<n;n+=5
  while n>=8:packed_sphere.append(word&255);word>>=8;n-=8
 assert n==0 and len(bits)==4672 and len(packed_core)==1760 and len(packed_sphere)==720
 payload=bits+packed_core+packed_sphere;assert len(payload)==7152
 b[0x2400:0x3fe0]=payload[:7136]
 b[0xe000:0xe400]=bytes(1024);b[0xdc50:0xdc50+len(helper)]=helper
 b[0xe1b0:0xe1b0+len(core_dict)]=bytes(core_dict);b[0xe1c0:0xe1c0+len(sphere_dict)]=bytes(sphere_dict)
 b[0xe1e0:0xe1f0]=payload[7136:];b[0xe200:0xe400]=bytes([255])*512
 (OUT/'packed_phase_cache.bin').write_bytes(payload)
 b[0x8c00:0x8f00]=bytes(768);b[0x8c00:0x8c00+len(cache)]=cache
 for at,data in copies:b[at:at+len(data)]=data
 b[0x88eb:0x8bf0]=bytes([255])*(0x8bf0-0x88eb);b[0x88eb:0x88eb+len(shaderbin)]=shaderbin
 # Dummy cells supply a fixed source index; colour/pixels come from compiled phase caches.
 b[0xcfa1:0xd3f1]=bytes(1104);b[0xd3f1:0xd481]=bytes(144)
 shutil.copytree(SRC/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True)
 records=[]
 for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
  data=bytearray(b if n==5 else(SRC/f'{name}_region.bin').read_bytes())
  for at,payload in shims:
   assert all(x==255 for x in data[at:at+len(payload)]),(name,hex(at));data[at:at+len(payload)]=payload
  if name=='boot':
   assert data[0x5172:0x5175]==bytes.fromhex('cd 85 8e');data[0x5172:0x5175]=bytes.fromhex('cd 14 1b')
  (OUT/f'{name}_region.bin').write_bytes(data);tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP';(OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{p:02X}',data[p*8192:(p+1)*8192],p)for p in range(8)));records.append(dict(file=tap,sha256=hashlib.sha256(data).hexdigest()))
 for f in ['launcher.bin','demand_loader.sym','boss_preview.bin','boss_preview.sym','overlay.bin','overlay.sym','gateway.bin','gateway.sym','player_damage.bin','projectile_clock.bin','projectile_clock.sym']:
  if(SRC/f).exists():shutil.copy2(SRC/f,OUT/f)
 (OUT/'manifest.json').write_text(json.dumps(dict(status='Experimental L5 preshift candidate, not validated',regions=records,sphere_cache=2304,packed_phase_bytes=7152,motion_bytes=len(helper),cache_helper_bytes=len(cache),shader_bytes=len(shaderbin),phase_fitting=report),indent=2))
 print('built',len(helper),len(cache),len(shaderbin))
if __name__=='__main__':main()
