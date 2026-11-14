from pathlib import Path
import json,sys,shutil,numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from boss_motion_assets_r60 import unpack;from build_rocket_fix import code
B=R/'build/fullgame/boss_pickup_r136';O=R/'build/fullgame/l4_openings_r137';O.mkdir(exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']:shutil.copy2(p,O/p.name)
shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
b=bytearray((B/'level04_region.bin').read_bytes());c=json.loads((B/'l4_shared_contract.json').read_text());cache=bytearray((B/'L4_expected_cache.bin').read_bytes());changes=[]
for ident,base,w,h in [(25,0,15,56),(26,1792,12,64),(27,3456,12,88)]:
 empty=np.load(R/f'build/graphics/l4_spectrum_openings_r137/original_empty_{ident}.npy');cleared=0
 for cy,cx in zip(*np.where(empty)):
  at=base+cx*h*2+cy*16
  if any(cache[at:at+16]):cleared+=1
  cache[at:at+16]=bytes(16)
 changes.append(dict(id=ident,original_empty_cells=int(empty.sum()),cleared_cells=cleared))
pretab=c['pretab'];packets=[]
for k in range(b[pretab]):
 at=pretab+1+k*4;ptr=int.from_bytes(b[at:at+2],'little');dest=int.from_bytes(b[at+2:at+4],'little')-0xc000;length=4096 if k==0 else len(cache)-4096;payload=pack(cache[dest:dest+length]);limit=c['external_end']if k==0 else pretab;assert ptr+len(payload)<=limit,(hex(ptr),len(payload),hex(limit));b[ptr:ptr+len(payload)]=payload;assert unpack(b[ptr:])==cache[dest:dest+length];packets.append(dict(start=ptr,end=ptr+len(payload),raw=length))
# Keep native actor-provided target coordinates, rather than invented offsets.
img=bytearray((B/'L4_runtime_image.bin').read_bytes());coord=int(json.loads((B/'walker_runtime.json').read_text())[3]['weakpoint_coordinates']) if False else next(q for q in json.loads((B/'walker_runtime.json').read_text())if q['level']==4)['weakpoint_coordinates'];off=coord-0xa000;assert img[off:off+4]==bytes.fromhex('ed4b3cdf');img[off+4]=0xc9
assert img.count(bytes.fromhex('32fba3'))==1;img=img.replace(bytes.fromhex('32fba3'),bytes.fromhex('22fba3'));at=img.find(bytes.fromhex('cdb0db0020'),0x292,0x2d0);assert at>=0;img[at:at+5]=bytes.fromhex('3a03a4b720')
# Withdraw the r135 helper and restore the original snake-only second packet.
sc=json.loads((B/'snake_contract.json').read_text());tail=pack((B/'L4_snake_art.bin').read_bytes()[216:]);b[0xb474:0xb567]=tail+bytes(0xb567-0xb474-len(tail));at=img.find(bytes.fromhex('2174d411d8da01'));assert at>=0;img[at+7:at+9]=len(tail).to_bytes(2,'little')
payload=pack(img);assert c['imageptr']+len(payload)<=0x3a00;b[c['imageptr']:0x3a00]=payload+bytes(0x3a00-c['imageptr']-len(payload))
# Restore the Spectrum rear target's native24x8 descriptor and source.
at=0xbb15+61*4;assert b[at:at+4]==bytes.fromhex('030200d4');b[at:at+4]=bytes.fromhex('030121d8')
(O/'level04_region.bin').write_bytes(b);(O/'L4_runtime_image.bin').write_bytes(img);(O/'L4_expected_cache.bin').write_bytes(cache)
for name in ['LEVEL04.TAP','START04.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)]
 (O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
c['bank1_end']=c['imageptr']+len(payload);sc['packets'][1][1]=0xb474+len(tail);sc['packed_end']=c['bank1_end'];(O/'snake_contract.json').write_text(json.dumps(sc,indent=2));c.pop('direct_cell_helper',None);c['native_target_coordinates_restored']=True;c['rear_target_size']=[24,8];(O/'l4_shared_contract.json').write_text(json.dumps(c,indent=2));(O/'opening_contract.json').write_text(json.dumps(dict(changes=changes,packets=packets,coordinate_helper=coord,packed_end=c['bank1_end'],rear_descriptor=at,scope='Original Spectrum transparent8x8cells and native target positions/sizes restored; no rescale or new animation script'),indent=2))
(O/'speed_contract.json').write_text(json.dumps(dict(r135_direct_copy_withdrawn=True,reason='Repeated hull rows in matched visual isolation; proven compositor restored',performance_gain_not_claimed=True),indent=2))
# Keep allocation metadata and assembly/binary companions consistent with active code.
wm=json.loads((B/'walker_runtime.json').read_text());w=next(q for q in wm if q['level']==4);w['immutable_end']=c['bank1_end'];w['native_target_coordinates_restored']=True;(O/'walker_runtime.json').write_text(json.dumps(wm,indent=2))
metas=json.loads((B/'generic_manifest.json').read_text());m=next(q for q in metas if q['level']==4);m['raw_cache_bytes']=len(cache);m['native_opening_mask_restored']=True;(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2))
start=w['extension']['restore_native_bank5']-0xa000;end=w['weakpoint_helper']-0xa000;(O/'L4_walker_extension.bin').write_bytes(img[start:end])
source=(B/'L4_walker_extension.asm').read_text();import re
source=re.sub(r'(LD HL,\$D474\s+LD DE,\$DAD8\s+LD BC,)\d+',r'\g<1>203',source);(O/'L4_walker_extension.asm').write_text(source)
coord_bytes=bytes(img[off:]);(O/'L4_weakpoint_coordinates.bin').write_bytes(coord_bytes);(O/'L4_weakpoint_coordinates.asm').write_text(f' ORG ${coord:04X}\n LD BC,($DF3C)\n RET\n; Unreachable bytes retained to preserve layout.\n DB '+','.join(str(v)for v in coord_bytes[5:])+'\n')
(O/'weakpoint_contract.json').write_text(json.dumps(dict(native_positions=True,native_sizes=[[24,8],[8,24],[24,8]],native_sources=[0xd7eb,0xd806,0xd821],parent_pairs=[[132,131],[135,130],[138,129]],rear_target_enlargement_withdrawn=True,r135_direct_copy_withdrawn=True),indent=2))
for stem in ['boss_motion_fixture','verify_native_revisits','verify_cold_launcher','verify_snake_runtime','probe_l4_damage','verify_boss_pickup','verify_followers']:
 s=(R/f'scripts/{stem}_r136.mjs').read_text().replace('boss_pickup_r136','l4_openings_r137').replace('boss_motion_fixture_r136','boss_motion_fixture_r137');(R/f'scripts/{stem}_r137.mjs').write_text(s)
