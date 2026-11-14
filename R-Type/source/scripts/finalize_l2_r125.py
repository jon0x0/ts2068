from pathlib import Path
import json,zipfile,hashlib,functools
R=Path.cwd();O=R/'build/fullgame/l2_scroll_projectile_r125';B=R/'build/fullgame/l2_complete_r124'
def j(n):return json.loads((O/n).read_text())
def blocks(p):
 b=p.read_bytes();out=[];at=0
 while at<len(b):
  n=int.from_bytes(b[at:at+2],'little');v=b[at+2:at+2+n];assert n>1 and len(v)==n and functools.reduce(int.__xor__,v,0)==0,(p,at);out.append((v[0],v[1:-1]));at+=n+2
 assert at==len(b);return out
for n in range(1,9):
 v=(O/f'level{n:02d}_region.bin').read_bytes();assert len(v)==65536
 for kind in ['LEVEL','START']:
  data=b''.join(d for flag,d in blocks(O/'rtype'/f'{kind}{n:02d}.TAP')if flag==255);want=v if kind=='LEVEL'else b''.join(v[p*8192:(p+1)*8192]for p in[0,1,4,5,6,7]);assert data==want,(kind,n)
 if n!=2:assert v==(B/f'level{n:02d}_region.bin').read_bytes()
