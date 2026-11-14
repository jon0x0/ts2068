from pathlib import Path
import sys,json,zipfile,hashlib,functools
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack
B=R/'build/fullgame/l4_speed_r135';O=R/'build/fullgame/boss_pickup_r136';ct=json.loads((O/'launcher_contract.json').read_text());c=json.loads((O/'l4_shared_contract.json').read_text());a=(O/'level04_region.bin').read_bytes();b=(B/'level04_region.bin').read_bytes();allowed=[(0x572c,0x572e),(0x59ec,0x59f9),(0x1c8,0x200),(0x1ff1,0x1ff4),(0xb474,0xb567)]+list(map(tuple,json.loads((O/'snake_contract.json').read_text())['packets']))+[(c['rawptr'],0x3a00),tuple(ct['launcher_packet']),tuple(ct['prefix_packet']),(0xa01,0xa03),(0xddbb,0xddbd),(0xdee1,0xdee3),(0xdf6c,0xdf6e)]
assert all(any(lo<=i<hi for lo,hi in allowed)for i,(x,y)in enumerate(zip(a,b))if x!=y),[(hex(i),x,y)for i,(x,y)in enumerate(zip(a,b))if x!=y and not any(lo<=i<hi for lo,hi in allowed)]
assert a[0xb400:0xb436]==b[0xb400:0xb436] and a[0xbc09:0xbc0d]==b[0xbc09:0xbc0d];assert ct['code_end']<=0xa9c7 and ct['packed_end']<=0x3a00
sc=json.loads((O/'snake_contract.json').read_text());allowed+=list(map(tuple,sc['packets']))
# Recheck all changed bytes with the two new immutable snake packets allowed.
assert all(any(lo<=i<hi for lo,hi in allowed) for i,(x,y) in enumerate(zip(a,b)) if x!=y)
z=zipfile.ZipFile(R/'convref/rtype-l4-snake-assets.zip')
frames=[z.read(f'snake/frame_{i:02d}.pairs.bin') for i in range(3)];mirrored=b''.join(frames[1][col*48+y*2:col*48+y*2+2] for col in range(3) for y in range(23,-1,-1));assert (O/'L4_snake_art.bin').read_bytes()==frames[0]+mirrored+frames[2]
raw=(O/'L4_snake_art.bin').read_bytes();assert len(raw)==432
assert all(v&192==0 for v in raw[1::2])
expanded=b''.join(unpack(a[lo:]) for lo,hi in sc['packets']);assert expanded[:432]==raw and expanded[432:]==bytes.fromhex('3afba3b7c8473a03a4b8c9')
assert sc['base']==0xda00 and sc['end']==0xdbb0 and 0xd950<=sc['base']<sc['end']<=0xdc50
assert sc['code_end']<=0xa9c7 and sc['packed_end']<=0x3a00
assert (O/'L4_runtime_art.bin').read_bytes()==(B/'L4_runtime_art.bin').read_bytes();assert unpack(a[c['imageptr']:])==(O/'L4_runtime_image.bin').read_bytes()
for file in ['snake_runtime_validation.json','native_revisits_validation.json']:
 d=json.loads((O/file).read_text());assert d['passed'],file
r=json.loads((O/'snake_runtime_validation.json').read_text());mapping={q['native']:q.get('id')for q in r['native_mappings']};assert all(mapping[i]==v for i,v in [(33,189),(34,188),(35,187),(52,184),(53,185),(54,186)]);assert json.loads((O/'snake_runtime_validation.json').read_text())['ordinary_updates']==600;assert len(json.loads((O/'native_revisits_validation.json').read_text())['results'])==12
assert all(x['passed']for x in json.loads((O/'unmodified_target_levels_fire_validation.json').read_text()))
d=json.loads((O/'l4_damage_probe.json').read_text());assert d['cleared'];assert all(sum(x['pc']==0xa57d and x['old']>0 and x['v']==x['old']-1 for x in d['healthWrites']if x['addr']==p)==32 for p in [0x851c,0x8537,0x8552])
def blocks(p):
 v=p.read_bytes();out=[];at=0
 while at<len(v):
  n=int.from_bytes(v[at:at+2],'little');part=v[at+2:at+2+n];assert len(part)==n and functools.reduce(int.__xor__,part,0)==0;out.append((part[0],part[1:-1]));at+=n+2
 assert at==len(v);return out
