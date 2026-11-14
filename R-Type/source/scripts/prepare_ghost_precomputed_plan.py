from pathlib import Path
import json,zipfile,subprocess,re
R=Path.cwd();O=R/'build/graphics/l1_ghost_converter';src=R/'src/l1_ghost_precomputed_plan.asm';exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';p=O/'ghost_plan_helper';r=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(src)],capture_output=True,text=True);assert not r.returncode,r.stdout+r.stderr
# Stable helper symbols from actualL1 runtime, not assumed source offsets.
sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(R/'build/fullgame/l1_head32_r110/L1_motion.sym').read_text(),re.I)}
print('actual plan helpers', {k:v for k,v in sy.items()if 'plan_'in k.lower()})
b=bytearray(0x300);z=zipfile.ZipFile(R/'convref/rtype-l1-ghost-assets.zip');oldlen=len((R/'build/fullgame/l1_head32_r110/L1_runtime_art.bin').read_bytes())
for pose in range(3):
 raw=z.read(f'ghost/frame_{pose:02d}.pairs.bin');base=0xa870+oldlen+pose*256
 for flip in [0]:
  at=pose*16
  for cy in range(4):
   for cx in range(4):
    sx=3-cx if flip&1 else cx;ys=31-cy*8 if flip&2 else cy*8;ptr=base+sx*64+ys*2;rows=[ys-y if flip&2 else ys+y for y in range(8)];visible=any(raw[sx*64+y*2+1]!=0 for y in rows);b[at]=0 if visible else 54;at+=1
helper=p.with_suffix('.bin').read_bytes();b[0x100:0x100+len(helper)]=helper;(O/'ghost_plan_cache.bin').write_bytes(b);print('plan cache',len(b),'helper',len(helper))
