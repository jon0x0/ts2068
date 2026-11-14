from pathlib import Path
import json,hashlib,zipfile,functools
R=Path.cwd();O=R/'build/fullgame/l2_orientations_r128';B=R/'build/fullgame/l2_roles_restore_r127'
def j(n):return json.loads((O/n).read_text())
def blocks(p):
 v=p.read_bytes();out=[];at=0
 while at<len(v):
  n=int.from_bytes(v[at:at+2],'little');b=v[at+2:at+2+n];assert n>1 and len(b)==n and functools.reduce(int.__xor__,b,0)==0;out.append((b[0],b[1:-1]));at+=n+2
 assert at==len(v);return out
for n in range(1,9):
 v=(O/f'level{n:02d}_region.bin').read_bytes()
 for kind in ['LEVEL','START']:
  actual=b''.join(data for flag,data in blocks(O/'rtype'/f'{kind}{n:02d}.TAP')if flag==255);expected=v if kind=='LEVEL'else b''.join(v[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]);assert actual==expected
 if n!=2:assert v==(B/f'level{n:02d}_region.bin').read_bytes()
assert any(b'R128 PREPARING' in b for _,b in blocks(O/'rtype/rt.tap'))
ct=j('L2_actor_contract.json');contract=j('orientation_contract.json');a=(O/'level02_region.bin').read_bytes();b=(B/'level02_region.bin').read_bytes();image=(O/'L2_runtime_image.bin').read_bytes();old=(B/'L2_runtime_image.bin').read_bytes();assert len(image)==len(old)
diff=[(i+0xa000,x,y)for i,(x,y)in enumerate(zip(old,image))if x!=y];assert diff==[(0xa7b1,9,4),(0xa7b4,56,48)],diff
allowed=[(ct['imageptr'],0x3820),(0x8000,0x82b3)]+[(p['address'],p['address']+p['old_bytes'])for p in contract['changed_packets']]
assert all(any(lo<=i<hi for lo,hi in allowed)for i,(x,y)in enumerate(zip(a,b))if x!=y)
assert 0xa000+len(image)<=0xa7c0 and contract['packed_runtime_end']<=0x3820
for name in ['actual_actor_decode_validation.json','scorpion_orientation_validation.json','actual_tile_decode_validation.json','actual_im2_validation.json','palette_missile_validation.json','native_revisits_validation.json','l2_boss_revisits_validation.json','debug_validation.json','dirty_refresh_validation.json','boss_background_validation.json','snake_roles_validation.json','snake_order_validation.json']:assert j(name)['passed'],name
assert j('scorpion_orientation_validation.json')['chosenExportsIndependentlyVerified'];assert contract['captured_orientation_bits']==[0,2,1,2,1,3,3,3,2,0]
assert j('snake_order_validation.json')['order']==[[i,198 if i<4 else 199]for i in range(13)]
assert len(j('native_revisits_validation.json')['results'])==12 and len(j('l2_boss_revisits_validation.json')['results'])==6
assert j('boss_background_validation.json')['after']==700 and len(j('boss_background_validation.json')['audits'])==5
fire=j('unmodified_l2_fire_validation.json');assert len(fire)==3 and all(v['passed']for v in fire)
game=j('L2_fine_approach.json');assert game['u']>=1547 and all(game['drawCounts'].get(str(i),0)>0 for i in range(180,190))
assert len(j('actual_actor_decode_validation.json')['reports'])==31
(O/'snake_parts_contract.json').write_text(json.dumps({'head':'native role0, original orientations','neck':'native role4, existing segment immediately after head','body_order':['spiny']*4+['round']*9,'tail':'native role6, original orientations','art_geometry_unchanged':True},indent=2))
validation=dict(passed=True,region_sha256=hashlib.sha256(a).hexdigest(),source_zip_sha256=contract['source_zip_sha256'],scorpion_frames_decoded_and_export_verified=10,source_orientation_family_comparisons='exact64x64 RGBA whole-image flips',runtime_body_mapping_bytes_changed=2,ordinary_approach_updates=game['u'],all10_scorpion_frames_observed=True,boss_updates=700,all13_body_positions_verified=True,body_order='head / existing neck /4spiny /9round /tail',general_transitions=12,boss_reset_revisits=6,cold_fire_cases=3,actor_decodes=31,tile_cases=128,palette_rows=96,terrain_scanlines=160,dirty_cells_injection_test=288,IM2_words=256,IM2_scope='Actual RAM words; fixed-FF emulator, not256hardware IRQ probes',other7levels_unchanged=True,all16level_tapes_reconstructed=True,hardware_tested=False)
(O/'validation_summary.json').write_text(json.dumps(validation,indent=2))
text="""R-Type TS2068 r128 - corrected L2 scorpion directions and snake anatomy

Replace the complete rtype folder, reset, launch rtype/rt.tap.
Startup identity: R128 PREPARING.

Your direction convention is used throughout the comparison and provenance:
FlipX=false means head right. FlipY=false means head down.
Frames0..9 captured flags (X,Y):
0 false,false;1 false,true;2 true,false;3 false,true;4 true,false;
5 true,true;6 true,true;7 true,true;8 false,true;9 false,false.
Frame3 is your confirmed false/true, also independently proven because its
64x64arcade source pixels are an exact vertical flip of Frame9.

The runtime normalization differed from the old preview labels. Frames2 and5
were the incorrectly facing game artwork: both have now been mirrored in X/Y,
bitmap AND8x1 colour planes together. All ten exact chosen exports are retained;
no rescaling, colour settings, animation sequence or frame-rate changes. Each
actual Z80 decode is verified against the chosen export with the corrected flip.
The four-direction comparison animates all ten with one fixed heading.

The native snake already has a separate neck segment (role4). Its sequence is
now head - existing neck - four spiny body sections - nine round sections - tail.
All13 body slots keep their anatomical type across native22/23 animation phases.
Head/tail orientation mappings and all sprite sizes are unchanged. Exactly two
expanded runtime bytes change the anatomy boundary; no extra drawing work.

The r127 boss-backdrop repair, native refresh bookkeeping, bank/stack/IM2
contracts and all other level artwork are retained. Corrected scorpion packets
fit their existing slots and are16bytes smaller; runtime image size is unchanged.
Source ZIPs, stable r99/r100 and stock64KB target unchanged. Full disk build.

Verified in scripted emulation:31 actual actor decodes including all ten chosen
scorpion exports;1547-update ordinary L2 approach observed all ten IDs;
700-update firing/boss test verified every body slot, immutable backdrop cache
and exact pixels/colours at five checkpoints;12 cold/cached transitions and6
long boss/reset/revisits;3 ordinary cold/fire cases;128 tiles,96 shared palette
rows,160 scrolling scanlines,288 injected dirty cells;debug/Space redraw;
actual256IM2words and all16level/start tapes/ZIP CRCs. Fixed-FF emulator,
not hardware IRQ probes. Long gameplay coverage uses invulnerability/game-over
bypasses; separate cold/fire tests do not. Real hardware confirmation pending.

Comparison: build/graphics/l2_orientations_r128/index.html
Build: scripts/build_l2_orientations_r128.py, preview_l2_orientations_r128.py,
listed verification scripts, then finalize_l2_orientations_r128.py.
"""
(O/'README.txt').write_text(text);(R/'docs/l2_orientations_r128.txt').write_text(text)
manifest={str(p.relative_to(O)).replace(chr(92),'/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((O/'rtype').rglob('*'))if p.is_file()};(O/'release_manifest.json').write_text(json.dumps(manifest,indent=2))
p=O/'RType_TS2068_r128.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for f in sorted((O/'rtype').rglob('*')):
  if f.is_file():z.write(f,f.relative_to(O))
 for name in ['README.txt','validation_summary.json','orientation_contract.json','snake_parts_contract.json','release_manifest.json']:z.write(O/name,name)
with zipfile.ZipFile(p)as z:assert z.testzip()is None
sha=hashlib.sha256(p.read_bytes()).hexdigest();(O/'RType_TS2068_r128.sha256').write_text(sha+'  '+p.name+'\n')
entry=f"\n\n203. r128 L2 orientation/anatomy correction (2026-11-10). User supplied all scorpion direction corrections, confirmed Frame3 falseX/trueY. ConventionfalseX=headright,falseY=headdown. All10source captures indexed with [0,2,1,2,1,3,3,3,2,0]bits; native canonical-left/up normalization[3,1,2,1,2,0,0,0,1,3]. Old labels disagreed with actual normalized game packets; actual reversed frames2/5 fixed by mirroring scorpion_base2 anddelta5 in BOTH axes, preserving paired bitmap/ECMplanes and exact exports. Compressed295->291 and193->181bytes inexisting slots, other packets untouched. Source64x64RGBA family comparisons exact after corrected whole-image flips (including3vs9 vertical), all31actualZ80decodes match and all10scorpions independently match chosen exports.\nNative snake role4 is already a separate neck piece. Final head/neck/4spiny/9round/tail order usesbodyordinals0..3=198,4..12=199. An initial unreleased draft added an extra round body before spines; corrected after checking native role4 and arcade assembly. Final actualgame700update trace verifies all13ordinals and stable type across22/23 phases. Exactly two runtime bytes A7B1:09->04 andA7B4:38->30; image size unchanged,A7BAend<unpatchA7C0/captureA7CC. Packedruntimeends{contract['packed_runtime_end']:04X}<3820. No new memory allocation,geometry,animationorder/rate or bankcode changes. Allregion changes constrained to2packets,compressedruntime,debugversion. Other7levels andr127bossrepair bitidentical.\nPASS:1547ordinary approach updates/all10scorpionIDs;700boss/firingupdates/5exactcache+backgroundchecks/13bodyroles;31decodes/128tiles/96palette160rows/288dirtyinjections;12coldcachedtransitions/6longbossresetrevisits/3normalcoldfire/debug/Space redraw;256actualRAM IM2words(fixedFF,not256hardwareIRQprobes);16TAPreconstruction/checksums,ZIPCRC. Previews headings.png/comparison.png and interactive index atbuild/graphics/l2_orientations_r128 are asset comparisons; actualboss_probe_690.home.png and ordinary approach captures are emulatedgameplay, not hardware. Images inspected. Longgame tests useinvulnerability/gameoverbypass. No hardwareconfirmation. SourceZIPs/referenceprojects/stable99/100/stock64KBunchanged. Candidate{p.relative_to(R)} SHA{sha}. docs/l2_orientations_r128.txt.\n"
if b'203. r128 L2 orientation'not in(R/'TEST_HISTORY.md').read_bytes():
 with(R/'TEST_HISTORY.md').open('ab')as f:f.write(entry.encode('ascii'))
 with(R/'PROJECT_STATE.md').open('ab')as f:f.write(f"\n2026-11-10 r128 L2 scorpion direction correction: userfalseXright/falseYdown,confirmedFrame3false/true;runtimeframes2/5 X/Ymirrored inexistingpackets;all10sourceorientation families exact andactualdecodes/exportchecksPASS. Snake usesexistingneck role4 then4spiny/9round body,headtailunchanged;2runtimebytes only,size/animationrate unchanged.1547approach/700bossupdates/all13roles/31decodes/12transitions6bossroutes/3coldfire/tapesZIP PASS. build/fullgame/l2_orientations_r128/RType_TS2068_r128.zip SHA{sha}; interactivepreview build/graphics/l2_orientations_r128/index.html; TEST_HISTORY203. Hardwarepending,stable100/stock64KB/referenceprojects unchanged.\n".encode('ascii'))
print(p);print(sha);print(json.dumps(validation))
