"""Package only after final TAP display/loading/collision/IRQ evidence passes."""
from pathlib import Path
import json,hashlib,zipfile,functools,shutil
R=Path(__file__).resolve().parents[1];O=R/'build/fullgame/normal_black_r161';j=lambda n:json.loads((O/n).read_text())
a=json.loads((R/'build/normal_black_audit/tap_fixed.json').read_text());assert a['passed']and len(a['levels'])==8 and all(v['maxExposed']==0 for v in a['levels'])
assert j('native_revisits_validation.json')['passed'] and len(j('native_revisits_validation.json')['results'])==14
assert j('visible_collision_validation.json')['passed'] and len(j('visible_collision_validation.json')['cases'])==7
assert j('all_vector_validation.json')['passed']and j('all_vector_validation.json')['cases']==256
assert all(v['passed']for v in j('unmodified_target_levels_fire_validation.json'))
count=0
for p in (O/'rtype').iterdir():
 if p.suffix.lower()!='.tap':continue
 data=p.read_bytes();at=0;parts=[]
 while at<len(data):
  n=int.from_bytes(data[at:at+2],'little');q=data[at+2:at+2+n];assert len(q)==n and functools.reduce(int.__xor__,q)==0
  if q[0]==255:parts.append(q[1:-1])
  at+=n+2
 assert at==len(data);count+=1
 if p.stem.startswith('LEVEL'):assert b''.join(parts)==(O/f'level{int(p.stem[-2:]):02d}_region.bin').read_bytes()
 if p.stem.startswith('START'):
  b=(O/f'level{int(p.stem[-2:]):02d}_region.bin').read_bytes();assert b''.join(parts)==b''.join(b[k*8192:(k+1)*8192]for k in [0,1,4,5,6,7])
assert count==20
text='R-Type TS2068 r161 - normal-black title, score and preparation displays\n\nReplace the complete rtype directory, reset, and start rtype/rt.tap.\nThe directory can be inside a subdirectory of the TAP folder. Keep the 20 TAP\nfiles together. Uses 512KB expanded RAM to cache all eight levels, or loads\none level at a time on demand. Individual stock64KB cartridges are separate.\n\nBright black remains a valid hardware colour. This release fixes game-produced\nbright black where normal-black space/paper is intended. The normal animated\nscore colours remain. TAP score paths and L7 preparation text are corrected;\nthe title initializer keeps ECM active while copying the native attribute plane.\nNo emulator palette flattening is required. No asset rescaling, bank relocation,\nnew buffers or gameplay/collision changes. Valid nonblack bright ECM pairs stay.\n\nENTER defines gameplay keys; suggested movement O P Q A, fire SPACE and Force\nENTER. Keyboard and native joystick work together. L then1..8 changes level;\nShift-L preloads levels; B, release, B jumps to the current boss with pickups;\nM toggles music; Shift-P pauses (plain P also works if not a selected game key).\n\nValidation: all8 cold-loaded title/score/gameplay frame audits;14 cold/cached\ntransitions, cold L1/L5 firing, displayed-frame projectile collision including\nnegative controls, L5 boss160updates/all256IM2targets. Actual IRQ return probes\nat0/255; remaining targets identical. Scripted emulation, not hardware or full\nall-boss playthrough confirmation. Previous archives and stable r99/r100 intact.\n'
(O/'README.txt').write_text(text,encoding='utf-8');(O/'rtype/README.txt').write_text(text,encoding='utf-8')
shutil.copy2(R/'build/normal_black_audit/tap_fixed.json',O/'normal_black_display_validation.json')
summary=dict(passed=True,release='r161',display_levels=8,display_frames=sum(v['framesAudited']for v in a['levels']),unintended_bright_black_pixels=0,cold_cached_transitions=14,tap_files=20,all_vector_targets=256,hardware_tested=False)
(O/'validation_summary.json').write_text(json.dumps(summary,indent=2));(O/'release_manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((O/'rtype').iterdir())if p.is_file()},indent=2))
p=O/'RType_TS2068_TSPico_r161.zip';assert not p.exists(),'Do not overwrite an archive'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED)as z:
 files=[(q,'rtype/'+q.name)for q in sorted((O/'rtype').iterdir())if q.is_file()]+[(O/n,n)for n in ['README.txt','release_manifest.json','validation_summary.json','normal_black_contract.json','normal_black_display_validation.json','native_revisits_validation.json','visible_collision_validation.json','all_vector_validation.json','unmodified_target_levels_fire_validation.json']]
 for q,name in files:
  i=zipfile.ZipInfo(name,(2026,11,15,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,q.read_bytes())
with zipfile.ZipFile(p)as z:assert z.testzip()is None
print(p);print(hashlib.sha256(p.read_bytes()).hexdigest())
