from pathlib import Path
import json,hashlib,zipfile,functools
R=Path.cwd();O=R/'build/fullgame/l2_roles_restore_r127';B=R/'build/fullgame/l2_snake_parts_r126'
def j(n):return json.loads((O/n).read_text())
def blocks(p):
 b=p.read_bytes();out=[];at=0
 while at<len(b):
  n=int.from_bytes(b[at:at+2],'little');v=b[at+2:at+2+n];assert n>1 and len(v)==n and functools.reduce(int.__xor__,v,0)==0,(p,at);out.append((v[0],v[1:-1]));at+=n+2
 assert at==len(b);return out
for n in range(1,9):
 v=(O/f'level{n:02d}_region.bin').read_bytes();assert len(v)==65536
 for kind in ['LEVEL','START']:
  data=b''.join(d for flag,d in blocks(O/'rtype'/f'{kind}{n:02d}.TAP')if flag==255);want=v if kind=='LEVEL'else b''.join(v[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]);assert data==want,(n,kind)
 if n!=2:assert v==(B/f'level{n:02d}_region.bin').read_bytes()
assert any(b'R127 PREPARING' in d for _,d in blocks(O/'rtype/rt.tap'))
assert 0xa000+len((O/'L2_runtime_image.bin').read_bytes())<=0xa7c0
a=(O/'level02_region.bin').read_bytes();b=(B/'level02_region.bin').read_bytes();assert a[0xe000:]==b[0xe000:];assert a[0xd920:0xdc40]==b[0xd920:0xdc40];assert a[0xa816:0xa84c]==b[0xa816:0xa84c];assert a[0xfb8:0xfc3]==b[0xfb8:0xfc3]
tc=j('integration_contract.json');assert int.from_bytes(a[0xfa0:0xfa2],'little')==tc['tile_symbols']['reverse_cache']
assert hashlib.sha256((R/'convref/rtype-l2-art-assets_v2.zip').read_bytes()).hexdigest()=='e16427f3fea28674b16bc8f3399a4acaa0c161a661f96b8fb9009e640c456ac6'
for n in ['actual_tile_decode_validation.json','actual_actor_decode_validation.json','actual_im2_validation.json','palette_missile_validation.json','native_revisits_validation.json','l2_boss_revisits_validation.json','debug_validation.json','boss_background_validation.json','snake_roles_validation.json','dirty_refresh_validation.json','boss_ceasefire_validation.json']:assert j(n)['passed'],n
bg=j('boss_background_validation.json');roles=j('snake_roles_validation.json');assert bg['after']==700 and len(bg['audits'])==5 and all(x['checked']==1744 for x in bg['audits']);assert roles['round']>0 and roles['spiny']>0
assert len(j('actual_actor_decode_validation.json')['reports'])==31;assert len(j('actual_tile_decode_validation.json')['results'])==128
assert len(j('native_revisits_validation.json')['results'])==12 and len(j('l2_boss_revisits_validation.json')['results'])==6
fire=j('unmodified_l2_fire_validation.json');assert len(fire)==3 and all(x['passed']for x in fire)
ct=j('background_repair_contract.json');ct.update(strategy='Predecoded immutable 18-tile stopped-boss backdrop; original native8CFD entry unchanged',cache={'bank':6,'start':0xcb00,'end_exclusive':0xd520,'bytes':2592,'format':'18 native144byte tiles:16x(tag+8pixels)','capture_code':[0xa7cc,0xa807],'copy_code':[0xb002,0xb0bf],'snapshot_end':0xcaf4,'IM2_start':0xd800,'global_palette_start':0xd940},unused_draft_gateway=False,reverse_palette_helper=0x3820,damage_flag=0x11cf,demand_driven=True,unused_dirty_marker=False,interrupt_contract='DI before every bank4 exposure; normal map restored before caller IFF',hardware_tested=False);(O/'background_repair_contract.json').write_text(json.dumps(ct,indent=2))
(O/'snake_parts_contract.json').write_text(json.dumps({'native_body_ids':[22,23],'chain_relative_roles':True,'round_slots':9,'spiny_slots':4,'round_arcade_cel':2450,'spiny_arcade_cel':2454,'frame_types_not_animation':True,'native_head_tail_ids_unchanged':list(range(25,31))},indent=2))
cycles=bg['repairCycles']/bg['repairCount'];perf={'cached_copy_cycles_per_call':cycles,'conservative_repaint_cycles_per_call':1287781.4991922455,'per_call_reduction_percent':100*(1-cycles/1287781.4991922455),'scope':'Emulated CPU cycles per repair invocation; not hardware FPS or whole-game speedup','repair_calls':bg['repairCount']};(O/'performance_validation.json').write_text(json.dumps(perf,indent=2))
validation={'passed':True,'region_sha256':hashlib.sha256(a).hexdigest(),'boss_firing_updates':700,'background_audits':bg['audits'],'immutable_cache_verified':True,'ceasefire_updates':700,'dirty_cells_injected_test':288,'unchanged_cells_do_not_force_refresh':True,'bank4_debug_code_intact':True,'body_draws':roles['bodyDraws'],'actor_packets':31,'tile_cases':128,'shared_palette_rows':96,'terrain_scanlines':160,'IM2_words':256,'IM2_scope':'Actual RAM words; fixed-FF emulator, not256 hardware IRQ probes','cold_fire_cases':3,'transition_routes':12,'boss_reset_routes':6,'all16_level_tapes_reconstructed':True,'other7_levels_unchanged':True,'hardware_tested':False};(O/'validation_summary.json').write_text(json.dumps(validation,indent=2))
text="""R-Type TS2068 r127 - L2 snake anatomy and boss backdrop repair

Replace the complete rtype folder, reset, and launch rtype/rt.tap.
Startup identity: R127 PREPARING. Select level2; double B previews the boss.

Snake head/tail orientation mappings remain unchanged. Native body records now
keep chain-relative anatomical roles:9 round2450 segments then4 spiny2454
segments. Both native animation phases retain the same part at each position.
This adapts the arcade's round/spiny arrangement to the existing13-body chain.

The stopped boss has an immutable predecoded2592-byte backdrop cache in L2
bank6 CB00..D51F, after the native source snapshot and before the D800 IM2 page.
Its pixels and legal8x1 colours are restored together after the displayed frame, updating native7800 attributes and7E00 dirty cells,
so opaque shot/actor erasures cannot permanently destroy the boss artwork.
Original native8CFD drawing entry is preserved. No gameplay/collision change.
Four fixed32x24 mouth descriptors use precomposed background artwork; the
nearly identical43 pose shares42's raw packet, preserving the proven decoder.
All ten selected scorpion frames and the earlier projectile palette fix remain.

The repair is189 bytes, with a59-byte initial capture helper. Drawing notifications avoid redundant repair scans. It flags only changed cells for visible refresh. Bank4 access is
interrupt-protected on EVERY call; caller mapping/IFF and alternate registers
are restored. A missed reverse-palette call after relocation was also fixed.
The full diagnostic RAM capture is preserved; its screen shows16 key fields.

Scripted emulation passed700 post-BB updates with sustained firing,5 exact
background bitmap/colour comparisons, immutable cache checks, stable mixed
snake roles,31 actual actor decodes,128 tile cases,96 shared palette rows and
160 scrolling scanlines. Twelve cold/cached transitions,6 boss/reset/revisit
routes,3 normal cold-start/fire timings, debug/Space redraw, all16 level tapes
and actual256 IM2 words passed. Long boss coverage uses invulnerability and a
game-over bypass; separate cold-start/fire tests do not. Hardware testing pending.

Measured cached repair cost is about274000 emulated CPU cycles per call versus
1288000 for the conservative redraw (about79% less). This is not a hardware FPS
measurement or a claim of an equivalent whole-game speedup. Temporary shared-cell colour
clash/opaque foreground edges remain possible; permanent backdrop damage is fixed.

Other seven levels, stable r99/r100 and the stock64KB target are unchanged.
This ZIP is the full banked disk candidate. Failed r127 diagnostic experiments
are excluded from the package. Build: scripts/build_l2_roles_r127.py then
scripts/finalize_l2_roles_r127.py after the listed final-binary checks.
"""
text=text.replace('about274000',f'about{round(cycles/1000)}000').replace('about79%',f"about{round(perf['per_call_reduction_percent'])}%");(O/'README.txt').write_text(text);(R/'docs/l2_roles_restore_r127.txt').write_text(text)
files={str(p.relative_to(O)).replace(chr(92),'/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((O/'rtype').rglob('*'))if p.is_file()};(O/'release_manifest.json').write_text(json.dumps(files,indent=2))
zpath=O/'RType_TS2068_r127.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for p in sorted((O/'rtype').rglob('*')):
  if p.is_file():z.write(p,p.relative_to(O))
 for name in ['README.txt','validation_summary.json','release_manifest.json','snake_parts_contract.json','background_repair_contract.json','performance_validation.json']:z.write(O/name,name)
with zipfile.ZipFile(zpath)as z:assert z.testzip()is None
sha=hashlib.sha256(zpath.read_bytes()).hexdigest();(O/'RType_TS2068_r127.sha256').write_text(sha+'  '+zpath.name+'\n')
warning=O/'DO_NOT_USE.txt'
if warning.exists():warning.rename(O/'FAILED_DRAFT_HISTORY.txt')
entry=f"\n\n202. Completed r127 L2 snake/boss fix (2026-11-10), supersedes failed diagnostic entries200/201. Native13-body chain uses stable9round2450/4spiny2454 roles plus unchanged head/tail orientations. Boss backdrop cached as18x144byte native tiles in DOCK6 CB00..D51F (2592bytes), after snapshot C700..CAF3 and before IM2 D800; palette D940 and live raw actor caches C000/C200 preserved. Capture59bytes atA7CC..A806 uses bank4 scratch82B3 only after tile decode; direct copier189bytes B002..B0BE restores bitmap and8x1 colours including black rows. Damage comparison only marks changed cells dirty; all288 cells exercised by injection test (unchanged cells retain flags). Native7800 attribute/7E00 dirty-cell maps updated to schedule visible refresh (the first cached draft repaired only the backbuffer and failed visual QA; withheld archive renamed pending_front_validation). DI before EVERY exposure of bank4 (active I84 vector hidden), map9 restored before outer alternate registers/IFF. Original8CFD entry and native0FB8 helper retained. Full native repaint reference passed but cost1287781 cycles/call; cached copy {cycles:.0f} cycles/call, {perf['per_call_reduction_percent']:.1f}% less per-call cost, not hardware FPS. Fullcopy may be invoked multiple times per native world update.\nRoot causes found in rejected prototypes: reused live0FB8 native helper, missed reverse_cache caller at0F9F after helper moved397D->3980, unsafe bank4 mapping between repeated calls, and a faulty mouth43 delta table. Final reverse-cache helper is3820, global-palette helper3980, both callers explicitly audited; demand notification covers both palette paths. Warm HOME source repair extended ABC7..B0DD to include the new retired mouth/cache-code range; lower dirty rows use HOME8000..807F, never bank4 debug code. Final43 aliases raw42; all31 runtime-table/decoder packets checked. Original320? No artwork dimension changes:mouth32x24, original tile silhouettes. Debug full capture retained, display compacted16fields. No new native joystick/input behavior.\nPASS finalbinary:700 post-BB updates/sustained firing; immutable18tile cache exact at5 checkpoints; each checkpoint1744 visible source scanline/cells, all pixels/visible colours exact in background. Snake {roles['bodyDraws']} body draws both roles stable. 31 actor packets incl4mouths/10scorpions;128tiles;96palette rows/160frontbackscanlines;256actual RAM IM2words (fixedFF emulator, not actual256IRQ/hardware probes);12cold/cached routes;6boss/reset/revisit routes;3normalcold/fire cases;debugdirectentry/Space redraw;16level/start TAP checksums/reconstruction plusrt.tap;other7regions/bank7/coldbootstrap/projectile sourceA816..A84B unchanged; ZIP CRC. Boss stress uses invulnerability/gameover bypass. Actual captures boss_probe_690.home.png and others inspected; foreground temporary matte/shared-cell clash remains possible, permanentbackgrounddamage fixed.\nCache boundaries and contracts in build/fullgame/l2_roles_restore_r127; previous rejected logs/JSON there are historical, final validation_summary binds region SHA. No hardware confirmation. Candidate RType_TS2068_r127.zip SHA{sha}. Stable99/100/stock64KB/sourceZIPs/reference projects unchanged. docs/l2_roles_restore_r127.txt.\n"
entry=entry.replace('Original320? ','')
if b'202. Completed r127'not in(R/'TEST_HISTORY.md').read_bytes():
 with(R/'TEST_HISTORY.md').open('ab')as f:f.write(entry.encode('ascii'))
 with(R/'PROJECT_STATE.md').open('ab')as f:f.write(f"\n2026-11-10 r127 completed L2 snake anatomy/boss backdrop fix, supersedes entries200/201 failed prototype. Immutable2592byte DOCK6CB00..D51F cache,189byte copier, stable9round/4spiny chain, originalhead/tail.700firingupdates/5exactbackground+cachechecks/31actors/128tiles/96palette160rows/12transitions6bossroutes/3coldfire/debug/tapesZIP PASS. PerrepairCPUcost reduced{perf['per_call_reduction_percent']:.1f}% vsconservative redraw,not hardwareFPS. build/fullgame/l2_roles_restore_r127/RType_TS2068_r127.zip SHA{sha};TEST_HISTORY202/docs/l2_roles_restore_r127.txt. Hardwarepending;stable100/stock64KBunchanged.\n".encode('ascii'))
print(zpath);print(sha);print(json.dumps(validation))