a=(O/'level02_region.bin').read_bytes();b=(B/'level02_region.bin').read_bytes();assert a[0xe000:]==b[0xe000:];assert a[0xd920:0xdc40]==b[0xd920:0xdc40],'Cold native bootstrap source must remain intact'
assert any(b'R125 PREPARING' in v for _,v in blocks(O/'rtype/rt.tap'))
for n in ['actual_tile_decode_validation.json','actual_actor_decode_validation.json','actual_im2_validation.json','palette_missile_validation.json','native_revisits_validation.json','l2_boss_revisits_validation.json','debug_validation.json']:assert j(n)['passed'],n
assert len(j('actual_tile_decode_validation.json')['results'])==128 and len(j('actual_actor_decode_validation.json')['reports'])==27
assert len(j('native_revisits_validation.json')['results'])==12 and len(j('l2_boss_revisits_validation.json')['results'])==6
fire=j('unmodified_l2_fire_validation.json');assert len(fire)==3 and all(x['passed']for x in fire)
f=j('L2_firing_approach.json');assert f['u']==1547 and all(str(i)in f['drawCounts']for i in range(180,190)) and set(x['fine']for x in f['fineShots'])==set(range(8))
r=j('boss_stop_probe.json');assert max(x['reveal']for x in r['rows'])==18 and all(x['reveal']==0 for x in r['rows']if not x['freeze'])
ct=j('integration_contract.json');ac=j('L2_actor_contract.json');ac['native_prefix_snapshot']=ct['snapshot'];ac['extension']['restore_native_bank5']=ct['tile_symbols']['restore_native'];ac['bank4_unchanged']=False;(O/'L2_actor_contract.json').write_text(json.dumps(ac,indent=2))
validation={'passed':True,'actual_global_palette_rows':96,'terrain_scanlines':160,'front_and_back_mapping_preserved':True,'actual_tile_cases':128,'actual_actor_packets':27,'all10_scorpion_frames_drawn':True,'sustained_firing_updates':1547,'sustained_firing_emulated_frames':f['frame'],'cold_fire_cases':3,'general_transition_routes':12,'boss_reset_transition_routes':6,'all16_tapes_reconstructed':True,'actual_IM2_words':256,'other7_levels_unchanged':True,'cold_bootstrap_source_preserved':True,'hardware_tested':False,'debug_test':'Direct entry and Space redraw only'}
(O/'validation_summary.json').write_text(json.dumps(validation,indent=2));(O/'integration_static_validation.json').write_text(json.dumps({'passed':True,'tape_checksums':True,'reconstruction':True,'other7_levels_identical_r124':True,'bank7_unchanged':True,'bootstrap_source_intact':True},indent=2))
text='''R-Type TS2068 r125 - L2 scrolling colours and player projectile fix

Replace the entire rtype folder, reset, and launch rtype/rt.tap.
Startup identity: R125 PREPARING.

r124 missed the regular flat-cell scrolling path: it reverted to the old yellow
terrain colours. That path now uses the selected per-scanline terrain palette.
It preserves the actual caller bank mapping, including back-buffer updates.
Boundary, initial and regular scrolling now use the same palette policy.

r124 also reused the live shared actor/projectile palette at1B20. All96 original
rows are now preserved losslessly in a423-byte compressed block. First use
expands it into L2 runtime RAM D940..DC3F AFTER the native bootstrap copy; the
cold bank image retains its original bootstrap bytes. All96 renderer rows have
been checked against the original table in actual emulated Z80 RAM.

To fit safely, tile packets use planar pixels and reconstruct redundant native
cell attributes exactly. All128 native/body/bounds/moving/stopped decoder cases
match expected bytes. The 52-entry pointer table uses retired authoring palette
space1160..11C7; the131-byte reveal hook uses106C..10EE. Initial-copy-only access
to those old palette ranges was traced; no normal gameplay reads in the r124
full-level firing audit. Scratch/source/bootstrap ownership is documented in
integration_contract.json and palette_contract.json. No bank7 storage reuse.

Selected L2 actors and all TEN scorpion frames retained. Native terrain bitmap
silhouettes/dimensions unchanged. Detailed boss reveal after stopping retained.
Other seven levels unchanged. Colours follow the chosen material settings with
a conservative full-row scrolling policy; this is not a new arcade tile map.

Verification: all96 shared palette rows; all160 terrain scanlines in both front
and back mappings;128 tile cases;27 actor packets;1547 sustained-firing updates
through the ordinary approach;3 unmodified cold/fire timings;12 general and6
boss/reset/revisit routes;18-tile stopped reveal;all16 tape checksums and full
reconstruction. Actual screen captures firing_64.home.png,
ordinary_L2_col54.home.png and boss_probe_160.home.png inspected. All256 IM2
words checked in actual RAM; emulator fixedFF vector, not hardware IRQ probes.
Long approach uses an invulnerability/game-over bypass for coverage. Separate
startup/fire tests do not. Debug direct-entry/font/Space redraw checked.

Hardware confirmation pending. Stable r99/r100, source ZIPs/reference projects
and stock64KB cartridge target remain unchanged. Full banked disk game only.
'''
(O/'README.txt').write_text(text);(R/'docs/l2_scroll_projectile_r125.txt').write_text(text)
p=O/'RType_TS2068_r125.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for f in sorted((O/'rtype').iterdir()):
  if f.is_file():z.write(f,'rtype/'+f.name)
 for n in ['README.txt','validation_summary.json','integration_static_validation.json','integration_contract.json','palette_contract.json','L2_actor_contract.json','selected_l2_choices.json']:z.write(O/n,n)
