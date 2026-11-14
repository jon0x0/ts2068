from pathlib import Path
import hashlib,json,subprocess,zipfile
R=Path.cwd();O=R/'build/fullgame/hardware_fire_r65';B=R/'build/fullgame/native_fit_r64'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes():return {str(p.relative_to(O)):sha(p)for p in list(O.glob('*_region.bin'))+[O/'launcher.bin']+list((O/'rtype').glob('*.tap'))+list((O/'rtype').glob('*.TAP'))}
frozen=hashes();old=sha(B/'RType_TS2068_r64.zip');assert old=='1f50c30d5fbd79e49f2fcbd1ae31df6b3b65e7f12eb77d05bfcb0128d4c26d41'
for n in ['boot']+[f'level{i:02}'for i in range(1,9)]:
 b=(O/f'{n}_region.bin').read_bytes();a=(B/f'{n}_region.bin').read_bytes();allowed={0x1a37,0x1a54}
 if n=='boot':allowed.update(range(0x7fa9,0x7fac))
 if n!='boot':
  allowed.update([0x1b03,0x1b12]);allowed.update(range(0x1b17,0x1b20));allowed.update(range(0xcc2,0xcc5))
  if n=='level05':spans=[(0xa000,0xa400),(0x9ea0,0x9ff0),(0x8f10,0x8f80)]
  else:spans=[(0x3a00,0x3ff0)]
  for lo,hi in spans:allowed.update(range(lo,hi))
 assert all(x==y or i in allowed for i,(x,y)in enumerate(zip(a,b))),n
 assert b[0x1a37]==0x8f and b[0x1a54]==0x7b
# All tape checksums, and LEVEL/START exact payload reconstruction.
def tape(p):
 b=p.read_bytes();blocks=[];pos=0
 while pos<len(b):
  l=int.from_bytes(b[pos:pos+2],'little');v=b[pos+2:pos+2+l];assert len(v)==l and len(v)>=2;assert __import__('functools').reduce(int.__xor__,v,0)==0;blocks.append(v);pos+=l+2
 assert pos==len(b);return blocks
for p in (O/'rtype').iterdir():
 if p.suffix.lower()=='.tap':tape(p)
for n in range(1,9):
 b=(O/f'level{n:02}_region.bin').read_bytes();ts=tape(O/f'rtype/LEVEL{n:02}.TAP');assert b''.join(v[1:-1]for v in ts[1::2])==b
 ts=tape(O/f'rtype/START{n:02}.TAP');assert b''.join(v[1:-1]for v in ts[1::2])==b''.join(b[p*8192:(p+1)*8192]for p in[0,1,4,5,6,7])
p=subprocess.run(['python','scripts/build_ui_r65.py'],capture_output=True,text=True);(O/'rebuild.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr;assert hashes()==frozen
subprocess.run(['python','scripts/write_r65_readme.py'],check=True)
zp=O/'RType_TS2068_r65.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED)as z:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file() and p.name!='RTBOOT.TAP':z.write(p,'rtype/'+p.name)
with zipfile.ZipFile(zp)as z:assert z.testzip() is None;assert 'rtype/rt.tap'in z.namelist();assert not any('RTFULL' in p for p in z.namelist())
assert sha(B/'RType_TS2068_r64.zip')==old
report={'zip':str(zp),'sha256':sha(zp),'bytes':zp.stat().st_size,'reproducible_products':len(frozen),'tape_checksums':True,'bounded_changes':True,'r64_zip_preserved':True,'L3_hardware_fragment':'unresolved; not reproduced in scripted diagnostics','stock_64KB':'unchanged','tests':json.loads((O/'r65_checks.json').read_text())+json.loads((O/'r65_extra_checks.json').read_text())}
(O/'validation_summary.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
