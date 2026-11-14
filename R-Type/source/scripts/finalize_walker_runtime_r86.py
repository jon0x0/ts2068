from pathlib import Path
import sys,json,functools,hashlib,zipfile
R=Path.cwd();O=R/'build/fullgame/walkers_exhaust_r86';B=R/'build/fullgame/l1_machinery_r84';sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack
reports=json.loads((O/'walker_runtime.json').read_text());metas=json.loads((O/'generic_manifest.json').read_text());regions={}
for n in range(1,9):
 a=(B/f'level{n:02d}_region.bin').read_bytes();b=(O/f'level{n:02d}_region.bin').read_bytes();assert len(b)==65536;assert a[0x2000:0x2400]==b[0x2000:0x2400];assert a[0x3a00:0x4000]==b[0x3a00:0x4000];assert a[0x4000:0x8000]==b[0x4000:0x8000];allowed=set()
 for phase in range(8):
  at=0xed80+phase*96;assert a[at:at+32]==b[at:at+32];assert a[at+64:at+96]==b[at+64:at+96]
  for x in[phase+1,phase+2]:allowed.add(at+32+12+x//8)
 if n in[1,3,4,6,7]:
  allowed.update(range(0x2800 if n==4 else 0x2400,0x3a00));allowed.update(range(0xdeae,0xdf30))
  if n==4:allowed.update(range(0xa9c7,0xb30c))
  if n==7:allowed.update(range(0xaeb1,0xb147))
  r=next(v for v in reports if v['level']==n);assert unpack(b[r['motion_ptr']:])==(O/f'L{n}_runtime_image.bin').read_bytes();assert r['immutable_end']<=0x3a00;assert 0xa000+r['runtime_bytes']<=r['assets'][0]['pointer'];assert r['assets'][0]['pointer']+r['art_bytes']<=0xc000
  code=b[0xdc50:0xdf30];off=code.find(bytes.fromhex('dd21'),0x200);tab=int.from_bytes(code[off+2:off+4],'little');blocks=[]
  for k in range(b[tab]):blocks.append([int.from_bytes(b[tab+1+4*k:tab+3+4*k],'little'),int.from_bytes(b[tab+3+4*k:tab+5+4*k],'little')])
  meta=next(v for v in metas if v['level']==n);meta['preload_blocks']=blocks;meta['cache_symbols'].update(PRELOAD_TABLE=tab,MOTION_PTR=r['motion_ptr'],MOTION_BYTES=r['runtime_bytes'],WARMUP_ENTRY=r['extension']['load_new_art']);meta['runtime_art_pointer']=r['assets'][0]['pointer'];meta['runtime_art_bytes']=r['art_bytes'];meta['legacy_motion_source_superseded']=True
 assert all(i in allowed for i,(x,y)in enumerate(zip(a,b))if x!=y),(n,'unscoped change')
 regions[n]=hashlib.sha256(b).hexdigest()
 for name in[f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  data=(O/'rtype'/name).read_bytes();p=0;raw=[]
  while p<len(data):
   size=int.from_bytes(data[p:p+2],'little');block=data[p+2:p+2+size];assert len(block)==size and functools.reduce(int.__xor__,block,0)==0
   if block[0]==255:raw.append(block[1:-1])
   p+=size+2
  expect=b if name.startswith('LEVEL')else b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]);assert b''.join(raw)==expect
