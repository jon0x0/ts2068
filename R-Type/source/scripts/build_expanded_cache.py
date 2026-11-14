"""Build a 512KB staging bundle of finite scroll phases and original level data.

Gameplay in region0 currently uses resident r8 optimizations. Expanded phase data
is NOT read by the current renderer: this is an asset/runtime-interface milestone,
not a claim that banked scrolling is integrated or faster.
"""
from pathlib import Path
import hashlib,json,struct
import numpy as np
from inventory_sources import tap_blocks
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'build/expanded_cache';out.mkdir(parents=True,exist_ok=True)
 core=(ROOT/'build/ecm_native/RType_level1_ECM_TSPico_RAM_r8.bin').read_bytes();b=bytes(0x4000)+(ROOT/'build/spectrum_baseline/postload_4000_FFFF.bin').read_bytes()
 tile_end=int.from_bytes(b[0xc4bc:0xc4be],'little');map_end=int.from_bytes(b[0xc4b4:0xc4b6],'little');tilemap=b[tile_end:map_end]
 assert len(tilemap)==535 and max(x&63 for x in tilemap)==21
 codes=sorted(set(tilemap));pool=[];pool_index={};indices=bytearray();canonical={};verified=0
 for code in codes:
  p=tile_end-((code&63)+1)*144;tile=np.zeros((32,32),dtype=np.uint8)
  for cy in range(4):
   for cx in range(4):
    attr=b[p];p+=1;ink=(attr&7)+((attr>>6&1)*8);paper=((attr>>3)&7)+((attr>>6&1)*8)
    bits=np.unpackbits(np.frombuffer(b[p:p+8],dtype=np.uint8)).reshape(8,8);p+=8;tile[cy*8:cy*8+8,cx*8:cx*8+8]=np.where(bits,ink,paper)
  if code&64:tile=tile[:,::-1]
  if code&128:tile=tile[::-1,:]
  canonical[code]=tile.copy()
  for phase in range(8):
   pixels=np.zeros((32,40),dtype=np.uint8);coverage=np.zeros((32,40),dtype=np.uint8);pixels[:,phase:phase+32]=tile;coverage[:,phase:phase+32]=1
   for y in range(32):
    planes=[(pixels[y]>>bit)&1 for bit in range(4)]+[coverage[y]];record=b''.join(np.packbits(v).tobytes() for v in planes);assert len(record)==25
    if record not in pool_index:pool_index[record]=len(pool);pool.append(record)
    indices+=struct.pack('<H',pool_index[record])
   verified+=1
 # Independent reconstruction from row records, checking geometry and transparent spill.
 for n,code in enumerate(codes):
  for phase in range(8):
   reconstructed=np.zeros((32,40),dtype=np.uint8);mask=np.zeros((32,40),dtype=np.uint8)
   for y in range(32):
    row=struct.unpack_from('<H',indices,((n*8+phase)*32+y)*2)[0];record=pool[row]
    for bit in range(4):reconstructed[y]|=np.unpackbits(np.frombuffer(record[bit*5:bit*5+5],dtype=np.uint8))<<bit
    mask[y]=np.unpackbits(np.frombuffer(record[20:25],dtype=np.uint8))
   assert np.array_equal(reconstructed[:,phase:phase+32],canonical[code]);assert mask.sum()==1024 and mask[:,:phase].sum()==0 and mask[:,phase+32:].sum()==0
 image=bytearray([255]*(512*1024));image[:65536]=core;image[65536:65544]=b'RTP512A1';cursor=73728;assets=[]
 def add(name,data):
  nonlocal cursor
  cursor=(cursor+255)&~255;start=cursor;end=start+len(data);assert end<=len(image),(name,end)
  image[start:end]=data;spans=[];p=start
  while p<end:
   count=min(end-p,8192-(p%8192));spans.append(dict(page=p//8192,region=p//65536,memdock_slot=(p//65536)*2,cpu_chunk=(p//8192)%8,offset=p%8192,length=count));p+=count
  assert b''.join(image[s['page']*8192+s['offset']:s['page']*8192+s['offset']+s['length']] for s in spans)==data
  assets.append(dict(name=name,physical_offset=start,bytes=len(data),sha256=sha(data),spans=spans));cursor=end
  (out/name).write_bytes(data)
 add('terrain_map.bin',tilemap);add('terrain_codes.bin',bytes(codes));add('phase_rows.u16',indices);add('phase_pool.5plane',b''.join(pool))
 blocks=tap_blocks((ROOT/'build/spectrum_baseline/reference.tap').read_bytes());levels=[v[1:-1] for v in blocks[9::2]];assert len(levels)==8 and sum(map(len,levels))==94886
 for n,data in enumerate(levels,1):add(f'level{n:02d}.bin',data)
 (out/'RType_level1_assets.ram512').write_bytes(image)
 for region in range(8):(out/f'region{region:02d}_slot{region*2:02d}.bin').write_bytes(image[region*65536:(region+1)*65536])
 manifest=dict(status='STAGING ONLY: expanded phase data is not consumed by current gameplay. No expanded-memory speed or hardware deployment claim.',image_bytes=len(image),image_sha256=sha(image),resident_region0_sha256=sha(core),region_count=8,page_count=64,used_through=cursor,free_bytes=len(image)-cursor,first_level_tile_codes=len(codes),phase_variants=verified,rows_before_dedup=verified*32,unique_rows=len(pool),row_bytes=25,raw_phase_bytes=verified*32*25,pooled_phase_bytes=len(indices)+len(pool)*25,format='40-pixel finite rows: four source colour-index bitplanes plus coverage; NOT final ECM attributes. Preserve palette until shared-cell composition.',source='Original postload checkpoint terrain codes/map; all eight unmodified TAP level payloads.',assets=assets,page_sha256=[sha(image[i*8192:(i+1)*8192]) for i in range(64)],runtime_requirement='HOME bank gateway with bounded stock MEMDOCK transfers and eight read-only selector-priming accesses; restore region0 before returning to DOCK code. Native runtime consumer still outstanding.')
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print({k:manifest[k] for k in ('status','image_bytes','used_through','free_bytes','phase_variants','unique_rows','raw_phase_bytes','pooled_phase_bytes')})
if __name__=='__main__':main()
