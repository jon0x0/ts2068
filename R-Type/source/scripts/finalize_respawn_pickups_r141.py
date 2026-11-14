from pathlib import Path
import json,zipfile,hashlib,functools
R=Path.cwd();B=R/'build/fullgame/l7_all_choices_r140';O=R/'build/fullgame/respawn_pickups_r141';j=lambda name:json.loads((O/name).read_text());r=j('respawn_recovery_validation.json');assert r['passed']and len(r['cycles'])==2 and all(q['actual_native_death']and q['force_lost']and q['recollected']and q['rear_fire']for q in r['cycles']);assert j('pickup_policy_validation.json')['passed'];assert j('native_revisits_validation.json')['passed'];assert len(j('native_revisits_validation.json')['results'])==12;assert all(q['passed']for q in j('unmodified_target_levels_fire_validation.json'))
a=(B/'level04_region.bin').read_bytes();b=(O/'level04_region.bin').read_bytes();diff=[i for i,(x,y)in enumerate(zip(a,b))if x!=y];assert all(0x1c8<=i<0x200 or 0x1fa3<=i<0x1fa6 for i in diff);assert b[0x4bd5:0x4bd8]==bytes.fromhex('32987a');assert j('respawn_contract.json')['helper_bytes']==55
for n in range(1,9):
 if n!=4:assert (O/f'level{n:02d}_region.bin').read_bytes()==(B/f'level{n:02d}_region.bin').read_bytes()
assert (O/'rtype/RTCORE.TAP').read_bytes()==(B/'rtype/RTCORE.TAP').read_bytes()
for p in (O/'rtype').glob('*.TAP'):
 src=p.read_bytes();at=0;parts=[]
 while at<len(src):
  n=int.from_bytes(src[at:at+2],'little');v=src[at+2:at+2+n];assert functools.reduce(int.__xor__,v)==0
  if v[0]==255:parts.append(v[1:-1])
  at+=n+2
 assert at==len(src)
 if p.name=='LEVEL04.TAP':assert b''.join(parts)==b
 if p.name=='START04.TAP':assert b''.join(parts)==b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7])
text='''R-Type TS2068 r141 - L4 boss weapon recovery

Replace the complete rtype folder, reset, run rtype/rt.tap.
All six r140 L7 artwork selections are retained unchanged.

From the L4 boss-return checkpoint onward, two ordinary Force upgrade pickups
are available near the player start: cells12/14,row10. If Force power is below2
and both pickup slots are empty, replacements appear. Existing pickups are
not overwritten and fully upgraded equipment does not generate more pickups.
They must be collected and docked normally; equipment is not granted directly.
The original double-B shortcut pickups remain available.

Two real native death->respawn->recollect->rear docking->rear fire cycles
passed in emulation. Ordinary scrolling/pickup-preservation conditions,
12cold/cached transitions and unmodified L4 cold startup/fire pass.
Only L4 bank0 helper/key-entry bytes changed, plus the version label. CORE,
other7level regions, all graphics, native respawn code and interrupt reservations
are unchanged. Hardware confirmation pending. Stable r100/stock64KB untouched.
'''
(O/'README.txt').write_text(text);(O/'rtype/README.txt').write_text(text)
summary=dict(passed=True,native_recovery_cycles=2,rear_fire_verified=True,no_auto_equipment=True,checkpoint_column=73,pickup_positions=[[12,10],[14,10]],cached_transitions=12,only_L4_bank0_changes=True,other7levels_and_CORE_unchanged=True,r140_art_retained=True,hardware_tested=False);(O/'validation_summary.json').write_text(json.dumps(summary,indent=2));(O/'release_manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((O/'rtype').iterdir())if p.is_file()},indent=2))
p=O/'RType_TS2068_r141.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED)as z:
 files=[(q,'rtype/'+q.name)for q in sorted((O/'rtype').iterdir())if q.is_file()]+[(O/name,name)for name in['README.txt','validation_summary.json','release_manifest.json','respawn_contract.json','pickup_policy_validation.json','respawn_recovery_validation.json','native_revisits_validation.json','unmodified_target_levels_fire_validation.json']]
 for q,name in files:
  info=zipfile.ZipInfo(name,(2026,11,13,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,q.read_bytes())
with zipfile.ZipFile(p)as z:assert z.testzip()is None
print(p,hashlib.sha256(p.read_bytes()).hexdigest())