for n in range(1,9):
 region=(O/f'level{n:02d}_region.bin').read_bytes()
 if n!=4:
  prev=(B/f'level{n:02d}_region.bin').read_bytes();assert all(0x572c<=i<0x572e or 0x59ec<=i<0x59f9 for i,(x,y)in enumerate(zip(region,prev))if x!=y)
 for kind in ['LEVEL','START']:
  got=b''.join(q for flag,q in blocks(O/'rtype'/f'{kind}{n:02d}.TAP')if flag==255);want=region if kind=='LEVEL'else b''.join(region[p*8192:(p+1)*8192]for p in[0,1,4,5,6,7]);assert got==want
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R135 PREPARING  ',b'R136 PREPARING  '))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 n=int.from_bytes(v[at:at+2],'little');part=bytearray(v[at+2:at+2+n]).replace(b'R135 PREPARING  ',b'R136 PREPARING  ');part[-1]=functools.reduce(int.__xor__,part[:-1],0);v[at+2:at+2+n]=part;at+=n+2
p.write_bytes(v);blocks(p)
core_before=b''.join(q for flag,q in blocks(B/'rtype/RTCORE.TAP')if flag==255);core_after=b''.join(q for flag,q in blocks(O/'rtype/RTCORE.TAP')if flag==255)
fc=json.loads((O/'follower_contract.json').read_text());expected=bytearray(core_before)
for q in fc['patches']:
 off=q['address']-0x8000;old=bytes.fromhex(q['old']);new=bytes.fromhex(q['new']);assert expected[off:off+len(old)]==old;expected[off:off+len(new)]=new
assert core_after==expected
l5=(O/'level05_region.bin').read_bytes();prev=(B/'level05_region.bin').read_bytes();assert l5[0x8f00:0x9001]==prev[0x8f00:0x9001] and l5[0x1c8:0x200]==prev[0x1c8:0x200]
for name in ['follower_validation.json','boss_pickup_validation.json']:
 assert json.loads((O/name).read_text())['passed']
pick=json.loads((O/'boss_pickup_validation.json').read_text());assert pick['docked_side']==2 and pick['collected_force_power']>=2 and any(q['rear']==2 and q['direction']in[1,3,5]for q in pick['force_beams'])
text="""R-Type TS2068 r136 - L4 boss pickup and faster followers

Replace the complete rtype folder, reset, launch rtype/rt.tap.
Startup: R136 PREPARING. Do not mix files between releases.

The L4 double-B shortcut places TWO ordinary weapon collectibles near the
ship. Collect both to obtain the powered Force; no automatic equipment.
The tested collection route docks it at the rear and produces native
backward-firing lasers. Use your configured Force detach/recall control
to change docking; move around the hull to attack from the other side.

Force recall movement now runs each game update instead of one in four.
Orbiting guns follow one update behind instead of three. These are native
logic improvements; their visual redraw still shares the main update rate.
Normal level progression and pickup/weapon rules are preserved.

L4 has 32-health targets; no visible opening/closing animation is asserted.
Settled-phase hull overlap can obstruct target access; this build does not
repair that geometry. The previous closed-target wording
was not supported by the tests. Target damage and native victory rechecked.
Preserves r135 drawing change and all approved artwork.

Verified native collection, rear docking and rear laser descriptors;
native follower routines; cold L1/L4/L5 startup/fire;12cached transitions;
600ordinaryupdates; real-shot L4 defeat with protected test player;
all16level tapes/checksums and ZIP integrity. Hardware testing pending.
Stable r100 and stock64KB remain unchanged.
"""
(O/'README.txt').write_text(text);(O/'rtype/README.txt').write_text(text)
summary=dict(passed=True,selected_pose_order=[33,34,35],runtime_ids=[189,188,187],pair_bytes=len(raw),snake_bank=6,snake_range=[0xda00,0xdbb0],size=[24,24],package_sha256=sc['package_sha256'],other7levels_bitidentical=False,other7levels_native_follower_changes_only=True,old3424live_art_bytes_unchanged=True,ordinary_updates=600,cold_cached_transitions=12,L4_native_victory=True,player_protected_in_aim_test=True,hardware_tested=False,code_end=sc['code_end'],packed_end=sc['packed_end']);(O/'validation_summary.json').write_text(json.dumps(summary,indent=2));(O/'release_manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((O/'rtype').iterdir())if p.is_file()},indent=2))
p=O/'RType_TS2068_r136.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED)as f:
 for q in sorted((O/'rtype').iterdir()):
  if q.is_file():f.write(q,'rtype/'+q.name)
 for name in ['README.txt','validation_summary.json','release_manifest.json','launcher_contract.json','snake_contract.json','speed_contract.json','follower_contract.json','follower_validation.json','boss_pickup_validation.json']:f.write(O/name,name)
with zipfile.ZipFile(p)as f:assert f.testzip()is None
print(p,hashlib.sha256(p.read_bytes()).hexdigest())
