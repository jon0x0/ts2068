from pathlib import Path
import json,zipfile,hashlib,functools
R=Path.cwd();O=R/'build/fullgame/startup_bulk_r77';B=R/'build/fullgame/terrain_token_fix_r76'
for n in range(1,9):assert(O/f'level{n:02d}_region.bin').read_bytes()==(B/f'level{n:02d}_region.bin').read_bytes()
assert(O/'rtype/RTCORE.TAP').read_bytes()==(B/'rtype/RTCORE.TAP').read_bytes();assert(O/'demand_loader.bin').stat().st_size==6142
for n in[1,3]:assert json.loads((O/f'initial_shift_L{n}.json').read_text())['passed']
assert json.loads((O/'preload_title_L5.json').read_text())['passed']
for n in[1,2,3]:assert json.loads((O/f'boss_level{n}.json').read_text())['passed']
def tape(p):
 raw=p.read_bytes();out=[];at=0
 while at<len(raw):
  size=int.from_bytes(raw[at:at+2],'little');v=raw[at+2:at+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;out.append(v);at+=size+2
 assert at==len(raw);return out
for p in(O/'rtype').iterdir():
 if p.suffix.lower()=='.tap':tape(p)
for n in range(1,9):
 raw=(O/f'level{n:02d}_region.bin').read_bytes();assert b''.join(v[1:-1]for v in tape(O/f'rtype/LEVEL{n:02d}.TAP')[1::2])==raw;assert b''.join(v[1:-1]for v in tape(O/f'rtype/START{n:02d}.TAP')[1::2])==b''.join(raw[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7])
readme='''R-Type TS2068 r77 - queued startup Load All stays in the loader
Replace complete lowercase rtype folder, reset, run rt.tap.

Initial progress now has a visible total. Shift-L queued during startup loads
remaining levels BEFORE game initialization, without the intermediate game/
context-snapshot/loading-screen round trip. Counter continues from initial
files to 406 total (70 initial files plus 7 x48 remaining level fragments),
rather than restarting at 0 of336. Load All completes at the title screen.
Changing selected level during initial loading remains supported. Normal
single-level startup still uses70; gameplay Load All counts remaining files.
All text remains small. Terrain/artwork/gameplay fixes are unchanged r76.

Implementation: cold entry in existing worker, with normal hot entry retained.
Cold bank5 transfer buffer uses E000 rather than the HOME core workspace; buffer
selection is restored afterwards. Initial validity mask survives cold handover.
Small8x8 digit table frees space for extension; loader remains6142 bytes.

Tests: queuedShift-L/released key, L1 and changed-to-L3 startup, all8resident
before title, visible406 total, standard loading video during bulk phase;
normal L1-L3boss routes and gameplay L5 LoadAll/title/cached fire restart pass.
All level images and core byte-identicalr76; all tape checksums/reconstruction
pass. Hardware confirmation pending. Stock64KB cartridge unchanged.
'''
(O/'README.txt').write_text(readme,encoding='ascii');z=O/'RType_TS2068_r77.zip'
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED)as f:
 for p in sorted((O/'rtype').iterdir())+[O/'README.txt']:
  info=zipfile.ZipInfo(str(p.relative_to(O)).replace('\\','/'),date_time=(2026,11,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;f.writestr(info,p.read_bytes())
with zipfile.ZipFile(z)as f:assert f.testzip()is None
report={'version':77,'bytes':z.stat().st_size,'sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'all_level_images_and_core_identical_r76':True,'loader_bytes':6142,'queued_startup_total':406,'cold_bulk_before_game':True,'queued_L1_changed_L3_passed':True,'visible_total_and_video_checks_passed':True,'hot_L5_preload_restart_passed':True,'normal_L1_L2_L3_bosses_passed':True,'tapes_valid':True,'hardware_tested':False};(O/'validation_summary.json').write_text(json.dumps(report,indent=2))
for name,text in [('PROJECT_STATE.md','Latest r77 queued Shift-L startup bulk loading runs before game init, avoiding snapshot/handover screen interruption. Visible total restored; queued count continues through406files rather than reset0of336. Normal startup70 unchanged. Small digit renderer/table reclaimed extension space; loader6142 unchanged. Cold worker separate entry preserves core workspace usingE000 bank5buffer, restores buffer selector; all-valid mask retained to title. Gamelevelimages/RTCORE byte-identicalr76. build/fullgame/startup_bulk_r77/RType_TS2068_r77.zip. TEST_HISTORY152.'),('TEST_HISTORY.md','152. Startup LoadAll continuity r77 (2026-11-07). Read state/history. User r76 missingtotal, blank/block then0to336. Missingtotal caused r74 staticdigit removal while initial startup onlyupdates numerator. Previous queued cold request entered native game then used hot snapshot; replaced with cold branch in existing preloadworker reached beforeprepare via loaderextension. Cold entry counts/loads other7levels and returns selectedregion withall-valid, clearsqueuedrequest, then one normalhandover to title. Cold bank5buffer E000 avoids worker8000 and retained HOME C000 coreworkspace; restores runtime C000 selector. No initialcontextsnapshot required. Hotworkerpath retained, coldflag binaryinitialized0. VALID targetmask initialized on both paths and copied to coldhandover, notcollapsed toselectedbit. Compact8x8digit renderer uses80bytes versus320, extension101bytes occupies reclaimedglyphpadding; loader6142bytes unchanged. UIcompressed1611<=1650, static070total visible, queuedprogress total406 andcoldworker startsdone70/includesinitialfiles, no0of336reset. Source scripts/build_startup_bulk_r77.py.\nInitial failed allocation1687>1650 resolved via compactglyphstorage, not shrinkinglogo. Screen-mode assertion initially includedfinalhandover41, scopedtoactivebulk3. Onscreen total sampling initially hit incompletepublication/staleworkerfields; finalverification waitsforcomplete406glyphs. Fontpath corrected. QueuedL1 and changedL3 tests pass all8resident beforetitle (8880/9029frames respectively); standardvideo maintained duringactivebulk, releasedShift-L recognized, actual406glyphs verified. bulk_progress.png inspected, showsnormaltextandvisible406total; capturedinitialverifyingstage stillshowsqueuedlabel. NormalL1/L2/L3 bossroutes pass160postjump; finalcounter change touchesstartup only. FinalhotL5LoadAll/title/cachedsocket2fire restart passes. All8levelimagesandRTCORE identicalr76; allTAP checksums/LEVEL/START reconstruction/ZIPCRCpass. No graphics/gameplaychanges, hardwarepending, stock64KB unchanged. Archive '+report['sha256']+' '+str(report['bytes'])+'bytes.')]:
 with(R/name).open('ab')as f:f.write(('\n\n'+text+'\n').encode('ascii'))
print(json.dumps(report,indent=2))
