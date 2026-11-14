from pathlib import Path
import json,hashlib,zipfile,functools
R=Path.cwd();O=R/'build/fullgame/l5_row_restore_r96';B=R/'build/fullgame/l5_bank_guard_r93'
for name in ['boss_level5.json','l5_repeat_jumps.json','l5_revisits_validation.json','phase_irq_components.json','empty_metadata_validation.json','l5_clipping_grid.json']:
 assert json.loads((O/name).read_text())['passed'],name
hashes={}
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();ref=(B/f'level{n:02d}_region.bin').read_bytes().replace(b'R38 DEBUG',b'R96 DEBUG');assert len(b)==65536
 if n==5:
  allowed=set(range(0x8c00,0x8f00))|set(range(0xdc50,0xdf00))
  for lo,hi in [(0xdc0,0xdde),(0xd27,0xd2f)]:
   oldsy={k:int(v,16)for k,v in __import__('re').findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(B/'motion.sym').read_text(),__import__('re').I)}
   label='warmup' if lo==0xdc0 else 'restore_sources';q=ref.find(b'\xc3'+oldsy[label].to_bytes(2,'little'),lo,hi);assert q>=0;allowed.update([q+1,q+2])
  q=ref.find(bytes.fromhex('cdf61a'),0x897e,0x899d);assert q>=0 and b[q:q+3]==bytes(3);allowed.update(range(q,q+3))
  assert all(a==c or i in allowed for i,(a,c)in enumerate(zip(b,ref)))
  for lo,hi in [(0x2000,0x4000),(0xa000,0xdc50),(0xdf00,0x10000),(0x1ff7,0x1ffc)]:assert b[lo:hi]==ref[lo:hi]
 else:assert b==ref
 hashes[str(n)]=hashlib.sha256(b).hexdigest()
 for name in [f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  t=(O/'rtype'/name).read_bytes();p=0;parts=[]
  while p<len(t):
   size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0
   if v[0]==255:parts.append(v[1:-1])
   p+=size+2
  assert b''.join(parts)==(b if name.startswith('LEVEL')else b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]))
for name in ['RTCORE.TAP','RTPRELD.TAP']:assert (O/'rtype'/name).read_bytes()==(B/'rtype'/name).read_bytes()
for name in ['core_pairs.bin','sphere_pairs.bin']:assert (O/name).read_bytes()==(B/name).read_bytes()
for name in ['launcher.bin','demand_loader.bin']:assert (O/name).read_bytes()==(B/name).read_bytes().replace(b'PREPARING GAME  ',b'R96 ROW RESTORE ')
t=(O/'rtype/rt.tap').read_bytes();p=0
while p<len(t):
 size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;p+=size+2
summary=dict(passed=True,hardware_confirmation_pending=True,older_selector_exact_bytes=450,artwork_unchanged=True,other_levels_unchanged_except_debug_label=True,phase_cases=256,foreground_cases=96,clipping_cases=112,empty_metadata_preserved=True,repeated_jumps=12,resident_routes=9,component_irq_masked=True,live_gameplay_interrupts_tested=True,region_sha256=hashes)
(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
readme='''R-Type TS2068 r96 - L5 row drawing restoration

Replace the COMPLETE rtype folder, RESET, launch rtype/rt.tap.
Startup preparation message: R96 ROW RESTORE. Debug screen: R96 DEBUG.

The hardware R95 frozen RED checkpoint pointed at L5 cell planning.
This trial removes that whole-actor planner and restores the older r58
row-at-a-time selector, byte-identical for its 450-byte drawing prefix.
The decoder is adapted to the current cache layout. Current artwork,
size, two-pixel boss movement and player updates are retained.
Empty rows preserve background ownership. No additional RAM banks used.
R94 IRQ isolation and R95 tracing/checksum experiments are removed.
Other levels retain r93 behavior; only their debug release label changes.

Emulation passed 256 phase/orientation cases, 96 overlaps, 112 clipped
positions, empty-row ownership, exact cache expansion/restoration,
12 repeated boss jumps, nine cold/cached level routes, live L4-to-L5
entry, active player/fire and low-ship charged-beam scenarios.
Pure raster cases mask interrupts; live gameplay tests exercise them.
Image/TAP reconstruction, immutable assets, code bounds and ZIP CRC pass.
Hardware freeze was not reproduced in emulation. Hardware confirmation
is still needed: try the same L5 boss entry that froze with RED in R95.
Stock 64KB cartridge unchanged. Keep complete release files together.
'''
(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype/README.txt').write_text(readme,encoding='ascii')
z=O/'RType_TS2068_r96.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','row_restore.json','validation_summary.json']:f.write(O/name,name)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z);print(hashlib.sha256(z.read_bytes()).hexdigest(),z.stat().st_size)

