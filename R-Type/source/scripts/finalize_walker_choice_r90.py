from pathlib import Path
import json,hashlib,functools,zipfile,sys
R=Path.cwd();O=R/'build/fullgame/walker_choice_r90';B=R/'build/fullgame/l1_machinery_r84';sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack
assert json.loads((O/'review_application_validation.json').read_text())['passed'];assert json.loads((O/'four_frame_validation.json').read_text())['passed'];assert json.loads((O/'repeated_jumps_validation.json').read_text())['passed'];assert json.loads((O/'initial_attribute_validation.json').read_text())['attributeAudits']==12
assert set(r['level']for r in json.loads((O/'boss_preview_validation.json').read_text())['results'])=={1,4,7};meta=json.loads((O/'generic_manifest.json').read_text());rr=json.loads((O/'walker_runtime.json').read_text());hashes={}
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
(O/'generic_manifest.json').write_text(json.dumps(meta,indent=2));summary=dict(passed=True,region_sha256=hashes,exact_reviewed_indices=True,accepted_and_unreviewed_assets_unchanged=True,affected_gameplay_levels=[1,4,7],unchanged_levels_vs_r89=[2,3,5,6,8],cold_cached_jumps=11,initial_attribute_audits=12,hardware_pending=True,stock64KB_unchanged=True);(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
readme="""R-Type TS2068 r90 - selected arcade gun walker

Replace the COMPLETE rtype folder, RESET, launch rtype/rt.tap.

Applied convref/rtype-new-gunwalker-r89.json:
Option A, brightness39, contrast70, saturation100, gamma1.01.
All four walking and two raised-gun poses use these same exact settings.
Installed on the shared gun-walker family in L1/L4/L7, at existing sizes.
This replaces the r89 optionB redraw with the chosen arcade-source conversion.
Three original walking cels plus the reviewed authored fourth intermediate;
original gun-raising cels retained. No new geometry enlargement.

Prior approved L6head/L1large/Before31 choices stay unchanged, as do the
accepted yellow bot and exhaust. All45other runtimeframes are byte-identical
r89; complete levels2/3/5/6/8 are byte-identical. Exact18 installed gun-walker
frames across three levels match the chosen converted palette indices.

Verified Z80 animation/stack/register contracts, affected levels1/4/7 gameplay
(including extendedL7),11cold/cachedleveltransitions andbank5assetreadback,
12initialnativeattributeaudits, bounds/static scope, allTAPchecksums and
levelreconstruction, ZIPCRC. Real-machine confirmation remains pending.
Expanded-RAM/disk build; existing stock64KBcartridge unchanged.

Existing in-game controls/key selection are unchanged. Keep the entire folder
from this release together; do not mix cached level files from older builds.
"""

(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype'/'README.txt').write_text(readme,encoding='ascii');z=O/'RType_TS2068_r90.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():i=zipfile.ZipInfo('rtype/'+p.name,(2026,11,7,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;f.writestr(i,p.read_bytes())
 i=zipfile.ZipInfo('README.txt',(2026,11,7,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;f.writestr(i,readme)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z);print(hashlib.sha256(z.read_bytes()).hexdigest(),z.stat().st_size)
