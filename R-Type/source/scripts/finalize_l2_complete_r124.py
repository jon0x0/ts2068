from pathlib import Path
import json,hashlib,zipfile
R=Path.cwd();O=R/'build/fullgame/l2_complete_r124';B=R/'build/fullgame/l2_integrated_r123'
def readj(n):return json.loads((O/n).read_text())
def blocks(p):
 b=p.read_bytes();out=[];at=0
 while at<len(b):
  n=int.from_bytes(b[at:at+2],'little');v=b[at+2:at+2+n];assert len(v)==n and n>1
  assert __import__('functools').reduce(int.__xor__,v,0)==0,(p,at)
  out.append((v[0],v[1:-1]));at+=n+2
 assert at==len(b);return out
assert hashlib.sha256((R/'convref/rtype-l2-art-assets_v2.zip').read_bytes()).hexdigest()=='e16427f3fea28674b16bc8f3399a4acaa0c161a661f96b8fb9009e640c456ac6'
for n in range(1,9):
 v=(O/f'level{n:02d}_region.bin').read_bytes();assert len(v)==65536
 for kind in ['LEVEL','START']:
  data=b''.join(d for f,d in blocks(O/'rtype'/f'{kind}{n:02d}.TAP')if f==255)
  want=v if kind=='LEVEL' else b''.join(v[p*8192:(p+1)*8192]for p in[0,1,4,5,6,7]);assert data==want,(kind,n)
 if n!=2:assert v==(B/f'level{n:02d}_region.bin').read_bytes()
a=(O/'level02_region.bin').read_bytes();b=(B/'level02_region.bin').read_bytes();assert a[0xe000:]==b[0xe000:]
assert a[0x84b4:0xa000]==b[0x84b4:0xa000]
assert any(b'R124 PREPARING' in v for _,v in blocks(O/'rtype/rt.tap'))
t=readj('tile_inputs.json');original=bytes(16384)+(R/'build/fullgame/foundation/level02.raw').read_bytes()
for n in range(34):
 tile=bytes.fromhex(t['tiles'][n]);old=original[0xe762-(n+1)*144:0xe762-n*144]
 for j in range(0,144,9):
  assert tile[j+1:j+9]==old[j+1:j+9]
  assert tile[j]==(134 if any(tile[j+1:j+9])else 7)
