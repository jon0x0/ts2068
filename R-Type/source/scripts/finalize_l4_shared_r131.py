from pathlib import Path
import json,hashlib,zipfile,functools
R=Path.cwd();O=R/'build/fullgame/l4_shared_r131';B=R/'build/fullgame/l2_star_guard_r130'
def j(n):return json.loads((O/n).read_text())
def blocks(p):
 b=p.read_bytes();out=[];at=0
 while at<len(b):
  n=int.from_bytes(b[at:at+2],'little');v=b[at+2:at+2+n];assert n>1 and len(v)==n and functools.reduce(int.__xor__,v,0)==0;out.append((v[0],v[1:-1]));at+=n+2
 assert at==len(b);return out
for n in range(1,9):
 v=(O/f'level{n:02d}_region.bin').read_bytes()
 for kind in ['LEVEL','START']:
  actual=b''.join(data for flag,data in blocks(O/'rtype'/f'{kind}{n:02d}.TAP')if flag==255);expected=v if kind=='LEVEL'else b''.join(v[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]);assert actual==expected
 if n!=4:assert v==(B/f'level{n:02d}_region.bin').read_bytes()
assert any(b'R131 PREPARING' in b for _,b in blocks(O/'rtype/rt.tap'))
c=j('l4_shared_contract.json');a=(O/'level04_region.bin').read_bytes();b=(B/'level04_region.bin').read_bytes();allowed=[(0x2800,0x3a00),(0xa4e9,0xa4e9+c['aux_bytes']),(0xa9c7,c['external_end'])]+[(p,p+1)for p in[0xddbb,0xddbc,0xdeb4,0xdeb5,0xdee1,0xdee2,0xdf6c]]
assert all(any(lo<=i<hi for lo,hi in allowed)for i,(x,y)in enumerate(zip(a,b))if x!=y);assert a[0x2000:0x2800]==b[0x2000:0x2800];assert a[0x8000:0xa000]==b[0x8000:0xa000];assert a[0xe000:]==b[0xe000:]
assert c['bank1_end']<=0x3a00 and c['code_end']<=0xa9c7 and c['rawend']==0xbfe0 and c['aux_bytes']==366
w=next(x for x in j('walker_runtime.json')if x['level']==4);l1=next(x for x in j('walker_runtime.json')if x['level']==1);raw=(O/'L4_runtime_art.bin').read_bytes();src=(B/'L1_runtime_art.bin').read_bytes();srcbase=l1['assets'][0]['pointer'];proof=[]
for q in w['assets']:
 if q['key']not in['round','shell32','ghost32']:continue
 s=next(v for v in l1['assets']if v['key']==q['key']and v['frame']==q['frame']);v=raw[q['pointer']-c['rawbase']:q['pointer']-c['rawbase']+q['bytes']];assert v==src[s['pointer']-srcbase:s['pointer']-srcbase+s['bytes']];assert all(t&192==0 for t in v[1::2])
 if q['key']in['round','ghost32']:
  name='rtype-l1-walker-snake-assets.zip'if q['key']=='round'else'rtype-l1-ghost-assets.zip';prefix='walker'if q['key']=='round'else'ghost';assert v==zipfile.ZipFile(R/'convref'/name).read(f'{prefix}/frame_{q["frame"]:02d}.pairs.bin')
 else:
  p=R/'build/graphics/walker_choice_r90';bits=(p/f'L6_head_{q["frame"]}.bits').read_bytes();at=(p/f'L6_head_{q["frame"]}.attrs').read_bytes();expected=bytes(x for col in range(4)for y in range(32)for x in[bits[y*4+col],at[y*4+col]]);assert v==expected
 proof.append(dict(key=q['key'],frame=q['frame'],size=q['size'],sha256=hashlib.sha256(v).hexdigest(),exact_approved_bytes=True))
