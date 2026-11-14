from pathlib import Path
import json,zipfile,hashlib,functools
R=Path.cwd();O=R/'build/fullgame/terrain_token_fix_r76';B=R/'build/fullgame/loading_text_r74'
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();old=(B/f'level{n:02d}_region.bin').read_bytes();allowed=set(range(0xcf0,0xcfc))|set(range(0xdc0,0xdc3))
 if n==2:allowed|=set(range(0xfb8,0xfc2))|set(range(14562,14573))
 assert all(a==c or i in allowed for i,(a,c)in enumerate(zip(b,old))),n
for name in['launcher.bin','demand_loader.bin','rtype/rt.tap','rtype/RTCORE.TAP','rtype/RTPRELD.TAP']:assert(O/name).read_bytes()==(B/name).read_bytes()
def tape(p):
 raw=p.read_bytes();out=[];at=0
 while at<len(raw):
  size=int.from_bytes(raw[at:at+2],'little');v=raw[at+2:at+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;out.append(v);at+=size+2
 assert at==len(raw);return out
for p in(O/'rtype').iterdir():
 if p.suffix.lower()=='.tap':tape(p)
for n in range(1,9):
 raw=(O/f'level{n:02d}_region.bin').read_bytes();assert b''.join(v[1:-1]for v in tape(O/f'rtype/LEVEL{n:02d}.TAP')[1::2])==raw;assert b''.join(v[1:-1]for v in tape(O/f'rtype/START{n:02d}.TAP')[1::2])==b''.join(raw[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7])
for n in range(1,9):assert json.loads((O/f'boss_level{n}.json').read_text())['passed']
assert json.loads((O/'preload_title_L2.json').read_text())['passed'];assert json.loads((O/'repeated_jumps_validation.json').read_text())['passed']
readme='''R-Type TS2068 r76 - terrain colour marker fix
Replace COMPLETE rtype folder, reset, run rt.tap.
Expanded512KB disk package; stock64KB target unchanged.

Fixes reproduced L3 colour corruption after visiting L2, including cached
re-entry. L2's custom token keeper incorrectly cleared native terrain bit7;
its exit restored Spectrum RES7 instead of ECM NOPs, contaminating later
levels. The keeper now preserves tokens, exit restores NOPs, and every level
initialization resets the common hook after native helper rebuild and before
level-specific warmup. No terrain pixel/palette changes are needed for L3.

Restores r74 artwork, including upgraded L2 r67 boss body/head/mouth. The full
r66 L2 rollback in r75 is superseded by this code fix. Small loading text and
r73 terrain rollback retained. No new graphics conversions in this release.

Eight cold/cached switches 2/3/2/3/1/3/2/3 pass and assert marker hook after
completed transitions. Fresh L2 and switched L3 scenes inspected; L3 before/
after image saved beside package. All8 boss routes pass, LoadAll/all8resident/
title/cached joystick-fire restart pass. Tape reconstruction/checksums pass.
Hardware confirmation pending. Other previously reported glitches remain open.
'''
(O/'README.txt').write_text(readme,encoding='ascii');z=O/'RType_TS2068_r76.zip'
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED)as f:
 for p in sorted((O/'rtype').iterdir())+[O/'README.txt']:
  info=zipfile.ZipInfo(str(p.relative_to(O)).replace('\\','/'),date_time=(2026,11,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;f.writestr(info,p.read_bytes())
with zipfile.ZipFile(z)as f:assert f.testzip()is None
report={'version':76,'sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'bytes':z.stat().st_size,'artwork_identical_r74':True,'L2_r67_artwork_reinstated_vs_r75':True,'eight_boss_routes_passed':True,'repeated_cold_cached_colour_transitions_passed':True,'preload_title_restart_passed':True,'tapes_valid':True,'hardware_tested':False};(O/'validation_summary.json').write_text(json.dumps(report,indent=2))
for name,text in [('PROJECT_STATE.md','Latest r76 fixes reproduced L3 colour corruption on L2 exit and L2 native terrain colours. Actual root: r67 token keeper cleared terrain bit7; restore trailer reinstated Spectrum RES7 at FF81 rather than ECM NOPs. Preserves tokens, restores NOPs, resets hook after native helper rebuild each initialization using retired CF0padding wrapper. Artwork returns to r74, reinstating upgraded L2 r67 body/head/mouth instead of r75 full rollback. Small loading text retained. build/fullgame/terrain_token_fix_r76/RType_TS2068_r76.zip. TEST_HISTORY151 supersedes root-cause uncertainty in150.'),('TEST_HISTORY.md','151. L3 colour-token contamination fixed r76 (2026-11-07). Read state/history. User photo r73 reproduced by route L2->L3: firstscreen cyan/green broad top and blue/red/magenta bottom; fresh L3 normal. r66/r75 fresh L3 palette/terrain unchanged, so earlier whole-level comparisons missed stateful code. Watch FF81: original fresh NOP/NOP; r73 postL2 RES7. Root in r67 keep_dictionary_token: CP90/RES7 stripped original terrain80..8F; restore_trailer hardcoded CB BF from Spectrum instead of full ECM00 00. Fixedkeeper preserves all token bytes, restore writes00 00 while maintaining following12 opcode. Common level initialization resets FF81/82 after native86C3 helper rebuild before warmup; 12byte register-preserving wrapper occupies retired0CF0..0CFFpadding (all45 verified), DC0CALL redirected. Guards run after transition completion; initial test accidentally asserted during key selection while stillL2, corrected; writer trace isolated actual hook writes. Build script/source r76 separate. Static diff permits only hook/wrapper/code edits versusr74; every artwork byte/palette unchanged. r75 fullrollback superseded: upgraded r67L2body/head/mouth reinstated. No claim exact per-instance styles identicalr66; L2scene now coherent yellow/purple, no garish bands.\nEight transitions2/3/2/3/1/3/2/3 covercold/cached entry, hook asserts00 00 outsideL2; all8bossroutes pass (L7700afterjump,others160), LoadAll/all8resident/title/cachedphysicalfire restart pass. FreshL2ordinary80 and switchedL3 screenshots inspected; L3_before_after.png shows reproducedbad versuscorrected. AllTAP checksums/LEVEL/START reconstruction/ZIPCRC pass. Hardware pending, other knownL3stationaryfragment issue not claimed fixed. Stock64KB unchanged. Archive '+report['sha256']+' '+str(report['bytes'])+'bytes.')]:
 with(R/name).open('ab')as f:f.write(('\n\n'+text+'\n').encode('ascii'))
print(json.dumps(report,indent=2))