ct=readj('integration_contract.json');assert ct['native_tiles']==34 and ct['boss_tiles']==18 and ct['no_fullscreen_scan']
assert max(ct['tile_symbols'].values())<65536
for n in ['actual_tile_decode_validation.json','actual_actor_decode_validation.json','actual_im2_validation.json','native_revisits_validation.json','l2_boss_revisits_validation.json','debug_validation.json']:assert readj(n)['passed']
assert len(readj('actual_tile_decode_validation.json')['results'])==128
assert len(readj('actual_actor_decode_validation.json')['reports'])==27
assert len(readj('native_revisits_validation.json')['results'])==12
assert len(readj('l2_boss_revisits_validation.json')['results'])==6
fire=readj('unmodified_l2_fire_validation.json');assert len(fire)==3 and all(x['passed'] for x in fire)
report=readj('L2_fine_approach.json');assert report['u']>=1547 and all(str(i)in report['drawCounts']for i in range(180,190));assert set(x['fine']for x in report['fineShots'])==set(range(8))
reveal=readj('boss_stop_probe.json');assert reveal['after']>=180
assert all(x['reveal']==0 for x in reveal['rows']if not x['freeze'])
assert max(x['reveal']for x in reveal['rows'])==18
# Actor extension restore helper moved; retain a single accurate exported contract.
p=O/'L2_actor_contract.json';j=readj(p.name);j['native_prefix_snapshot']=ct['snapshot'];j['extension']['restore_native_bank5']=ct['tile_symbols']['restore_native'];j['terrain_boss_integration']='integration_contract.json';p.write_text(json.dumps(j,indent=2))
validation={'passed':True,'actual_actor_packets':27,'all10_scorpion_frames_drawn':True,'actual_tile_cases':128,'native_tiles_preserved':34,'boss_tiles_separate':18,'all8_scroll_phases_captured':True,'reveal_after_native_stop':True,'all16_tapes_reconstructed':True,'cold_fire_cases':3,'general_transition_routes':12,'long_boss_reset_transition_routes':6,'IM2_actual_RAM_words':256,'ordinary_updates':report['u'],'ordinary_emulated_frames':report['frame'],'other7_levels_identical_r123':True,'dock7_unchanged':True,'hardware_tested':False,'debug_scope':'Direct banked entry/ROM font/Space redraw; live chord not established in this test'}
(O/'validation_summary.json').write_text(json.dumps(validation,indent=2));(O/'integration_static_validation.json').write_text(json.dumps({'passed':True,'native_geometry_preserved':True,'source_zip_preserved':True,'tapes_checksum_and_reconstruction':True,'stable_r99_r100_unchanged':True},indent=2))
text='''R-Type TS2068 r124 - complete selected L2 integration

Replace the complete rtype folder, reset, and launch rtype/rt.tap.
Startup identity: R124 PREPARING. Select 2 for level 2; B twice previews boss.

Selected v2 actor art retained: all TEN scorpion exports (native heading flips
preserved), C shell walker, white-legged creature, emergence heads and snake.
All27 actor packets decode exactly in actual emulated RAM.

L2 scrolling terrain retains all34 native tile silhouettes and dimensions.
Selected arcade-material colour guidance is projected into coherent per-scanline
ink-on-black palettes. This conservative full-row policy trades local colour
variation for safe single-pixel horizontal scrolling. It is not a new one-to-one
arcade terrain tile extraction. Blank sky cells remain sky, not opaque rectangles.

Fixed the old collision between terrain IDs19..33 and the boss tiles. Boss art
now uses separate IDs34..51. While entering it uses a coherent moving palette;
after the actual native stop, its detailed selected red/white/yellow artwork is
repainted one occupied tile per update into BOTH the background and screen.
No repeated full-screen palette scan. Alternate registers are preserved.

Native prefix snapshot/restore covers A458..A84B. Packed tile data uses the old
terrain storage plus retired palette space; no player code/data in DOCK7 is reused.
Duplicate diagnostic font replaced with the same native ROM font at3D00; debug
screen remains readable. Other seven levels are byte-identical to r123.

Validation: 128 actual Z80 tile cases,27 actor packets,all10 scorpion IDs drawn,
all8 scrolling phases captured;1547 ordinary updates;3 unmodified cold/fire cases;
12 general and6 long boss/reset/revisit routes;all16 level/start tape checksums
and reconstruction. All256 IM2 words checked in actual RAM; emulator IRQ vector
is fixedFF, not256 hardware IRQ probes. Long route uses invulnerability/game-over
bypass. Debug direct-entry/font/Space redraw tested; live chord not established
by this test. Actual RAM images recorded and inspected.

Performance: ordinary1547-update run38775 emulated frames versus r12339205.
This is a small emulator improvement, not a hardware FPS measurement. Large
selected actors remain more expensive than the older smaller graphics.

Hardware validation pending. Stable r99/r100 and stock64KB read-only cartridge
remain unchanged. This is the full banked disk game candidate, not a new64KB ROM.
'''
(O/'README.txt').write_text(text);(R/'docs/l2_complete_r124.txt').write_text(text)
archive=O/'RType_TS2068_r124.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file():z.write(p,'rtype/'+p.name)
 for name in ['README.txt','validation_summary.json','integration_static_validation.json','selected_l2_choices.json','L2_actor_contract.json','integration_contract.json']:z.write(O/name,name)
