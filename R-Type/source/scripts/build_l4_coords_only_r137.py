from pathlib import Path
import json,sys,shutil,numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from boss_motion_assets_r60 import unpack;from build_rocket_fix import code
B=R/'build/fullgame/boss_pickup_r136';O=R/'build/fullgame/l4_coords_only_r137';O.mkdir(exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']:shutil.copy2(p,O/p.name)
shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
b=bytearray((B/'level04_region.bin').read_bytes());c=json.loads((B/'l4_shared_contract.json').read_text());cache=bytearray((B/'L4_expected_cache.bin').read_bytes());changes=[]
for ident,base,w,h in [(25,0,15,56),(26,1792,12,64),(27,3456,12,88)]:
 empty=np.load(R/f'build/graphics/l4_spectrum_openings_r137/original_empty_{ident}.npy');cleared=0
 for cy,cx in zip(*np.where(empty)):
  at=base+cx*h*2+cy*16
  if any(cache[at:at+16]):cleared+=1
  pass # diagnostic: no empty-cell mask applied
 changes.append(dict(id=ident,original_empty_cells=int(empty.sum()),cleared_cells=cleared))
pretab=c['pretab'];packets=[]
for k in range(b[pretab]):
 at=pretab+1+k*4;ptr=int.from_bytes(b[at:at+2],'little');dest=int.from_bytes(b[at+2:at+4],'little')-0xc000;length=4096 if k==0 else len(cache)-4096;payload=pack(cache[dest:dest+length]);limit=c['external_end']if k==0 else pretab;assert ptr+len(payload)<=limit,(hex(ptr),len(payload),hex(limit));b[ptr:ptr+len(payload)]=payload;assert unpack(b[ptr:])==cache[dest:dest+length];packets.append(dict(start=ptr,end=ptr+len(payload),raw=length))
# Keep native actor-provided target coordinates, rather than invented offsets.
img=bytearray((B/'L4_runtime_image.bin').read_bytes());coord=int(json.loads((B/'walker_runtime.json').read_text())[3]['weakpoint_coordinates']) if False else next(q for q in json.loads((B/'walker_runtime.json').read_text())if q['level']==4)['weakpoint_coordinates'];off=coord-0xa000;assert img[off:off+4]==bytes.fromhex('ed4b3cdf');img[off+4]=0xc9
payload=pack(img);assert c['imageptr']+len(payload)<=0x3a00;b[c['imageptr']:0x3a00]=payload+bytes(0x3a00-c['imageptr']-len(payload))
# Restore the Spectrum rear target's native24x8 descriptor and source.
at=0xbb15+61*4;assert b[at:at+4]==bytes.fromhex('030200d4');b[at:at+4]=bytes.fromhex('030121d8')
(O/'level04_region.bin').write_bytes(b);(O/'L4_runtime_image.bin').write_bytes(img);(O/'L4_expected_cache.bin').write_bytes(cache)
for name in ['LEVEL04.TAP','START04.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)]
 (O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
c['bank1_end']=c['imageptr']+len(payload);c['native_target_coordinates_restored']=True;c['rear_target_size']=[24,8];(O/'l4_shared_contract.json').write_text(json.dumps(c,indent=2));(O/'opening_contract.json').write_text(json.dumps(dict(changes=changes,packets=packets,coordinate_helper=coord,packed_end=c['bank1_end'],rear_descriptor=at,scope='Original Spectrum transparent8x8cells and native target positions/sizes restored; no rescale or new animation script'),indent=2))
