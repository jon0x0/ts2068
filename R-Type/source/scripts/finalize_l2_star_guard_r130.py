from pathlib import Path
import json,hashlib,zipfile,functools
R=Path.cwd();O=R/'build/fullgame/l2_star_guard_r130';B=R/'build/fullgame/l2_pre_copy_r129'
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
assert any(b'R130 PREPARING' in b for _,b in blocks(O/'rtype/rt.tap'))
a=(O/'level02_region.bin').read_bytes();b=(B/'level02_region.bin').read_bytes();allowed=[(0x10d7,0x10f0),(0x11b4,0x11c9),(0x3820,0x3a00),(0x8000,0x82b3)]
assert all(any(lo<=i<hi for lo,hi in allowed)for i,(x,y)in enumerate(zip(a,b))if x!=y)
assert a[0xa000:]==b[0xa000:];assert (O/'L2_runtime_image.bin').read_bytes()==(B/'L2_runtime_image.bin').read_bytes();assert (O/'cached_boss.bin').read_bytes()==(B/'cached_boss.bin').read_bytes()
for n in ['actual_actor_decode_validation.json','scorpion_orientation_validation.json','actual_tile_decode_validation.json','actual_im2_validation.json','palette_missile_validation.json','native_revisits_validation.json','l2_boss_revisits_validation.json','debug_validation.json','overlap_plane_validation.json','boss_visible_validation.json','boss_ceasefire_front_validation.json','snake_visible_order_validation.json','star_protection_validation.json','live_star_validation.json']:assert j(n)['passed'],n
assert len(j('native_revisits_validation.json')['results'])==12 and len(j('l2_boss_revisits_validation.json')['results'])==6
for n in ['boss_visible_validation.json','boss_ceasefire_front_validation.json']:
 d=j(n);assert d['after']==700 and len(d['audits'])==5 and all(x['frontChecked']==7523 and x['checked']==1744 for x in d['audits'])
