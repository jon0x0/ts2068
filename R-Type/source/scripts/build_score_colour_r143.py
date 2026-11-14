from pathlib import Path
import shutil,json,functools
R=Path.cwd();B=R/'build/fullgame/l4_health_r142';O=R/'build/fullgame/score_colour_r143';O.mkdir(exist_ok=True)
for p in B.iterdir():
 if p.is_file() and p.suffix in ['.bin','.asm','.sym','.json'] and not any(k in p.name for k in ['validation','summary','manifest']):shutil.copy2(p,O/p.name)
shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
old=bytes.fromhex('cd66142100580100033e47cd7300c39076');new=bytes.fromhex('cd6614cdcb76c39076')+bytes(8)
for p in O.glob('level??_region.bin'):
 b=p.read_bytes();assert b.count(old)==1;p.write_bytes(b.replace(old,new))
for p in (O/'rtype').glob('*.TAP'):
 s=p.read_bytes();v=bytearray();at=0
 while at<len(s):
  n=int.from_bytes(s[at:at+2],'little');q=s[at+2:at+2+n];assert functools.reduce(int.__xor__,q)==0
  data=q[:-1].replace(old,new).replace(b'R142',b'R143');q=data+bytes([functools.reduce(int.__xor__,data)]);v+=len(q).to_bytes(2,'little')+q;at+=n+2
 p.write_bytes(v)
for n in ['launcher.bin','demand_loader.bin']:
 p=O/n;p.write_bytes(p.read_bytes().replace(b'R142',b'R143'))
s=(R/'scripts/boss_motion_fixture_r142.mjs').read_text().replace('l4_health_r142','score_colour_r143');(R/'scripts/boss_motion_fixture_r143.mjs').write_text(s)
s=(R/'scripts/verify_highscore_r138.mjs').read_text().replace('boss_motion_fixture_r138','boss_motion_fixture_r143').replace('f-boot<840','u<20')
s=s.replace("if(level===7)fs.writeFileSync", "const attrs=()=>Array.from(m.ram.slice(0x5800,0x5b00));const first=attrs();assert(first.includes(0x47));assert(first.some(v=>v>=0x41&&v<=0x46));call(m,0x76cb);const second=attrs();assert(second.some((v,i)=>v!==first[i]));assert(second.every((v,i)=>i%64<32?v===0x47:v>=0x41&&v<=0x47));if(level===7)fs.writeFileSync")
(R/'scripts/verify_highscore_r143.mjs').write_text(s)