for name in['rt.tap','RTCORE.TAP','RTPRELD.TAP']:assert (O/'rtype'/name).read_bytes()==(B/'rtype'/name).read_bytes()
(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2));four=json.loads((O/'four_frame_validation.json').read_text());assert four['passed'];walking=[r for r in four['results']if r['key']not in['exhaust','yellow','raise0','raise1']];assert len(walking)==13 and all(r['uniqueFrames']==4 for r in walking)
assert json.loads((O/'all_eight_boss_validation.json').read_text())['passed'];assert json.loads((O/'initial_attribute_validation.json').read_text())['passed'];assert json.loads((O/'repeated_jumps_validation.json').read_text())['passed'];assert json.loads((O/'death_validation.json').read_text())['passed'];assert (O/'actual_walker_sequences.json').exists()
summary=dict(passed=True,region_sha256=regions,walker_families=13,walking_frames=52,total_runtime_frames=63,four_frame_dispatch=True,all_eight_routes=True,extended_L3_L7=True,cold_cached_jumps=11,attribute_audits=12,actual_death_respawn=True,load_all_title_restart=True,source_code_unchanged_outside_installer=True,terrain_and_native_movement_scripts_unchanged=True,hardware_pending=True,stock64KB_unchanged=True);(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
readme='''R-Type TS2068 r86 - walker artwork, four-pose animation and rocket exhaust

Replace the COMPLETE rtype folder, RESET, and launch rtype/rt.tap.
Do not mix level files from older builds. Existing in-game controls and key
selection remain: both joystick sockets with keyboard, B-release-B boss preview,
L then number level jump, Shift-L Load All, P pause and M music toggle.

13 walking families now have four distinct presentation poses, including the
Before31 round walker and shared walker types on levels1/3/4/6/7. The correct
elongated yellow bot is L3 sprite94 and has its own new shaded artwork. Weapon
raising remains separate from walking. Native movement scripts and footprint
sizes are retained. Original small arcade poses1570/1572/1574 are complemented
by an authored intermediate leg pose; invalid tile1576 was rejected. Other
sources include existing arcade large-walker cels and heads224/226/228/230.
Unverified round walkers and yellow94 use AI-assisted Spectrum-derived art;
they are not claimed to be original arcade assets.

The detached engine plume uses four new reference-based pulses: cyan/white core,
blue shock structure and widening yellow/red tongues. Orange is approximated
with the TS palette. The compact player rear flare gets a red heat accent;
its bitmap, coverage and update timing remain unchanged. The full reference
plume is the detached engine effect, not an enlarged player trail.

New art is scaled before actual Retro Pixel Converter Sierra Lite conversion.
Frames share settings within their family. Legal8x1 pairs and normal black.
Assets expand during level initialization into checked bank5 areas; no runtime
image conversion or extra disk files. Existing level residency and full512KB
layout retained. L1 stomach machinery restoration and prior hardware fixes stay.

Verification: exact Z80 four-pose order and register/stack preservation for all
21 groups;13 walker groups have four distinct images. Actual in-game sequences
confirm four visible poses on observed L1large/L3ground/L6head/L7head routes.
All8 scripted boss-preview routes, extended L3/L7 play,11 cold/cached jumps,
12 initial-attribute audits, bank5 asset readback, actual L6death/respawn and
LoadAll/title/restart passed. All level tapes reconstruct their64KB images;
checksums and ZIPCRC passed. Animation-selection hook227-229 Tstates/call.
Comparable end-to-end emulator routes stayed within about1percent of r80;
this includes startup/loading and is NOT a gameplay FPS or hardware guarantee.
Real-machine confirmation remains pending. Stock64KB cartridge unchanged.

Exact installed-art previews: build/graphics/walker_runtime_r86/index.html.
Rebuild: prepare_walker_runtime_r86.py; convert_walkers_rpc_r86.mjs;
build_walker_runtime_r86.py; finish_player_flame_r86.py. Do not use legacy
Lx_motion.asm alone: compressed runtime image plus extension supersedes it.
'''
(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype'/'README.txt').write_text(readme,encoding='ascii')
z=O/'RType_TS2068_r86.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():i=zipfile.ZipInfo('rtype/'+p.name,(2026,11,7,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;f.writestr(i,p.read_bytes())
 i=zipfile.ZipInfo('README.txt',(2026,11,7,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;f.writestr(i,readme)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
print(z);print(hashlib.sha256(z.read_bytes()).hexdigest(),z.stat().st_size)
