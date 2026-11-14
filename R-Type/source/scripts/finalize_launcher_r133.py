from pathlib import Path
import sys,json,zipfile,hashlib,functools
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack
B=R/'build/fullgame/boss_targets_r132';O=R/'build/fullgame/launcher_r133';ct=json.loads((O/'launcher_contract.json').read_text());c=json.loads((O/'l4_shared_contract.json').read_text());a=(O/'level04_region.bin').read_bytes();b=(B/'level04_region.bin').read_bytes();allowed=[(c['rawptr'],0x3a00),tuple(ct['launcher_packet']),tuple(ct['prefix_packet']),(0xa01,0xa03),(0xddbb,0xddbd),(0xdee1,0xdee3),(0xdf6c,0xdf6e)]
assert all(any(lo<=i<hi for lo,hi in allowed)for i,(x,y)in enumerate(zip(a,b))if x!=y),[(hex(i),x,y)for i,(x,y)in enumerate(zip(a,b))if x!=y and not any(lo<=i<hi for lo,hi in allowed)]
assert a[0xb400:0xb436]==b[0xb400:0xb436] and a[0xbc09:0xbc0d]==b[0xbc09:0xbc0d];assert ct['code_end']<=0xa9c7 and ct['packed_end']<=0x3a00
z=zipfile.ZipFile(R/'build/graphics/l4_launcher_selected_r133/selected_assets.zip');raw=b''.join(z.read(f'launcher/frame_{i:02d}.pairs.bin')for i in range(3));assert raw==(O/'L4_launcher_art.bin').read_bytes();assert all(v&192==0 for v in raw[1::2]);assert unpack(a[ct['launcher_packet'][0]:])==raw
assert (O/'L4_runtime_art.bin').read_bytes()==(B/'L4_runtime_art.bin').read_bytes();assert unpack(a[c['imageptr']:])==(O/'L4_runtime_image.bin').read_bytes()
for file in ['launcher_runtime_validation.json','launcher_pose_validation.json','native_revisits_validation.json']:
 d=json.loads((O/file).read_text());assert d['passed'],file
r=json.loads((O/'launcher_pose_validation.json').read_text());mapping={q['native']:q.get('id')for q in r['native_mappings']};assert all(mapping[i]==184+i-52 for i in [52,53,54]);assert json.loads((O/'launcher_runtime_validation.json').read_text())['ordinary_updates']==600;assert len(json.loads((O/'native_revisits_validation.json').read_text())['results'])==12
assert all(x['passed']for x in json.loads((O/'unmodified_target_levels_fire_validation.json').read_text()))
d=json.loads((O/'l4_damage_probe.json').read_text());assert d['cleared'];assert all(sum(x['pc']==0xa57d and x['old']>0 and x['v']==x['old']-1 for x in d['healthWrites']if x['addr']==p)==32 for p in [0x851c,0x8537,0x8552])
def blocks(p):
 v=p.read_bytes();out=[];at=0
 while at<len(v):
  n=int.from_bytes(v[at:at+2],'little');part=v[at+2:at+2+n];assert len(part)==n and functools.reduce(int.__xor__,part,0)==0;out.append((part[0],part[1:-1]));at+=n+2
 assert at==len(v);return out
for n in range(1,9):
 region=(O/f'level{n:02d}_region.bin').read_bytes()
 if n!=4:assert region==(B/f'level{n:02d}_region.bin').read_bytes()
 for kind in ['LEVEL','START']:
  got=b''.join(q for flag,q in blocks(O/'rtype'/f'{kind}{n:02d}.TAP')if flag==255);want=region if kind=='LEVEL'else b''.join(region[p*8192:(p+1)*8192]for p in[0,1,4,5,6,7]);assert got==want
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R132 PREPARING  ',b'R133 PREPARING  '))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 n=int.from_bytes(v[at:at+2],'little');part=bytearray(v[at+2:at+2+n]).replace(b'R132 PREPARING  ',b'R133 PREPARING  ');part[-1]=functools.reduce(int.__xor__,part[:-1],0);v[at+2:at+2+n]=part;at+=n+2
p.write_bytes(v);blocks(p)
text='''R-Type TS2068 r133 - selected L4 twin rocket launcher

Replace the complete rtype folder, reset, launch rtype/rt.tap.
Startup: R133 PREPARING. Do not mix files from different builds.

Your assisted Spectrum launcher selection is installed exactly at24x24:
native52upright,53diagonal,54horizontal. Existing native flips/directions stay.
Shared assist83, brightness39, contrast40, saturation74, gamma1.12, SierraLite.
No invented animation or arcade pose substitution. Other7levels unchanged.

Preserves r132 boss repairs. All3L4weakpoints again lose32health from real
shots and reach the native victory routine in emulation (protected player).
600ordinaryupdates, actual pose selector/RAM bytes,12cold/cached transitions,
unmodified L4startup/fire, all16level tapes/checksums and ZIP verified.
Hardware testing remains pending. Stable r100 and stock64KB remain unchanged.
'''
(O/'README.txt').write_text(text);(O/'rtype/README.txt').write_text(text)
summary=dict(passed=True,selected_pose_order=[52,53,54],runtime_ids=[184,185,186],pair_bytes=len(raw),size=[24,24],choices_sha256=ct['choices_sha256'],other7levels_bitidentical=True,old3424live_art_bytes_unchanged=True,ordinary_updates=600,cold_cached_transitions=12,L4_native_victory=True,player_protected_in_aim_test=True,hardware_tested=False,code_end=ct['code_end'],packed_end=ct['packed_end']);(O/'validation_summary.json').write_text(json.dumps(summary,indent=2));(O/'release_manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((O/'rtype').iterdir())if p.is_file()},indent=2))
p=O/'RType_TS2068_r133.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED)as f:
 for q in sorted((O/'rtype').iterdir()):
  if q.is_file():f.write(q,'rtype/'+q.name)
 for name in ['README.txt','validation_summary.json','release_manifest.json','launcher_contract.json']:f.write(O/name,name)
with zipfile.ZipFile(p)as f:assert f.testzip()is None
print(p,hashlib.sha256(p.read_bytes()).hexdigest())
