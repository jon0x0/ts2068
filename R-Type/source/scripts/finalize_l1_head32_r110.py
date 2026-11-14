from pathlib import Path
import json,sys,functools,zipfile,hashlib,numpy as np
R=Path.cwd();B=R/'build/fullgame/l1_chosen_r107';O=R/'build/fullgame/l1_head32_r110';sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack
c=json.loads((O/'head32_contract.json').read_text());w=next(v for v in json.loads((O/'walker_runtime.json').read_text())if v['level']==1);meta=next(v for v in json.loads((O/'generic_manifest.json').read_text())if v['level']==1);raw=(O/'L1_runtime_art.bin').read_bytes();oldraw=(B/'L1_runtime_art.bin').read_bytes();assert raw[:len(oldraw)]==oldraw;assert len(raw)==len(oldraw)+1024;assert c['imageend']<=0xa900 and c['artend']<=0xc000 and c['end']<=0x3a00
for a in w['assets']:
 if a['key']!='shell32':continue
 A=R/'build/graphics/walker_choice_r90';i=a['frame'];at=np.frombuffer((A/f'L6_head_{i}.attrs').read_bytes(),np.uint8).reshape(32,4);bt=np.frombuffer((A/f'L6_head_{i}.bits').read_bytes(),np.uint8).reshape(32,4);v=np.stack([bt.T,at.T],2).tobytes();p=a['pointer']-0xa900;assert raw[p:p+256]==v;assert not np.any(at&192)
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();old=(B/f'level{n:02d}_region.bin').read_bytes();assert len(b)==65536
 if n==1:
  allowed=set(range(0x2400,0x3a00))|{c['preload_table_operand'],c['preload_table_operand']+1,c['install_operand'],c['install_operand']+1,c['warmup_operand'],c['warmup_operand']+1};assert all(x==y or i in allowed for i,(x,y)in enumerate(zip(b,old)));assert b[0xa000:0xc000]==old[0xa000:0xc000];assert b[0x2000:0x2400]==old[0x2000:0x2400];assert unpack(b[c['rawptr']:])==raw;assert unpack(b[c['imageptr']:])==(O/'L1_runtime_image.bin').read_bytes();assert unpack(b[c['backup_ptr']:])==bytes.fromhex(meta['backup']);assert unpack(b[0x2400:])==bytes(3024)
 else:assert b==old
 for name in [f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  t=(O/'rtype'/name).read_bytes();p=0;parts=[]
  while p<len(t):
   size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0
   if v[0]==255:parts.append(v[1:-1])
   p+=size+2
  assert b''.join(parts)==(b if name.startswith('LEVEL')else b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]))
