from pathlib import Path
O=Path('build/fullgame/boss_guard_r94');old=b'PREPARING GAME  ';new=b'R94 PREPARING   '
for name in ['demand_loader.bin','launcher.bin']:
 p=O/name;b=p.read_bytes();assert b.count(old)==1;p.write_bytes(b.replace(old,new))
p=O/'rtype/rt.tap';b=bytearray(p.read_bytes());at=0
while at<len(b):
 n=int.from_bytes(b[at:at+2],'little');v=bytearray(b[at+2:at+2+n]).replace(old,new);c=0
 for x in v[:-1]:c^=x
 v[-1]=c;b[at+2:at+2+n]=v;at+=n+2
p.write_bytes(b)
