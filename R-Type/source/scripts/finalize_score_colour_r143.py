from pathlib import Path
import json,zipfile,hashlib,functools
R=Path.cwd();B=R/'build/fullgame/l4_health_r142';O=R/'build/fullgame/score_colour_r143'
assert json.loads((O/'highscore_validation.json').read_text())['passed']
for n in range(1,9):
 a=(B/f'level{n:02d}_region.bin').read_bytes();b=(O/f'level{n:02d}_region.bin').read_bytes();assert len(a)==len(b) and all(0x19d2<=i<0x19e3 for i,(x,y)in enumerate(zip(a,b))if x!=y)
count=0
for p in (O/'rtype').glob('*.TAP'):
 s=p.read_bytes();at=0;parts=[]
 while at<len(s):
  n=int.from_bytes(s[at:at+2],'little');q=s[at+2:at+2+n];assert len(q)==n and functools.reduce(int.__xor__,q)==0
  if q[0]==255:parts.append(q[1:-1])
  at+=n+2
 assert at==len(s);count+=1
 if p.name.startswith('LEVEL'):
  assert b''.join(parts)==(O/f'level{int(p.stem[-2:]):02d}_region.bin').read_bytes()
 if p.name.startswith('START'):
  b=(O/f'level{int(p.stem[-2:]):02d}_region.bin').read_bytes();assert b''.join(parts)==b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7])
assert (O/'rtype/RTCORE.TAP').read_bytes()==(B/'rtype/RTCORE.TAP').read_bytes()
text='''R-Type TS2068 r143 - original high-score colors restored

Replace complete rtype folder, reset, run rtype/rt.tap.
The score restore now initializes the original alternating white/color rows
using native routine76CB, instead of forcing all attributes white. The
original seven-color phase and native animation routine are retained.
Standard-video restoration from the score corruption repair is retained.
All r142 changes, including16health per L4 target and recovery pickups, remain.

L4/L7 cold gameplay followed by actual score-display caller tested in emulation.
Native palette phase advances and white/colored rows coexist. Video mode0,
bank09, shadow0 verified. Direct native palette calls verify color progression;
this is not a full natural death/name-entry hardware test. All8level helper
changes bounded to existing17bytes; CORE unchanged. All20TAP checksums and
all LEVEL/START reconstruction pass. Hardware testing pending.
'''
(O/'README.txt').write_text(text);(O/'rtype/README.txt').write_text(text)
summary=dict(passed=True,levels_tested=[4,7],native_palette=0x76cb,core_unchanged=True,tap_files=count,hardware_tested=False)
(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
(O/'release_manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in sorted((O/'rtype').iterdir())if p.is_file()},indent=2))
p=O/'RType_TS2068_r143.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED)as z:
 for q,name in [(q,'rtype/'+q.name)for q in sorted((O/'rtype').iterdir())if q.is_file()]+[(O/n,n)for n in ['README.txt','validation_summary.json','release_manifest.json','highscore_validation.json']]:
  i=zipfile.ZipInfo(name,(2026,11,13,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o100644<<16;z.writestr(i,q.read_bytes())
with zipfile.ZipFile(p)as z:assert z.testzip()is None
sha=hashlib.sha256(p.read_bytes()).hexdigest()
with (R/'TEST_HISTORY.md').open('a',encoding='utf-8')as f:f.write('\n\n231. r143 score color restoration. r138 repair forced white attributes; replace existing17byte19D2 helper fill with native76CB palette initialization, retaining CALL1466 standard-mode restoration and JP7690. Original alternating white/color rows and seven-color phase preserved; no new allocation. L4/L7 cold20updates then real92EF score caller PASS mode0/map09/shadow0, colored+white attrs; direct76CB call advances colors. Not natural full death/name-entry or hardware proof. Initial test incorrectly entered76CE(mid-instruction), rejected/corrected using original snapshot signature76CB. Initial strict modulo64 layout assertion did not match native INC L row pattern; corrected to native color/coexistence/phase assertions, no runtime changes for assertion. Only19D2..19E2 differs in all8regions; CORE unchanged.20TAP checksums,allLEVEL/START reconstruction,ZIPCRC PASS. Stable100/stock64KB/priorarchives unchanged. '+str(p.relative_to(R))+' SHA256'+sha+' Hardwarepending.\n')
with (R/'PROJECT_STATE.md').open('a',encoding='utf-8')as f:f.write('\nr143 original native score palette restored alongside standard-mode repair; L4/L7 phase/static tests PASS, hardwarepending. '+str(p.relative_to(R))+' SHA'+sha+' TEST_HISTORY231.\n')
(R/'docs/score_colour_r143.txt').write_text(text+'\nSHA256 '+sha)
print(p);print(sha)
