from pathlib import Path
import json,hashlib,zipfile,functools
R=Path.cwd();O=R/'build/fullgame/l5_cold_start_r98';B=R/'build/fullgame/l5_cell_atomic_r97'
for name in ['boss_level5.json','l5_repeat_jumps.json']:
 assert json.loads((O/name).read_text())['passed'],name
startup=json.loads((O/'startup_selected_validation.json').read_text());assert len(startup)==2 and all(r['boot']>=0 and r['titles']>0 and r['region']==r['level']-1 and not r['fatal'] for r in startup)
hashes={}
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();ref=(B/f'level{n:02d}_region.bin').read_bytes().replace(b'R97 DEBUG',b'R98 DEBUG');assert len(b)==65536
 if n==5:
  sites=json.loads((B/'atomic_patch.json').read_text())['atomic_ei_sites'];allowed=set(sites)|{0xd9,0xda}
  assert b[0xd8:0xdb]==bytes.fromhex('c3d9dd')
  assert b.find(bytes.fromhex('c3d9dd'),0xdc0,0xdde)>=0
  assert all(ref[q]==0 and b[q]==0xfb for q in sites)
  assert all(a==c or i in allowed for i,(a,c)in enumerate(zip(b,ref)))
  assert b[0x2000:]==ref[0x2000:] or all(b[q]==ref[q]for q in range(0x2000,65536)if q not in sites)
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
for name in ['launcher.bin','demand_loader.bin']:assert (O/name).read_bytes()==(B/name).read_bytes().replace(b'R97 CELL TEST   ',b'R98 START FIX   ')
t=(O/'rtype/rt.tap').read_bytes();p=0
while p<len(t):
 size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;p+=size+2
summary=dict(passed=True,hardware_confirmation_pending=True,startup_reproduced_before_fix=True,cold_gateway_target=0xddd9,initial_selection_startup=startup,interrupt_behavior_restored_r96=True,artwork_unchanged=True,repeated_jumps=12,region_sha256=hashes)
(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
readme='''R-Type TS2068 r98 - L5 initial-load gateway repair

Replace the COMPLETE rtype folder, RESET, launch rtype/rt.tap.
Confirm R98 START FIX. Select L5 during loading; after title/start use B,
release, B to jump to its boss.

Reproduced startup failure by selecting L5 before initial loading completed
in BOTH r96 and r97. Earlier gameplay fixtures selected L5 after the first
title had booted and missed this route. The cold gateway at00D4 still
jumped toDDDC after the row-selector rollback moved warmup toDDD9. That
entered the address operand of LD (MAIN_SP),SP, so the stack was not saved.
The separate level-switch gateway was updated; the initial one was missed.
This build updates the cold target and statically checks BOTH gateways.

R97's two EI-to-NOP changes are reverted to r96 interrupt behavior.
Explicit GREEN selection/CYAN row-copy/BLACK cell-return checkpoints remain.
Current artwork, dimensions, two-pixel movement and all asset banks remain.

Unmodified startup title tests: initial L1 and early-selected L5 pass.
The exact early-L5 load followed by start/double-B and160bossupdates passes;
12repeatedbossjumps pass. Gameplay stress still bypasses game-over handling;
the startup/title test does not patch game code. Static change whitelist,
immutable assets, all tape checksums/reconstruction and ZIPCRC pass.

This fixes the reproduced initial-load failure. The separate real-machine
boss emergence freeze remains unconfirmed. If it recurs, report border
colour and how far the boss appeared. Stock64KB target unchanged.
'''
(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype/README.txt').write_text(readme,encoding='ascii')
z=O/'RType_TS2068_r98.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','startup_patch.json','validation_summary.json']:f.write(O/name,name)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z);print(hashlib.sha256(z.read_bytes()).hexdigest(),z.stat().st_size)