with zipfile.ZipFile(p)as z:assert z.testzip()is None and 'rtype/rt.tap'in z.namelist()
sha=hashlib.sha256(p.read_bytes()).hexdigest();(O/'SHA256.txt').write_text(sha+'  '+p.name+'\n')
entry=f'''
198. r125 L2 post-first-frame terrain yellow and corrupted player missile regressions (2026-11-10). Rootcauses: r124 changed initial/boundary colour paths but left flat0E40 and slow0E00 resolving86 through oldFBD0 yellow row; r124 incorrectly retired liveglobal actor/projectile palette1B20..1E1F. Fixed highmarked0E91 resolver to row_palette via0FB1; actualIN A,(F4) caller mapping preserved, not hardcoded3. Initial forced-map3 draft produced large vertical bitmap streaks in backbuffer updates despite directdecoder tests; visuallycaught/quarantined, actualmap-preserving fix verified. Teststack5CE0 invalidwhenmap7 mapsDOCK2, movedteststacktoHOMEFFF0; both3/7 returnmapping and160scanlines nowchecked.
Lossless planar tilecodec5185bytes (nativeattrs redundant/derived from cellpixels) frees room for423bytecompressed ORIGINAL768byteglobalpalette. Originalsource1B20 nowintentionallyreused onlywithrenderer157A CALLglobal_palette instead ofLDBC1B20. Firstglobalcall AFTERcoldbootstrap expands intoDOCK6D940..DC3F; lowGLOBAL_FLAG prevents repeateddecompression. ColdbankimageD920..DC40 remainsbyte-identicaltor124. Initial proposedstaticbank6relocation FAILEDstartup because D930+is audio/bootstrapsource mirroredHOMEF930+,notfree; rejected. No bank7reuse. Pointertable1160..11C7, reveal106C..10EE usesretiredauthoringpaletteconstantregions; fullbaselinefiringauditfoundonlyinitialloadcopies (PC5E04), newtargetreads separatelyexpected. Nativeattributereconstruction39E0; interleave~1DEAx; globalhelper3998. Actual128decoderoutputs exact; all27actors/all10scorpions retained.
PASS finalbinary:96sharedglobalpalette rows exact,160terrainrows bothmaps3/7,128tilecases/27actorpackets,256actualRAMIM2words(fixedFFemulator/not256actualIRQprobes),1547sustainedfireupdates38561emulatedframes,all10scorpionIDs,all8finephases;3unmodifiedcoldfiretimings;12generaltransitions;6longboss/samelevel/cachedrevisits;18bossrevealafterstop;debugdirectentry/SpaceRAMredraw;all16tapechecksums/reconstruction,other7levelsidenticalr124,bank7unchanged,ZIPCRC. Visualfiring_64.home.png/ordinary_L2_col54.home.png/boss_probe_160.home.png inspected (finalcorrectterrain/noverticalstreaks); diagnosticsbuild/fullgame/l2_scroll_projectile_r125. Failedflat-map3captures overwrittenbyfinalcapture, failuredescription here; low_spare_audit.json/bank6_spare_audit.json retainedunderl2_complete_r124. No hardwareconfirmation. Priorr124staticdecodercoveragewasinsufficienttoestablishlivepaletteownership/end-to-endscrolling; futurechecks include actualpalettebytes, bank-sensitivecallercontracts and sustainedfirevisuals.
Candidatebuild/fullgame/l2_scroll_projectile_r125/RType_TS2068_r125.zip SHA{sha}; docs/l2_scroll_projectile_r125.txt. Stable99/100,stock64KB/referenceprojects/originalZIPsunchanged.
'''
state=f'''
2026-11-10 r125 fixesr124L2yellow-scroll/playerprojectilepalette regressions. Regularflat/slowpaths usechosenrowpalette withactualbankmappingpreserved; original96globalpalette rows retainedlosslessly andexpandedonlyAFTERnativebootstrap. Planartilepack5185bytes/52table inretiredauthoringpalette, all128tileoutputs exact. Sustainedfire1547updates,96palette/160rowchecks,27actors,3coldfire,12general+6bossroutes,tape/ZIPchecksPASS;visualfinalcapturesinspected. build/fullgame/l2_scroll_projectile_r125/RType_TS2068_r125.zip SHA{sha}. TEST_HISTORY198/docs/l2_scroll_projectile_r125.txt. Hardwarepending;stable100/stock64KBunchanged. Buildscripts/build_l2_final_r125.py thenfinalize_l2_r125.py; formerexperimentalstaticbank6layoutrejected.
'''
if b'198. r125 L2 post-first-frame'not in(R/'TEST_HISTORY.md').read_bytes():
 with(R/'TEST_HISTORY.md').open('ab')as f:f.write(entry.encode('ascii'))
 with(R/'PROJECT_STATE.md').open('ab')as f:f.write(state.encode('ascii'))
print(p);print(sha);print(json.dumps(validation))
