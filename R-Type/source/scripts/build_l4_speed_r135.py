from pathlib import Path
import shutil,sys,json
sys.path.insert(0,'scripts')
from build_rocket_fix import code
R=Path.cwd();B=R/'build/fullgame/snake_r134';O=R/'build/fullgame/l4_speed_r135';O.mkdir(exist_ok=True)
for p in B.iterdir():
 if p.is_file() and p.suffix in ['.bin','.asm','.sym','.json']:shutil.copy2(p,O/p.name)
shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
from pack_optimal_r87 import pack_optimal
from boss_motion_assets_r60 import unpack
b=bytearray((B/'level04_region.bin').read_bytes());ct=json.loads((B/'l4_shared_contract.json').read_text());img=bytearray((B/'L4_runtime_image.bin').read_bytes())
# Preserve incoming prior-cell owner in the otherwise unused src slot.
assert img.count(bytes.fromhex('22fba3'))==1;img=img.replace(bytes.fromhex('22fba3'),bytes.fromhex('32fba3'))
pat=bytes.fromhex('3a03a4b720');at=img.find(pat,0x292,0x2d0);assert at>=0;img[at:at+5]=bytes.fromhex('cdb0db0020')
helper=bytes.fromhex('3afba3b7c8473a03a4b8c9');sc=json.loads((B/'snake_contract.json').read_text());raw=(B/'L4_snake_art.bin').read_bytes();payload=pack_optimal(raw[216:]+helper);assert len(payload)<=0xb567-0xb474
b[0xb474:0xb567]=payload+bytes(0xb567-0xb474-len(payload));pat=bytes.fromhex('2174d411d8da01cb00');p0=img.find(pat);assert p0>=0;img[p0+7:p0+9]=len(payload).to_bytes(2,'little')
packet=pack_optimal(bytes(img));assert ct['imageptr']+len(packet)<=0x3a00
b[ct['imageptr']:0x3a00]=packet+bytes(0x3a00-ct['imageptr']-len(packet));(O/'L4_runtime_image.bin').write_bytes(img);(O/'level04_region.bin').write_bytes(b)
for name in ['LEVEL04.TAP','START04.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)]
 (O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
sc['packets'][1][1]=0xb474+len(payload);sc['packed_end']=ct['imageptr']+len(packet);(O/'snake_contract.json').write_text(json.dumps(sc,indent=2));ct['bank1_end']=ct['imageptr']+len(packet);ct['direct_cell_helper']=[0xdbb0,0xdbbb];(O/'l4_shared_contract.json').write_text(json.dumps(ct,indent=2))
(O/'speed_contract.json').write_text(json.dumps(dict(purpose='Direct prepared-cell copy when incoming prior-owner is zero; compositor retained for overlaps',packed_end=ct['imageptr']+len(packet)),indent=2))
for stem in ['boss_motion_fixture','probe_l4_damage','verify_native_revisits','verify_cold_launcher','verify_snake_runtime','profile_l4_stars']:
 s=(R/f'scripts/{stem}_r134.mjs').read_text().replace('snake_r134','l4_speed_r135').replace('boss_motion_fixture_r134','boss_motion_fixture_r135');(R/f'scripts/{stem}_r135.mjs').write_text(s)
