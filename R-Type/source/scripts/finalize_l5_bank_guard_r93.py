from pathlib import Path
import json,hashlib,zipfile,functools
R=Path.cwd();O=R/'build/fullgame/l5_bank_guard_r93';B=R/'build/fullgame/l4_speed_r92';P=R/'build/fullgame/bank5_restore_r91'
assert json.loads((O/'native_revisits_validation.json').read_text())['passed'];assert json.loads((O/'l5_repeat_jumps.json').read_text())['passed'];assert json.loads((O/'boss_level5.json').read_text())['passed']
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();ref=P if n==5 else B;assert b==(ref/f'level{n:02d}_region.bin').read_bytes();assert len(b)==65536
 for name in [f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  assert (O/'rtype'/name).read_bytes()==(ref/'rtype'/name).read_bytes();t=(O/'rtype'/name).read_bytes();p=0;parts=[]
  while p<len(t):
   size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0
   if v[0]==255:parts.append(v[1:-1])
   p+=size+2
  assert b''.join(parts)==(b if name.startswith('LEVEL')else b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]))
for name in ['rt.tap','RTCORE.TAP','RTPRELD.TAP']:assert (O/'rtype'/name).read_bytes()==(B/'rtype'/name).read_bytes()
summary={'passed':True,'level5_entire_region_and_tapes_exact_r91':True,'level5_boss_payload_2400_3fe0_restored':True,'other_seven_levels_exact_r92':True,'repeated_boss_jumps':12,'cold_cached_transitions':12,'hardware_lockup_not_reproduced':True,'hardware_confirmation_pending':True};(O/'l5_bank_contract.json').write_text(json.dumps(summary,indent=2))
readme='''R-Type TS2068 r93 - L5 boss bank regression repair

Replace the COMPLETE rtype folder, RESET, launch rtype/rt.tap.

r92's generic hotkey installer wrote into DOCK1:3A00..3DFF on every level.
L5 is an exception: that bank contains its boss phase payload, and L5 uses
its separate HOME hotkey variant. 972 payload bytes were changed in error.
L5's complete64KB image and LEVEL05/START05 tapes are restored byte-for-byte
from r91. Its HOME hotkey code stays unchanged. Generic key installation now
explicitly excludes L5. Every other level is byte-identical to r92, including
its L4 speed-trial movement tradeoff and captured level-key behavior.

Fresh L5 boss, L4-to-L5 boss, twelve repeated L5 boss jumps, twelve cold/cached
level switches/native-source checks, exact payload/image/TAP contracts and
checksums, ZIPCRC passed. The hardware lockup itself was not reproduced in
emulation, including on the broken r92 data. This repairs a confirmed data
corruption regression, not proof that every real-machine lockup is resolved.

Stock64KB target unchanged. Do not mix release files; reset clears cached RAM.
'''
(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype/README.txt').write_text(readme,encoding='ascii')
z=O/'RType_TS2068_r93.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','regression_repair.json','l5_bank_contract.json']:f.write(O/name,name)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z);print(hashlib.sha256(z.read_bytes()).hexdigest(),z.stat().st_size)
