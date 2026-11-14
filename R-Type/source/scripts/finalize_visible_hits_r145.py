from pathlib import Path
import json,functools,zipfile,hashlib,shutil
R=Path.cwd();B=R/'build/fullgame/preparing_r144';O=R/'build/fullgame/visible_hits_r145';j=lambda n:json.loads((O/n).read_text())
for n in ['visible_collision_validation.json','native_revisits_validation.json','l5_retired_flip_validation.json','all_vector_validation.json']:assert j(n)['passed']
assert len(j('visible_collision_validation.json')['cases'])==7
assert len(j('native_revisits_validation.json')['results'])==14
assert set(q['to']for q in j('native_revisits_validation.json')['results'])==set(range(1,9))
r=j('settled_force_defeat.json');assert r['passed']and r['victory']and all(v==16 for v in r['counts'].values())
assert all(q['passed']for q in j('unmodified_target_levels_fire_validation.json'))
e=(O/'projectile_clock.bin').read_bytes();assert len(e)==663 and 0x5880+len(e)<0x5b5b
for n in range(1,9):
 a=(B/f'level{n:02d}_region.bin').read_bytes();b=(O/f'level{n:02d}_region.bin').read_bytes();assert len(a)==len(b)==65536
 assert all(0xf100<=i<0xf397 for i,(x,y)in enumerate(zip(a,b))if x!=y)
 assert b[0xf100:0xf397]==e
 assert a[0x8000:0xa000]==b[0x8000:0xa000]
count=0;coreOld=b'';coreNew=b''
for p in (O/'rtype').glob('*.TAP'):
 s=p.read_bytes();at=0;parts=[]
 while at<len(s):
  n=int.from_bytes(s[at:at+2],'little');q=s[at+2:at+2+n];assert len(q)==n and functools.reduce(int.__xor__,q)==0
  if q[0]==255:parts.append(q[1:-1])
  at+=n+2
 assert at==len(s);count+=1
 if p.name.startswith('LEVEL'):assert b''.join(parts)==(O/f'level{int(p.stem[-2:]):02d}_region.bin').read_bytes()
 if p.name.startswith('START'):
  b=(O/f'level{int(p.stem[-2:]):02d}_region.bin').read_bytes();assert b''.join(parts)==b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7])
 if p.name=='RTCORE.TAP':coreNew=b''.join(parts)
s=(B/'rtype/RTCORE.TAP').read_bytes();at=0
while at<len(s):
 n=int.from_bytes(s[at:at+2],'little');q=s[at+2:at+2+n];at+=n+2
 if q[0]==255:coreOld+=q[1:-1]
