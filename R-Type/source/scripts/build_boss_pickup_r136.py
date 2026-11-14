from pathlib import Path
import json,shutil,sys,functools,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
B=R/'build/fullgame/l4_speed_r135';O=R/'build/fullgame/boss_pickup_r136';O.mkdir(exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in ['.bin','.asm','.sym','.json']:shutil.copy2(p,O/p.name)
shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
def blocks(p):
 d=p.read_bytes();out=[];a=0
 while a<len(d):
  n=int.from_bytes(d[a:a+2],'little');v=d[a+2:a+2+n];assert functools.reduce(int.__xor__,v,0)==0
  if v[0]==255:out.append(v[1:-1])
  a+=n+2
 return b''.join(out)
core=bytearray(blocks(B/'rtype/RTCORE.TAP'))
patches=[(0x972c,bytes.fromhex('e603'),bytes.fromhex('e600')),(0x99ec,bytes.fromhex('2c3a897ae603fe03200321da83'),bytes.fromhex('2d2d2d7dfeda300321e0830000'))]
for addr,old,new in patches:
 assert len(old)==len(new) and core[addr-0x8000:addr-0x8000+len(old)]==old,(hex(addr),core[addr-0x8000:addr-0x8000+len(old)].hex())
 core[addr-0x8000:addr-0x8000+len(old)]=new
(O/'rtype/RTCORE.TAP').write_bytes(b''.join(code(f'RTCORE{k:02X}',core[k*1024:(k+1)*1024],k)for k in range(22)))
src=""" ORG $01C8
 CALL $8BAE
 LD A,2
 LD ($7AC1),A
 XOR A
 LD ($7AC2),A
 LD A,($7AA1)
 ADD A,4
 LD ($7AC3),A
 LD A,($7AA2)
 LD ($7AC4),A
 LD A,2
 LD ($7AC5),A
 XOR A
 LD ($7AC6),A
 LD A,($7AA1)
 ADD A,6
 LD ($7AC7),A
 LD A,($7AA2)
 LD ($7AC8),A
 RET
 ASSERT $ <= $0200
"""
(O/'boss_pickup.asm').write_text(src);q=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={O/"boss_pickup.bin"}',str(O/'boss_pickup.asm')],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr;helper=(O/'boss_pickup.bin').read_bytes()
for name in ['boot']+[f'level{n:02d}'for n in range(1,9)]:
 b=bytearray((B/f'{name}_region.bin').read_bytes())
 for addr,old,new in patches:
  off=addr-0x4000;assert b[off:off+len(old)]==old;b[off:off+len(old)]=new
 if name=='level04':
  assert all(v==255 for v in b[0x1c8:0x1c8+len(helper)]);b[0x1c8:0x1c8+len(helper)]=helper;at=b.find(bytes.fromhex('cdae8b'),0x1fd4,0x1ff7);assert at>=0;b[at:at+3]=bytes.fromhex('cdc801')
 (O/f'{name}_region.bin').write_bytes(b)
 if name!='boot':
  n=int(name[-2:]);(O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
  parts=[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in [0,1,4,5,6,7]for t in range(8)]
  (O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',v,k)for k,v in enumerate(parts)))
(O/'follower_contract.json').write_text(json.dumps(dict(patches=[dict(address=a,old=b.hex(),new=c.hex())for a,b,c in patches],pickup_level=4,pickup_type=2,pickup_count=2,pickup_offsets=[4,6],pickup_helper=[0x1c8,0x1c8+len(helper)],boss_shortcut_only=True,force_recall_tick_divisor_before=4,force_recall_tick_divisor_after=1,bit_history_lag_before=3,bit_history_lag_after=1),indent=2))
for stem in ['boss_motion_fixture','verify_native_revisits','verify_cold_launcher','verify_snake_runtime','probe_l4_damage']:
 s=(R/f'scripts/{stem}_r135.mjs').read_text().replace('l4_speed_r135','boss_pickup_r136').replace('boss_motion_fixture_r135','boss_motion_fixture_r136');(R/f'scripts/{stem}_r136.mjs').write_text(s)
