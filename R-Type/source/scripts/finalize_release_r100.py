from pathlib import Path
import json,hashlib,zipfile,shutil,functools,re
R=Path(__file__).resolve().parents[1];B=R/'build/fullgame/irq_layout_r99';O=R/'build/releases/r100'
startup=json.loads((O/'startup_selected_validation.json').read_text());fire=json.loads((O/'unmodified_fire_validation.json').read_text());assert len(startup)==2 and all(r['boot']>=0 and r['titles']>0 and r['region']==r['level']-1 for r in startup);assert len(fire)==3 and all(r['passed']for r in fire)
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();a=(B/f'level{n:02d}_region.bin').read_bytes();assert b==a.replace(b'R99 DEBUG',b'R100 INFO')
 for name in [f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  t=(O/'rtype'/name).read_bytes();p=0;parts=[]
  while p<len(t):
   size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0
   if v[0]==255:parts.append(v[1:-1])
   p+=size+2
  assert b''.join(parts)==(b if name.startswith('LEVEL')else b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]))
b=(O/'level05_region.bin').read_bytes();assert b[0x8f00:0x9000]==bytes([0x5b])*256
sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(O/'motion.sym').read_text(),re.I)};target=b'\xc3'+sy['warmup'].to_bytes(2,'little');assert b[0xd8:0xdb]==target and target in b[0xdc0:0xdde];assert b[0x1ff7:0x1ffc]==bytes.fromhex('3e19d3f4c9')
for name in ['RTBOOT.TAP','RTCORE.TAP','RTPRELD.TAP']:assert (O/'rtype'/name).read_bytes()==(B/'rtype'/name).read_bytes()
for name in ['launcher.bin','demand_loader.bin']:assert (O/name).read_bytes()==(B/name).read_bytes().replace(b'R99 PREPARING   ',b'R100 PREPARING  ')
# Every tape block, including the launcher and shared core.
for p in (O/'rtype').glob('*.tap'):
 t=p.read_bytes();at=0
 while at<len(t):
  size=int.from_bytes(t[at:at+2],'little');v=t[at+2:at+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;at+=size+2
readme='''R-Type TS2068 - Release r100 (2026-11-08)

INSTALL
Replace the complete rtype folder, reset, and launch rtype/rt.tap.
The folder may be inside a subdirectory beneath /TAP; keep its files together.
Startup preparation text is R100 PREPARING.

This release promotes the working r99 baseline. Game code and artwork are
identical to r99; only fixed-length release/info labels have changed.
All eight levels and their current assets are included. The full disk build
uses the existing 512KB RAM layout and loads/caches levels on demand.
No r94-r98 experimental drawing or interrupt-isolation patches are retained.
L5 keyboard/UI data stays outside its complete temporary interrupt table.

CONTROLS
The game asks you to define gameplay keys; your choices remain authoritative.
Keyboard and native joystick work together. Joystick fire can start play.
M toggles music. P pauses; use Shift-P if P is assigned to a gameplay action.
L followed by 1-8 changes level. Shift-L preloads all levels and returns to
its title screen. B, release, B jumps to the boss for artwork testing.

VALIDATION
User reported r99 working again on the real machine after the reported
L5 startup/fire/boss-entry failures. This is not an all-level hardware test.
r100 changes labels only and repeats initial L1/L5 startup and three firing
scenarios without modifying gameplay/game-over code. All8 image/tape
contracts, checksums, full vector-page and gateway reservations pass.
Earlier r99 boss/pause/joystick/vector tests remain applicable by code identity.

TARGETS
This archive is the full eight-level disk release. The separate stock64KB
read-only cartridge target remains unchanged and is not represented as an
eight-level cartridge by this release. Original source archives are preserved.
'''
(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype/README.txt').write_text(readme,encoding='ascii')
files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted((O/'rtype').iterdir())if p.is_file()}
manifest=dict(release='r100',date='2026-11-08',baseline='r99',baseline_hardware_report='User: yes that is working again now.',hardware_scope='Reported regression route; no additional all-level hardware coverage claimed.',runtime_identical_except_version_strings=True,hardware_tested_release='r99',fresh_release_tests=dict(startup=startup,fire=fire),files=files,stock64KB_target_unchanged=True)
(O/'release_manifest.json').write_text(json.dumps(manifest,indent=2))
z=O/'RType_TS2068_r100.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','release_manifest.json']:f.write(O/name,name)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
sha=hashlib.sha256(z.read_bytes()).hexdigest();(O/'SHA256SUMS.txt').write_text(sha+'  '+z.name+'\n',encoding='ascii')
latest=dict(release='r100',archive='build/releases/r100/'+z.name,sha256=sha,bytes=z.stat().st_size,hardware_baseline='r99',runtime_changes='Version strings only')
(R/'build/releases/latest.json').write_text(json.dumps(latest,indent=2));shutil.copy2(z,R/'build/releases/RType_TS2068_latest.zip')
print(json.dumps(latest))
