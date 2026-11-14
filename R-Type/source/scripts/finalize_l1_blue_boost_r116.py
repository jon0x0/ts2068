from pathlib import Path
import json,sys,zipfile,functools,hashlib
R=Path.cwd();B=R/'build/fullgame/l1_ghost_r114';O=R/'build/fullgame/l1_blue_boost_r116';sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack;from build_reviewed_r72 import frames
c=json.loads((O/'blue_contract.json').read_text());w=next(x for x in json.loads((O/'walker_runtime.json').read_text())if x['level']==1);meta=next(x for x in json.loads((O/'generic_manifest.json').read_text())if x['level']==1);z=zipfile.ZipFile(R/'convref/rtype-l1-blue-enemy-assets.zip');assert z.testzip()is None;choices=json.loads(z.read('choices.json'));blue=(O/'L1_blue_art.bin').read_bytes();assert blue==b''.join(z.read(f'blue/frame_{i:02d}.pairs.bin')for i in range(2));assert len(blue)==800;assert all(a&192==0 for a in blue[1::2]);assert blue[:400]!=blue[400:];assert(B/'L1_runtime_art.bin').read_bytes()==(O/'L1_runtime_art.bin').read_bytes();assert c['guard_bytes']==31 and c['end']<=0x3a00 and c['blueend']==0xc620 and c['blueend']<0xc7d0<0xc900;image=(O/'L1_runtime_image.bin').read_bytes();assert image[-31:]==bytes([0xa7])*31;assert b'\x21\x00\xc9\x11\x00\xc3\xcd\x4f\xde'in(O/'blue_load.bin').read_bytes()
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();old=(B/f'level{n:02d}_region.bin').read_bytes();assert len(b)==65536
 if n==1:
  used=set(range(16))|{t&127 for d in frames(old,1)for _,t,_ in d['cells']if t!=54};source=set()
  for r in c['source_ranges']:
   assert 0x2000<=r['address']<r['address']+r['bytes']<=0x2400;source.update(range(r['address'],r['address']+r['bytes']));assert all(((p-0x2000)//8)not in used for p in range(r['address'],r['address']+r['bytes']))
  allowed=source|set(range(0x2400,0x3a00))|{c['preload_table_operand'],c['preload_table_operand']+1,c['install_operand'],c['install_operand']+1,c['warmup_operand'],c['warmup_operand']+1};assert all(x==y or i in allowed for i,(x,y)in enumerate(zip(b,old)));assert b[0xa000:0xc000]==old[0xa000:0xc000];assert b[0xe000:]==old[0xe000:];assert all(b[0x2000+t*8:0x2008+t*8]==old[0x2000+t*8:0x2008+t*8]for t in used);packed=b''.join(b[r['address']:r['address']+r['bytes']]for r in c['source_ranges'])+bytes(c['source_tail']);assert unpack(packed)==blue and len(packed)==411;assert unpack(b[c['rawptr']:])==(O/'L1_runtime_art.bin').read_bytes();assert unpack(b[c['imageptr']:])==image;cache=unpack(b[c['cache_source']:]);assert cache==(O/'L1_preload_cache.bin').read_bytes();assert cache[:0x200]==(R/'build/graphics/l1_ghost_converter/ghost_plan_cache.bin').read_bytes()[:0x200];assert unpack(b[c['backup_ptr']:])==bytes.fromhex(meta['backup'])
 else:assert b==old
 for name in [f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  t=(O/'rtype'/name).read_bytes();i=0;parts=[]
  while i<len(t):
   size=int.from_bytes(t[i:i+2],'little');v=t[i+2:i+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0
   if v[0]==255:parts.append(v[1:-1])
   i+=size+2
  assert b''.join(parts)==(b if name.startswith('LEVEL')else b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]))
for name in ['RTCORE.TAP','RTPRELD.TAP','RTBOOT.TAP']:assert(O/'rtype'/name).read_bytes()==(B/'rtype'/name).read_bytes()
for p in(O/'rtype').glob('*.tap'):
 t=p.read_bytes();i=0
 while i<len(t):
  size=int.from_bytes(t[i:i+2],'little');v=t[i+2:i+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;i+=size+2
for name in ['blue_live_validation.json','ghost_live_validation.json','shared_live_validation.json','native_revisits_validation.json','precomputed_equivalence.json']:assert json.loads((O/name).read_text())['passed']
fire=json.loads((O/'unmodified_l1_fire_validation.json').read_text());assert len(fire)==3 and all(x['passed']and x['region']==0 for x in fire);timing=json.loads((O/'timing_comparison.json').read_text());a,b=timing['reports'];assert b['loaderStackChecks']>=1;early=(b['combined']['meanMs']/a['combined']['meanMs']-1)*100;busy=(b['ghost']['meanMs']/a['ghost']['meanMs']-1)*100
summary=dict(passed=True,base='r114',sourceZIP=c['source_zip_sha256'],exactExportedFrames=True,frames=2,size=[40,40],settings=choices['families']['blue']['settings'],previousBank5ArtUnchanged=True,other7LevelsIdentical=True,sourceStoredOnlyInUnusedColourRows=True,sourceBank7Unchanged=True,layout=c,boostDraws=1320,ghostDraws=10866,guardIntact=True,loaderStackChecks=b['loaderStackChecks'],earlyUpdateTimeChangePercent=early,busyUpdateTimeChangePercent=busy,hardwarePending=True);(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
readme=f'''R-Type TS2068 r116 - chosen flying action/boost enemy

Replace the COMPLETE rtype folder, reset, launch rtype/rt.tap.
Startup R116 PREPARING. OrdinaryL1 shows this enemy; doubleBskipsencounters.

Native41 now uses your EXACTtwoexported40x40actionposes260/262, alternating
whileflying. Settingsbrightness56/contrast56/saturation100/gamma0.35/SierraLite.
Noresize,reconversion orreplacementwithwalkingposes. Native movement/collision
and40x40footprint retained. Earlierchosenwalkers,snake,ghosts,L3exhaustretained;
bank5pairedartbyte-identicalr114 and all7otherlevelregionsbyte-identical.

New800byteart lives in retiredbank6cache C300..C61F. ExistingghosthelperC100,
blue-loaderC200/tableC260,ghostvariablesC2F0 do notoverlap. Packedsource411bytes
is gathered from22ranges in unusedDOCK1palette rows into scratchC900, then
expanded toC300. Everycolourrow referencedbyoriginalnativegraphicsandfirst16
reservedrowsremainsunchanged. Transparentmarker54neverreadsitscolourrow.
IMPORTANTforfuturebuilders: blue_contract.json source_ranges are now reserved;
neverreuse these rows for anotherpaletteconversion. Source unchanged after
1800updates and cachedrevisits. Bank7 is byte-identicalr114; no assetstorethere.
An earlierunpublishedbank7sourceexperimentfailedrevisittestandwasdiscarded.

Loaderstackuses isolatedDOCK6C7F0/saveC7F2 whilepreloading/gathering, with
callerSPandmappingrestored. Realstartupobservationspassed2stackrestorechecks.
Existingruntimeimage freshlyzerosactorphasearray; redundantclearremoved.
NativeIDs>=205guardedbefore compact205entrymap, twoframecounterforbase184.
Runtimeguard31bytes intact, bank5artA870..BFFF, newartendsC620, packedend39FE
below3A00. No extraRAMbank or changes to native bitmap/descriptordata.

Tests:1800ordinaryupdates/1320boostdraws/bothposes/exactbank6bytes/source/guard,
10866ghostdraws,96oldnewghost-planequivalencecases,threecoldfiretimings,
12cold/cachedlevelroutes, scope/source/asset/bounds/decode/TAPreconstruction/
checksums/ZIPCRC pass. Longordinarytraces explicitlyusegameoverbypass; coldfire
testsdoNOT. ActualRAMcomparisonincluded. Hardwareconfirmationpending.

CPU-emulatedtimingvsr114: early130..500updatetime {early:+.1f}%, busyghostwindow
920..1100 {busy:+.1f}% in thisspecificnofiretrace. DifferencesinIRQtiming affect
comparison; not proof ofa universalFPSgain orphysicalhardwaremeasurements.
Existingr114busyghostslowdownvsoriginalwhite24 remains; no redrawspeedclaim.

Stock64KBcartridgetargetseparate/unchanged. Stable100andpriorr114archiveskept.
''';(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype/README.txt').write_text(readme,encoding='ascii');(R/'docs/l1_blue_boost_r116.txt').write_text(readme,encoding='ascii')
pack=O/'RType_TS2068_r116.zip'
with zipfile.ZipFile(pack,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','validation_summary.json','selected_blue_choices.json','timing_comparison.json','blue_gameplay_comparison.png']:f.write(O/name,name)
with zipfile.ZipFile(pack)as f:assert f.testzip()is None
sha=hashlib.sha256(pack.read_bytes()).hexdigest();print(pack);print(sha,pack.stat().st_size)
entry=f'''\n192. Exactchosen40x40flyingboostintegration r116 (2026-11-09). Userchoosesaction/boostfromconvref/rtype-l1-blue-enemy-assets.zip SHA{c['source_zip_sha256']}/CRCpass. Exact2x400bytecolumnpairs ROM260/262,56brightness56contrast100saturationgamma.35/SierraLite. Native41->184/185twoframeactor-localcounterwhileflying, notwalkingposes. Existing40x40footprint/nativeflight/collisionunchanged. Allbank5art6032byteprefixand7otherregionsidenticalr114; priorghost/snake/acceptedwalkers/L3exhaustretained.\nMemory: new800byteart C300..C61F inretiredDOCK6cacheafter768byteghostpreload; ghosthelperC100/bluegatherloaderC200/chunktableC260/ghostvarsC2F0 separate. Packedsource411bytes initiallytestedatDOCK7F900zerosbeyondnativecopyF87C; ordinaryinitialartpassbutsourceoverwrittenandcachedL1revisitcorruptedresidentart. Testcaughtfailure, noZIPreleased. Replacedwith22scatterranges/411bytesin52unreferencedpalette rows includingrow54whichisneverreadascolour(transparentmarker). Allfirst16andallactualnativecolourrows/staticnativeframesunchanged. GatherstoC900..CA9A, decompressC300, bank7nowentirelyidenticalr114. Firstpalettecapacityexcluding54was408bytes;3bytestailfititerationand3A1Eoverflowdiscarded. Includedunused54rowandremovedredundantphaseclear/post-gathermapwrite, usedstackcounterloop; fits39FE<3A00 with2bytesmargin. Source rangesareRESERVEDinblue_contractforfutureconverters, donotreusethemforpaletteart. Exactstaticproofusednativecolourrowsnotchangedandsourcepackeddecode800pass.\nRuntime205entryidmapplusCP205guardpreventsoutofboundslookups; native201..204mappingretained. Specialbase184usesAND1, other4posegroupsunchanged. LoaderwrapssaveSP C7F2/privateSP C7F0 aroundpreloadandgather; alwaysvisibleDOCK6 through6F/ED mappings. Helperdoesnotresettooverlapping5CF0; addressedbeforefirsttestedbuild, no suchbrokenversionreleased. Expandedruntimealwaysfreshlyzerosactor_phases; redundantLDIRclearremovedforpacking. Finalguard31A7bytesendA870 andexistingartendsC000; bluecacheendsC620, privatestackC7F0, scratchC900 nonoverlap. ActualloadercallerSP/map restored2timesinmeasuredstartup.\nFinal1800ordinaryupdates/1320boostdraws/bothvirtual184185/exactresidentbank6art/sourceguardPASS; sourcefirstu480tou1799. Previousghost10866draws/all3poses, snake674round783head79drawsPASS. Longtracesgameoverbypassexplicit. ThreecoldfiretimingswithoutbypassPASS;12cold/cachedroutesincludingpreviouslyfailingL1returns verifyboostart+sourcebyteidentityPASS;96ghostplan-equivalencecasesPASSwithfinalsharedcache. StaticexactZIPframes/preservedbank5art/7regions/usedpaletterows/nativebitmap+descriptors/bank7/scope/bounds/packetdecode/planbackup/all16LEVELSTARTreconstruction/allTAPchecksums/ZIPCRCpass.\nTimingmatchednofireroute: r114vsr116early130..500mean177.43->178.29ms ({early:+.2f}%time); busyghost920..1100mean420.10->414.10ms ({busy:+.2f}%time). Nativeupdate-boundaryCPUcycles3528000Hz, nothardwareFPS/playerIRQcadence/universalgain; IRQtimingvarieswithartcost. Complete1800run41976->42554emulatedframes includesstartup+differentlaterencounters. No claimtocureexistingr114ghostslowdown.\nActualRAMu960blue_gameplay_0/1.pngandblue_gameplay_comparison.pnggenerated/visuallyinspected: originalcyanreplacedbychosenred/gold/whitebodywithblueboostexhaust, whole40x40 retained, twoactionposes. No userimageediting/sourceAI. Sourcesbuild_l1_blue_boost_r116.py/src/l1_blue_art_load.asm; scriptsverify_l1_nofire_r116.mjs,verify_cold_l1_fire_r116.mjs,verify_native_revisits_r116.mjs,verify_ghost_precomputed_equivalence_r116.mjs,measure_l1_blue_boost_r116.mjs,finalize_l1_blue_boost_r116.py;docs/l1_blue_boost_r116.txt. Packagebuild/fullgame/l1_blue_boost_r116/RType_TS2068_r116.zip SHA256{sha} {pack.stat().st_size}bytes. Hardwarepending,stablelatest100/previousr114preserved;sourcearchives/referenceprojects/stock64KBunchanged.\n'''
with(R/'TEST_HISTORY.md').open('ab')as f:f.write(entry.encode('ascii'))
with(R/'PROJECT_STATE.md').open('ab')as f:f.write(b'\n2026-11-09 candidate r116: exactchosen2pose40x40boostenemy native41; build/fullgame/l1_blue_boost_r116/RType_TS2068_r116.zip. Oldbank5art/other7regionsunchanged. IMPORTANT reserved411bytepackedsource in unusedpalette ranges documentedblue_contract.json: futurepaletteconvertersmustpreservetheseranges. No bank7assetstorage. Native1800update/3coldfire/12revisit/96ghost-equivalence/staticchecksPASS; hardwarepending. TEST_HISTORY192/docs/l1_blue_boost_r116.txt. Stablelatest100preserved.\n')
