"""Native per-level reference builds before ECM/streaming integration."""
from pathlib import Path
import sys,json,hashlib,zlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from inventory_sources import tap_blocks
from native_compat import patch_input
def main():
 out=ROOT/'build/fullgame/foundation';out.mkdir(parents=True,exist_ok=True)
 baseline=(ROOT/'build/spectrum_baseline/postload_4000_FFFF.bin').read_bytes();blocks=tap_blocks((ROOT/'build/spectrum_baseline/reference.tap').read_bytes());levels=[b[1:-1]for b in blocks[9::2]];assert len(levels)==8
 boot=(ROOT/'build/native/boot.bin').read_bytes();records=[]
 for level,payload in enumerate(levels,1):
  logical=bytearray(baseline);logical[0xc4ae-0x4000:0xc4ae-0x4000+len(payload)]=payload;logical[0x719c-0x4000]=48+level
  raw=bytes(logical);ram,patches=patch_input(ROOT,raw);rom=bytearray(b'\xff'*65536)
  for source,dest in [(7,2),(1,3),(2,4),(3,5),(5,6),(6,7)]:rom[source*8192:(source+1)*8192]=ram[(dest-2)*8192:(dest-1)*8192]
  rom[0x8000:0x8000+len(boot)]=boot;code=(ROOT/'build/native/input.bin').read_bytes();rom[0x1a00:0x1a00+len(code)]=code
  path=out/f'level{level:02d}';path.with_suffix('.dck').write_bytes(bytes([0]+[2]*8)+rom);path.with_suffix('.raw').write_bytes(raw);path.with_suffix('.payload').write_bytes(payload)
  mem=bytes(0x4000)+raw;word=lambda a:int.from_bytes(mem[a:a+2],'little');map_start=word(0xc4bc);map_end=word(0xc4b4);world=mem[map_start:map_end];tiles=max(v&63 for v in world)+1;terrain_start=map_start-tiles*144;descriptor_start=word(0xc4ba);descriptors=(terrain_start-descriptor_start)//4
  assert len(world)%5==0 and (terrain_start-descriptor_start)%4==0
  enemies=[]
  for ident in range(descriptors):
   d=descriptor_start+ident*4;w,h=mem[d:d+2];p=word(d+2);enemies.append(dict(id=ident+1,width=w,height=h,pointer=p))
  records.append(dict(level=level,payload_bytes=len(payload),payload_sha256=hashlib.sha256(payload).hexdigest(),zlib_bytes=len(zlib.compress(payload,9)),map_start=map_start,map_end=map_end,map_columns=len(world)//5,terrain_tiles=tiles,terrain_start=terrain_start,enemy_descriptors=descriptors,enemy_descriptors_start=descriptor_start,enemies=enemies,header=list(payload[:32]),dck_sha256=hashlib.sha256(path.with_suffix('.dck').read_bytes()).hexdigest()))
 (out/'manifest.json').write_text(json.dumps(dict(status='Native per-level diagnostic references; no full-game progression/ECM claim',levels=records,compressed_payload_total=sum(x['zlib_bytes']for x in records)),indent=2))
 print([{k:v[k]for k in ['level','payload_bytes','zlib_bytes','map_columns','terrain_tiles','enemy_descriptors']}for v in records]);print('zlib lower-bound budget',sum(v['zlib_bytes']for v in records))
if __name__=='__main__':main()
