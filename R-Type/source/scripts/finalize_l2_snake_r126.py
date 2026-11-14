from pathlib import Path
import json,hashlib,zipfile,functools
R=Path.cwd();O=R/'build/fullgame/l2_snake_parts_r126';B=R/'build/fullgame/l2_scroll_projectile_r125'
def j(n):return json.loads((O/n).read_text())
a=(O/'L2_runtime_image.bin').read_bytes();b=(B/'L2_runtime_image.bin').read_bytes();assert len(a)==len(b);diff=[i for i,(x,y)in enumerate(zip(a,b))if x!=y];assert diff==[0x704] and b[0x704]==198 and a[0x704]==199
ct=j('snake_parts_contract.json');assert ct['head_tail_ids']=={str(n):a[j('L2_actor_contract.json')['extension']['id_map']-0xa000+n]for n in range(25,31)}
assert j('snake_gameplay_validation.json')['passed'] and j('snake_gameplay_validation.json')['body199']>=455
assert j('actual_actor_decode_validation.json')['passed'] and j('palette_missile_validation.json')['passed'] and j('native_revisits_validation.json')['passed']
def blocks(p):
 b=p.read_bytes();out=[];at=0
 while at<len(b):
  n=int.from_bytes(b[at:at+2],'little');v=b[at+2:at+2+n];assert len(v)==n and n>1 and functools.reduce(int.__xor__,v,0)==0;out.append((v[0],v[1:-1]));at+=n+2
 assert at==len(b);return out
for n in range(1,9):
 v=(O/f'level{n:02d}_region.bin').read_bytes()
 for kind in ['LEVEL','START']:
  data=b''.join(d for f,d in blocks(O/'rtype'/f'{kind}{n:02d}.TAP')if f==255);assert data==(v if kind=='LEVEL'else b''.join(v[p*8192:(p+1)*8192]for p in[0,1,4,5,6,7]))
 if n!=2:assert v==(B/f'level{n:02d}_region.bin').read_bytes()
assert any(b'R126 PREPARING' in d for _,d in blocks(O/'rtype/rt.tap'))
validation={'passed':True,'runtime_mapping_bytes_changed':1,'body_draws_verified':j('snake_gameplay_validation.json')['body199'],'native22_draws':j('snake_gameplay_validation.json')['native22'],'native23_draws':j('snake_gameplay_validation.json')['native23'],'actor_decode_packets':27,'shared_palette_rows':96,'terrain_scanlines_front_back':160,'general_transitions':12,'all16_tapes_reconstructed':True,'other7_levels_unchanged':True,'hardware_tested':False}
(O/'validation_summary.json').write_text(json.dumps(validation,indent=2))
text='''R-Type TS2068 r126 - stable L2 snake body parts

Replace the complete rtype folder, reset, and launch rtype/rt.tap.
Startup identity: R126 PREPARING.

The arcade export explicitly describes parts/orientations, not a gait cycle.
Native Spectrum body descriptors22/23 were alternating between arcade cels2454
and2450. Both now use the repeated cel2450/palette5 body (export frame02, ID199).
Head/tail descriptors25..30 keep their orientation mappings. Movement, collision,
animation clocks, source artwork, all ten scorpion frames and r125 palette fixes
are unchanged. Exactly ONE byte in the expanded L2 runtime image changed.

Scripted actual gameplay:455 body draws (221 native22,234 native23) consistently
mapped to199 through the boss encounter. The frame160 actual-RAM image was
visually inspected. All27 actor packets decode exactly,96 shared palette rows
match,160 terrain scanlines tested in both mappings;12 cold/cached transitions
pass. All16 level/start tapes reconstructed and checksummed;other7 levels exact
r125. This is emulation coverage, not real-hardware confirmation. Boss stress
uses the existing invulnerability/game-over bypass for coverage.

Full banked disk candidate. Stable r99/r100 and stock64KB target unchanged.
'''
(O/'README.txt').write_text(text);(R/'docs/l2_snake_parts_r126.txt').write_text(text)
p=O/'RType_TS2068_r126.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 for f in sorted((O/'rtype').iterdir()):
  if f.is_file():z.write(f,'rtype/'+f.name)
 for n in ['README.txt','validation_summary.json','snake_parts_contract.json','integration_contract.json','palette_contract.json']:z.write(O/n,n)
with zipfile.ZipFile(p)as z:assert z.testzip()is None
sha=hashlib.sha256(p.read_bytes()).hexdigest();(O/'SHA256.txt').write_text(sha+'  '+p.name+'\n')
entry=f'''
199. r126 L2 snake part identity fix (2026-11-10). Userphotos13087/13088 show native bodyanimation alternating anatomically different exported parts. v2choices provenance explicitly says parts/orientations, not gaitcycle:cel2450p5offset140 commonbody vs2454p5offset236 alternatepart. Priorintegration mappednative22->198(frame03/2454),23->199(frame02/2450). Both now199;25..30head/tail orientations unchanged. ExactlyONE expandedruntimebyteA704(physicalimage704)198->199. Compressedmotion sourceend3831same;noextra code,cache,memoryoranimationcost. Allchosenimagesretained,normalbodyusesrepeatedsource2450.
PASS actualgameplay455bodydraws(221native22/234native23) all199 through180post-BBupdates;head/tailmapsunchanged. All27actorpacketsdecodeexact;96sharedpalette rows/160frontbackterrainrowsPASS;12cold/cachedroutesPASS;all16tapechecksums/reconstruction,other7levelsidenticalr125,ZIPCRC. Imagebuild/fullgame/l2_snake_parts_r126/boss_probe_160.home.png rendered/visuallyinspected;trace snake_gameplay_validation.json. Scriptedbossrouteusespriorinvulnerability/gameoverbypass,notnormalcompletion/hardwareconfirmation. No fresh3coldfireorlongfullapproach rerun:exactmapping-onlychange,existingstart/transitioncoverageappropriate. SourceZIPs/referenceprojects/stable99/100/stock64KBunchanged. Candidatebuild/fullgame/l2_snake_parts_r126/RType_TS2068_r126.zip SHA{sha};docs/l2_snake_parts_r126.txt.
'''
if b'199. r126 L2 snake part identity'not in(R/'TEST_HISTORY.md').read_bytes():
 with(R/'TEST_HISTORY.md').open('ab')as f:f.write(entry.encode('ascii'))
 with(R/'PROJECT_STATE.md').open('ab')as f:f.write(f'\n2026-11-10 r126 L2snakebodypartfix: native22/23bothmapcommonarcade2450body199,head/tail25..30unchanged. Oneexpandedruntimebyteonly.455bodydraws/27actors/96palette/160rows/12transitions/tapesZIPchecksPASS;actualRAMimageinspected/hardwarepending. build/fullgame/l2_snake_parts_r126/RType_TS2068_r126.zip SHA{sha};TEST_HISTORY199/docs/l2_snake_parts_r126.txt. Stable100/stock64KBunchanged.\n'.encode('ascii'))
print(p);print(sha)
