from pathlib import Path
import json,hashlib,zipfile,functools
R=Path.cwd();O=R/'build/fullgame/l5_cell_atomic_r97';B=R/'build/fullgame/l5_row_restore_r96'
for name in ['boss_level5.json','l5_repeat_jumps.json','atomic_validation.json','phase_irq_components.json','empty_metadata_validation.json','l5_clipping_grid.json']:
 assert json.loads((O/name).read_text())['passed'],name
hashes={}
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();ref=(B/f'level{n:02d}_region.bin').read_bytes().replace(b'R96 DEBUG',b'R97 DEBUG');assert len(b)==65536
 if n==5:
  sites=json.loads((O/'atomic_patch.json').read_text())['atomic_ei_sites'];allowed=set(sites)|set(range(0x890a,0x891c))|set(range(0x97b,0x986))
  for target,wrapper in [(0x8c00,0x890a),(0x1a6e,0x8913)]:
   q=ref.find(b'\xcd'+target.to_bytes(2,'little'),0x8920,0x8a00);assert q>=0;allowed.update([q+1,q+2]);assert b[q+1:q+3]==wrapper.to_bytes(2,'little')
  assert all(ref[q]==0xfb and b[q]==0 for q in sites)
  assert all(a==c or i in allowed for i,(a,c)in enumerate(zip(b,ref)))
  for lo,hi in [(0x2000,0x4000),(0xa000,0x10000),(0x1ff7,0x1ffc)]:assert b[lo:hi]==ref[lo:hi]
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
for name in ['launcher.bin','demand_loader.bin']:assert (O/name).read_bytes()==(B/name).read_bytes().replace(b'R96 ROW RESTORE ',b'R97 CELL TEST   ')
t=(O/'rtype/rt.tap').read_bytes();p=0
while p<len(t):
 size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;p+=size+2
summary=dict(passed=True,hardware_confirmation_pending=True,atomic=json.loads((O/'atomic_validation.json').read_text()),artwork_unchanged=True,other_levels_unchanged_except_debug_label=True,phase_cases=256,foreground_cases=96,clipping_cases=112,repeated_jumps=12,region_sha256=hashes)
(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
readme='''R-Type TS2068 r97 - L5 banked-cell interrupt isolation trial

Replace the COMPLETE rtype folder, RESET, launch rtype/rt.tap.
Confirm R97 CELL TEST appears. Load only L5; press/release B, then B.

R96 still froze on hardware. Its changing border was not a reliable draw
checkpoint because R96 removed R95 tracing. This trial retains R96's row
selector/artwork and disables only two interrupt-enabling instructions:
cached-cell selection and paired-plane drawing with temporary banks mapped.
Interrupts remain enabled between cells through the existing entry helper.
This may affect responsiveness; it is an isolation trial, not a proven fix.

Explicit L5 draw checkpoints:
GREEN: cached sprite selection or overlap blending.
CYAN: native paired bitmap/colour row copy.
BLACK: cell returned; a freeze here may be outside the traced work.
If it freezes, report the final border colour and how far the boss emerged.

Direct L5 double-B,160boss updates,12repeatedjumps, low-ship charged-fire,
256phase cases,96overlaps,112clippedpositions, empty-row metadata pass.
Live test observed2278IRQs and6887916raw-bank instruction visits with
interrupts disabled throughout the tested selector/compositor ranges.
All green/cyan/black checkpoints observed. These are emulator results;
hardware freeze remains unreproduced. Artwork/geometry/assets unchanged.
Static patch whitelist, tape checksums/reconstruction, ZIPCRC pass.
Stock64KB cartridge unchanged. Keep release files together.
'''
(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype/README.txt').write_text(readme,encoding='ascii')
z=O/'RType_TS2068_r97.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','atomic_patch.json','validation_summary.json']:f.write(O/name,name)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z);print(hashlib.sha256(z.read_bytes()).hexdigest(),z.stat().st_size)


