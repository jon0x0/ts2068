from pathlib import Path
import json,hashlib,subprocess,zipfile,functools
R=Path.cwd();O=R/'build/fullgame/startup_r66';B=R/'build/fullgame/hardware_fire_r65'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
oldsha=sha(B/'RType_TS2068_r65.zip');assert oldsha=='27187756c65a85e61e126f32f42315e48283852fa9a21491f7b5afc0f5210ff0'
for n in range(1,9):
 a=(B/f'level{n:02d}_region.bin').read_bytes();b=(O/f'level{n:02d}_region.bin').read_bytes();allowed=set()
 spans=[(0xa30,0xbc0),(0xdb,0xf7)]+([(0xa000,0xa43f)]if n==5 else[(0x3a00,0x3e3f)])
 for lo,hi in spans:allowed.update(range(lo,hi))
 assert all(x==y or k in allowed for k,(x,y)in enumerate(zip(a,b))),n
 # All changes in the native low loader-copy area must be the copied size word.
 ds=[k for k in range(0xa30,0xbc0)if a[k]!=b[k]];assert len(ds)<=2
assert (O/'rtype/RTCORE.TAP').read_bytes()==(B/'rtype/RTCORE.TAP').read_bytes()
assert (O/'boot_region.bin').read_bytes()==(B/'boot_region.bin').read_bytes()
def hashes():return {str(p.relative_to(O)):sha(p)for p in list(O.glob('*_region.bin'))+[O/'launcher.bin']+list((O/'rtype').glob('*.tap'))}
frozen=hashes();q=subprocess.run(['python','scripts/build_startup_r66.py'],capture_output=True,text=True);(O/'rebuild.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stdout+q.stderr;assert hashes()==frozen
readme='''R-Type TS2068 r66 - expanded RAM disk game

Replace the complete rtype folder and reset. Start lowercase rt.tap.
Keep all supplied files together; subdirectories below /TAP are supported.

During initial loading, press Shift-L briefly to queue Load All. LOAD ALL QUEUED
confirms acceptance. Release the keys; the request remains latched even if you
select another starting level with1-8. The required startup assets and shared
core finish and verify, then all missing levels load before the title opens.

Stages: READING FILES; VERIFYING MEMORY (full RAM readback); PREPARING GAME
(memory/graphics setup). PREP RAM is the brief context preparation before
Load All. The big numeric counter remains visible while files transfer.

L at title or Shift-L during play also loads all; completion returns to title.
P pauses (Shift-P if P is a defined gameplay key); P resumes. Keys are defined
by the game. Keyboard and both native joystick sockets operate together.
All r65 joystick-fire and keyboard-setup fixes are retained.

This release changes loading, not gameplay artwork or geometry. L2 terrain
presentation and remaining Spectrum artwork are still under investigation.
Offline L2 geometry/arcade comparison: build/graphics/l2_geometry_review_r66.
The remaining L3 hardware fragment is also unresolved. Stock64KB unchanged.
Scripted emulator checks pass; physical-hardware confirmation is still needed.
'''
(O/'rtype/README.txt').write_text(readme);(R/'docs/r66_readme.txt').write_text(readme)
def tape(p):
 raw=p.read_bytes();out=[];at=0
 while at<len(raw):
  l=int.from_bytes(raw[at:at+2],'little');v=raw[at+2:at+2+l];assert len(v)==l and functools.reduce(int.__xor__,v,0)==0;out.append(v);at+=l+2
 assert at==len(raw);return out
for p in (O/'rtype').glob('*.tap'):tape(p)
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();assert b''.join(v[1:-1]for v in tape(O/f'rtype/LEVEL{n:02d}.TAP')[1::2])==b;assert b''.join(v[1:-1]for v in tape(O/f'rtype/START{n:02d}.TAP')[1::2])==b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7])
zp=O/'RType_TS2068_r66.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED)as z:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file()and p.name!='RTBOOT.TAP':z.write(p,'rtype/'+p.name)
with zipfile.ZipFile(zp)as z:assert z.testzip()is None;assert 'rtype/rt.tap'in z.namelist()
assert sha(B/'RType_TS2068_r65.zip')==oldsha
report={'sha256':sha(zp),'bytes':zp.stat().st_size,'reproducible_primary_products':len(frozen),'all_tapes_valid':True,'gameplay_graphics_geometry_unchanged':True,'r65_zip_preserved':True,'checks':json.loads((O/'r66_checks.json').read_text()),'L2_scroll':'open; normal-route completed-world lower bands measured1px/update','L2_graphics':'isolated-head alternatives and original Spectrum comparison; not installed'};(O/'validation_summary.json').write_text(json.dumps(report,indent=2));print(report)
