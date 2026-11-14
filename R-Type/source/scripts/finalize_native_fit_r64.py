from pathlib import Path
import sys,json,hashlib,functools,zipfile
import numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import LAYOUTS,unpack
O=R/'build/fullgame/native_fit_r64';B=R/'build/fullgame/l6_selected_r63';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def blocks(p):
 b=p.read_bytes();off=0;rows=[]
 while off<len(b):
  n=int.from_bytes(b[off:off+2],'little');v=b[off+2:off+2+n];assert len(v)==n and functools.reduce(int.__xor__,v,0)==0;rows.append(v);off+=n+2
 assert off==len(b);return rows

def main():
 checks=json.loads((O/'current_checks.json').read_text());assert len(checks)==14 and all(v['passed']for v in checks)
 frozen=json.loads((O/'frozen_r64.json').read_text());assert all(sha(O/p)==h for p,h in frozen.items())
 import build_native_fit_r64 as builder
 builder.OUT=R/'build/diagnostics/native_fit_r64_rebuild';builder.main();assert all(sha(builder.OUT/p)==h for p,h in frozen.items())
 (O/'reproducibility_r64.json').write_text(json.dumps({'passed':True,'products':len(frozen),'differences':[]},indent=2))
 for n in range(1,9):
  b=(O/f'level{n:02d}_region.bin').read_bytes();old=(B/f'level{n:02d}_region.bin').read_bytes();assert len(b)==65536;allowed=set(range(0xcc2,0xcdf))|set(range(0xf100,0xf380))
  allowed.update(range(0xa000,0xa400)if n==5 else range(0x3a00,0x3e00))
  if n==6:
   for lo,hi in [(0x2400,0x3a00),(0xa000,0xa4ae),(0xdc50,0xe400),(0x9fc,0xa06)]:allowed.update(range(lo,hi))
   assert b[0xa4ae:0xdc50]==old[0xa4ae:0xdc50],'L6 native AI/events altered'
   assert b[0xe000:0xe2d0]==old[0xe000:0xe2d0]
  if n==7:
   allowed.update(range(0x2000,0x2400));mem=bytes(0xc000)+old[0xa000:0xe000];layout=LAYOUTS[6]
   for ident in json.loads((O/'l7_art_manifest.json').read_text())['ids']:
    d=layout['enemies'][ident-1];p=d['pointer']
    for _ in range(d['width']*d['height']):
     if mem[p]==54:p+=1;continue
     allowed.update(range(p-0x2000,p-0x2000+9));p+=9
   assert b[layout['enemy_descriptors_start']-0x2000:layout['terrain_start']-0x2000]==old[layout['enemy_descriptors_start']-0x2000:layout['terrain_start']-0x2000]
   assert b[0x2000:0x2200]==old[0x2000:0x2200],'Reserved original palette rows changed'
  bad=[i for i,(x,y)in enumerate(zip(b,old))if x!=y and i not in allowed];assert not bad,(n,bad[:20])
  rs=blocks(O/'RTYPE'/f'LEVEL{n:02d}.TAP');assert len(rs)==16
  for k in range(8):assert rs[2*k+1][1:-1]==b[k*8192:(k+1)*8192]
  rs=blocks(O/'RTYPE'/f'START{n:02d}.TAP');assert len(rs)==96
  for k,(page,sub)in enumerate((p,s)for p in[0,1,4,5,6,7]for s in range(8)):assert rs[2*k+1][1:-1]==b[page*8192+sub*1024:page*8192+(sub+1)*1024]
  assert b[0xeb:0xf7]==old[0xeb:0xf7],'Live dispatcher overwritten'
  assert b[0xf100:0xf380]==(O/'projectile_clock.bin').read_bytes()
 boot=(O/'boot_region.bin').read_bytes();old=(B/'boot_region.bin').read_bytes();allowed=set(range(0xcc2,0xcdf))|set(range(0xf100,0xf380))|set(range(0xa042,0xa045));assert all(x==y or i in allowed for i,(x,y)in enumerate(zip(boot,old)))
 assert len(unpack(boot[0x3400:0x3fe0]))==8192
 core=b''.join(v[1:-1]for v in blocks(O/'RTYPE/RTCORE.TAP')if v[0]==255);assert len(core)==22528 and core[0x656:0x659]==bytes.fromhex('cd db 00');assert core[20480+0x42:20480+0x45]==bytes.fromhex('cd d7 0c')
 contracts=json.loads((O/'r64_contracts.json').read_text());assert contracts['home_hot_bytes']<=1024 and contracts['hot_bytes']<=1024
 for i in range(140,146):
  a=np.load(R/f'build/graphics/r64_native_fit/L6_{i}.npy');assert a.shape==(32,16) and all(len(set(row[x:x+8]))<=2 for row in a for x in[0,8])
 for p in O.glob('L7_sprite*.npy'):
  a=np.load(p);assert a.max()<=7 and all(len(set(row[x:x+8]))<=2 for row in a for x in range(0,a.shape[1],8))
 assert sha(B/'RType_TS2068_r63.zip')=='739ca53a0e70c7db176275efa2b82d2b00c919c78992084b20277caf4a6c0446'
 for p in (O/'RTYPE').glob('*.TAP'):blocks(p)
 text=(R/'docs/r64_readme.txt').read_text(encoding='utf-8');(O/'README.txt').write_text(text,encoding='utf-8');(O/'RTYPE/README.txt').write_text(text,encoding='utf-8')
 report={'build':'r64','hardware_confirmed':False,'scope':'expanded512KB disk; stock64KB unchanged','checks':checks,'reproducibility':{'products':len(frozen),'identical':True},'contracts':contracts,'L7_art':json.loads((O/'l7_art_manifest.json').read_text()),'bolt_cleanup':json.loads((O/'bolt_redraw_fixed.json').read_text()),'L3_ordinary':json.loads((O/'ordinary_L3_validation.json').read_text()),'L3_hardware_status':'Reproducible bolt ownership loss fixed; exact user photo not yet hardware-confirmed','tape_reconstruction':True,'bounded_change_contracts':True}
 (O/'validation_summary.json').write_text(json.dumps(report,indent=2));archive=O/'RType_TS2068_r64.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  for p in [O/'README.txt',O/'validation_summary.json']:z.write(p,p.name)
  for p in sorted((O/'RTYPE').iterdir()):
   if p.is_file() and p.name!='RTBOOT.TAP':z.write(p,'RTYPE/'+p.name)
 with zipfile.ZipFile(archive)as z:assert z.testzip()is None
 (O/'package_sha256.txt').write_text(sha(archive)+'  '+archive.name+'\n');print('PACKAGED',archive,sha(archive))
if __name__=='__main__':main()
