from pathlib import Path
import sys,json,zipfile,hashlib,functools
import numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack
B=R/'build/fullgame/boss_pickup_r136';O=R/'build/fullgame/l4_openings_r137'
j=lambda f:json.loads((O/f).read_text());ct=j('l4_shared_contract.json');oc=j('opening_contract.json');a=(O/'level04_region.bin').read_bytes();b=(B/'level04_region.bin').read_bytes()
allowed=[(ct['imageptr'],0x3a00),(0xa9c7,ct['external_end']),(0x2800,ct['pretab']),(0xb474,0xb567),(0xbc09,0xbc0d)]
assert all(any(lo<=i<hi for lo,hi in allowed)for i,(x,y)in enumerate(zip(a,b))if x!=y)
raw=bytearray((B/'L4_expected_cache.bin').read_bytes());native=bytes(0x4000)+(R/'build/fullgame/foundation/level04.raw').read_bytes();manifest=json.loads((R/'build/fullgame/foundation/manifest.json').read_text())['levels'][3]
assert hashlib.sha256((R/'build/fullgame/foundation/level04.payload').read_bytes()).hexdigest()==manifest['payload_sha256']
for ident,base,w,h in [(25,0,15,56),(26,1792,12,64),(27,3456,12,88)]:
 mask=np.load(R/f'build/graphics/l4_spectrum_openings_r137/original_empty_{ident}.npy');d=next(q for q in manifest['enemies']if q['id']==ident);ptr=d['pointer']
 for cy in range(h//8):
  for cx in range(w):
   tag=native[ptr];ptr+=1 if tag==54 else 9;assert bool(mask[cy,cx])==(tag==54)
   if tag==54:at=base+cx*h*2+cy*16;raw[at:at+16]=bytes(16)
assert bytes(raw)==(O/'L4_expected_cache.bin').read_bytes()
for q in oc['packets']:
 v=unpack(a[q['start']:]);start=0 if q['raw']==4096 else 4096;assert v==raw[start:start+q['raw']]
img=bytearray((B/'L4_runtime_image.bin').read_bytes());off=oc['coordinate_helper']-0xa000;img[off+4]=0xc9;img=img.replace(bytes.fromhex('32fba3'),bytes.fromhex('22fba3'));at=img.find(bytes.fromhex('cdb0db0020'),0x292,0x2d0);assert at>=0;img[at:at+5]=bytes.fromhex('3a03a4b720');at=img.find(bytes.fromhex('2174d411d8da01'));assert at>=0;img[at+7:at+9]=(203).to_bytes(2,'little');assert bytes(img)==(O/'L4_runtime_image.bin').read_bytes()==unpack(a[ct['imageptr']:])
assert a[0xbc09:0xbc0d]==bytes.fromhex('030121d8')
for lo,hi in [(0xed69,0xee06),(0xee06,0xeea7),(0xeea7,0xef00)]:assert a[lo-0x2000:hi-0x2000]==native[lo:hi]
assert unpack(a[0xb474:])==(O/'L4_snake_art.bin').read_bytes()[216:]
assert a[0x1c8:0x200]==b[0x1c8:0x200] and a[0x1fd4:0x1ff7]==b[0x1fd4:0x1ff7]
for f in ['snake_runtime_validation.json','native_revisits_validation.json','follower_validation.json','boss_pickup_validation.json']:assert j(f)['passed'],f
assert j('snake_runtime_validation.json')['ordinary_updates']==600 and len(j('native_revisits_validation.json')['results'])==12
assert all(q['passed']for q in j('unmodified_target_levels_fire_validation.json'))
defeat=j('settled_force_defeat.json');assert defeat['passed'] and defeat['victory'] and all(v==32 for v in defeat['counts'].values());assert len(defeat['hits'])==96 and min(q['encounter']for q in defeat['hits'])>=200
for addr in [0x851c,0x8537,0x8552]:
 hits=[q for q in defeat['hits']if q['a']==addr];assert len(hits)==32 and hits[0]['from']==32 and hits[-1]['to']==0
ray=j('L4_target_audit.json');targets={q['slot']:q for q in ray['targets']};assert targets[4]['settledClearLeft']>0 and targets[7]['settledClearLeft']>0 and targets[10]['settledClearRight']>0
assert (O/'rtype/RTCORE.TAP').read_bytes()==(B/'rtype/RTCORE.TAP').read_bytes()
def blocks(p):
 d=p.read_bytes();out=[];at=0
 while at<len(d):
  n=int.from_bytes(d[at:at+2],'little');v=d[at+2:at+2+n];assert len(v)==n and functools.reduce(int.__xor__,v,0)==0;out.append((v[0],v[1:-1]));at+=n+2
 assert at==len(d);return out
for n in range(1,9):
 region=(O/f'level{n:02d}_region.bin').read_bytes()
 if n!=4:assert region==(B/f'level{n:02d}_region.bin').read_bytes()
 for kind in ['LEVEL','START']:
  v=b''.join(q for flag,q in blocks(O/'rtype'/f'{kind}{n:02d}.TAP')if flag==255);expected=region if kind=='LEVEL'else b''.join(region[p*8192:(p+1)*8192]for p in [0,1,4,5,6,7]);assert v==expected
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R136 PREPARING  ',b'R137 PREPARING  '))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 n=int.from_bytes(v[at:at+2],'little');part=bytearray(v[at+2:at+2+n]).replace(b'R136 PREPARING  ',b'R137 PREPARING  ');part[-1]=functools.reduce(int.__xor__,part[:-1],0);v[at+2:at+2+n]=part;at+=n+2
p.write_bytes(v);blocks(p)
text="""R-Type TS2068 r137 - original L4 openings restored

Replace the COMPLETE rtype folder, reset, launch rtype/rt.tap.
Startup: R137 PREPARING. Do not mix build files.

Compared with actual original Spectrum boss animation. Restored its
transparent hull cells, native target positions and original target sizes:
front24x8, middle8x24, rear24x8. Retains ECM artwork/shading elsewhere.
The original three native hull-motion scripts are byte-identical.

The opening action comes from the hull pieces moving apart. The targets
were incorrectly placed inside filled hull in the earlier conversion.
All three now expose firing windows after entrance. Each has32health.
Post-entrance test waited200bossupdates, collected rearForce, then killed
rear/middle/front with32registered hits each and native victory at613.
Test player was protected; no enemy health/timer edits. Hardware pending.

r135 direct-copy optimization WITHDRAWN: matched visual tests revealed
repeated hull rows. Proven compositor restored. Restoring transparent cells reduces draw work:
matched settled-scene emulation used20.3%fewerTstates,25.5%higher cadence
thanr136 over60updates (200..260); not a hardware measurement.
L4 double-B two ordinary weapon pickups and faster native followers from
r136 retained. Rear Force lasers were verified after natural collection.
Other7level regions, CORE, loader behavior and all approved other art unchanged.
Joystick-only Force detach/recall is still not implemented; use configured key.

600ordinaryupdates,12cold/cached transitions, coldL1/L4/L5fire, pickup/rear
laser/nativefollowers, settled target rays/actual defeat,16TAP/static/ZIP checks.
Stable r100, r99 archive and stock64KB target unchanged.
"""
(O/'README.txt').write_text(text);(O/'rtype/README.txt').write_text(text)
summary=dict(passed=True,original_hull_scripts_bitidentical=True,original_empty_cells_restored=78,newly_cleared_cells=47,native_target_positions=True,target_sizes=[[24,8],[8,24],[24,8]],r135_direct_copy_withdrawn=True,other7levels_bitidentical=True,CORE_bitidentical=True,ordinary_updates=600,cold_cached_transitions=12,settled_fight_first_hit=min(q['encounter']for q in defeat['hits']),settled_fight_victory=defeat['encounter'],hits_per_target=defeat['counts'],player_protected=True,hardware_tested=False,settled_scene_cycle_reduction_percent=(1-220916441/277326480)*100,settled_scene_cadence_gain_percent=(277326480/220916441-1)*100)
(O/'validation_summary.json').write_text(json.dumps(summary,indent=2));(O/'release_manifest.json').write_text(json.dumps({q.name:hashlib.sha256(q.read_bytes()).hexdigest()for q in sorted((O/'rtype').iterdir())if q.is_file()},indent=2))
p=O/'RType_TS2068_r137.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED)as f:
 for q in sorted((O/'rtype').iterdir()):
  if q.is_file():f.write(q,'rtype/'+q.name)
 for name in ['README.txt','validation_summary.json','release_manifest.json','opening_contract.json','settled_force_defeat.json','Spectrum_ECM_animation_comparison.png','targets_open_annotated.png','performance_comparison.json']:f.write(O/name,name)
with zipfile.ZipFile(p)as f:assert f.testzip()is None
print(p,hashlib.sha256(p.read_bytes()).hexdigest())
