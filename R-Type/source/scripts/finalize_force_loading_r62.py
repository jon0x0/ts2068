from pathlib import Path
import json,hashlib,zipfile,functools
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/force_loading_r62'
def main():
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 assert json.loads((OUT/'reproducibility_r62.json').read_text())['passed']
 checks=json.loads((OUT/'current_checks.json').read_text());assert len(checks)==9 and all(x['passed']for x in checks)
 frozen=json.loads((OUT/'frozen_r62.json').read_text());assert all(sha(OUT/p)==v for p,v in frozen.items())
 def payloads(file):
  b=file.read_bytes();at=0;rows=[]
  while at<len(b):
   n=int.from_bytes(b[at:at+2],'little');v=b[at+2:at+2+n];assert len(v)==n and functools.reduce(int.__xor__,v,0)==0;rows.append(v);at+=n+2
  assert at==len(b);return rows
 for n in range(1,9):
  b=(OUT/f'level{n:02d}_region.bin').read_bytes();assert len(b)==65536
  old=(ROOT/f'build/fullgame/startup_r61/level{n:02d}_region.bin').read_bytes();assert b[0xe000:0xfb98]==old[0xe000:0xfb98] and b[0xfb9b:]==old[0xfb9b:]
  assert b[0xfb98:0xfb9b]==bytes.fromhex('c3 c3 fd')
  for at in [0x4abc,0x4c2f,0x5286,0x52e4,0x538f]:assert b[at:at+3]==bytes.fromhex('cd 02 00')
  assert b[0xa496:0xa499]==bytes.fromhex('cd 0d 00')
  for lo,hi in [(0xc00,0x2000),(0x4000,0x6600),(0xa000,0xd87c)]:
   for i in range(lo,hi-2):
    if (n,i)in [(2,0xd55b),(6,0xc732)]:
     # Operand bytes, not instruction starts: AND FC / JP E6DC.
     assert (n==2 and b[i-1:i+3]==bytes.fromhex('e6 fc b5 fd'))or(n==6 and b[i-1:i+3]==bytes.fromhex('c3 dc e6 fd'));continue
    if b[i] in [0xcd,0xc3]:assert not 0xfda5<=int.from_bytes(b[i+1:i+3],'little')<0xfe03,'Missed relocated native entry'

  rows=payloads(OUT/'RTYPE'/f'LEVEL{n:02d}.TAP');assert len(rows)==16
  for k in range(8):assert rows[k*2][0]==0 and rows[k*2+1][0]==255 and rows[k*2+1][1:-1]==b[k*8192:(k+1)*8192]
  rows=payloads(OUT/'RTYPE'/f'START{n:02d}.TAP');assert len(rows)==96
  for k,(page,sub)in enumerate((p,s)for p in [0,1,4,5,6,7]for s in range(8)):
   assert rows[k*2][0]==0 and rows[k*2+1][0]==255 and rows[k*2+1][1:-1]==b[page*8192+sub*1024:page*8192+(sub+1)*1024]
 boot=(OUT/'boot_region.bin').read_bytes();helper=(OUT/'force_collision.bin').read_bytes();assert len(helper)<=64 and boot[0x3173:0x3173+len(helper)]==helper;assert boot[0xdb98:0xdb9b]==bytes.fromhex('c3 c3 fd');assert boot[0xa059:0xa05c]==bytes.fromhex('cd 02 00')
 assert len(payloads(OUT/'RTYPE/RTCORE.TAP'))==44
 assert len(payloads(OUT/'RTYPE/RTPRELD.TAP')[1][1:-1])==8192
 assert len((OUT/'demand_loader.bin').read_bytes())<6144
 assert len((OUT/'level_hotkeys_home.bin').read_bytes())<=1024
 text=(ROOT/'docs/r62_readme.txt').read_text();(OUT/'README.txt').write_text(text);(OUT/'RTYPE/README.txt').write_text(text)
 report={'build':'r62','hardware_confirmed':False,'open_issues':['Reported L3 terrain-edge glitch not identified in the guarded emulator route','L6 minor-enemy graphics are offline proposals awaiting review'],'checks':checks,'force':json.loads((OUT/'force_validation.json').read_text()),'L3':json.loads((OUT/'ordinary_L3_validation.json').read_text()),'repeated_jumps':json.loads((OUT/'repeated_jumps_validation.json').read_text()),'static_tape_reconstruction':True,'source_hashes':frozen,'scope':'expanded-memory disk; stock64KB unchanged'};(OUT/'validation_summary.json').write_text(json.dumps(report,indent=2))
 archive=OUT/'RType_TS2068_r62.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  z.write(OUT/'README.txt','README.txt');z.write(OUT/'validation_summary.json','validation_summary.json')
  for p in sorted((OUT/'RTYPE').iterdir()):
   if p.is_file() and p.name!='RTBOOT.TAP':z.write(p,'RTYPE/'+p.name)
 with zipfile.ZipFile(archive)as z:assert z.testzip()is None
 (OUT/'package_sha256.txt').write_text(sha(archive)+'  '+archive.name+'\n');print(archive,sha(archive))
if __name__=='__main__':main()
