from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_loading_text import encoded
def main():
 source=ROOT/'build/fullgame/loading_text_r28';out=ROOT/'build/fullgame/preview_end_r29';out.mkdir(parents=True,exist_ok=True);records=[]
 for name in [f'Level_{n}.dck'for n in range(1,9)]+['RType_level1_cartridge_r28.rom']:
  old=(source/name).read_bytes();data=bytearray(old);prefix=9 if name.endswith('.dck')else 0
  # The standalone tape-loader entry is never needed: all resident level data
  # is already loaded. Use its initial clear/prepare calls and native text draw.
  signature=bytes.fromhex('cd c2 b9 cd c3 86 3e 02 32 89 7a' if name.endswith('.rom') else 'cd c2 73 cd c3 86 3e 02 32 89 7a')
  found=[i for i in range(len(old))if old.startswith(signature,i)]
  assert len(found)==1,(name,found)
  at=found[0];stub=bytes.fromhex('cd c2 73 cd c3 86 af d3 ff 32 00 be 21 00 58 11 01 58 01 ff 02 36 47 ed b0 01 08 08 21 80 72 cd 81 c0 01 08 0c 21 90 72 cd 81 c0 fb 76 18 fd')
  if name.endswith('.rom'):stub=stub.replace(bytes.fromhex('cd c2 73'),bytes.fromhex('cd c2 b9')).replace(bytes.fromhex('21 80 72'),bytes.fromhex('21 80 b8')).replace(bytes.fromhex('21 90 72'),bytes.fromhex('21 90 b8'))
  data[at:at+len(stub)]=stub
  before=encoded('LEVEL READY - PRESS ANY KEY'.ljust(32));after=encoded('PREVIEW COMPLETE')+encoded('RESET TO REPLAY'.ljust(16))
  assert len(before)==len(after)==32
  assert data.count(before)==1;pos=data.find(before);data[pos:pos+32]=after
  dest='RType_level1_cartridge_r29.rom'if name.endswith('.rom')else name.replace('.dck','_preview_r29.dck')
  (out/dest).write_bytes(data)
  records.append(dict(file=dest,source=name,sha256=hashlib.sha256(data).hexdigest(),loader_offset=at-prefix,changes='Replace unused tape loader entry with native completion text and IRQ-enabled wait; no cassette calls reachable from that entry'))
  if name.endswith('.rom'):(out/'RType_level1_cartridge_r29.dck').write_bytes(bytes([0,2,2,2,2,2,2,2,2])+data)
 (out/'manifest.json').write_text(json.dumps(records,indent=2));print('Built',len(records),'standalone loader fixes')
if __name__=='__main__':main()



