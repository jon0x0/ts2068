from pathlib import Path
import sys,json,hashlib,functools,zipfile,shutil
R=Path.cwd();sys.path.insert(0,str(R/'scripts'))
O=R/'build/fullgame/l6_selected_r63';B=R/'build/fullgame/force_loading_r62'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 checks=json.loads((O/'current_checks.json').read_text());assert len(checks)==6 and all(v['passed']for v in checks)
 frozen=json.loads((O/'frozen_r63.json').read_text());assert all(sha(O/p)==s for p,s in frozen.items())
 import build_l6_selected_r63 as builder
 rebuild=R/'build/diagnostics/l6_selected_r63_rebuild';builder.OUT=rebuild;builder.main()
 differences=[p for p,h in frozen.items() if sha(rebuild/p)!=h];assert not differences,differences
 (O/'reproducibility_r63.json').write_text(json.dumps({'passed':True,'products':len(frozen),'differences':differences},indent=2))
 def blocks(p):
  b=p.read_bytes();off=0;rows=[]
  while off<len(b):
   n=int.from_bytes(b[off:off+2],'little');v=b[off+2:off+2+n];assert len(v)==n and functools.reduce(int.__xor__,v,0)==0;rows.append(v);off+=n+2
  assert off==len(b);return rows
 for n in range(1,9):
  data=(O/f'level{n:02d}_region.bin').read_bytes();assert len(data)==65536
  if n!=6:assert data==(B/f'level{n:02d}_region.bin').read_bytes()
  rs=blocks(O/f'RTYPE/LEVEL{n:02d}.TAP');assert len(rs)==16
  for k in range(8):assert rs[2*k+1][1:-1]==data[k*8192:(k+1)*8192]
  rs=blocks(O/f'RTYPE/START{n:02d}.TAP');assert len(rs)==96
  for k,(page,sub)in enumerate((p,s)for p in [0,1,4,5,6,7]for s in range(8)):assert rs[2*k+1][1:-1]==data[page*8192+sub*1024:page*8192+(sub+1)*1024]
 assert (O/'boot_region.bin').read_bytes()==(B/'boot_region.bin').read_bytes();assert (O/'launcher.bin').read_bytes()==(B/'launcher.bin').read_bytes()
 data=(O/'level06_region.bin').read_bytes();rec=json.loads((O/'generic_manifest.json').read_text())[0]
 assert rec['level']==6 and rec['raw_cache_bytes']<=0x1800 and rec['preloaded'];assert rec['motion_ptr']+rec['motion_image_bytes']<=0x3a00
 assert data[0x3a00:0x3fe0]==(B/'level06_region.bin').read_bytes()[0x3a00:0x3fe0]
 assert int.from_bytes(data[0xaab:0xaad],'little')==(O/'demand_loader.bin').stat().st_size
 assert data[0xe350+13*11]==0 and data[0xe3f0]==0
 assert sha(B/'RType_TS2068_r62.zip')=='e3e067696e54563880e59ad2fa6974340a2c56d497f56e4c6b0fdf2515f69574'
 for p in (O/'RTYPE').glob('*.TAP'):blocks(p)
 text=(R/'docs/r63_readme.txt').read_text(encoding='utf-8');(O/'README.txt').write_text(text,encoding='utf-8');(O/'RTYPE/README.txt').write_text(text,encoding='utf-8')
 report={'build':'r63','scope':'Expanded512KB disk; stock64KB unchanged','hardware_confirmed':False,'checks':checks,'reproducibility':{'products':len(frozen),'identical':True},'selected_art':json.loads((O/'selected_art.json').read_text()),'L6':json.loads((O/'l6_art_validation.json').read_text()),'cache_bytes':rec['raw_cache_bytes'],'motion_code_bytes':rec['motion_image_bytes'],'tapes_verified':True,'known_issue':'Previously reported L3 terrain-edge glitch remains open'}
 (O/'validation_summary.json').write_text(json.dumps(report,indent=2))
 archive=O/'RType_TS2068_r63.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  for p in [O/'README.txt',O/'validation_summary.json']:z.write(p,p.name)
  for p in sorted((O/'RTYPE').iterdir()):
   if p.is_file() and p.name!='RTBOOT.TAP':z.write(p,'RTYPE/'+p.name)
 with zipfile.ZipFile(archive)as z:assert z.testzip()is None
 (O/'package_sha256.txt').write_text(sha(archive)+'  '+archive.name+'\n');print('PACKAGED',archive,sha(archive))
if __name__=='__main__':main()
