from pathlib import Path
import shutil,subprocess,sys,functools,json
R=Path.cwd();B=R/'build/fullgame/preparing_r144';O=R/'build/fullgame/visible_hits_r145';O.mkdir(exist_ok=True)
for p in B.iterdir():
 if p.is_file() and p.suffix in ['.bin','.asm','.sym','.json'] and not any(k in p.name for k in ['validation','summary','release_manifest','trace']):shutil.copy2(p,O/p.name)
shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
s=(B/'projectile_clock.asm').read_text();assert s.count('CALL $C0E4')==3;s=s.replace('CALL $C0E4','CALL visible_owner').replace('        ASSERT $ <= $5B5B','')
s+='''
visible_owner:
 CALL $C0E4 ; original lookup computes DE=7E00+cell; BC/HL stay intact
 LD A,E
 ADD A,$80
 LD E,A
 LD A,D
 ADC A,$7A
 LD D,A
 LD A,$8D
 OUT ($F4),A
 LD A,(DE)
 LD E,A
 LD A,$0D
 OUT ($F4),A
 LD A,E
 RET
 ASSERT $ <= $5B50
''' ;p=O/'projectile_clock.asm';exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
p.write_text(s);q=subprocess.run([str(exe),f'--raw={O}/projectile_clock.bin',f'--sym={O}/projectile_clock.sym',str(p)],capture_output=True,text=True);assert not q.returncode,q.stdout+q.stderr
e=(O/'projectile_clock.bin').read_bytes().ljust(640,b'\0');(O/'projectile_clock.bin').write_bytes(e);print(len(e),hex(0x5880+len(e)));oldlen=640;assert len(e)<=0x2d0
sys.path.insert(0,'scripts');from build_rocket_fix import code
for n in range(1,9):
 p=O/f'level{n:02d}_region.bin';b=bytearray((B/p.name).read_bytes());assert b[0xf100:0xf380]==(B/'projectile_clock.bin').read_bytes();assert n==5 or not any(b[0xf380:0xf100+len(e)]);b[0xf100:0xf100+len(e)]=e;p.write_bytes(b)
 for name in [f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[k*8192+t*1024:k*8192+(t+1)*1024]for k in [0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
p=O/'rtype/RTCORE.TAP';s=p.read_bytes();v=bytearray();at=0;changes=0
while at<len(s):
 n=int.from_bytes(s[at:at+2],'little');q=s[at+2:at+2+n];data=q[:-1]
 for pat in [bytes.fromhex('2100f1118058018002'),bytes.fromhex('2180581100f1018002')]:
  changes+=data.count(pat);data=data.replace(pat,pat[:-2]+len(e).to_bytes(2,'little'))
 v+=n.to_bytes(2,'little')+data+bytes([functools.reduce(int.__xor__,data)]);at+=n+2
assert changes==2;p.write_bytes(v)
for name in ['launcher.bin','demand_loader.bin']:
 p=O/name;p.write_bytes(p.read_bytes().replace(b'R144',b'R145'))
p=O/'rtype/rt.tap';s=p.read_bytes();at=0;v=bytearray()
while at<len(s):
 n=int.from_bytes(s[at:at+2],'little');data=s[at+2:at+1+n].replace(b'R144',b'R145');v+=n.to_bytes(2,'little')+data+bytes([functools.reduce(int.__xor__,data)]);at+=n+2
p.write_bytes(v)
s=(R/'scripts/boss_motion_fixture_r144.mjs').read_text().replace('preparing_r144','visible_hits_r145');(R/'scripts/boss_motion_fixture_r145.mjs').write_text(s)
(O/'collision_contract.json').write_text(json.dumps(dict(old_engine_bytes=640,new_engine_bytes=len(e),lookup='visible_owner in projectile_clock.sym',retained_owner_map=0xf880,irq_vector=0x5b5b,rule='Normal/spread IRQ projectile queries use the same published-frame owner map as the player; original native damage/armor/weak-point rules unchanged; no rectangle inflation'),indent=2))
