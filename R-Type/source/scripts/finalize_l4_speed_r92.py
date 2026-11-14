from pathlib import Path
import json,functools,hashlib,zipfile
R=Path.cwd();O=R/'build/fullgame/l4_speed_r92';B=R/'build/fullgame/bank5_restore_r91'
for f in ['synth_equivalence.json','short_level_keys.json','restore_helper_validation.json','native_revisits_validation.json','four_frame_validation.json']:assert json.loads((O/f).read_text())['passed'],f
assert [x['level']for x in json.loads((O/'boss_preview_validation.json').read_text())['results']]==[4]
rr=json.loads((O/'walker_runtime.json').read_text());hashes={}
for r in rr:
 n=r['level'];assert (O/f'L{n}_runtime_art.bin').read_bytes()==(B/f'L{n}_runtime_art.bin').read_bytes();assert r['immutable_end']<=0x3a00;assert r['extension']['sprite_hook']<=0xa4ae
 if n==4:assert 0xa000+r['runtime_bytes']<=0xa9c7
for n in range(1,9):
 a=(B/f'level{n:02d}_region.bin').read_bytes();b=(O/f'level{n:02d}_region.bin').read_bytes();assert len(b)==65536
 assert n!=5 or b==a,'L5 uses HOME hotkeys; DOCK1 is occupied boss payload'
 allowed=set(range(0x3a00,0x3e00))if n!=5 else set()
 if n==4:allowed.update(range(0x2800,0x3a00));allowed.update(range(0xdc50,0xe000))
 assert all(i in allowed for i,(x,y)in enumerate(zip(a,b))if x!=y),(n,'unscoped difference')
 assert a[0x2000:0x2400]==b[0x2000:0x2400];assert a[0x8000:0xdc50]==b[0x8000:0xdc50]
 hashes[n]=hashlib.sha256(b).hexdigest()
 for name in [f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  t=(O/'rtype'/name).read_bytes();p=0;parts=[]
  while p<len(t):
   size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0
   if v[0]==255:parts.append(v[1:-1])
   p+=size+2
  assert p==len(t);assert b''.join(parts)==(b if name.startswith('LEVEL')else b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]))
for name in ['rt.tap','RTCORE.TAP','RTPRELD.TAP']:assert (O/'rtype'/name).read_bytes()==(B/'rtype'/name).read_bytes()
assert (O/'boot_region.bin').read_bytes()==(B/'boot_region.bin').read_bytes()
old=json.loads((R/'build/diagnostics/l4_speed_r92/masked_L4.json').read_text());new=json.loads((R/'build/diagnostics/l4_speed_r92_fast/masked_L4.json').read_text());historic=json.loads((R/'build/diagnostics/l4_historical_r67/masked_L4.json').read_text());keys=json.loads((O/'short_level_keys.json').read_text())
perf={'scope':'Deterministic 480 emulated 60Hz frames with same boss shortcut/control workload; world updates are not display FPS. Different builds run different subsequent game states.','sample_seconds':8,'r67_world_updates':historic['world_updates'],'r91_world_updates':old['world_updates'],'r92_world_updates':new['world_updates'],'ratio':new['world_updates']/old['world_updates'],'r91_player_position_changes':sum(a['x']!=b['x']for a,b in zip(old['positions'],old['positions'][1:])),'r92_player_position_changes':sum(a['x']!=b['x']for a,b in zip(new['positions'],new['positions'][1:])),'short_level_keys':keys,'tradeoff':'L4 large components25/26/27 use native horizontal cell steps; fine2px vertical movement retained. Other bosses unchanged.','hardware_pending':True};assert perf['ratio']>=2;(O/'performance_comparison.json').write_text(json.dumps(perf,indent=2))
readme='''R-Type TS2068 r92 - L4 speed trial

Replace the complete rtype folder, RESET, launch rtype/rt.tap.

L4 large boss components25/26/27 retain original artwork and size. No new
palette, scale or hit-box changes. Visibility checks no longer perform full
color synthesis. Unshifted full cells use raw paired rows directly.

TRADEOFF: these three L4 pieces use native horizontal cell steps, rather
than synthesizing every2pixel horizontal phase. Fine2pixel vertical movement
is retained. Other bosses retain their existing movement. This is a speed
trial, not a claim that all boss animation is now fast.

Same480emulated60Hzframe workload: r67=3worldupdates,r91=3,r92=6.
This doubles measured world progress, not screen refresh or every sprite's
animation rate. World updates are still expensive. Player position changes
were147 versus136 in that sample; the player remains separately updated.

During the L4 fight, brief L then number presses are captured by IRQ and
consumed at the next safe main boundary. Four-frame key presses were
remembered; level change accepted17frames after the number began. Disk load
time is separate. The latch does not abort a drawing operation mid-write.

4096row/phase/flip/color equivalence cases,21animation groups, source restore
helper,12cached/coldrevisits, L4bossgameplay, bounds,TAPreconstruction/checksums,
ZIPCRC pass. Actual hardware testing pending. All runtime artwork unchanged
r91. Includes r91native source restoration. Stock64KB target unchanged.

See performance_comparison.json for the measured comparison and limits.
'''
(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype/README.txt').write_text(readme,encoding='ascii');(O/'validation_summary.json').write_text(json.dumps(dict(passed=True,region_sha256=hashes,artwork_unchanged=True,hardware_pending=True,stock64KB_unchanged=True),indent=2))
z=O/'RType_TS2068_r92.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','performance_comparison.json']:f.write(O/name,name)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z);print(hashlib.sha256(z.read_bytes()).hexdigest(),z.stat().st_size);print(perf)
