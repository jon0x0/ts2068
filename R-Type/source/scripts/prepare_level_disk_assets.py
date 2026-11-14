"""Stage per-level disk streams for demand loading; not a runtime release."""
from pathlib import Path
import hashlib,json,struct,zipfile
ROOT=Path(__file__).resolve().parents[1]
def block(flag,data):
 crc=flag
 for v in data:crc^=v
 return struct.pack('<H',len(data)+2)+bytes([flag])+data+bytes([crc])
def main():
 image=(ROOT/'build/fullgame/loading_text_r28/RType_TS2068_fullgame_r28.ram512').read_bytes();assert len(image)==524288
 out=ROOT/'build/fullgame/demand_loading';out.mkdir(parents=True,exist_ok=True);records=[]
 for level in range(1,9):
  region=image[(level-1)*65536:level*65536];data=b''
  for page in range(8):
   raw=region[page*8192:(page+1)*8192]
   header=bytes([3])+f'RL{level}PAGE{page}'.encode().ljust(10,b' ')+struct.pack('<HHH',len(raw),page,0x8000)
   data+=block(0,header)+block(255,raw)
  name=f'LEVEL{level:02d}.TAP';(out/name).write_bytes(data)
  pos=0;decoded=[];idx=0
  while pos<len(data):
   size=int.from_bytes(data[pos:pos+2],'little');b=data[pos+2:pos+2+size];assert __import__('functools').reduce(int.__xor__,b)==0
   if idx%2:decoded.append(b[1:-1])
   else:assert int.from_bytes(b[14:16],'little')==idx//2
   pos+=size+2;idx+=1
  assert b''.join(decoded)==region
  records.append(dict(level=level,file=name,bytes=len(data),pages=8,region_sha256=hashlib.sha256(region).hexdigest(),file_sha256=hashlib.sha256(data).hexdigest()))
 (out/'asset_manifest.json').write_text(json.dumps(dict(status='Staged assets only; on-demand runtime not yet implemented',cwd_policy='All filenames relative to directory in which launcher is opened; no cd / or fixed folder',records=records),indent=2));print('Verified8 per-level streams,8 pages each; not a playable loader')
if __name__=='__main__':main()
