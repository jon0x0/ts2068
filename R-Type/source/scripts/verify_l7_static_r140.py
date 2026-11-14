from pathlib import Path
import json,sys,numpy as np,zipfile,hashlib
R=Path.cwd();sys.path.insert(0,'scripts');from boss_motion_assets_r60 import unpack
O=R/'build/fullgame/l7_all_choices_r140';B=R/'build/fullgame/highscore_r138';b=(O/'level07_region.bin').read_bytes();old=(B/'level07_region.bin').read_bytes();ct=json.loads((O/'l7_choices_contract.json').read_text());w=next(q for q in json.loads((O/'walker_runtime.json').read_text())if q['level']==7);t=w['preload_table'];got=bytearray(8448)
for k in range(b[t]):
 ptr=int.from_bytes(b[t+1+k*4:t+3+k*4],'little');dest=int.from_bytes(b[t+3+k*4:t+5+k*4],'little')-0xb200;v=unpack(b[ptr:]);assert dest>=0 and dest+len(v)<=len(got);got[dest:dest+len(v)]=v
raw=(O/'L7_runtime_art.bin').read_bytes();cache=(O/'L7_expected_cache.bin').read_bytes();assert got[:3136]==raw[::2]+raw[1::2];assert got[3584:]==cache[::2]+cache[1::2];assert unpack(b[ct['imageptr']:])==(O/'L7_runtime_image.bin').read_bytes();assert b[0xd300:0xd800]==old[0xd300:0xd800];assert b[0xd800:0xd910]==old[0xd800:0xd910];assert b[0x1c8:0x200]==old[0x1c8:0x200]
# Audit every native authoring stream after repacking; descriptor bounds and empty cells.
l=json.loads((R/'build/fullgame/foundation/manifest.json').read_text())['levels'][6];mem=bytes(0xc000)+b[0xa000:0xe000];checked=[]
for q in json.loads((O/'native_mask_contract.json').read_text())['entries']:
 a=l['enemy_descriptors_start']+(q['id']-1)*4;ww,hh=mem[a:a+2];p=int.from_bytes(mem[a+2:a+4],'little');start=p
 for _ in range(ww*hh):
  tag=mem[p];p+=1 if tag==54 else 9
 assert start==q['ptr'] and p-start==q['bytes'];checked.append(q['id'])
for n in range(1,9):
 if n!=7:assert (O/f'level{n:02d}_region.bin').read_bytes()==(B/f'level{n:02d}_region.bin').read_bytes()
assert (O/'rtype/RTCORE.TAP').read_bytes()==(B/'rtype/RTCORE.TAP').read_bytes()
files=0
for p in (O/'rtype').glob('*.TAP'):
 src=p.read_bytes();pos=0;payload=[]
 while pos<len(src):
  n=int.from_bytes(src[pos:pos+2],'little');v=src[pos+2:pos+2+n];assert __import__('functools').reduce(int.__xor__,v)==0
  if v[0]==255:payload.append(v[1:-1])
  pos+=n+2
 assert pos==len(src)
 if p.name=='LEVEL07.TAP':assert b''.join(payload)==b
 if p.name=='START07.TAP':assert b''.join(payload)==b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7])
 files+=1
(O/'static_validation.json').write_text(json.dumps(dict(passed=True,all_six_exports=True,raw_bytes=len(raw),cache_bytes=len(cache),combined_stream_bytes=len(got),packed_end=ct['end'],native_masks=checked,script_storage_unchanged=True,im2_unchanged=True,other7levels_unchanged=True,CORE_unchanged=True,tape_files=files),indent=2));print('static contracts PASS',ct['end'],files)
