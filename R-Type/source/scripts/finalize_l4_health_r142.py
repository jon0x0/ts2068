from pathlib import Path
import json,zipfile,hashlib,functools
R=Path.cwd();B=R/'build/fullgame/respawn_pickups_r141';O=R/'build/fullgame/l4_health_r142'
j=lambda n:json.loads((O/n).read_text())
r=j('settled_force_defeat.json');assert r['passed'] and r['victory'] and list(r['counts'].values())==[16]*3 and len(r['hits'])==48
for a in r['counts']:
 h=[q for q in r['hits'] if str(q['a'])==a];assert h[0]['from']==16 and h[-1]['to']==0
assert min(q['encounter']for q in r['hits'])>=200
assert j('respawn_recovery_validation.json')['passed']
a=(B/'level04_region.bin').read_bytes();b=(O/'level04_region.bin').read_bytes();diff=[i for i,(x,y)in enumerate(zip(a,b))if x!=y];assert diff==[0xcf5a,0xcf61,0xcf68];assert all(a[i]==32 and b[i]==16 for i in diff)
for n in range(1,9):
 if n!=4:assert (O/f'level{n:02d}_region.bin').read_bytes()==(B/f'level{n:02d}_region.bin').read_bytes()
assert (O/'rtype/RTCORE.TAP').read_bytes()==(B/'rtype/RTCORE.TAP').read_bytes()
count=0
for p in (O/'rtype').glob('*.TAP'):
 s=p.read_bytes();at=0;parts=[]
 while at<len(s):
  n=int.from_bytes(s[at:at+2],'little');v=s[at+2:at+2+n];assert len(v)==n and functools.reduce(int.__xor__,v)==0
  if v[0]==255:parts.append(v[1:-1])
  at+=n+2
 assert at==len(s);count+=1
 if p.name=='LEVEL04.TAP':assert b''.join(parts)==b
 if p.name=='START04.TAP':assert b''.join(parts)==b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7])
readme='''R-Type TS2068 r142 - easier L4 boss

Replace the complete rtype folder, reset, run rtype/rt.tap.
Each of the three L4 targets now has16 health instead of32:48 registered
one-point damage hits total instead of96. Native damage/victory rules,
openings, geometry and artwork are unchanged. All r141 pickup recovery
and r140 artwork selections are retained.

Native settled boss defeat passed in scripted emulation:16 hits per target,
48 total, native victory reached. Player protection only; no enemy health
or timer edits during the test. Two actual native death/respawn/recollect/
rear-dock/rear-fire cycles also passed. Static checks confirm only three
L4 region bytes changed; other seven levels and CORE are identical.
All TAP checksums and L4 reconstruction passed. Hardware testing pending.
Stable r100, stock64KB target and prior release archives are unchanged.
'''
(O/'README.txt').write_text(readme);(O/'rtype/README.txt').write_text(readme)
summary=dict(passed=True,health_per_target=16,previous_health=32,targets=3,total_registered_hits=48,native_victory=True,native_recovery_cycles=2,region_changes=diff,other7levels_and_CORE_unchanged=True,tap_files_checked=count,hardware_tested=False)
(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
(O/'release_manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((O/'rtype').iterdir())if p.is_file()},indent=2))
p=O/'RType_TS2068_r142.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED)as z:
 files=[(q,'rtype/'+q.name)for q in sorted((O/'rtype').iterdir())if q.is_file()]+[(O/n,n)for n in ['README.txt','validation_summary.json','release_manifest.json','health_contract.json','settled_force_defeat.json','respawn_recovery_validation.json']]
 for q,n in files:
  i=zipfile.ZipInfo(n,(2026,11,13,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,q.read_bytes())
with zipfile.ZipFile(p)as z:assert z.testzip()is None
sha=hashlib.sha256(p.read_bytes()).hexdigest()
entry=f'\n\n230. r142 L4 boss health halved (2026-11-13). Only native health sources EF5A/EF61/EF68 (region CF5A/CF61/CF68) changed32->16 relative to r141; all other region bytes, other7levels and CORE identical. Scripted settled encounter: normal pickup/docking/input, firing starts after200boss updates;16 native one-point hits per target,48total, native F59D victory at encounter{r["encounter"]}. Player protection only; no enemy HP/timer edits during test. Two real native death/respawn/recollect/rear-dock/rear-fire cycles PASS. All{count}TAP checksums and LEVEL04/START04 reconstruction, ZIP CRC PASS. Diagnostic trace_l4_health_init.mjs intentionally stopped at201 to locate32HP source writes; its failed defeat result is not credited as a passing test and may replace loose r141 diagnostic JSON; archived r141 ZIP unchanged. No new interrupt or hardware claim; unchanged L5/CORE preserves earlier reservations/proofs. Hardwarepending. build/fullgame/l4_health_r142/RType_TS2068_r142.zip SHA256{sha}. Scripts build_l4_health_r142.py,probe_l4_settled_force_r142.mjs,verify_respawn_recovery_r142.mjs,finalize_l4_health_r142.py. Stable100/stock64KB/referenceprojects/priorarchivesunchanged.\n'
with (R/'TEST_HISTORY.md').open('a',encoding='utf-8')as f:f.write(entry)
with (R/'PROJECT_STATE.md').open('a',encoding='utf-8')as f:f.write(f'\n2026-11-13 r142 L4 health16per target(previous32),48registeredhits total. Native victory/recovery/staticTAP/ZIP PASS; allr141pickup/artretained. build/fullgame/l4_health_r142/RType_TS2068_r142.zip SHA{sha}. TEST_HISTORY230;hardwarepending.\n')
(R/'docs/l4_health_r142.txt').write_text(readme+'\nSHA256 '+sha+'\n')
print(json.dumps(summary));print(p);print(sha)
