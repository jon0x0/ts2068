from pathlib import Path
import json,zipfile,hashlib,functools
R=Path.cwd();B=R/'build/fullgame/score_colour_r143';O=R/'build/fullgame/preparing_r144'
for n in range(1,9):
 a=(B/f'level{n:02d}_region.bin').read_bytes();b=(O/f'level{n:02d}_region.bin').read_bytes()
 if n!=7:assert a==b
 else:
  diff=[i for i,(x,y)in enumerate(zip(a,b))if x!=y];assert all(i in [0xd9,0xda,0xddb,0xddc]or 0xdf50<=i<0xdff3 for i in diff),diff
assert (O/'rtype/RTCORE.TAP').read_bytes()==(B/'rtype/RTCORE.TAP').read_bytes()
for name in ['preparation_validation.json','cached_preparation_validation.json','native_revisits_validation.json']:
 assert json.loads((O/name).read_text())['passed']
assert all(q['passed']for q in json.loads((O/'unmodified_target_levels_fire_validation.json').read_text()))
count=0
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
text='''R-Type TS2068 r144 - clean silent L7 preparation

Replace complete rtype folder, reset, run rtype/rt.tap.
The substantial L7 art preparation delay now shows a small PREPARING LEVEL
message on clean black space, with all three AY volumes and beeper silenced.
Both cold and runtime preparation gateways use the same presentation.
No per-frame work is added. The art preparation itself still takes about5s.
All r143 graphics, score colors and L4 health/recovery improvements retained.

Cold L7 preparation:293 emulator display frames with stable framebuffer and
zero AY volumes, followed by real firing gameplay. Repeated cold/cached routes
and L7 preparation screen/sound checks pass. These are scripted emulator
checks, not hardware confirmation. Other seven level regions and CORE are
byte-identical; L5 IM2/UI reservations unchanged. All20TAP checksums and
LEVEL/START reconstruction pass. Stable100 and stock64KB target unchanged.
'''
(O/'README.txt').write_text(text);(O/'rtype/README.txt').write_text(text)
(O/'validation_summary.json').write_text(json.dumps(dict(passed=True,level=7,wrapper_start=0xdf50,wrapper_bytes=163,cold_and_runtime=True,other7levels_and_CORE_unchanged=True,tap_files=count,hardware_tested=False),indent=2))
(O/'release_manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((O/'rtype').iterdir())if p.is_file()},indent=2))
p=O/'RType_TS2068_r144.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED)as z:
 for q,name in [(q,'rtype/'+q.name)for q in sorted((O/'rtype').iterdir())if q.is_file()]+[(O/n,n)for n in ['README.txt','validation_summary.json','release_manifest.json','preparation_validation.json','cached_preparation_validation.json','native_revisits_validation.json','unmodified_target_levels_fire_validation.json','preparing_screen.png']]:
  i=zipfile.ZipInfo(name,(2026,11,13,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,q.read_bytes())
with zipfile.ZipFile(p)as z:assert z.testzip()is None
sha=hashlib.sha256(p.read_bytes()).hexdigest()
with (R/'TEST_HISTORY.md').open('a',encoding='utf-8')as f:f.write('\n\n232. r144 clean silent L7 preparation. User reports long delay/residual sound/garbage on L7 start and transitions. Both00D4 cold and0DC0 runtime JPDEDB now routeDF50wrapper; maps unchanged49, executes fromDOCK6, HOMEdisplay remains visible.163bytesDF50..DFF2 audited free beyond generic cache helper DSDF50 and livevarsDF30..DF44; does not reuse D300scripts,D800IM2,nor packedbank1. DI, beeper0, AYvol8/9/10=0, standardFFmode/shadow0, clearHOME4000..57FF and normal5800attrs; small7pxPREPARINGLEVEL bitmappublished then JPDEDB original warmup. Originalwarmup safe5CF0stack andcodec/planarart unchanged. No extra gameplay/frame cost. Cold preparation293displayframes stablebitmap+zeroAYuntilwarmupreturn then30realgameupdates PASS. Coldfire526updates3909IRQs PASS.12cachedroutes and4L7preparationinvocationsstable/silent PASS; initial exactly2invocation expectation rejected because native initialization usesadditionalpasses, assertion now coversall. Diagnostic preparing_screen.png rendered and inspected: cleanblack, smallwhitecenteredtext. OnlyL7gatewaytargets and163wrapperbytes plusversionlabels differ; other7regions/CORE exactidentity,all20TAPchecksum/reconstruction/ZIPCRC PASS. No hardwareconfirmation; no change to other levels presentation. Scripts build_preparing_r144.py,verify_preparation_r144.mjs,verify_cold_launcher_r144.mjs,verify_native_revisits_r144.mjs,finalize_preparing_r144.py. '+str(p.relative_to(R))+' SHA256'+sha+' Stable100/stock64KB/priorarchives/referenceprojectsunchanged.\n')
with (R/'PROJECT_STATE.md').open('a',encoding='utf-8')as f:f.write('\nr144 clean/silent smalltext L7preparation onbothcold/runtimegateways. Stable293frameprep/realcoldfire/12cachedroutes/allTAP PASS,hardwarepending;other7regionsunchanged. '+str(p.relative_to(R))+' SHA'+sha+' TEST_HISTORY232.\n')
(R/'docs/preparing_r144.txt').write_text(text+'\nSHA256 '+sha)
print(p);print(sha)