star=j('star_protection_validation.json');live=j('live_star_validation.json');assert star['cases']==9728 and star['writesInside']==0 and star['writesOutside']>0 and live['starInside']==0 and live['starOutside']>0
negative=json.loads((B/'star_negative_control_r130.json').read_text());assert not negative['passed'] and negative['writesInside']==11408
fire=j('unmodified_l2_fire_validation.json');assert len(fire)==3 and all(v['passed']for v in fire)
p0=json.loads((B/'controlled_profile_r129.json').read_text())['profile']['updateTimes'];p1=j('controlled_profile_r130.json')['profile']['updateTimes'];c0=(p0['230']-p0['100'])/130;c1=(p1['230']-p1['100'])/130
perf=dict(r129_cycles_per_update=c0,r130_cycles_per_update=c1,change_percent=100*(c1/c0-1),scope='Matched update-indexed firing, updates100..230, fixed-FF scripted emulation. CPU cycles, not hardware FPS.')
(O/'performance_comparison.json').write_text(json.dumps(perf,indent=2))
contract=dict(strategy='Explicit native star erase and draw guards; conservative x64..255 occlusion only when L2 stopped flag7A8E is nonzero.',native_hooks={'BEEA':'CALL11BE, checks old erase cell, preserves DEC C and result flags','BF11':'CALL10D7, checks new draw cell; skips original native return on occlusion'},guards=[0x10d7,0x10ef],cleanup=[0x11be,0x11c9],native_metadata_unchanged=True,boss_copier_and_all_graphics_unchanged=True,install=[0x3836,0x3845,0x39cb,0x39d6],restore=[0x39f2,0x3a00,0x39d6,0x39e0],restore_mapping='4F exposes HOME bank5 during unpatch, then6F restores DOCK5 caller. Interrupts already disabled.',global_palette=0x398b,reverse_cache=0x3820,get_tile=0x3870,save_native=0x3974,restore_native=0x3927,ordinary_star_motion='Native path retained when stopped flag is0. Stars remain active at x0..63 during stopped encounter.',occlusion_limit='Bounding region rather than per-pixel silhouette: stars are also hidden in gaps within x64..255.',hardware_tested=False)
(O/'star_guard_contract.json').write_text(json.dumps(contract,indent=2))
quiet=j('boss_ceasefire_front_validation.json');back_diagnostic=[{'after':v['after'],'differences':v['backMismatch']}for v in quiet['audits']]
summary=dict(quiet_intermediate_background_diagnostic=back_diagnostic,quiet_background_scope='Intermediate background differs at300; all7523 actual visible pixels still exact at all5 checkpoints. No claim of quiet-phase background identity.',passed=True,region_sha256=hashlib.sha256(a).hexdigest(),star_sweep=star,live_star_writes=live,r129_negative_control_writes=negative['writesInside'],boss_firing_updates=700,boss_ceasefire_updates=700,visible_pixels_per_checkpoint=7523,checkpoints_per_run=5,background_scanline_cells_per_checkpoint=1744,transitions=12,boss_revisit_routes=6,cold_fire_cases=3,actor_decodes=31,tile_cases=128,palette_rows=96,terrain_rows=160,actual_RAM_IM2_words=256,IM2_scope='Fixed-FF emulator, not256hardware IRQ probes',all16tapes_reconstructed=True,performance=perf,hardware_tested=False)
(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
text=f'''R-Type TS2068 r130 - L2 boss star trails/holes

Replace the complete rtype folder, reset, launch rtype/rt.tap.
Startup identity: R130 PREPARING. Full disk build.

Native stars run in interrupts between boss redraws. Both their old-pixel erase
and new-pixel draw now respect the stopped L2 boss region. Stars at x0..63 stay
active; x64..255 is conservatively occluded during the stopped encounter,
including gaps in that region. Ordinary scrolling stars retain the native path.
No extra boss redraw, new RAM allocation, artwork or animation changes.
The r129 selective background and foreground restoration are preserved.

Native sweep:9728cases (19active records of21slots x4speeds x32positions
x4clockphases), zero writes into occupied boss cells; r129 negative control
writes11408. Actual live700update firing encounter: zero star writes into boss,
{live['starOutside']} outside. Two700update firing/ceasefire runs verify actual7523visible
boss pixels at five checkpoints each. Firing also verifies1744background
scanlinecells per checkpoint. Quiet-phase intermediate background differs at
update300; actual visible output remains exact. Diagnostic retained in summary.
12cold/cached transitions,6longbossrevisits,3ordinary cold/fire cases,31actor
and128tile decodes,96palette160terrain rows,debug/Space,256actualRAM IM2words,
all16tape reconstructions/TAP checksums/ZIPCRC pass. Long boss tests use
invulnerability/game-over bypasses. Fixed-FF emulator, not hardware probes.

Matched CPU cost versus r129: {perf['change_percent']:+.2f}% ({c1:.0f}cycles/update).
This is scripted emulator CPU measurement, not hardware FPS.
Other7levels, all artwork/cache/runtime-image bytes, stable99/100, stock64KB
and reference projects/source ZIPs are unchanged. Hardware confirmation pending.

Build: scripts/build_l2_star_guard_r130.py, finalize_l2_star_guard_r130.py.
'''
(O/'README.txt').write_text(text);(R/'docs/l2_star_guard_r130.txt').write_text(text)
manifest={str(p.relative_to(O)).replace(chr(92),'/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((O/'rtype').rglob('*'))if p.is_file()};(O/'release_manifest.json').write_text(json.dumps(manifest,indent=2))
p=O/'RType_TS2068_r130.zip'
def add(f,name):
 info=zipfile.ZipInfo(str(name).replace(chr(92),'/'),(2026,11,10,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,f.read_bytes())
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for f in sorted((O/'rtype').rglob('*')):
  if f.is_file():add(f,f.relative_to(O))
 for n in ['README.txt','validation_summary.json','star_guard_contract.json','performance_comparison.json','release_manifest.json']:add(O/n,n)
with zipfile.ZipFile(p)as z:assert z.testzip()is None
sha=hashlib.sha256(p.read_bytes()).hexdigest();(O/'RType_TS2068_r130.sha256').write_text(sha+'  '+p.name+'\n')
entry=f'''\n\n205. r130 L2 interrupt star occlusion (2026-11-10).
User observes trails/holes between boss redraws. NativeBEFF/BF01/BF03 erase andBF25/BF40/BF42 draw run inIRQ, independently of8689 finalcomposition. Native sweep of19active records/21slots x4speeds x32positions x4clockphases=9728cases reproduced11408writes into boss inr129. Final explicit BEEA CALL11BE guards old erase cell and preserves DEC C/result flags; BF11 CALL10D7 guards new draw cell and native early return. Shared predicate10E2 uses stopped7A8E and xcolumn>=8; conservative horizontal occlusion x64..255, including black gaps, not per-pixel masking. Native wrap cleanup x0 cannot touch boss. Ordinary stars and left-quarter stars remain native. Exact r129copier/asset/runtime/cache bytes retained; no extra redraw. Guard10D7..10EE,cleanup11BE..11C8,not overlappingmusic11D0. No sharednative metadata modifications.
Discarded unreleased prototypes tried7B/7E/81metadata markers. Direct sweeps could pass while liveIRQwatch caught native copy clearingflags;7E-marker optimization also failed exactbackgroundcolour checks. No failed prototype ZIP released. Final guard sweep zero inside/{star['writesOutside']}outside; live700update firing zero inside/{live['starOutside']}outside whilebossactuallypresent; both700firing/ceasefire runs exact7523actualvisiblepixels x5checks. Firing background1744scanlinecells x5exact; quiet intermediatebackground differs1517 bitmap/colour comparisons at300, other4checkpoints exact. Probe separates intermediateback fromactualfront; allactualfrontchecksPASS. Do not claim quietbackgroundidentity; diagnosticretained. Scene-presence gating excludes post-boss star writes, which are legitimate. Short140update diagnostic proved starzero but intentionally failed13-role coverage (only4observed); final700update rolecoveragepasses.
Installer uses existingbank1padding3836/39CB. Restore39F2->39D6 returns original BEEA0A0DA7/BF110AA7C0. Initial cached-core audit caught writes going toDOCK5 under6F; fixedunpatch switches4F toexposeHOMEbank5, restores6F beforeDOCK5caller. Redundant868Cpoll restoration removed (installer neverchangespoll); complete cold/runtime references audited: reverse3820/gettile3870/global398B/save3974/restore3927 unchanged fromr129 afterfinallayout, lowcold1DE/render157B/FA0/highinstaller/runtimeCall checked. Native core/cachedworkspace/stack integrity pass12transitions/6longbossroutes. Source regiondiffrestricted lowguardspadding/native loader/debugversion; A000..FFFFbitidenticalr129,other7regionsbitidentical. All31actor/128tile/96palette160terrain/debug/3unmodifiedcoldfire/256RAMIM2words/16TAPreconstruction/ZIPCRC pass. FixedFF,not256hardware IRQ probes;longgame usesbypasses. CPU matched100..230update mean {c0:.2f}r129 vs{c1:.2f}r130 ({perf['change_percent']:+.4f}%),not hardwareFPS. Actual boss_visible_690.home.png inspected after final render; emulatedgameplay,hardwarepending. Candidate {p.relative_to(R)} SHA{sha}. Stable100/stock64KB/referenceprojects/sourceZIPs unchanged.\n'''
if b'205. r130 L2 interrupt star'not in(R/'TEST_HISTORY.md').read_bytes():
 with(R/'TEST_HISTORY.md').open('ab')as f:f.write(entry.encode('ascii'))
 with(R/'PROJECT_STATE.md').open('ab')as f:f.write(f'\n2026-11-10 r130 L2 nativeIRQ star erase/draw occlusion while7A8Estopped,x64..255;leftstarsremain. Noextra redraw/artwork changes.9728nativecases/700liveIRQzero bosswrites;two700visiblepixelruns/12transitions6bossroutes/contractsPASS. HOMEbank5unpatch visibility4F then6Faudited. CPUchange{perf["change_percent"]:+.4f}%vsr129. {p.relative_to(R)} SHA{sha}. TEST_HISTORY205;hardwarepending;stable100/stock64KB unchanged.\n'.encode('ascii'))
if sha.encode('ascii')not in(R/'TEST_HISTORY.md').read_bytes():
 with(R/'TEST_HISTORY.md').open('ab')as f:f.write(f'\n206. r130 final archive confirmation: exact final binary quiet-phase probe repeated700updates; all7523visiblepixels pass5checks, intermediateback diagnostic unchanged. ZIP now uses fixed entry timestamps/permissions for reproducible packaging. Final SHA{sha} supersedes entry205 archive checksum only; region{summary["region_sha256"]},TAPmanifest andgamebehavior unchanged.\n'.encode('ascii'))
 with(R/'PROJECT_STATE.md').open('ab')as f:f.write(f'\nr130 final reproducible archive SHA{sha}; TEST_HISTORY206 supersedes205 ZIPchecksum only; binary unchanged.\n'.encode('ascii'))
print(p);print(sha);print(json.dumps(summary))
