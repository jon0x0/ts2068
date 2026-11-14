from pathlib import Path
import json,hashlib,zipfile,functools,sys
R=Path.cwd();B=R/'build/fullgame/plume_diameter_r103';O=R/'build/fullgame/full_plume_r104';sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack
c=json.loads((O/'diameter_contract.json').read_text());plume=json.loads((O/'plume_validation.json').read_text());assert c['passed']and plume['passed'];assert json.loads((O/'native_revisits_validation.json').read_text())['passed'];fire=json.loads((O/'unmodified_fire_validation.json').read_text());assert len(fire)==3 and all(x['passed']and x['region']==2 for x in fire)
meta=next(v for v in json.loads((O/'walker_runtime.json').read_text())if v['level']==3);a=(B/'L3_runtime_art.bin').read_bytes();b=(O/'L3_runtime_art.bin').read_bytes();assert len(a)==len(b)==2752;allowed=set();base=meta['assets'][0]['pointer']
for item in meta['assets']:
 if item['key']!='exhaust':continue
 p=item['pointer']-base;allowed.update(range(p,p+192));assert a[p+160:p+192]!=b[p+160:p+192];assert all(b[p+y*2+1]&0xc0==0 for y in range(96))
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
for name in ['launcher.bin','demand_loader.bin']:assert (O/name).read_bytes()==(B/name).read_bytes().replace(b'R103 PREPARING  ',b'R104 PREPARING  ')
for p in (O/'rtype').iterdir():
 if p.suffix.lower()!='.tap':continue
 t=p.read_bytes();at=0
 while at<len(t):
  size=int.from_bytes(t[at:at+2],'little');v=t[at+2:at+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;at+=size+2
summary=dict(passed=True,base='r103',legacy_exhaust_section_replaced=True,mechanical_rim_and_other_art_unchanged=True,sprite_size=[48,16],frames=4,renderer_bridge_and_player_unchanged=True,other_levels_identical=True,no_new_ram_banks=True,asset_layout=c,live_plume=plume,normal_fire=fire,hardware_confirmation_pending=True);(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
readme='''R-Type TS2068 r104 - complete large L3 rocket photo-exhaust

Replace complete rtype folder, RESET, launch rtype/rt.tap.
Startup R104 PREPARING. Test ordinary L3 play, not the double-B shortcut.

The checkered section preserved in r103 was old rocket exhaust, not nozzle.
It is now replaced by the photo-based plume across the complete48x16sprite,
right up to the separate mechanical rim. That rim/body artwork is unchanged.
All4frames retain the full16pixel plume diameter at the join. Sprite bounds,
draw bridge, renderer, animation cadence and player flame are unchanged.
No new RAM banks. Packed data remains within its reserved allocation;
the unchanged loader image has an updated compressed-source address only.
Other7levels, includingL5, remain byte-identical to r103/r100.

Actualgameplay81draws/all4poses and callerstate checks pass. Three coldL3fire
scenarios without game-over bypass pass. The separate rapidfire stress uses
game-over bypass; cold/cachedlevel/native-source checks pass. Static scope,
unchanged runtimecode/player/otherart, packetidentity, bank bounds, allTAP
reconstruction/checksums and ZIPCRC pass. Comparison image is actualgameRAM.
Hardware confirmation pending. Keep previous archives as fallbacks.
No unrelated artwork proposals included. Stock64KB cartridge unchanged.
''';(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype/README.txt').write_text(readme,encoding='ascii')
z=O/'RType_TS2068_r104.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','validation_summary.json','full_plume_comparison.png']:f.write(O/name,name)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z);print(hashlib.sha256(z.read_bytes()).hexdigest(),z.stat().st_size)
