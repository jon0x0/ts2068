from pathlib import Path
import json,hashlib,functools,zipfile,re
R=Path.cwd();O=R/'build/fullgame/l5_trace_r95';B=R/'build/fullgame/boss_guard_r94'
for name in ['checkpoint_validation.json','cache_integrity_validation.json','l5_live_guard_validation.json','native_revisits_validation.json','l5_revisits_validation.json','charged_jump_validation.json','l5_clipping_grid.json']:assert json.loads((O/name).read_text())['passed'],name
assert json.loads((O/'l5_clipping_grid.json').read_text())['cases']==112
ms={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9a-f]+)',(O/'motion.sym').read_text(),re.I)};hashes={}
for n in range(1,9):
 a=(B/f'level{n:02d}_region.bin').read_bytes();b=(O/f'level{n:02d}_region.bin').read_bytes();assert len(b)==65536;lab=a.index(b'R94 DEBUG');allowed=set(range(lab,lab+9))
 if n==5:
  allowed.update(range(0xdc50,0xdf00));allowed.update(range(0xe340,0xe3f0));allowed.update(range(0x890a,0x8920));allowed.update(range(0x97b,0x986));allowed.update(range(0xdc0,0xdde));allowed.update(range(0xd27,0xd2f))
  for oldtarget in [0x8c00,0x1a6e]:
   p=a.find(b'\xcd'+oldtarget.to_bytes(2,'little'),0x8920,0x8a00);assert p>=0;allowed.update(range(p,p+3))
  assert b[0x2400:0x3fe0]==a[0x2400:0x3fe0];assert b[0x1fa3:0x2000]==a[0x1fa3:0x2000];assert b[0xdf00:0xe340]==a[0xdf00:0xe340];assert b[0xe3f0:]==a[0xe3f0:];assert 0xdc50+len((O/'motion.bin').read_bytes())<=0xdf00;assert 0xe340+len((O/'l5_cache_check.bin').read_bytes())<=0xe3f0
  assert b'\xc3'+ms['warmup'].to_bytes(2,'little')in b[0xdc0:0xdde];assert b'\xc3'+ms['restore_sources'].to_bytes(2,'little')in b[0xd27:0xd2f]
 assert all(i in allowed for i,(x,y)in enumerate(zip(a,b))if x!=y),(n,'unscoped difference');hashes[n]=hashlib.sha256(b).hexdigest()
 for name in [f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  t=(O/'rtype'/name).read_bytes();p=0;parts=[]
  while p<len(t):
   size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0
   if v[0]==255:parts.append(v[1:-1])
   p+=size+2
  assert b''.join(parts)==(b if name.startswith('LEVEL')else b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]))
for name in ['RTCORE.TAP','RTPRELD.TAP']:assert (O/'rtype'/name).read_bytes()==(B/'rtype'/name).read_bytes()
assert (O/'launcher.bin').read_bytes()==(B/'launcher.bin').read_bytes().replace(b'R94 PREPARING   ',b'R95 TRACE TEST  ')
t=(O/'rtype/rt.tap').read_bytes();p=0
while p<len(t):
 size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert functools.reduce(int.__xor__,v,0)==0;p+=size+2
assert b'R95 TRACE TEST  'in t
p=O/'demand_loader.asm';p.write_text(p.read_text().replace('R94 PREPARING   ','R95 TRACE TEST  '))
summary=dict(passed=True,diagnostic_only=True,r94_hardware_freeze_confirmed=True,hardware_cause_unresolved=True,region_sha256=hashes,phase_artwork_unchanged=True,clip_cases=112,cache_checker_good_and_injected_failures=True,guard_repeated_jumps=12,l5_specific_transitions=9,general_transitions=12,held_charge_jumps=2,stock64KB_unchanged=True);(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
readme='''R-Type TS2068 R95 - L5 hardware checkpoint DIAGNOSTIC

Replace the complete rtype folder, RESET, launch rtype/rt.tap.
Confirm R95 TRACE TEST appears before gameplay. Debug screen says R95 DEBUG.
The real-machine freeze is NOT fixed or reproduced in emulation. This build
identifies which part stops when only the first boss rows appear above HUD.

If it freezes, photograph the whole screen INCLUDING THE BORDER and report
its last colour. Normal checkpoint colours change briefly while drawing:
BLUE: actor phase/cache selection (includes first cache integrity check).
RED: cell visibility and clipping planning.
MAGENTA: planning returned; native cell dispatch follows.
GREEN: selecting a cached cell, or blending an overlap.
CYAN: native paired-row copy.
BLACK: a cell returned; failure may be between cell calls or elsewhere.

A SOLID YELLOW SCREEN means the expanded core cache failed its checksum.
A SOLID WHITE SCREEN means the expanded sphere cache failed its checksum.
These are deliberate diagnostic stops requiring RESET. They remain visible
if your video adapter hides borders. The checks run once per world setup,
before the first compiled boss draw, and introduce a short pause.

This retains R94's L5 gameplay IRQ isolation and its player/fire update
tradeoff. Trace writes also change timing; absence of a freeze here would
not by itself establish a fix. No graphics/size/palette/hitbox changes.
All checkpoints use border bits only; no beeper bit is set.

Verified normal L5 boss, all six normal checkpoints,112clipped positions,
twelve guarded boss jumps, nine L5cold/cached reentries plus twelve general
level transitions, held-fire boss jumps, low ship/chargedbeam release,
checksum pass/register/stack preservation and injected core/sphere failures
with full yellow/white screen. All immutable phase/dictionary/trampoline,
code boundaries, TAP reconstruction/checksums, ZIPCRC checks pass.
Actual R94 lockup photo is the hardware evidence; R95 awaits hardware test.
Stock64KB target unchanged. Keep all files from this folder together.

Border port mapping checked against TS2068 Technical Manual Table2.1.13-1
and Section2.1.13.2. PortFF is documented read/write; no change was made based
on the rejected speculation that reading it was invalid.
https://www.retromaniek.pl/wp-content/uploads/2019/09/Timex-Sinclair-2068-Technical-Manual-best.pdf
'''
(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype/README.txt').write_text(readme,encoding='ascii')
z=O/'RType_TS2068_r95_trace.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','trace_legend.json','validation_summary.json']:f.write(O/name,name)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z);print(hashlib.sha256(z.read_bytes()).hexdigest(),z.stat().st_size)
