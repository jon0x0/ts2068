from pathlib import Path
import json,hashlib,functools,zipfile,sys
R=Path.cwd();O=R/'build/fullgame/walker_selection_r89';B=R/'build/fullgame/l1_machinery_r84';sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack
assert json.loads((O/'review_application_validation.json').read_text())['passed'];assert json.loads((O/'four_frame_validation.json').read_text())['passed'];assert json.loads((O/'repeated_jumps_validation.json').read_text())['passed'];assert json.loads((O/'initial_attribute_validation.json').read_text())['attributeAudits']==12
assert 'Targets 20608' in(O/'gameplay_test.log').read_text();meta=json.loads((O/'generic_manifest.json').read_text());rr=json.loads((O/'walker_runtime.json').read_text());hashes={}
for n in range(1,9):
 a=(B/f'level{n:02d}_region.bin').read_bytes();b=(O/f'level{n:02d}_region.bin').read_bytes();assert len(b)==65536;allowed=set();assert a[0x2000:0x2400]==b[0x2000:0x2400];assert a[0x3a00:0x4000]==b[0x3a00:0x4000];assert a[0x4000:0x8000]==b[0x4000:0x8000]
 for phase in range(8):
  at=0xed80+phase*96;assert a[at:at+32]==b[at:at+32]and a[at+64:at+96]==b[at+64:at+96]
  for x in[phase+1,phase+2]:allowed.add(at+32+12+x//8)
 if n in[1,3,4,6,7]:
  allowed.update(range(0x2800 if n==4 else 0x2400,0x3a00));allowed.update(range(0xdeae,0xdf30))
  if n==4:allowed.update(range(0xa9c7,0xb30c))
  if n==7:allowed.update(range(0xaeb1,0xb147));allowed.update(range(0xa998,0xab4e))
  r=next(r for r in rr if r['level']==n);assert r['immutable_end']<=0x3a00;assert unpack(b[r['motion_ptr']:])==(O/f'L{n}_runtime_image.bin').read_bytes();assert 0xa000+r['runtime_bytes']<=r['assets'][0]['pointer'];assert r['assets'][0]['pointer']+r['art_bytes']<=0xc000;cache=b[0xdc50:0xdf30];off=cache.find(bytes.fromhex('dd21'),0x200);tab=int.from_bytes(cache[off+2:off+4],'little');blocks=[[int.from_bytes(b[tab+1+4*k:tab+3+4*k],'little'),int.from_bytes(b[tab+3+4*k:tab+5+4*k],'little')]for k in range(b[tab])];mm=next(m for m in meta if m['level']==n);mm['preload_blocks']=blocks;mm['cache_symbols'].update(PRELOAD_TABLE=tab,MOTION_PTR=r['motion_ptr'],MOTION_BYTES=r['runtime_bytes'],WARMUP_ENTRY=r['extension']['load_new_art']);mm['runtime_art_pointer']=r['assets'][0]['pointer'];mm['runtime_art_bytes']=r['art_bytes'];mm['legacy_motion_source_superseded']=True
 assert all(i in allowed for i,(x,y)in enumerate(zip(a,b))if x!=y),(n,'unscoped difference');hashes[n]=hashlib.sha256(b).hexdigest()
 for name in[f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  t=(O/'rtype'/name).read_bytes();p=0;parts=[]
  while p<len(t):
   size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0
   if v[0]==255:parts.append(v[1:-1])
   p+=size+2
  assert b''.join(parts)==(b if name.startswith('LEVEL')else b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]))
for name in['rt.tap','RTCORE.TAP','RTPRELD.TAP']:assert(O/'rtype'/name).read_bytes()==(B/'rtype'/name).read_bytes()
(O/'generic_manifest.json').write_text(json.dumps(meta,indent=2));summary=dict(passed=True,region_sha256=hashes,exact_reviewed_indices=True,accepted_and_unreviewed_assets_unchanged=True,affected_gameplay_levels=[1,3,4,6,7],unchanged_levels_vs_r86=[2,5,8],cold_cached_jumps=11,initial_attribute_audits=12,hardware_pending=True,stock64KB_unchanged=True);(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
readme='''R-Type TS2068 r89 - saved review choices and new gun walker

Replace the COMPLETE rtype folder, RESET, launch rtype/rt.tap.
Existing key selection, both native joysticks, B-release-B boss preview,
L then number level jump, Shift-L Load All, P pause and M music remain.

Applied rtype-walker-candidates-r88.json EXACTLY:
- L6 head32 B: brightness52 contrast59 saturation82 gamma0.87.
- L1 large40 C: brightness51 contrast67 saturation80 gamma1.44.
- Before31 round3 KEEP: exact earlier appearance and three native drawings
  in its four-step loop (second pose repeated), no invented fourth drawing.
Unreviewed entries, including L7 head, are unchanged. Accepted L3 yellow94 and
rocket exhaust are byte-identical to r86. L1 stomach machinery is retained.

The rejected blue_21..25 set is replaced on L1/L4/L7 by new option B: a new
arcade-reference-inspired gun-walker redraw, normal32x24 walking and24x24
raised-gun footprints. Four distinct walking poses plus two raising poses,
shared body alignment and settings, calibrated blue armour/silver cooling ribs.
This is generated reference-inspired art, not an original arcade asset.
Alternative A is a fresh arcade conversion; C is a larger40x32 proposal only.
Comparison with live exact RPC controls:
build/graphics/walker_selection_r89/index.html
The review JSON for these alternatives is separate from the applied r88 file.

Actual RPC CPU adjustments, segment-coverage pairs, Sierra Lite and source-red
cell constraints from the r88 review. Normal palette selected at conversion;
no later brightness normalization. All installed selected palette indices
match their converted/kept output exactly. No geometry enlargement installed.
Native movement scripts, loader and common game code are unchanged.

Verified: all21 Z80 dispatch groups, distinct poses (keep baseline has3), exact
selected indices30frames,33frozen frames, affected1/3/4/6/7gameplay routes with
extendedL3/L7,11cold/cachedlevel transitions and bank5readback,12attributeaudits,
allTAP checksums and level reconstruction, memory bounds and ZIPCRC. Levels
2/5/8arebyte-identicalr86. Hardware confirmation pending. Expanded-RAM/disk
build only; existing stock64KB cartridge unchanged.

Build sources: prepare_walker_selection_r89.py,convert_walker_selection_r89.mjs,
integrate_walker_selection_r89.py,build_walker_selection_r89.py,
finish_player_flame_r89.py,verify_review_application_r89.py,
finalize_walker_selection_r89.py. Runtime code images are compressed and the
extension generator supersedes legacyL_motion.asm alone. Unchanged existing
Z80 decoder uses improved offline packet selection for L7.
'''
(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype'/'README.txt').write_text(readme,encoding='ascii');z=O/'RType_TS2068_r89.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():i=zipfile.ZipInfo('rtype/'+p.name,(2026,11,7,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;f.writestr(i,p.read_bytes())
 i=zipfile.ZipInfo('README.txt',(2026,11,7,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;f.writestr(i,readme)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z);print(hashlib.sha256(z.read_bytes()).hexdigest(),z.stat().st_size)
