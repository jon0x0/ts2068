from pathlib import Path
import json,hashlib,zipfile,functools
R=Path.cwd();O=R/'build/fullgame/l2_pre_copy_r129';B=R/'build/fullgame/l2_orientations_r128'
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
assert any(b'R129 PREPARING' in b for _,b in blocks(O/'rtype/rt.tap'))
a=(O/'level02_region.bin').read_bytes();b=(B/'level02_region.bin').read_bytes();assert a[0xe000:]==b[0xe000:];assert a[0xd920:0xdc40]==b[0xd920:0xdc40];assert a[0xa816:0xa84c]==b[0xa816:0xa84c];assert (O/'L2_runtime_image.bin').read_bytes()==(B/'L2_runtime_image.bin').read_bytes()
assert len((O/'cached_boss.bin').read_bytes())==216 and len((O/'front_check.bin').read_bytes())==15
for n in ['actual_actor_decode_validation.json','scorpion_orientation_validation.json','actual_tile_decode_validation.json','actual_im2_validation.json','palette_missile_validation.json','native_revisits_validation.json','l2_boss_revisits_validation.json','debug_validation.json','overlap_plane_validation.json','boss_visible_validation.json','boss_ceasefire_validation.json','snake_visible_order_validation.json']:assert j(n)['passed'],n
assert len(j('native_revisits_validation.json')['results'])==12 and len(j('l2_boss_revisits_validation.json')['results'])==6
for n in ['boss_visible_validation.json','boss_ceasefire_validation.json']:
 d=j(n);assert d['after']==700 and len(d['audits'])==5 and all(x['frontChecked']==7523 and x['checked']==1744 for x in d['audits'])
