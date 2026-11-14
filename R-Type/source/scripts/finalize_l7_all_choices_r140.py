from pathlib import Path
import json,zipfile,hashlib
R=Path.cwd();O=R/'build/fullgame/l7_all_choices_r140';B=R/'build/fullgame/highscore_r138';j=lambda name:json.loads((O/name).read_text())
assert j('all_vector_validation.json')['passed'];assert j('all_vector_validation.json')['cases']==256;assert j('static_validation.json')['passed'];assert j('shuffle_validation.json')['passed'];assert j('native_revisits_validation.json')['passed'];assert len(j('native_revisits_validation.json')['results'])==12;assert j('runtime_validation.json')['passed'];assert j('clean_wall_validation.json')['passed'];assert all(q['passed']for q in j('unmodified_target_levels_fire_validation.json'));assert j('highscore_validation.json')['passed']
# Pair assets are the exact submitted exports, never converter rerenders.
selections=json.loads((R/'build/graphics/l7_final_inputs/selections.json').read_text());source_manifest=[]
for q in selections:
 p=R/'convref'/q['file'];z=zipfile.ZipFile(p);assert z.testzip()is None;doc=json.loads(z.read('choices.json'));fam=doc['families']['walker'];frames=[]
 for f in fam['frames']:
  k=f['frame'];raw=z.read(f'walker/frame_{k:02d}.pairs.bin');assert raw==(R/f'build/graphics/l7_final_inputs/{q["key"]}_{k}.pairs').read_bytes();frames.append(dict(frame=k,width=f['width'],height=f['height'],pair_sha256=hashlib.sha256(raw).hexdigest()))
 source_manifest.append(dict(key=q['key'],file=q['file'],sha256=hashlib.sha256(p.read_bytes()).hexdigest(),settings=q['settings'],frames=frames))
(O/'chosen_assets_manifest.json').write_text(json.dumps(source_manifest,indent=2))
text='''R-Type TS2068 r140 - complete selected L7 artwork integration

Install: replace the complete rtype folder, reset, run rtype/rt.tap.
Startup identity: R140 PREPARING. Full eight-level disk/512KB RAM target.
The preserved stock64KB cartridge target and stable r100 archive are unchanged.

Installed selections:
- White arcade walker: native14..17; chosen three poses in native0/1/2/1 order.
- Blue/cyan variant: native30..32, all three chosen poses.
- Red/yellow/green enemy: native37, chosen arcade598 conversion.
- Asteroid/orb: native35, chosen16x16 image.
- Emerging machinery: native51, chosen24x48 image.
- Wall enemy: chosen four articulated poses. Housing41 is fixed; moving42..45
  use the selected left half, with original42/43/44/45/44/43 timing. The fixed
  housing uses the chosen rest-pose right half so it remains stable.

Native erase/source masks are updated for the selected silhouettes. Native
movement scripts and overall sprite footprints are retained. The wall joint
is at the original16pixel boundary; no enlarged moving housing.

Lossless planar streams are expanded and interleaved during L7 preparation.
The independent interleave test measured16,860,831Tstates for both buffers,
about4.8seconds at3.528MHz, plus decompression. This cost is during preparation,
not every gameplay frame. No new use of native script storage or IM2 pages.

Validation:600protected firing updates,2160-update wall encounter captures,
12cold/cached level transitions, unmodified L7 startup/fire, high-score display
transition, exact RAM artwork/cache checks, all20TAP checksums/reconstruction,
other7level regions andCORE byte-identical to r138. Visual wall captures
inspected. Long encounter tests prevent player death; they are not a full
unmodified playthrough. Hardware confirmation remains pending.
'''
(O/'README.txt').write_text(text);(O/'rtype/README.txt').write_text(text)
report=dict(passed=True,source_packs=6,raw_art_bytes=3136,cache_bytes=4864,packed_end=j('l7_choices_contract.json')['end'],storage_limit=0x3a00,cold_cached_transitions=12,cold_unmodified_L7_fire=True,protected_firing_updates=600,protected_wall_updates=2160,highscore_probe=True,native_scripts_storage_unchanged=True,IM2_unchanged=True,other7levels_unchanged=True,CORE_unchanged=True,wall_fixed_housing=True,hardware_tested=False)
(O/'validation_summary.json').write_text(json.dumps(report,indent=2));manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((O/'rtype').iterdir())if p.is_file()};(O/'release_manifest.json').write_text(json.dumps(manifest,indent=2))
p=O/'RType_TS2068_r140.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED)as z:
 for f in sorted((O/'rtype').iterdir()):
  if f.is_file():
   info=zipfile.ZipInfo('rtype/'+f.name,(2026,11,13,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,f.read_bytes())
 for name in ['README.txt','validation_summary.json','release_manifest.json','chosen_assets_manifest.json','native_mask_contract.json','l7_choices_contract.json','static_validation.json','shuffle_validation.json','native_revisits_validation.json','runtime_validation.json','clean_wall_validation.json','all_vector_validation.json']:
  info=zipfile.ZipInfo(name,(2026,11,13,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,(O/name).read_bytes())
with zipfile.ZipFile(p)as z:assert z.testzip()is None
print(p,hashlib.sha256(p.read_bytes()).hexdigest())
