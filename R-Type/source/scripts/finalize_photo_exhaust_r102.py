from pathlib import Path
import json,hashlib,zipfile,functools
R=Path.cwd();B=R/'build/releases/r100';O=R/'build/fullgame/photo_exhaust_r102'
plume=json.loads((O/'plume_validation.json').read_text());assert plume['passed'];assert json.loads((O/'native_revisits_validation.json').read_text())['passed'];fire=json.loads((O/'unmodified_fire_validation.json').read_text());assert len(fire)==3 and all(x['passed']and x['region']==2 for x in fire)
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();a=(B/f'level{n:02d}_region.bin').read_bytes()
 if n==3:
  bridge=(O/'plume_bridge.bin').read_bytes();assert len(bridge)==25;assert a[0x1c8:0x200]==bytes([255])*56;assert b[0x1c8:0x1c8+len(bridge)]==bridge;assert b[0xd22d:0xd233]==bytes.fromhex('cdc801000000');allowed=set(range(0x1c8,0x1c8+len(bridge)))|set(range(0xd22d,0xd233));assert all(x==y or i in allowed for i,(x,y)in enumerate(zip(a,b)))
 else:assert b==a
 for name in [f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  t=(O/'rtype'/name).read_bytes();at=0;parts=[]
  while at<len(t):
   size=int.from_bytes(t[at:at+2],'little');v=t[at+2:at+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0
   if v[0]==255:parts.append(v[1:-1])
   at+=size+2
  assert b''.join(parts)==(b if name.startswith('LEVEL')else b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]))
for name in ['L3_runtime_art.bin','L3_runtime_image.bin','player_flame_phases.bin']:assert (O/name).read_bytes()==(B/name).read_bytes()
for name in ['RTCORE.TAP','RTPRELD.TAP','RTBOOT.TAP']:assert (O/'rtype'/name).read_bytes()==(B/'rtype'/name).read_bytes()
for name in ['launcher.bin','demand_loader.bin']:assert (O/name).read_bytes()==(B/name).read_bytes().replace(b'R100 PREPARING  ',b'R102 PREPARING  ')
for p in (O/'rtype').iterdir():
 if p.suffix.lower()!='.tap':continue
 t=p.read_bytes();at=0
 while at<len(t):
  size=int.from_bytes(t[at:at+2],'little');v=t[at+2:at+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;at+=size+2
summary=dict(passed=True,base='r100',only_level3_changed=True,bridge_bytes=25,native_call_site='HOME:F22D / source region:D22D',bridge='DOCK0:01C8',photo_frames_unchanged=True,no_added_ram_banks=True,plume=plume,normal_fire=fire,other_levels_byte_identical=True,player_flame_unchanged=True,hardware_confirmation_pending=True)
(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
readme='''R-Type TS2068 r102 - large L3 rocket photo-exhaust integration

Replace complete rtype folder, RESET, launch rtype/rt.tap.
Startup text R102 PREPARING. Select L3 and play the ordinary rocket encounter.
The boss shortcut skips this event; do not use it to check the plume.

The original approved photo-based four-frame artwork was already packed,
but the large rocket used a separate native draw call that bypassed it.
That dedicated call now uses the existing upgraded sprite renderer.
The saved photo-converted frames224..227 are used unchanged,48x16.
No replacement artwork was invented; the player flame is unchanged.
Only L3's native plume call and25bytes of previouslyunused low-ROM padding
change. All other levels,including L5,are byte-identical to working r100.
No extra RAM banks, sprite-size changes or renderer rewrites.

Ordinary L3 play confirms81draws cyclingall4frames;81stack/index/shared-ID
return checks pass, saved coordinates and executablebank preserved.
Rapid-fire stress includesgame-overbypass; separate three coldL3 startup/fire
scenarios pass with no gameplay/game-over patch. Cachedlevelroutes pass.
Static change whitelist/allTAPchecksums/LEVEL-STARTreconstruction/ZIPCRC pass.
Gameplay comparison PNG is decoded from actual before/after HOME screen RAM.
These are emulation results; hardware confirmation of this change is pending.

Keep r100 as your hardware-confirmed fallback. No unrelated r101 artwork
proposals are installed. The stock64KB cartridge remains unchanged.
'''
(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype/README.txt').write_text(readme,encoding='ascii')
z=O/'RType_TS2068_r102.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','validation_summary.json','plume_gameplay_comparison.png']:f.write(O/name,name)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z);print(hashlib.sha256(z.read_bytes()).hexdigest(),z.stat().st_size)
