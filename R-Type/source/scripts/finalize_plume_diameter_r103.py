from pathlib import Path
import json,hashlib,zipfile,functools,sys
R=Path.cwd();B=R/'build/fullgame/photo_exhaust_r102';O=R/'build/fullgame/plume_diameter_r103';sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack
c=json.loads((O/'diameter_contract.json').read_text());plume=json.loads((O/'plume_validation.json').read_text());assert c['passed']and plume['passed'];assert json.loads((O/'native_revisits_validation.json').read_text())['passed'];fire=json.loads((O/'unmodified_fire_validation.json').read_text());assert len(fire)==3 and all(x['passed']and x['region']==2 for x in fire)
meta=next(v for v in json.loads((O/'walker_runtime.json').read_text())if v['level']==3);a=(B/'L3_runtime_art.bin').read_bytes();b=(O/'L3_runtime_art.bin').read_bytes();assert len(a)==len(b)==2752;allowed=set();base=meta['assets'][0]['pointer']
for item in meta['assets']:
 if item['key']!='exhaust':continue
 p=item['pointer']-base;allowed.update(range(p,p+160));assert a[p+160:p+192]==b[p+160:p+192];assert all(b[p+y*2+1]&0xc0==0 for y in range(96))
assert all(x==y or i in allowed for i,(x,y)in enumerate(zip(a,b)))
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();a=(B/f'level{n:02d}_region.bin').read_bytes()
 if n==3:
  allowed=set(range(c['rawptr'],0x3a00))|{c['install_operand'],c['install_operand']+1};assert all(x==y or i in allowed for i,(x,y)in enumerate(zip(a,b)));assert b[:8192]==a[:8192];assert unpack(b[c['rawptr']:])==(O/'L3_runtime_art.bin').read_bytes();assert unpack(b[c['imageptr']:])==(B/'L3_runtime_image.bin').read_bytes();assert c['end']<=0x3a00
 else:assert a==b
 for name in [f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  t=(O/'rtype'/name).read_bytes();p=0;parts=[]
  while p<len(t):
   size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0
   if v[0]==255:parts.append(v[1:-1])
   p+=size+2
  assert b''.join(parts)==(b if name.startswith('LEVEL')else b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]))
for name in ['L3_runtime_image.bin','player_flame_phases.bin','plume_bridge.bin']:assert (O/name).read_bytes()==(B/name).read_bytes()
for name in ['RTCORE.TAP','RTPRELD.TAP','RTBOOT.TAP']:assert (O/'rtype'/name).read_bytes()==(B/'rtype'/name).read_bytes()
for name in ['launcher.bin','demand_loader.bin']:assert (O/name).read_bytes()==(B/name).read_bytes().replace(b'R102 PREPARING  ',b'R103 PREPARING  ')
for p in (O/'rtype').iterdir():
 if p.suffix.lower()!='.tap':continue
 t=p.read_bytes();at=0
 while at<len(t):
  size=int.from_bytes(t[at:at+2],'little');v=t[at+2:at+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;at+=size+2
summary=dict(passed=True,base='r102',nozzle_height=16,plume_join_height=16,frames=4,sprite_size=[48,16],nozzle_art_unchanged=True,renderer_bridge_and_player_unchanged=True,other_levels_identical=True,no_new_ram_banks=True,asset_layout=c,live_plume=plume,normal_fire=fire,hardware_confirmation_pending=True);(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
readme='''R-Type TS2068 r103 - large L3 plume diameter

Replace the complete rtype folder, RESET, launch rtype/rt.tap.
Startup: R103 PREPARING. Test ordinary L3 play; double-B skips this rocket.

The original photo-based plume is widened vertically to match the16pixel
nozzle mouth across all4frames. Its length and48x16sprite bounds are unchanged.
The nozzle's final8pixel column is byte-identical. No changes to player flame,
rocket draw bridge, renderer, hitbox, animation cadence or other seven levels.
Compressed artwork grows200bytes; its unchanged loader image is relocated
within the same reserved bank allocation, ending2FF9 below3A00. Runtime RAM
size is unchanged. No additional banks or live instructions in the renderer.

Actual gameplay81draws/all4frames and caller state pass while firing.
Three coldL3startup/fire timings pass without game-over bypass. Separate
400update stress uses game-over bypass; cachedlevel/native-source checks pass.
Static changed-byte whitelist, untouched nozzle/renderer/player/otherlevels,
packet decode identity, code/data bounds, TAPreconstruction/checksums, ZIPCRC
pass. Comparison PNG comes from actual gameplay screen RAM.
Hardware confirmation pending. Keep r100/r102 archives as fallbacks.
No unrelated artwork proposals included; stock64KB cartridge unchanged.
''';(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype/README.txt').write_text(readme,encoding='ascii')
z=O/'RType_TS2068_r103.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','validation_summary.json','plume_diameter_comparison.png']:f.write(O/name,name)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z);print(hashlib.sha256(z.read_bytes()).hexdigest(),z.stat().st_size)
