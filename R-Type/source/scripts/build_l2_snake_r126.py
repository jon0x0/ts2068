from pathlib import Path
import json,shutil,sys,re,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from build_rocket_fix import code
B=R/'build/fullgame/l2_scroll_projectile_r125';O=R/'build/fullgame/l2_snake_parts_r126';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.json','.sym','.asm']and not any(s in p.name for s in ['validation','approach','trace','probe','mismatch','.home.','native_jump','final_l2']):shutil.copy2(p,O/p.name)
ct=json.loads((B/'L2_actor_contract.json').read_text());image=bytearray((B/'L2_runtime_image.bin').read_bytes());offset=ct['extension']['id_map']-0xa000;assert image[offset+22]==198 and image[offset+23]==199;image[offset+22]=199
b=bytearray((B/'level02_region.bin').read_bytes());meta=json.loads((B/'generic_manifest.json').read_text());m=next(v for v in meta if v['level']==2);ip=m['motion_ptr'];v=pack(image);assert ip+len(v)<=0x3848;b[ip:0x3848]=v.ljust(0x3848-ip,b'\0');(O/'L2_runtime_image.bin').write_bytes(image)
# Version label changes in diagnostic heading only; preserve its code/data addresses.
assert b'R125 DEBUG'in b[0x8000:0x82b3];b[0x8000:0x82b3]=b[0x8000:0x82b3].replace(b'R125 DEBUG',b'R126 DEBUG')
(O/'level02_region.bin').write_bytes(b)
for name in ['LEVEL02.TAP','START02.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R125 PREPARING  ',b'R126 PREPARING  '))
p=O/'rtype/rt.tap';v=bytearray(p.read_bytes());at=0
while at<len(v):
 n=int.from_bytes(v[at:at+2],'little');block=bytearray(v[at+2:at+2+n]).replace(b'R125 PREPARING  ',b'R126 PREPARING  ');check=0
 for x in block[:-1]:check^=x
 block[-1]=check;v[at+2:at+2+n]=block;at+=n+2
p.write_bytes(v)
(O/'snake_parts_contract.json').write_text(json.dumps({'id_map':ct['extension']['id_map'],'native_body_ids':[22,23],'body_id':199,'arcade_body':'cel2450 palette5, export frame02','head_tail_ids':{str(n):image[offset+n]for n in range(25,31)},'runtime_changes':[{'offset':offset+22,'before':198,'after':199}],'motion_packed_end':ip+len(pack(image)),'no_animation_clock_change':True},indent=2))
for stem in ['boss_motion_fixture','verify_cold_l2_fire','verify_native_revisits','verify_l2_boss_revisits','verify_l2_decode','verify_l2_tiles','trace_l2_reveal','verify_palette_missile']:
 p=R/f'scripts/{stem}_r125.mjs';s=p.read_text(encoding='utf-8-sig').replace('l2_scroll_projectile_r125','l2_snake_parts_r126').replace('boss_motion_fixture_r125','boss_motion_fixture_r126');(R/f'scripts/{stem}_r126.mjs').write_text(s)
print('Single runtime mapping-byte change',hex(offset+22),'198 -> 199; packed end',hex(ip+len(pack(image))))

