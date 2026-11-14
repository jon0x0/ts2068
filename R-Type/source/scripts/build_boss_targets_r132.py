from pathlib import Path
import sys,json,shutil,subprocess,re
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from pack_optimal_r87 import pack_optimal as pack;from boss_motion_assets_r60 import unpack;from build_rocket_fix import code
B=R/'build/fullgame/l4_shared_r131';O=R/'build/fullgame/boss_targets_r132';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file() and p.suffix in ['.bin','.asm','.sym','.json'] and not any(t in p.name for t in ['validation','probe','trace','.home.','expected','actual']):shutil.copy2(p,O/p.name)
b=bytearray((B/'level04_region.bin').read_bytes());image=(B/'L4_runtime_image.bin').read_bytes();entry=0xa000+len(image)
s=f''' ORG ${entry:04X}
; Only the three native weakpoints may overwrite their own invulnerable parent.
weakpoint_visibility:
 LD A,(IY+5)
 CP $3B
 JR Z,source_ok
 CP $4B
 JR Z,source_ok
 CP $5B
 JR NZ,ordinary
source_ok:
 LD A,(IY+5)
 RRCA
 RRCA
 RRCA
 RRCA
 AND $0F
 NEG
 ADD A,$86
 PUSH BC
 LD B,A
 LD A,(DE)
 CP B
 POP BC
 JR NZ,ordinary
accept:
 ; Drop only the compositor gate return; restore mapping and native source.
 POP AF
 SCF
 PUSH AF
 LD A,9
 JP $0E10
ordinary:
 JP $A22E
'''
p=O/'L4_weakpoint_visibility';p.with_suffix('.asm').write_text(s);exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';q=subprocess.run([str(exe),f'--raw={p}.bin',f'--sym={p}.sym',str(p)+'.asm'],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr
image+=p.with_suffix('.bin').read_bytes()
coords=0xa000+len(image)
coord_source=f''' ORG ${coords:04X}
 LD BC,($DF3C)
 LD A,($DF3E)
 CP 58
 JR Z,front
 CP 60
 RET NZ
 LD BC,($850D)
 INC B
 INC B
 INC B
 INC B
 RET
front:
 LD BC,($8516)
 INC C
 INC C
 INC C
 INC B
 INC B
 INC B
 RET
'''
p2=O/'L4_weakpoint_coordinates';p2.with_suffix('.asm').write_text(coord_source);q=subprocess.run([str(exe),f'--raw={p2}.bin',str(p2)+'.asm'],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr
image=bytearray(image);pat=bytes.fromhex('ed4b3cdffde1dde13e6d');at=image.rfind(pat);assert at>=0;image[at:at+4]=b'\xcd'+coords.to_bytes(2,'little')+b'\0';image+=p2.with_suffix('.bin').read_bytes();image=bytes(image)
assert 0xa000+len(image)<=0xa9c7
c=json.loads((B/'l4_shared_contract.json').read_text());ip=c['imageptr'];packet=pack(image);assert ip+len(packet)<=0x3a00,(hex(ip+len(packet)),len(packet));assert unpack(packet)==image
# Match the rear green bulb with a 24x16 target, using retired redirected round31 storage.
weak=bytearray()
for cy in range(2):
 for cx in range(3):
  weak.append(12)
  for dy in range(8):
   y=cy*8+dy;weak.append(sum(128>>k for k in range(8)if ((cx*8+k-11.5)/11.8)**2+((y-15)/15.5)**2<=1))
assert len(weak)==54
b[0xb400:0xb400+len(weak)]=weak
at=0xbb15+61*4;assert b[at:at+4]==bytes.fromhex('030121d8');b[at:at+4]=bytes.fromhex('030200d4')
assert b[0xa00:0xa03]==bytes.fromhex('c32ea2');b[0xa01:0xa03]=entry.to_bytes(2,'little');b[ip:0x3a00]=packet+bytes(0x3a00-ip-len(packet));(O/'level04_region.bin').write_bytes(b);(O/'L4_runtime_image.bin').write_bytes(image)
for name in ['LEVEL04.TAP','START04.TAP']:
 parts=[b[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[b[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',v,k)for k,v in enumerate(parts)))
(O/'weakpoint_contract.json').write_text(json.dumps(dict(entry=entry,image_end=0xa000+len(image),packed_end=ip+len(packet),parent_pairs=[[132,131],[135,130],[138,129]],native_sources=[0xd7eb,0xd83c],retired_round31_target=[0xd400,0xd436],rear_target_size=[24,16],scope='Candidate; defeat test pending'),indent=2))
s=(R/'scripts/boss_motion_fixture_r131.mjs').read_text().replace('l4_shared_r131','boss_targets_r132');(R/'scripts/boss_motion_fixture_r132.mjs').write_text(s)
s=(R/'scripts/probe_l4_weakpoints_r131.mjs').read_text().replace('l4_shared_r131','boss_targets_r132').replace('boss_motion_fixture_r131','boss_motion_fixture_r132').replace('bossUpdates<180','bossUpdates<400');(R/'scripts/probe_l4_weakpoints_r132.mjs').write_text(s)
print(O,hex(entry),hex(ip+len(packet)))

# L1 eye open-state native overlay; keep this in the existing gate allocation.
gate=""" ORG $0D01
 POP AF
 LD A,(IY+5)
 CP $11
 JP Z,$8F0B
 LD A,(DE)
 OR A
 JP Z,$8F0B
 LD ($5C82),A
 LD A,($8EB1)
 LD ($5C81),A
 DI
 CALL $09FC
 LD A,9
 OUT ($F4),A
 EI
 OR A
 RET
 ASSERT $ <= $0D27
"""
p3=O/'L1_eye_gate';p3.with_suffix('.asm').write_text(gate);q=subprocess.run([str(exe),f'--raw={p3}.bin',str(p3)+'.asm'],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr
v=bytearray((B/'level01_region.bin').read_bytes());g=p3.with_suffix('.bin').read_bytes();v[0xd01:0xd01+len(g)]=g
(O/'level01_region.bin').write_bytes(v)
# L3 has space for a dispatch around the existing compositor; only its native mounts/engine.
v=bytearray((B/'level03_region.bin').read_bytes());im=(B/'L3_runtime_image.bin').read_bytes();start=0xa000+len(im);oldpaint=int.from_bytes(v[0xa01:0xa03],'little')
helper=f""" ORG ${start:04X}
 LD A,IYH
 CP 133
 JR NZ,ordinary
 LD A,(IY+5)
 CP 4
 JR Z,publish
 CP 6
 JR Z,publish
 CP $38
 JR NZ,ordinary
publish:
 ; Cached hull already supplies the visible gun/engine image. Publish the
 ; native target without invoking a second native pixel copy through it.
 LD A,($7A9C)
 LD (DE),A
ordinary:
 LD A,$29
 JP ${oldpaint:04X}
"""
p3=O/'L3_native_targets';p3.with_suffix('.asm').write_text(helper);q=subprocess.run([str(exe),f'--raw={p3}.bin',str(p3)+'.asm'],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr
im+=p3.with_suffix('.bin').read_bytes();metas=json.loads((B/'generic_manifest.json').read_text());m3=next(x for x in metas if x['level']==3);ptr=m3['motion_ptr'];packet=pack(im);assert ptr+len(packet)<=0x3a00;v[ptr:0x3a00]=packet+bytes(0x3a00-ptr-len(packet));v[0xa01:0xa03]=start.to_bytes(2,'little');(O/'level03_region.bin').write_bytes(v);(O/'L3_runtime_image.bin').write_bytes(im);m3['motion_image_bytes']=len(im);next(x for x in metas if x['level']==4)['motion_image_bytes']=len(image);(O/'generic_manifest.json').write_text(json.dumps(metas,indent=2))
for n in [1,3]:
 v=(O/f'level{n:02d}_region.bin').read_bytes()
 for name in [f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  parts=[v[k*8192:(k+1)*8192]for k in range(8)]if name.startswith('LEVEL')else[v[p*8192+t*1024:p*8192+(t+1)*1024]for p in[0,1,4,5,6,7]for t in range(8)];(O/'rtype'/name).write_bytes(b''.join(code(('RTPAGE'if name.startswith('LEVEL')else'RTSTART')+f'{k:02X}',a,k)for k,a in enumerate(parts)))

# Publish authoritative allocation ends so later artwork/UI work cannot reuse helpers.
wmeta=json.loads((O/'walker_runtime.json').read_text());ct=json.loads((O/'l4_shared_contract.json').read_text())
ct.update(code_end=0xa000+len(image),bank1_end=ip+len(pack(image)))
(O/'l4_shared_contract.json').write_text(json.dumps(ct,indent=2))
for row in wmeta:
 if row['level']==3:row.update(runtime_bytes=len(im),immutable_end=ptr+len(pack(im)),native_target_helper=start)
 if row['level']==4:row.update(runtime_bytes=len(image),immutable_end=ip+len(pack(image)),weakpoint_helper=entry,weakpoint_coordinates=coords)
(O/'walker_runtime.json').write_text(json.dumps(wmeta,indent=2))
