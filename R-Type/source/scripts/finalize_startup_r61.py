from pathlib import Path
import json,hashlib,zipfile,functools
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/startup_r61'
def main():
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 assert json.loads((OUT/'reproducibility_r61.json').read_text())['passed']
 checks=json.loads((OUT/'current_checks.json').read_text());assert len(checks)==8 and all(x['passed']for x in checks)
 frozen=json.loads((OUT/'frozen_r61.json').read_text());assert all(sha(OUT/p)==v for p,v in frozen.items())
 def payloads(file):
  b=file.read_bytes();at=0;rows=[]
  while at<len(b):
   n=int.from_bytes(b[at:at+2],'little');v=b[at+2:at+2+n];assert len(v)==n and functools.reduce(int.__xor__,v,0)==0;rows.append(v);at+=n+2
  assert at==len(b);return rows
 for n in range(1,9):
  b=(OUT/f'level{n:02d}_region.bin').read_bytes();assert len(b)==65536
  assert b[0xa496:0xa499]==bytes.fromhex('cd 0d 00')
  for lo,hi in [(0xc00,0x2000),(0x4000,0x6600),(0xa000,0xd87c)]:
   for i in range(lo,hi-2):
    if (n,i)in [(2,0xd55b),(6,0xc732)]:
     # Operand bytes, not instruction starts: AND FC / JP E6DC.
     assert (n==2 and b[i-1:i+3]==bytes.fromhex('e6 fc b5 fd'))or(n==6 and b[i-1:i+3]==bytes.fromhex('c3 dc e6 fd'));continue
    if b[i] in [0xcd,0xc3,0xc2,0xca,0xd2,0xda,0xe2,0xea,0xf2,0xfa,0xc4,0xcc,0xd4,0xdc,0xe4,0xec,0xf4,0xfc]:assert not 0xfda5<=int.from_bytes(b[i+1:i+3],'little')<0xfde9,'Missed popup entry'

  rows=payloads(OUT/'RTYPE'/f'LEVEL{n:02d}.TAP');assert len(rows)==16
  for k in range(8):assert rows[k*2][0]==0 and rows[k*2+1][0]==255 and rows[k*2+1][1:-1]==b[k*8192:(k+1)*8192]
  rows=payloads(OUT/'RTYPE'/f'START{n:02d}.TAP');assert len(rows)==96
  for k,(page,sub)in enumerate((p,s)for p in [0,1,4,5,6,7]for s in range(8)):
   assert rows[k*2][0]==0 and rows[k*2+1][0]==255 and rows[k*2+1][1:-1]==b[page*8192+sub*1024:page*8192+(sub+1)*1024]
 assert len(payloads(OUT/'RTYPE/RTCORE.TAP'))==44
 assert len(payloads(OUT/'RTYPE/RTPRELD.TAP')[1][1:-1])==8192
 assert len((OUT/'demand_loader.bin').read_bytes())<6144
 assert len((OUT/'level_hotkeys_home.bin').read_bytes())<=1024
 text=(ROOT/'docs/r61_readme.txt').read_text();(OUT/'README.txt').write_text(text);(OUT/'RTYPE/README.txt').write_text(text)
 report={'build':'r61','hardware_confirmed':False,'checks':checks,'repeated_jumps':json.loads((OUT/'repeated_jumps_validation.json').read_text()),'static_tape_reconstruction':True,'source_hashes':frozen,'scope':'expanded-memory disk; stock64KB unchanged'};(OUT/'validation_summary.json').write_text(json.dumps(report,indent=2))
 archive=OUT/'RType_TS2068_r61.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  z.write(OUT/'README.txt','README.txt');z.write(OUT/'validation_summary.json','validation_summary.json')
  for p in sorted((OUT/'RTYPE').iterdir()):
   if p.is_file() and p.name!='RTBOOT.TAP':z.write(p,'RTYPE/'+p.name)
 with zipfile.ZipFile(archive)as z:assert z.testzip()is None
 (OUT/'package_sha256.txt').write_text(sha(archive)+'  '+archive.name+'\n');print(archive,sha(archive))
if __name__=='__main__':main()
