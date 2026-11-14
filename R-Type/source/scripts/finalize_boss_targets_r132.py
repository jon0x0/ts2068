from pathlib import Path
import json,hashlib,functools,zipfile
R=Path.cwd();O=R/'build/fullgame/boss_targets_r132';B=R/'build/fullgame/l4_shared_r131'
def j(n):return json.loads((O/n).read_text())
def blocks(p):
 b=p.read_bytes();out=[];at=0
 while at<len(b):
  n=int.from_bytes(b[at:at+2],'little');v=b[at+2:at+2+n];assert len(v)==n and n>=2 and functools.reduce(int.__xor__,v,0)==0;out.append((v[0],v[1:-1]));at+=n+2
 assert at==len(b);return out
reports=[]
for n in range(1,9):
 v=(O/f'level{n:02d}_region.bin').read_bytes();old=(B/f'level{n:02d}_region.bin').read_bytes();assert len(v)==65536
 if n not in [1,3,4]:assert v==old
 else:
  if n==1:ranges=[(0xd01,0xd27)]
  elif n==3:ranges=[(0xa01,0xa03),(next(x for x in j('generic_manifest.json')if x['level']==3)['motion_ptr'],0x3a00)]
  else:ranges=[(0xa01,0xa03),(j('l4_shared_contract.json')['imageptr'],0x3a00),(0xb400,0xb436),(0xbc09,0xbc0d)]
  assert all(any(a<=i<b for a,b in ranges)for i,(a,b)in enumerate(zip(old,v))if a!=b),n
 for kind in ['LEVEL','START']:
  data=b''.join(x for flag,x in blocks(O/'rtype'/f'{kind}{n:02d}.TAP')if flag==255);want=v if kind=='LEVEL'else b''.join(v[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]);assert data==want,(kind,n)
 report=j(f'L{n}_target_audit.json');assert report['level']==n and report['updates']>=300 and report['jumps']==1;reports.append(report)
required={1:[2],2:[1],3:[1,8,12,13,26,27],4:[4,7,10],5:[27],6:list(range(1,11)),7:[26],8:[15,21,22,23]}
summary=[]
for r in reports:
 n=r['level'];targets={v['slot']:v for v in r['targets']};proof=[]
 for slot in required[n]:
  t=targets[slot];assert t['owned']>0,(n,slot,'No collision ownership');proof.append({k:t.get(k)for k in ['slot','types','owned','clearLeftRay','onScreen']})
 summary.append(dict(level=n,updates=r['updates'],targets=proof,scope='Live collision ownership and observed ray opportunities; not an all-boss defeat claim.'))
assert j('weakpoint_gateway_validation.json')['passed'];assert j('native_revisits_validation.json')['passed'];assert len(j('native_revisits_validation.json')['results'])==12
assert all(x['passed']for x in j('unmodified_target_levels_fire_validation.json'))
d=j('l4_damage_probe.json');damage=[]
for addr in [0x851c,0x8537,0x8552]:
 hits=[h for h in d['healthWrites']if h['addr']==addr and h['pc']==0xa57d and h['old']>0 and h['v']==h['old']-1 and h['after']<947];assert hits,hex(addr);damage.append(dict(actor=hex(addr),real_shot_decrements=len(hits),lowest_health=min(h['v']for h in hits)))
(O/'boss_target_review.json').write_text(json.dumps(dict(levels=summary,L4_real_shot_damage=damage,L4_verified_victory=bool(d['cleared']),player_invulnerability_for_aim_tests=True,other5regions_bitidentical=True,hardware_tested=False),indent=2))
# Rebrand only the finished candidate, without touching the stable release pointer.
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R131 PREPARING  ',b'R132 PREPARING  '))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 n=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+n]).replace(b'R131 PREPARING  ',b'R132 PREPARING  ');block[-1]=functools.reduce(int.__xor__,block[:-1],0);v[at+2:at+2+n]=block;at+=n+2
p.write_bytes(v)
text='''R-Type TS2068 r132 - boss target repairs (512KB disk build)

Replace the complete rtype folder, reset, launch rtype/rt.tap.
Startup: R132 PREPARING. Keep the level files together; do not mix releases.

L1: restore native open-eye collision/drawing over the cached body.
L3: publish native gun/engine target ownership without a duplicate pixel copy.
L4: restore weak-point ownership over its parent hull; align front and middle
weak points with green artwork. Rear green target is24x16; health remains32.

Eight boss scenes audited for target ownership; three changed levels pass
unmodified cold-start/fire checks and12cold/cached transitions. Real player
shots damage all three L4 targets. Diagnostic aim tests use player protection.
See boss_target_review.json for measured coverage and whether a complete L4
victory was observed. This is not a claim that every boss was defeated or that
these changes have been tested on hardware.

Double B previews the current boss. Existing user-defined controls remain.
The stock64KB cartridge and stable r100 release are unchanged.

The interactive twin-launcher shading editor is a separate offline preview;
its unapproved trial artwork is not installed in this game build.
'''
(O/'README.txt').write_text(text);(O/'rtype/README.txt').write_text(text)
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((O/'rtype').iterdir())if p.is_file()};(O/'release_manifest.json').write_text(json.dumps(dict(version=132,files=manifest,review='boss_target_review.json',hardware_tested=False),indent=2))
z=O/'RType_TS2068_r132.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','release_manifest.json','boss_target_review.json']:f.write(O/name,name)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z,hashlib.sha256(z.read_bytes()).hexdigest());print(json.dumps(damage), 'verified victory',d['cleared'])