with zipfile.ZipFile(archive)as z:assert z.testzip()is None and 'rtype/rt.tap'in z.namelist()
sha=hashlib.sha256(archive.read_bytes()).hexdigest();(O/'SHA256.txt').write_text(sha+'  '+archive.name+'\n')
entry=f'''
197. Complete selected L2 integration r124 (2026-11-10). Actor27packets/all10scorpions retained fromv2ZIP e16427f3fea28674b16bc8f3399a4acaa0c161a661f96b8fb9009e640c456ac6. Native34terrainIDs0..33 restored with original bitmaps/dimensions, independentbossIDs34..51 replace old19..36 collision. Sky7cells retained; marking emptycells86 reproduced huge player smear via native RL terrain writer8970, fixed. Selected material rowinks at8343/boss83E3; conservative fullrow palette policy (not exact gap8 projection or new arcade silhouettes). Movingboss nonblackunion mask; selected richpairs restored after DOCK3:7A8E stop,18occupiedtiles/oneperupdate using8CFD into backbuffer and primary. Bypassnativeocclusion only during explicitrepaint via balancedPOP AF/SCF/RET guard. SharedHOME868C hook installed/restored, fullmain+alternate registers preserved. Finepalette0100runsmap3,lookup0F80runs0B; preserve0190/01A0/0FC3 nativehelpers. Worldstate readmap1B withIRQpreserved. No fullscreen scan.
Bounded1levelXOR/LZ tilecodec5521bytes, nativefloorB442..C762 plusretiredlowpalette; duplicatepackets aliased; scratch82B3..8342 fromdebugduplicatefont. DebugROMfont3D00,codeends82B3; fixedowneddata ends84B4. Baseline fontarea read/write audit empty; DOCK7unusedspace proposal rejected by actual heavycode/datareads/writes. NativeprefixA458..A84B snapshotDOCK6C700..CAF3, lowownedflag; restoreHOMEprefix thennativehighsource toDOCK6 LAST. No bank7 reuse. Loader3848..39FA; boundaries asserted.
PASS:128actualZ80tilecases,27actorpackets,all10scorpionIDsdrawn,all8finephasescaptured,1547ordinaryupdates38775emulatedframes;3unmodifiedcold/firecases;12generalcold/cachedroutes;6longboss/samelevelreset/revisitroutes;256actualRAMIM2words5B5B(fixedFFemulator,notactual256IRQprobes);all16tapesreconstructed/checksums,other7regionsr123identical,DOCK7unchanged,ZIPCRC. Revealtraceboss_stop_probe.json no revealbeforestop/all18complete. Directdebugentry/ROMfont/SpaceRAMredrawPASS; initial livechord test did notestablish takeover (pc8383/map89), forcedFD20also notvalid; no liveIRQclaim. DebugactualRAMimage debug_final.png readable. Images boss_probe_160.home.png and ordinary_L2_col54.home.png inspected; intermediatefailedsky/primaryonlyrepaint experiments notdelivered. Diagnostics inbuild/fullgame/l2_complete_r124 andbuild/graphics/l2_integrate_r119. Sourcechecker excludesonlyintentionalL2HOMEplanC4F2..C635/tileC700..C78Fwhileinstalled; restexact.
Performance smallr12339205tor12438775emulatedframesfor1547updates;not hardwareFPS,largeractorsstillcostly. Hardwarepending;stable99/100,stock64KB,referenceprojects/sourceZIPsunchanged. Candidate{archive.relative_to(R).as_posix()} SHA{sha};docs/l2_complete_r124.txt.
'''
state=f'''
2026-11-10 r124 complete selectedL2integrationcandidate:27actorpackets/all10scorpions retained,34nativeterrainIDs/silhouettes restored,18separatebosstiles,coherentmovingpalette andstoppedbossrichreveal. Nativeprefixsnapshotexpanded1012bytes,ROMfontreclaimsduplicateonly,DOCK7unchanged. 128tile/27actorchecks,1547ordinaryupdates,3coldfire,12general+6boss/reset/revisits,16tapereconstruction/ZIPPASS. Conservativefullrowterraincolourpolicy,notnewarcadesilhouettes. build/fullgame/l2_complete_r124/RType_TS2068_r124.zip SHA{sha}. TEST_HISTORY197/docs/l2_complete_r124.txt;hardwarepending/stable100/stock64KBunchanged.
'''
if b'197. Complete selected L2 integration r124'not in(R/'TEST_HISTORY.md').read_bytes():
 with(R/'TEST_HISTORY.md').open('ab')as f:f.write(entry.encode('ascii'))
 with(R/'PROJECT_STATE.md').open('ab')as f:f.write(state.encode('ascii'))
print(archive);print(sha);print(json.dumps(validation))
