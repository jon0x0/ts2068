from pathlib import Path
import shutil,json,hashlib,zipfile
R=Path.cwd();B=R/'build/fullgame/l4_openings_r137';O=R/'build/fullgame/highscore_r138';O.mkdir(exist_ok=True)
for p in B.iterdir():
 if p.is_file() and p.suffix in ['.bin','.json','.sym','.asm']:shutil.copy2(p,O/p.name)
shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
old=bytes.fromhex('cd9076cd0000af3276be');new=bytes.fromhex('cdd219cd0000af3276be');changes=[]
for p in O.glob('level??_region.bin'):
 b=p.read_bytes();assert b[0x52ef:0x52f9]==old;p.write_bytes((b[:0x52ef]+new+b[0x52f9:]).replace(b'R137',b'R138'))
for p in (O/'rtype').glob('*.TAP'):
 src=p.read_bytes();out=bytearray();pos=0;count=0
 while pos<len(src):
  n=int.from_bytes(src[pos:pos+2],'little');v=bytearray(src[pos+2:pos+2+n]);assert not __import__('functools').reduce(int.__xor__,v)
  if v[0]==255:
   data=bytes(v[1:-1]);count+=data.count(old);data=data.replace(old,new).replace(b'R137',b'R138');v=bytearray([255])+data;v.append(__import__('functools').reduce(int.__xor__,v))
  out+=len(v).to_bytes(2,'little')+v;pos+=n+2
 if bytes(out)!=src:p.write_bytes(out)
 if count:changes.append(dict(file=p.name,calls=count))
assert sum(q['calls']for q in changes)==10,changes
(O/'highscore_contract.json').write_text(json.dumps(dict(caller=0x92ef,old=0x7690,new=0x19d2,scope='Post-death caller uses shared 17-byte score restore, now calls menu restore and resident 0073 attribute fill; no new allocations',tapes=changes),indent=2))
s=(R/'scripts/boss_motion_fixture_r137.mjs').read_text().replace('l4_openings_r137','highscore_r138');(R/'scripts/boss_motion_fixture_r138.mjs').write_text(s)
print(changes)

for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R137',b'R138'))


# Replace the existing 17-byte score restore in place: restore standard mode,
# initialise standard attributes using the resident fill utility, draw scores.
a=bytes.fromhex('3e0bd3f4af32f03fd3ff3e09d3f4c39076');v=bytes.fromhex('cd66142100580100033e47cd7300c39076');assert len(a)==len(v)==17
for p in O.glob('level??_region.bin'):
 b=p.read_bytes();assert b[0x19d2:0x19e3]==a;p.write_bytes(b[:0x19d2]+v+b[0x19e3:])
for p in (O/'rtype').glob('*.TAP'):
 src=p.read_bytes();out=bytearray();pos=0
 while pos<len(src):
  n=int.from_bytes(src[pos:pos+2],'little');q=bytearray(src[pos+2:pos+2+n])
  if q[0]==255:
   data=bytes(q[1:-1]).replace(a,v);q=bytearray([255])+data;q.append(__import__('functools').reduce(int.__xor__,q))
  out+=len(q).to_bytes(2,'little')+q;pos+=n+2
 p.write_bytes(out)