assert len(proof)==11
for n in ['l4_shared_runtime_validation.json','l4_shared_boss_validation.json','native_revisits_validation.json','native_revisit_attribute_validation.json']:assert j(n)['passed'],n
assert j('l4_shared_runtime_validation.json')['ordinary_updates']==600 and j('l4_shared_boss_validation.json')['boss_updates']==400 and len(j('native_revisits_validation.json')['results'])==12
summary=dict(passed=True,region_sha256=hashlib.sha256(a).hexdigest(),approved_frames=proof,native_ids=[5,6,7,8,9,19,20,21,28,29,30,31],ordinary_updates=600,boss_updates=400,cold_cached_transitions=12,original_boss_cache_bytes_verified=5744,live_art_bytes_verified=3424,source_lifetimes_and_native_pose_hook_verified=True,all16tapes_reconstructed=True,other7levels_bitidentical=True,terrain_palette_and_L4_boss_art_unchanged=True,hardware_tested=False)
(O/'validation_summary.json').write_text(json.dumps(summary,indent=2));(O/'approved_source_proof.json').write_text(json.dumps(proof,indent=2))
text='''R-Type TS2068 r131 - L4 shared approved ECM walkers

Replace the complete rtype folder, reset, launch rtype/rt.tap.
Startup: R131 PREPARING. Full disk build.

White ghost L4 native19..21: exact saved L1 ghost ZIP,3poses,32x32.
White/magenta walking head L4 native5..9: approved C32x32 conversion already
used in L1 (saved L6_head artwork). Four matching native poses6..9 retain
order; extra native5 uses the first approved pose. All4approvedframes retained.
Round yellow walker L4 native28..31: exact chosen walker ZIP used in L1,
4poses24x24. No resampling, new conversion or settings changes.
Existing L4 gunwalker14..18 remains unchanged.

The first two families lacked L4 runtime mappings; the round walker used older
art. There are now11exact approved frame assets serving the12native IDs.
Native collision/movement scripts remain unchanged;32x32art has a larger
visual footprint than original24x24. No claimed hardware performance result.

Space remains within existing RAM allocation. ArtworkB280..BFDF (3424bytes).
Boss cache5744bytes is unchanged; repartitioned compression expands first,
before its source storage is reused. A366byte second art stream uses only
retired native head packets; HOME backup is copied to temporary prefix RAM,
expanded to the tail, then the main stream overwrites that temporary prefix.
Preload remains gated by the existing cache-valid flag and uses a visible
scratch stack. Original restore/respawn and cold/cached paths retained.

PASS actualZ80 cold L4 title/game starts,600ordinaryupdates with all3families
observed, exact3424liveartbytes and5744boss cachebytes, native-ID/pose tests,
400update BB boss fight/art retention,12cold/cached transitions including
L4revisit,640nativeattrs pertransition,all16TAP reconstructions/checksums/ZIPCRC.
Gameplay tests use invulnerability diagnostics; not hardware confirmation.

Other7levels (including r130 L2 star fix),L4boss artwork,terrain/palettes,
stable99/100,stock64KB and reference/source ZIPs unchanged.
Comparison: build/graphics/l4_shared_review_r131/confirmed_families.png
Scripts: build_l4_shared_r131.py,verify_l4_shared_runtime_r131.mjs,
verify_l4_shared_boss_r131.mjs,verify_native_revisits_r131.mjs,
finalize_l4_shared_r131.py. Hardware confirmation pending.
'''
(O/'README.txt').write_text(text);(R/'docs/l4_shared_r131.txt').write_text(text)
manifest={str(p.relative_to(O)).replace(chr(92),'/'):hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((O/'rtype').rglob('*'))if p.is_file()};(O/'release_manifest.json').write_text(json.dumps(manifest,indent=2))
p=O/'RType_TS2068_r131.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
 def add(f,name):
  i=zipfile.ZipInfo(str(name).replace(chr(92),'/'),(2026,11,12,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,f.read_bytes())
 for f in sorted((O/'rtype').rglob('*')):
  if f.is_file():add(f,f.relative_to(O))
 for n in ['README.txt','validation_summary.json','l4_shared_contract.json','approved_source_proof.json','release_manifest.json']:add(O/n,n)
 add(R/'build/graphics/l4_shared_review_r131/confirmed_families.png','confirmed_families.png')
with zipfile.ZipFile(p)as z:assert z.testzip()is None
sha=hashlib.sha256(p.read_bytes()).hexdigest();(O/'RType_TS2068_r131.sha256').write_text(sha+'  '+p.name+'\n')
entry=f'''\n\n207. r131 L4 shared approved ECM walkers (2026-11-12).
Exact original bitmap/dimension comparisons confirm L4ghost19..21=L1native35..37; L4head6..9=L1native30..33 (also L6head10..13), extraL4head5=L6native9. L4round28..31=L1native53..56. Previous L4maps omitted ghost/head, and round stillusedr90olderassets. Reuse EXACT chosen3ghost32poses from convref/rtype-l1-ghost-assets.zip,4Chead32poses from saved walker_choice_r90/L6_head files (same latestL1),4round24poses from convref/rtype-l1-walker-snake-assets.zip. All11runtimeassets independently match bothlatestL1 and originalchosen exports, legalnormal8x1pairs. Noresampling/settings/newart. All12nativeIDs mapped; firstnativehead5usesapprovedpose0,6..9match4nativeposes; roundretains4celcycle. Existing gunwalker14..18 unchanged.
Raw3424bytes B280..BFDF, codeend{c['code_end']:04X}<A9C7,immutableend{c['bank1_end']:04X}<3A00. Nativeboss expanded5744bytes unchanged, preloadsplit1000 externalA9C7..{c['external_end']-1:04X} extends onlyinto nowredirectedround28..31 source. Aux366bytesA4E9..A656 reusesonlyredirectedhead5..9 packets; HOME C4E9backup -> temporaryB280prefix -> expand tailBD00..BFDF, thenmain2688byteprefix. Originalpreload relocatedbeforeart torespectsource lifetime; originalwarmupconditionalCALL removed andcache-validE3F0gate retained innewentry. Scratchstack5CF0keptvisible across6F/ED/2Fmaps,IX/nativeSPpreserved. Initialunreleased probes caught earlypreloadcallerstackvisibility, wronglycheckingboss cachebeforepreload, secondinitializationdecompressingoverwrittenstorage, and directtestsentinelwrittenHOMEwhileDOCK7mapped; allcorrectedbeforeZIP. Actualsource-lifetime/code/RAMtests nowpass title+gamestart2loads andcachedtransitions. Every cold/runtimegateway patched: preloadtableDEB4/5, imageDEE1/2, fastvisibilityDDBB/C, fastpairDF6C; newprefix fastsynthjump updated andintraextension symbolsreassembled. Otherregiondifferencesrestricted bank1packets/retiredsource7gatewaybytes;L4palette2000..27FF,bank4code/IM2,bank7,allother7levels bitidenticalr130.
PASS actualZ80coldL4+600ordinaryupdates/all3familiesnaturallyobserved/3424exactliveartbytes/5744exactbosscachebytes/12nativeIDposehookcases;600ordinary+400BBbossupdates/artretention;12coldcachedtransitionsincluding2L4visits/nativecore+cachedsource+640attrsperaudit;16TAPreconstruction/checksums/ZIPCRC. Diagnosticinvulnerability,not hardware. Comparisonconfirmed_families.png isassetpreview; L4_ordinary_500.home.png andL4_boss_300.home.png actualemulatedgameplay, inspected. No hardwareFPSclaim. Terrain/L4bossart,r130L2starfix,stable100,stock64KB/referenceprojects/originalZIPs unchanged. Candidate{p.relative_to(R)} SHA{sha}.\n'''
if b'207. r131 L4 shared approved'not in(R/'TEST_HISTORY.md').read_bytes():
 with(R/'TEST_HISTORY.md').open('ab')as f:f.write(entry.encode('ascii'))
 with(R/'PROJECT_STATE.md').open('ab')as f:f.write(f'\n2026-11-12 r131 L4 reuseexactapprovedghost32/Chead32/round24: native19..21/5..9/28..31.11exportverifiedframes,600ordinary+400bossupdates/12transitions/RAMsource-lifetime/tapesZIPPASS. {p.relative_to(R)} SHA{sha}. TEST_HISTORY207;comparison build/graphics/l4_shared_review_r131/confirmed_families.png. Hardwarepending,other7levels/stable100/stock64KB unchanged.\n'.encode('ascii'))
print(p);print(sha)
