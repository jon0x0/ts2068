from pathlib import Path
import json,hashlib,functools,zipfile
R=Path.cwd();O=R/'build/fullgame/boss_guard_r94';B=R/'build/fullgame/l5_bank_guard_r93';live=json.loads((O/'l5_live_guard_validation.json').read_text());assert live['passed']and live['finishCount']==12 and live['callbacksDuringCriticalSection']==0
assert json.loads((O/'native_revisits_validation.json').read_text())['passed'];assert json.loads((O/'boss_level5.json').read_text())['passed']
hashes={}
for n in range(1,9):
 a=(B/f'level{n:02d}_region.bin').read_bytes();b=(O/f'level{n:02d}_region.bin').read_bytes();assert len(b)==65536;label=a.index(b'R38 DEBUG');allowed=set(range(label,label+9))
 if n==5:
  allowed.update(range(0x1fa3,0x1ff7));allowed.update(range(0xdfc0,0xe000));q=b.find(bytes.fromhex('cdc0df'),0xdddc,0xde04);assert q>=0;allowed.update(range(q,q+3));assert b[0x1ff7:0x1ffc]==bytes.fromhex('3e19d3f4c9');assert b[0x2000:0x4000]==a[0x2000:0x4000];assert b[0xdf80:0xdfc0]==a[0xdf80:0xdfc0]
 assert all(i in allowed for i,(x,y)in enumerate(zip(a,b))if x!=y),(n,'unscoped difference')
 assert a[0xa000:0xdc50]==b[0xa000:0xdc50];assert a[0xe000:]==b[0xe000:];hashes[n]=hashlib.sha256(b).hexdigest()
 for name in [f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  t=(O/'rtype'/name).read_bytes();p=0;parts=[]
  while p<len(t):
   size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0
   if v[0]==255:parts.append(v[1:-1])
   p+=size+2
  assert b''.join(parts)==(b if name.startswith('LEVEL')else b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]))
for name in ['RTCORE.TAP','RTPRELD.TAP']:assert (O/'rtype'/name).read_bytes()==(B/'rtype'/name).read_bytes()
launcher=(O/'launcher.bin').read_bytes();assert launcher== (B/'launcher.bin').read_bytes().replace(b'PREPARING GAME  ',b'R94 PREPARING   ')
t=(O/'rtype/rt.tap').read_bytes();p=0
while p<len(t):
 size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;p+=size+2
assert b'R94 PREPARING   'in t
home=(O/'boss_level5.home.bin').read_bytes();old=(B/'boss_level5.home.bin').read_bytes();assert home[0xf8b0:0xfa33]==old[0xf8b0:0xfa33];assert home[0xfa33:0xfa3d]==bytes.fromhex('214bfd35afd3fec3068b')
summary=dict(passed=True,diagnostic_only=True,hardware_freeze_unresolved=True,live_guard=live,region_sha256=hashes,l5_phase_payload_unchanged=True,l5_1ff7_trampoline_preserved=True,adjacent_audio_code_preserved=True,stock64KB_unchanged=True);(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
readme='''R-Type TS2068 R94 - L5 interrupt isolation DIAGNOSTIC

Replace the COMPLETE rtype folder, RESET, launch rtype/rt.tap.
Before gameplay look for the small message R94 PREPARING.
The diagnostic photo screen also identifies itself as R94 DEBUG.

The reported hardware freeze remains unconfirmed in emulation. This build
isolates gameplay IRQ reentrancy during L5 boss emergence and drawing.
L5's checkpoint rebuild uses a guarded state; player/projectile callbacks
also wait while the interrupted code has the raw L5 drawing bank selected.
Normal IRQ handling stays enabled. No audio mute command was added; AY output
continues during gameplay. Native initialization itself may suppress sound.

This is an isolation trial, not a confirmed hardware fix. Player and firing
updates can be less smooth while drawing the boss. Artwork, sizes, terrain,
phase payload and the L4 speed changes are retained. L5's special return
trampoline1FF7 is preserved, along with adjacent audio code. Its existing
64byte dictionary-tail gap holds the installer; no source bank is reused.

Validated: twelve repeated boss jumps; exact live guard and full return stub;
zero gameplay callbacks in guarded IRQ sections; AY output during gameplay;
fresh L5 and L4-to-L5 boss; twelve cold/cached level switches/native source
checks; unchanged phase payloads, code/allocation boundaries, TAP checksums
and exact reconstruction, ZIPCRC. Emulated active-input8second sample:
r93=27worldupdates/92playerpositionchanges; R94=31/80. These are comparative
samples, not displayFPS or hardware measurements; subsequent states differ.

Please test the same first upward L5 boss movement after confirming the R94
loading label. Reset is required to clear old resident RAM and old IRQ code.
Stock64KB target unchanged. Do not mix this folder with older level files.
'''
(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype/README.txt').write_text(readme,encoding='ascii')
z=O/'RType_TS2068_r94_diagnostic.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','boss_guard.json','validation_summary.json']:f.write(O/name,name)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z);print(hashlib.sha256(z.read_bytes()).hexdigest(),z.stat().st_size)