for name in ['RTCORE.TAP','RTPRELD.TAP','RTBOOT.TAP']:assert (O/'rtype'/name).read_bytes()==(B/'rtype'/name).read_bytes()
for p in (O/'rtype').glob('*.tap'):
 t=p.read_bytes();a=0
 while a<len(t):
  size=int.from_bytes(t[a:a+2],'little');v=t[a+2:a+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;a+=size+2
live=json.loads((O/'shared_live_validation.json').read_text());assert live['passed']and {d['virtual']for d in live['draws']}=={176,177,178,179};assert json.loads((O/'l1_nofire_validation.json').read_text())['passed'];assert json.loads((O/'native_revisits_validation.json').read_text())['passed'];fire=json.loads((O/'unmodified_l1_fire_validation.json').read_text());assert len(fire)==3 and all(v['passed']and v['region']==0 for v in fire);timing=json.loads((O/'timing_comparison.json').read_text());assert timing['passed'];assert all(v['cachePointerChecks']>0 for v in timing['reports'])
rs={x['name']:x for x in timing['reports']};cost=dict(shell32_vs24_percent=(rs['C32']['shell']['meanMs']/rs['C24']['shell']['meanMs']-1)*100,snake_stress32_vs24_percent=(rs['C32_snake_stress']['snake']['meanMs']/rs['C24_snake_stress']['snake']['meanMs']-1)*100,normal_overall32_vs24_percent=(rs['C32']['combined']['meanMs']/rs['C24']['combined']['meanMs']-1)*100)
summary=dict(passed=True,base='r107',exact_selected32x32=True,settings=dict(brightness=52,contrast=59,saturation=82,gamma=.87),frames=4,previous_walker_snake_art_unchanged=True,other7levels_unchanged=True,normalBlack=True,layout=c,liveDraws=len(live['draws']),coldFire=fire,measured_cost=cost,hardware_pending=True);(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
readme=f'''R-Type TS2068 r110 - selected C shell walker, full32x32

Replace the COMPLETE rtype folder, reset, launch rtype/rt.tap.
Startup R110 PREPARING. Ordinary L1 shows this walker later in the level;
double-B skips the ordinary encounter.

The magenta-front shell (native30-33) now uses your selected C artwork:
exact32x32 B+mods52/59/82/gamma0.87, all4savedposes. No downscaling or clipping.
The native pose order, movement and collision logic remain unchanged.
Your r107 round walker and snake artwork remain byte-identical, as do all
seven other level regions, including the complete L3 rocket exhaust.

Uses the existing compiled renderer and existing bank allocation. Retired an
unreferenced pre-expanded walker cache whose IDs already map to bank5 art;
kept its3024byte zero-filled initialization block. Originalcache backup retained
in build artifacts. All activecompiled pointers checked outside retiredcache.
Runtimeimage endA83D < artbaseA900, artendBD90 < C000, packedend3729 < 3A00.
No extra bank or geometry/movement change. Native bitmap sources untouched.

Measured deterministic emulation, not real-hardware FPS:
32vs24 same-art renderer: +{cost['shell32_vs24_percent']:.1f}%mean update time during shell encounter,
+{cost['snake_stress32_vs24_percent']:.1f}%in controlled simultaneous head+snake stress,
+{cost['normal_overall32_vs24_percent']:.1f}%across normal130..500 update interval.
The stress test substitutes this head for another walker's drawing only in the
test fixture. Shipping gameplay has no synthetic actor substitution.

Ordinary700update nofire trace sees79draws/all4headposes, plus existingwalker
and snake; longtraces usegameover bypass. Three coldL1firetimings WITHOUTthe
bypass and12cold/cachedlevelroutes pass. Exactart/prefixidentity, native-source,
scope, packetidentity, bankbounds, TAPreconstruction/checksums and ZIPCRC pass.
Hardware confirmation pending. Stable r100 fallback kept unchanged.
Stock64KB cartridge is separate and unchanged by this disk/512KB candidate.
''';(O/'README.txt').write_text(readme,encoding='ascii');(O/'rtype/README.txt').write_text(readme,encoding='ascii');(R/'docs/l1_head32_r110.txt').write_text(readme,encoding='ascii')
z=O/'RType_TS2068_r110.zip'
with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as f:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():f.write(p,'rtype/'+p.name)
 for name in ['README.txt','validation_summary.json','timing_comparison.json','head32_gameplay_comparison.png']:f.write(O/name,name)
with zipfile.ZipFile(z)as f:assert f.testzip()is None
sha=hashlib.sha256(z.read_bytes()).hexdigest();print(z);print(sha,z.stat().st_size);print(cost)
entry=f'''\n188. Full32x32 selected C shell integration r110 (2026-11-09). User accepts24butprefers32iffitsandrequestsattentiontoupdateratewithsnake. Builtfromr107, notclippedunpublishedr109. Native30-33mapstaticvirtual176-179 viaexistinghook toexactfourchosenr90L6_head32pairedpixels52/59/82/gamma0.87. Originalnativeposeorder retained, nofake4stepgaitcycling. Nativebitmap/descriptordata, coordinates/collisionlogic unchanged. Exact32x32storageall4poses; nofit-to-old54maskclipping. Previouslychosenr107roundwalker/snake/artprefixunchanged andother7regionsbitidentical.\nSpace: existing3024byteexpandedcache solelyholds21-25/201-204, allalreadyredirectedbyid_map; everyactivetablepointerusesbank5art. Retiredduplicatecachecontent, keptsame3024bytezeroexpandedinitialization toavoidchangingpreloaderloop. Originalexpandedcachearchived. Movedpackedplanbackup/preloadtable/art/runtimeimagewithallcorrespondingoperandsadjusted; planbackupdecodeidentityPASS. RuntimeimageendA83D < A900, artendBD90<C000, payloadend3729<3A00. Nativebankrestorehelperandcoremotionlogicunchangedapartfromplanbackupsourceoperand. Native-sourcecontractinitialfieldcomparedA000..E000whichincludesintentionalcacheloaderoperands; clarifiedtocorrectnativebitmap/sourceA000..BFFF, assertionPASS. No extraRAMbank/sourcearchive/reference/stock64KBchange.\nActualordinary700updates/nofire79sharedheaddraws/all4virtualposes176-179,403rounddraws/330snakedrawsPASS. Longtracegameoverbypassexplicit. ThreecoldL1firetimingswithoutbypassPASS. Twelve cold/cachedroutes/native-source/attributes/core/assetidentityPASS. StaticexactCbytes/previousrawprefix/scopewhitelist/7regions/planbackup/zero-preload/runtimepacketdecode/bankbounds/all16LEVEL/STARTreconstruction/allTAPchecksums/ZIPCRCpass.\nFive deterministic520updateruns measureactualCPUcyclesatnative94F1boundaries3528000Hz, nofire,gameoverbypass: old24baseline,C24samepipeline,C32,andC24/C32controlledsnakestress. StresssubstitutesonlydrawID30-33forroundwalker53-56duringu155..240; shippinggameunchanged. Activecompiledcachebasechecked405baseline/484eachnewrun, allA900..BFFF, noneusesretiredC000cache. Naturalheadwindow425..500: C24mean182.94ms/5.466updates/s,C32mean192.76ms/5.188updates/s (+{cost['shell32_vs24_percent']:.2f}%time). Controlledhead+snakewindow155..240:C24mean202.35ms/4.942updates/s,C32mean206.61ms/4.840updates/s (+{cost['snake_stress32_vs24_percent']:.2f}%time). Normal130..500overall+{cost['normal_overall32_vs24_percent']:.2f}%time32vs24. CPUemulationmeasurementsNOTphysicalFPSorplayerinterruptcadence. Ordinarysnakewindownearlysamewhenheadabsent.\nActualRAMu440head_gameplay_0.png(r107)/head_gameplay_1.png(r110)andhead32_gameplay_comparison.pnggenerated/visuallyinspected: selectedlargerheadintact,inairaboveterrain, nooldmaskmissinghead. Noanchorcorrectionneededforobservedairbornepose. OtherordinarycapturedHOMEbinsretainedwithoutclaimofrenderedimages. Earlier24draftclipped92/10pixelswasnotpublished/reused. Comparison24timingtargetunpublished, onlysamplerendererassetssmaller. Scriptsbuild_l1_head32_r110.py,build_l1_head24_timing_r110.py,measure_l1_head32_r110.mjs,verify_l1_nofire_r110.mjs,verify_cold_l1_fire_r110.mjs,verify_native_revisits_r110.mjs,finalize_l1_head32_r110.py. Docs/l1_head32_r110.txt. Package build/fullgame/l1_head32_r110/RType_TS2068_r110.zip SHA256{sha}, {z.stat().st_size}bytes. Hardwarepending;lateststable100andallpriorarchivespreserved.\n'''
with(R/'TEST_HISTORY.md').open('ab')as f:f.write(entry.encode('ascii'))
with(R/'PROJECT_STATE.md').open('ab')as f:f.write(b'\n2026-11-09 candidate r110: selected C32x32 shell walker for L1native30-33; build/fullgame/l1_head32_r110/RType_TS2068_r110.zip. r107artprefix/other7regionsunchanged; full4poses/coldfire/12revisits/staticcontracts pass. Measured32vs24 +5.4%headencountertime,+2.1%controlledhead+snaketime. Hardwarepending;stablelatest remainsr100. TEST_HISTORY188/docs/l1_head32_r110.txt.\n')