diff=[i for i,(x,y)in enumerate(zip(coreOld,coreNew))if x!=y];assert diff==[0x152e,0x1df5],diff
# Capture the audit evidence in this release folder, leaving the earlier release untouched.
for n in ['l1_collision_timing_trace.json','owner_coverage_trace.json']:shutil.copy2(B/n,O/n)
coverage=json.loads((O/'owner_coverage_trace.json').read_text());assert len(coverage)==1500 and not any(q['missing']for q in coverage)
readme='''R-Type TS2068 r145 - collision coverage follows the displayed frame

Replace complete rtype folder, reset, run rtype/rt.tap.
Fast normal/spread shots now query the retained displayed-frame owner map
already used by the smooth player. Previously they queried the next frame's
working map while enemies were still displayed at their previous positions.
This shared change applies to all eight levels. Native damage, armor,
transparent gaps, boss openings/weak points and weapon behavior are retained.
No global rectangle inflation or sprite rescaling.

The earlier24x24-versus32x32 explanation was incomplete: the compiled renderer
already builds collision ownership at its actual enlarged dimensions. A1500draw
L1 audit (including walkers) found no missing owners immediately after drawing;
the reproduced problem is the time mismatch between that map and display.

Negative controls reproduce both old errors (missing a displayed target and
hitting a future position). Fixed cases, terrain, empty gaps and reused-actor
safety pass. Real L1 firing reaches native damage.14cold/cached transitions
cover all8levels. Cold L1/L5 firing and L4 native16hits/target victory pass.
L5 boss160updates/13components and all256IM2targets pass; actual return probes
at0/255, remaining targets identical. These are scripted emulation checks,
not hardware confirmation or complete all-boss playthroughs.

Clock code remains below5B5B vector/private stacks. Source grows640->663bytes;
F380..F396 retires23bytes of an obsolete L5 flipped cache prefix. The current
phased renderer has no direct base reference and no non-copy reads in the
cold/boss trace. Active artwork, native descriptors and L5 IM2/UI are unchanged.
CORE differs only in two copy-length bytes. All20TAP checksums and LEVEL/START
reconstruction pass. L7 silent preparation, score colors, L4 recovery retained.
Stable r100 and stock64KB cartridge target unchanged.
'''
(O/'README.txt').write_text(readme);(O/'rtype/README.txt').write_text(readme)
summary=dict(passed=True,all8levels_shared_fix=True,negative_controls=2,fixed_collision_cases=5,transitions=14,l1_rendered_cells_audited=1500,missing_owner_after_draw=0,L4_native_victory=True,L5_vector_targets=256,engine_bytes=len(e),core_changed_bytes=diff,tap_files=count,hardware_tested=False)
(O/'validation_summary.json').write_text(json.dumps(summary,indent=2));(O/'release_manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((O/'rtype').iterdir())if p.is_file()},indent=2))
p=O/'RType_TS2068_r145.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED)as z:
 files=[(q,'rtype/'+q.name)for q in sorted((O/'rtype').iterdir())if q.is_file()]+[(O/n,n)for n in ['README.txt','validation_summary.json','release_manifest.json','collision_contract.json','visible_collision_validation.json','native_revisits_validation.json','l5_retired_flip_validation.json','all_vector_validation.json','unmodified_target_levels_fire_validation.json','settled_force_defeat.json','l1_collision_timing_trace.json']]
 for q,name in files:
  i=zipfile.ZipInfo(name,(2026,11,13,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,q.read_bytes())
with zipfile.ZipFile(p)as z:assert z.testzip()is None
sha=hashlib.sha256(p.read_bytes()).hexdigest()
with (R/'TEST_HISTORY.md').open('a',encoding='utf-8')as f:f.write('\n\n234. r145 displayed-frame projectile collision (2026-11-13). User requests artwork-matching collision everywhere intended. Correct earlier incomplete24vs32descriptor inference: compiled renderer supplies enlarged dimensions and visibility plans to native owner publication;1500actualL1draws IDs12/18/19/30-33/41/49-51/53-55 have0nonemptycells missing ownership immediately after draw. Native descriptors alone do not establish compiled collision footprint. Timing trace1305updates found91projectile queries with workingowner<80but retained displayedowner81..F9; no stale-signature rejects. IRQ bolts were querying future working7E00grid while visible frame still had actor atpreviousposition.\nMinimal final fix retains original640byte clock instructions except3lookupCALLtargets, adds23byte visible_owner at5B00..5B16: originalC0E4computesDE, add7A80toaddress retainedF880+cell, map8Dread, restore0D, returnowner; BC/HLpreserved, DEscratch asnative. Reuseexistingplayerretainedmap; no frame scans, no mask/rectangleinflation; native charged/missile/main-loopdamage rules unchanged. Both cold/runtime COREcopycounts640->663 (only2changedbytes atconcatenated152E/1DF5). SourceF100..F396 grows23bytes intoobsoleteL5flippedcacheprefix. Currentmotion/cacheimages andnativecompositorhave no LD DE/HL,F380base reference; actualcold/boss160update13componenttrace has0non-block graphicsreads ofretiredprefix. Testfixturebridges5E04/7B04 explicitlyinspect bankcopies, Z80blockcopyCPU.pc maypointpastEDB0; audit excludes those knowncopies, not general reads. AllL5IM2/UI reservations unchanged, runtimeend5B17 safely below5B5Bvector and5B60privateworkspace.\nRejectedcompact prototypes failed size, and an automaticJP->JR trial broke fixed3byte dispatch entries; never released, final original jump table and all clock body behavior retained. Early isolated tests carriedrunning CPU/bankstate and misdispatch artifacts fromrejectedprototype; final directprivate-stack unitcases use explicitmode2 and unchanged dispatch. Negativecontrols: oldclock misses retainedenemy andhits futureenemy; finalreversesboth. ActualnativeHP3->2 onshownenemy; future/empty/reusedactor no damage, terrainqueuednormally. RealL1protectedfiring1287updates154queued/146resolver/85damage-pathentries,0stale rejects; baselinecounts are notsame-gameplaytrajectory orproofeveryintersectingpixelhits.\nPASS14transitions coverall8levels includingcoldL5/L8, cachedL7preparationstable/silent; coldunmodifiedL1fire488updates3655IRQs/L5fire424updates4372IRQs. L4settlednormalpickup/reardock pilot16hits each/nativevictory encounter575, playerprotected,noenemyHP/timeredits. L5BBboss160updates13components,256vectorentriesidentical5B5B, actualreturnprobes0/255/fixedFFemulation; nohardwareclaim. Olderall-bossmotionharnesshit establishedC7F0preloadstack, knownL2selfmods and locked-axisL2snakes; corrected allowances/skip but finalvector/bossclaim scopedL5, notallbossdefeats. All20TAPchecksum/allLEVELSTARTreconstruction/staticmutation/ZIPCRC PASS. Activeart/descriptors/bossopenings/armor/pickupbehavior unchanged; stable100/stock64KB/priorarchives/referencesunchanged. '+str(p.relative_to(R))+' SHA256'+sha+' Hardwarepending. Scripts build_visible_hits_r145.py,verify_visible_collision_r145.mjs,trace_owner_coverage_r144.mjs,trace_l1_collision_timing_r144.mjs,trace_l1_damage_r145.mjs,verify_native_revisits_r145.mjs,verify_cold_launcher_r145.mjs,verify_all_vectors_r145.mjs,probe_l4_settled_force_r145.mjs,finalize_visible_hits_r145.py.\n')
with (R/'PROJECT_STATE.md').open('a',encoding='utf-8')as f:f.write('\nr145 fast normal/spread collision now uses existing displayed-frame F880owner map acrossall8levels instead offutureworkingmap. Corrects earlier native-descriptor-only footprint inference. Actualcompiled footprints alreadyowner-expanded; no blanketinflation. Negativecontrols/nativeHP/gaps/reusedactor/14alllevelroutes/coldL1L5/L4victory/L5vectors/staticTAP PASS. Source663bytes retires23obsoleteL5flipcachebytes;currentactiveart/IM2 unchanged. '+str(p.relative_to(R))+' SHA'+sha+' TEST_HISTORY234;hardwarepending.\n')
(R/'docs/visible_hits_r145.txt').write_text(readme+'\nSHA256 '+sha)
print(p);print(sha)