u=j('overlap_plane_validation.json');assert u['nonemptyCells']==221 and u['emptyCellsSkipped']==67
fire=j('unmodified_l2_fire_validation.json');assert len(fire)==3 and all(v['passed']for v in fire)
p0=json.loads((B/'controlled_profile_r128.json').read_text())['profile']['updateTimes'];p1=j('controlled_profile_r129.json')['profile']['updateTimes'];c0=(p0['230']-p0['100'])/130;c1=(p1['230']-p1['100'])/130
perf=dict(baseline_r128_cycles_per_update=c0,r129_cycles_per_update=c1,cycle_reduction_percent=100*(1-c1/c0),scope='Same update-indexed firing input, updates100..230, scripted BB encounter; fixed-FF emulator and gameplay bypasses. CPU cycles, not measured hardware FPS.')
(O/'performance_comparison.json').write_text(json.dumps(perf,indent=2))
contract=dict(strategy='End-of-scene boss foreground composition at HOME8689 before timing wait868C; actor-owned background restoration; skip empty cached art cells.',native_owner_plane='7E00..807F, crosses DOCK3/HOME boundary; bank4 unmapped before access',front='Restore bitmap and ECM colour for all218 nonempty8x8 cache cells every active repair; boss wins overlapping actor cells including black padding.',background='Restore only nonzero actor-owned cells; clear ownership and restore native7800 metadata. Empty70 cells untouched.',hook=0x8689,original_call=0x1400,poll_unchanged=0x868c,gateway=0x10d1,cache=[0xcb00,0xd520],copier=[0xb002,0xb0da],skip_empty=[0xa807,0xa816],projectile_source_preserved=[0xa816,0xa84c],global_palette=0x398b,reverse_cache=0x3820,owner_scratch=0x11c9,interrupts='DI before bank4 mapping; restore map9 before IFF/register restoration.',artwork_and_runtime_image_unchanged=True,other7levels_unchanged=True)
(O/'background_repair_contract.json').write_text(json.dumps(contract,indent=2))
summary=dict(passed=True,region_sha256=hashlib.sha256(a).hexdigest(),boss_firing_updates=700,boss_ceasefire_updates=700,visible_pixels_verified_per_checkpoint=7523,checkpoints_per_run=5,background_scanline_cells_per_checkpoint=1744,art_cells=218,empty_cells_skipped=70,transitions=12,boss_revisit_routes=6,cold_fire_cases=3,actor_decodes=31,tile_cases=128,palette_rows=96,terrain_rows=160,actual_RAM_IM2_words=256,IM2_scope='Fixed-FF emulation; not256hardware IRQ probes',tapes_reconstructed=16,performance=perf,hardware_tested=False)
(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
text=f'''R-Type TS2068 r129 - L2 snake/boss layering and draw optimization

Replace the complete rtype folder, reset, launch rtype/rt.tap.
Startup identity: R129 PREPARING. Full disk build.

Restores the stopped boss's foreground after entity drawing, so the snake and
projectile cleanup cannot leave erased patches on its right side. Bitmap and
8x1 ECM colours are restored together. Boss artwork wins overlapping occupied
8x8 cells, including their black padding; this is not per-pixel alpha blending.
Empty boss cells remain available to actors.

Skips70 empty cached cells and restores the background only in actor-owned
cells. Same artwork, dimensions,13body segments, anatomy and animation rates.
Matched scripted encounter costs {perf['cycle_reduction_percent']:.1f}% fewer CPU cycles per update
than r128. This is emulator CPU measurement, not hardware FPS; the encounter
can still be demanding. r128 scorpion directions and snake anatomy retained.

Verified: two700-update encounters with firing/ceasefire; five checkpoints each
compare7523 actual visible boss pixels and1744 background scanline cells;
221occupied/67empty-cell injection test (direct fixture);12cold/cached transitions,6longboss
revisit routes,3ordinary cold/fire cases;31actual actor decodes,128tilecases,
96globalpalette and160terrain rows,debug/Space redraw,256actual RAM IM2words,
all16LEVEL/START tape reconstructions and TAP/ZIP checksums.
Long encounter tests use invulnerability/game-over bypasses; separate cold/fire
tests do not. Fixed-FF emulator; no hardware IRQ or hardware gameplay claim.

Other7levels, projectile source, cold bootstrap, source ZIPs, reference projects,
stable r99/r100 and stock64KB target preserved. No new graphics in this build.
Actual gameplay capture: boss_visible_690.home.png in this build directory.
Build: scripts/build_l2_pre_copy_r129.py and finalize_l2_pre_copy_r129.py.
Real hardware confirmation pending.
'''
(O/'README.txt').write_text(text);(R/'docs/l2_pre_copy_r129.txt').write_text(text)
manifest={str(p.relative_to(O)).replace(chr(92),'/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((O/'rtype').rglob('*'))if p.is_file()};(O/'release_manifest.json').write_text(json.dumps(manifest,indent=2))
p=O/'RType_TS2068_r129.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for f in sorted((O/'rtype').rglob('*')):
  if f.is_file():z.write(f,f.relative_to(O))
 for n in ['README.txt','validation_summary.json','background_repair_contract.json','performance_comparison.json','release_manifest.json']:z.write(O/n,n)
with zipfile.ZipFile(p)as z:assert z.testzip()is None
sha=hashlib.sha256(p.read_bytes()).hexdigest();(O/'RType_TS2068_r129.sha256').write_text(sha+'  '+p.name+'\n')
entry=f'''\n\n204. r129 L2 boss/snake foreground and speed (2026-11-10).
Native main copy is8653/CALL8979; entity drawing follows. Previous background-only repair did not prevent visible actor padding/cleanup erasing stopped boss. Hook8689 replaces CALL1400 with CALL10D1, invokes1160 repair then1400, before original868C timing poll. Restore both actual front bitmap/ECM planes for218 nonempty cached cells; boss wins overlapping8x8cells including black padding, not per-pixel alpha. Restore background only where native7E00..807F actor ownership is nonzero, clear owner/native7800 tag; skip70empty cachecells. Ownership plane crosses DOCK3/HOME; bank4 must be unmapped before reading. DI around bank4 coordinate reads, restoremap9 before IFF/registers.216byte copierB002..B0D9,15byte empty helperA807..A815, projectileA816..A84B unchanged, low11C9 reused. CacheCB00..D51F unchanged; runtime image bitidenticalr128. Gateway relocation audit: reverse3820/global398B,cold1DE,renderer157B,FA0,runtime restore and installer save targets; unpatch restores8689 and868C. Other7regions/bank7/coldD920..DC3F/projectile source unchanged.
Rejected unreleased shortcuts: interpreting owner0 as dirty and front cell-tag validity both failed exact visible-pixel checks. Final safe path always restores nonempty foreground, only selective background. PASS two700update sustained-fire/ceasefire tests,5checkpoints each7523visiblepixels plus1744backgroundscanlinecells;221art/67empty direct-fixture ownership injection/codebank check;12coldcached transitions/6longbossrevisits/3unmodifiedcoldfire/31actors/128tiles/96palette160terrainrows/debug;256actualRAM IM2words,not256hardware IRQ probes;all16TAP reconstructions and ZIPCRC. Longgame tests use bypasses. Actual boss_visible_690.home.png inspected; emulatedgameplay notassetpreview/hardware. Matched update-indexed controls updates100..230: r128 {c0:.2f} vsr129 {c1:.2f} cycles/update ({perf['cycle_reduction_percent']:.2f}% fewer),not hardwareFPS. No geometry/segment/rate reduction. Candidate {p.relative_to(R)} SHA{sha}. Hardwarepending;stable100/stock64KB/referenceprojects unchanged.\n'''
if b'204. r129 L2 boss/snake'not in(R/'TEST_HISTORY.md').read_bytes():
 with(R/'TEST_HISTORY.md').open('ab')as f:f.write(entry.encode('ascii'))
 with(R/'PROJECT_STATE.md').open('ab')as f:f.write(f'\n2026-11-10 r129 L2 stopped-boss foreground composition8689,218artcells/70empty skipped,actor-ownedbackground restoration;13body/art unchanged;two700update actualvisiblepixeltests/12transitions6bossroutes/3coldfire/contracts PASS. Matched CPU cycles down{perf["cycle_reduction_percent"]:.2f}% vsr128,hardwarepending. {p.relative_to(R)} SHA{sha}. TEST_HISTORY204. Stable100/stock64KB unchanged.\n'.encode('ascii'))
print(p);print(sha);print(json.dumps(summary))
