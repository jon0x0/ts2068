from pathlib import Path
import json,sys,functools,zipfile,hashlib
R=Path.cwd();B=R/'build/fullgame/l1_head32_r110';O=R/'build/fullgame/l1_ghost_r114';sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack
c=json.loads((O/'ghost_contract.json').read_text());w=next(v for v in json.loads((O/'walker_runtime.json').read_text())if v['level']==1);meta=next(v for v in json.loads((O/'generic_manifest.json').read_text())if v['level']==1);raw=(O/'L1_runtime_art.bin').read_bytes();old=(B/'L1_runtime_art.bin').read_bytes();assert raw[:len(old)]==old and len(raw)==len(old)+768;z=zipfile.ZipFile(R/'convref/rtype-l1-ghost-assets.zip');assert z.testzip()is None
for a in w['assets']:
 if a['key']=='ghost32':assert raw[a['pointer']-c['artbase']:a['pointer']-c['artbase']+256]==z.read(f"ghost/frame_{a['frame']:02d}.pairs.bin")
assert c['imageend']==c['artbase'] and c['guard_bytes']==18 and c['artend']==0xc000 and c['end']<=0x3a00;image=(O/'L1_runtime_image.bin').read_bytes();assert image[-18:]==bytes([0xa7])*18
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();a=(B/f'level{n:02d}_region.bin').read_bytes();assert len(b)==65536
 if n==1:
  allowed=set(range(0x2400,0x3a00))|{c['preload_table_operand'],c['preload_table_operand']+1,c['install_operand'],c['install_operand']+1,c['warmup_operand'],c['warmup_operand']+1};assert all(x==y or i in allowed for i,(x,y)in enumerate(zip(a,b)));assert a[0xa000:0xc000]==b[0xa000:0xc000];assert a[0x2000:0x2400]==b[0x2000:0x2400];assert unpack(b[c['rawptr']:])==raw and unpack(b[c['imageptr']:])==image;assert unpack(b[0x2400:])==(R/'build/graphics/l1_ghost_converter/ghost_plan_cache.bin').read_bytes();assert unpack(b[c['backup_ptr']:])==bytes.fromhex(meta['backup'])
 else:assert a==b
 for name in [f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  t=(O/'rtype'/name).read_bytes();p=0;parts=[]
  while p<len(t):
   size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0
   if v[0]==255:parts.append(v[1:-1])
   p+=size+2
  assert b''.join(parts)==(b if name.startswith('LEVEL')else b''.join(b[k*8192:(k+1)*8192]for k in [0,1,4,5,6,7]))
for name in ['RTCORE.TAP','RTPRELD.TAP','RTBOOT.TAP']:assert(B/'rtype'/name).read_bytes()==(O/'rtype'/name).read_bytes()
for p in(O/'rtype').glob('*.tap'):
 t=p.read_bytes();i=0
 while i<len(t):
  n=int.from_bytes(t[i:i+2],'little');v=t[i+2:i+2+n];assert len(v)==n and functools.reduce(int.__xor__,v,0)==0;i+=n+2
for name in ['ghost_live_validation.json','shared_live_validation.json','native_revisits_validation.json','precomputed_equivalence.json']:
 assert json.loads((O/name).read_text())['passed']
fire=json.loads((O/'unmodified_l1_fire_validation.json').read_text());assert len(fire)==3 and all(x['passed']and x['region']==0 for x in fire);timing=json.loads((O/'timing_comparison.json').read_text());rs=timing['reports'];oldMs=rs[0]['ghost']['meanMs'];unoptMs=rs[1]['ghost']['meanMs'];newMs=rs[2]['ghost']['meanMs'];cost=(newMs/oldMs-1)*100;gain=(1-newMs/unoptMs)*100
summary=dict(passed=True,base='r110',sourceZIP=c['source_zip_sha256'],exactExportedFrames=True,frames=3,size=[32,32],settings=json.loads(z.read('choices.json'))['families']['ghost']['settings'],previousArtUnchanged=True,other7LevelsIdentical=True,layout=c,precomputedPlanEquivalenceCases=96,ghostDraws=10866,guardIntact=True,oldGhostUpdateMs=oldMs,newGhostUpdateMs=newMs,updateTimeCostPercent=cost,precomputedTimeSavingPercent=gain,hardwarePending=True);(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
readme=f'''R-Type TS2068 r114 - chosen arcade ghost artwork

Replace the COMPLETE rtype folder, reset, launch rtype/rt.tap.
Startup R114 PREPARING. Ghosts appear later in ordinaryL1 (not double-B).

Your exact exported32x32cels450/452/454 palette6 replace native35/36/37.
Settings56/66/89/gamma0.74, SierraLite, normalpalette. No recolouring or resize.
Three native poses select corresponding three exported frames. Previous chosen
walkers, snake and L3 exhaust are retained; all7otherlevelregions byte-identical.

Compiledart relocated A900->A870 tofit6032bytes endingexactlyC000. Runtimeimage
endsA870 including18byte A7guard; executable/data endsA85E. Guard intact after
1800updates. Packedpayload397B<3A00. No extraRAMbank. Nativegraphics sources,
movement and collision logic unchanged. Head/ghost32visuals exceed native24
footprints as previously discussed; collision logic retains original behaviour.

Cached per-tilevisibility removes repeatedghostsource scanning. Uses768bytes
of the alreadyretired bank6cache, with smallhelperatC100. Same foreground,
clipping and IRQ setup; other sprites fall back to originalplanner. Exactplan
headers/endpointer match originalplanner in96pose/flip/position tests.

PERFORMANCE (emulated CPUcycles, not physicalhardwareFPS):
Busyghostwindow920..1100 mean update {newMs:.1f}ms versus {oldMs:.1f}ms oldwhite24x24.
This is {cost:.1f}%moreupdate time. Optimization saves {gain:.1f}%versus initial32x32
implementation. Largercolourghosts still have material cost in busy encounters.
The previoussnake/headwindows are nearlyunchanged. Playerinterruptcadence is
not measured by these nativewhole-scene intervals.

1800ordinaryupdates/10866ghostdraws/all3poses/exactRAMart/guardPASS; testuses
explicitgameoverbypass. ThreecoldL1firetimings WITHOUTbypass and12cold/cached
levelroutesPASS. ExactZIPassetidentity/otherart/native-source/scope/bankbounds,
packetdecode/planbackup/allTAPreconstruction/checksums/ZIPCRC pass.
Hardwareconfirmation pending. Stable100/r110archives retained. No unoptimized
r113packagepublished. Stock64KBtarget remains separate and unchanged.
''';(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype/README.txt').write_text(readme,encoding='ascii');(R/'docs/l1_ghost_r114.txt').write_text(readme,encoding='ascii')
pack=O/'RType_TS2068_r114.zip'
with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','validation_summary.json','selected_ghost_choices.json','timing_comparison.json','ghost_gameplay_comparison.png']:f.write(O/name,name)
with zipfile.ZipFile(pack)as f:assert f.testzip()is None
sha=hashlib.sha256(pack.read_bytes()).hexdigest();print(pack);print(sha,pack.stat().st_size)
entry=f'''\n190. Chosen ghost32 integration + precomputed plans r114 (2026-11-09). User supplies convref/rtype-l1-ghost-assets.zip; CRCpass/SHA{c['source_zip_sha256']}. Explicitchoicesinstructionoverridesexportdecision=tweak. Exact3columnpaired32x32frames450/452/454palette6,56brightness66contrast89saturationgamma.74/SierraLite installednative35-37->staticvirtual180-182, nativeposeorderretained. No reconversion/resize/newart. Allpriorrawartprefixunchanged; allother7regionsidenticalr110includingL3exhaust/L5. Nativebitmap/palette/descriptors/coordinates/collisionunchanged.\nArt6032bytes requiresA870..BFFF exactly; runtimeendA85Eplus18byteA7guardtoA870; guardintactafter1800updates. No extraRAMbank. Payload397B<3A00. Unoptimizedr113initial700updatetestfoundnoghosts(targetnotyetspawned); extendedto1800, firstghostu902,10866draws/all3virtualposesPASS. Initialbenchmarkscriptbadclosingbracketfixed,testonly. Unoptimizedghostmean440.71ms/2.269updates/svsr110old24mean311.33ms/3.212updates/s inwindow920..1100. Nativeper-poseprecomputedvisibilityrequestedbyquality/performanceintent: exactsameart, 3x16flags +C100helper inretiredDOCK6cache,768bytepreload, skipsoriginalsource-scanningandrowmaskbuildingforghostsphase0 only; allothersfallbackDCEF. SourcepointersderivedfromalignedBD00/BE00/BF00 plusflipmask, not arbitrarycalleraddresses. Existing0080foreground+clipchecks andrawIRQvectorsetup retained; targetplansbuiltusingexistingA44D/A45E helpers. Full4fliptemplates exceededcompressed3A00 (3BCC); compact4bytetriplesstill3A5C, reducedto48flagbytes+253bytehelperfits397B, no overflowartifactreleased.\nEquivalenceharnessinitialgenericFFE0stackinvalidunderbankmapping(loopPC3), correctedtesttoexistingbankstableDOCK2private5CE0stack. First96caseattemptcaughtstalescreen_x/yDDA7/DDA8fromoldsource; actualcurrentmetadataDE27/DE28, correctedbeforegameplay/package. Final96cases all3poses4flips8positionsincludingclipped/foregroundcomparemeaningfulplanheaders/end/IX/map/IexactPASS. No mismatchingoptimizedversionpublished.\nFinaloptimized1800updates/10866ghostdraws/all3poses, previoussnake674round783head79draws, exactRAMart/18byteguardPASS. Longtracegameoverbypassexplicit. ThreecoldL1firetimingswithoutbypassPASS. Twelvecold/cachedroutes/native-source/attributes/core/artidentityPASS. Staticexactexportassetprefix/7regions/scope/nativebitmap/palette/backup/runtime/cachepacket/bankbounds/all16LEVELSTARTreconstructions/allTAPchecksums/ZIPCRCpass. Optimizedghostmean420.10ms/2.380updates/s, {gain:.2f}%timeimprovementoverunoptimizedbutstill+{cost:.2f}%timevsoldwhite24. Snakewindow201.42vs201.44ms, head193.73vs192.76ms, earlyoverall177.43vs176.75ms. Explicitlyreportedcrowdedghostslowdown,nofalseperformanceequivalenceclaim. AlltimingsdeterministicemulatedCPUcycles3528000Hz,nothardwareFPS/playerIRQcadence.\nActualRAMghost_920/940/960/1000.pngr113generated;ghost_940visuallyinspected. r113ghost_gameplay_comparison.pngrecorded. Finalr114ghost_gameplay_0/1.pngandghost_gameplay_comparison.pngu960generated/visuallyreviewed:goldgrayredchosenheadsintact,3poseslargerthanold24. Earlierheadcomparison andeditorimagesunchanged. Scriptsbuild_l1_ghost_r113/114.py,prepare_ghost_precomputed_plan.py,verify_ghost_precomputed_equivalence.mjs,verify_l1_nofire_r113/114.mjs,verify_cold_l1_fire_r113/114.mjs,verify_native_revisits_r113/114.mjs,measure_l1_ghost_r113/114.mjs,finalize_l1_ghost_r114.py;src/l1_ghost_precomputed_plan.asm;docs/l1_ghost_r114.txt. Packagebuild/fullgame/l1_ghost_r114/RType_TS2068_r114.zip SHA256{sha} {pack.stat().st_size}bytes. Hardwarepending;stablelatest100andpriorr110preserved;references/sourcearchives/stock64KBunchanged.\n'''
with(R/'TEST_HISTORY.md').open('ab')as f:f.write(entry.encode('ascii'))
with(R/'PROJECT_STATE.md').open('ab')as f:f.write(b'\n2026-11-09 candidate r114: chosen arcadeghost32/native35-37 withprecomputedvisibility; build/fullgame/l1_ghost_r114/RType_TS2068_r114.zip. Exactexport3poses;1800update/coldfire/12revisit/96plan-equivalence/staticcontracts pass. Busyghostencounter+35%updatetimevsr110old24;hardwarepending. Priorart/other7levelsunchanged;stablelatest100preserved. TEST_HISTORY190/docs/l1_ghost_r114.txt.\n')
