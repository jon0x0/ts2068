"""Derive independently clocked normal/spread bolts from the frozen r54 build."""
from pathlib import Path
import subprocess, shutil, re, json, hashlib
from build_rocket_fix import code
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'build/fullgame/player_weapons_r54'
OUT=ROOT/'build/fullgame/projectile_clock_r55'

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 shutil.copytree(SRC/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True)
 def asm(name,file,defines=''):
  source=OUT/(name+'.asm');source.write_text(defines+(ROOT/file).read_text())
  r=subprocess.run([str(ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={OUT/(name+".bin")}',f'--sym={OUT/(name+".sym")}',str(source)],cwd=ROOT,capture_output=True,text=True)
  assert r.returncode==0,r.stdout+r.stderr
  return (OUT/(name+'.bin')).read_bytes()
 engine=asm('projectile_clock','src/projectile_clock.asm');assert len(engine)<=640
 defines=f'ENGINE_LENGTH EQU {len(engine)}\nGATEWAY EQU $9501\n'
 gate=asm('projectile_gateway','src/projectile_gateway.asm',defines)
 hits=asm('projectile_hits','src/projectile_hits.asm',defines)
 assert len(gate)==91 and len(hits)==66
 shims=[(a,asm('projectile_shim'+str(i),'src/projectile_shims.asm',f'SECTION EQU {i}\n'))for i,a in enumerate([0x190,0x1e20,0x19e3,0x9b6])]
 hooks=[(a,asm('projectile_hook'+str(i),'src/projectile_hooks.asm',defines+f'SECTION EQU {i}\n'))for i,a in enumerate([0x1928,0xfd4,0xf70,0x986,0x9de7,0x1a91,0x9554])]
 records=[]
 for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
  b=bytearray((SRC/f'{name}_region.bin').read_bytes())
  assert b[0xfbd2:0xfbd6]==bytes(4)
  assert not any(b[0xf100:0xf380])
  b[0xf100:0xf100+len(engine)]=engine
  for at,payload in shims:b[at:at+len(payload)]=payload
  for at,payload in hooks:
   if at>=0x9000:continue
   assert all(v==(0 if at==0x1928 else 255)for v in b[at:at+len(payload)]),(name,hex(at))
   b[at:at+len(payload)]=payload
  assert b[0xe39:0xe3d]==bytes.fromhex('218a7ac9')
  b[0xe39:0xe3d]=bytes.fromhex('c3281900')
  assert b[0xfb81:0xfb84]==bytes.fromhex('cd37fb')
  b[0xfb81:0xfb84]=bytes.fromhex('cd8609')
  assert b[0x1488:0x148b]==bytes.fromhex('cd000d')
  b[0x1488:0x148b]=bytes.fromhex('cdf994')
  assert b[0xa09:0xa0c]==bytes.fromhex('2100a0')
  b[0xa09:0xa0c]=bytes.fromhex('cde79d')
  if name=='boot':
   assert b[0x54f6]==0xc3 # old coarse movement below this jump is unreachable
   b[0x54f9:0x54f9+len(gate)]=gate
   b[0x5da5:0x5da5+len(hits)]=hits
   for at,payload in hooks:
    if at>=0x9000:b[at-0x4000:at-0x4000+len(payload)]=payload
   b[0xdb00:0xdbc0]=b[0xfb00:0xfbc0]
  (OUT/f'{name}_region.bin').write_bytes(b)
  tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP'
  (OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{p:02X}',b[p*8192:(p+1)*8192],p)for p in range(8)))
  records.append(dict(file=tap,level=n,sha256=hashlib.sha256(b).hexdigest()))
 for f in ['overlay.bin','overlay.sym','player_damage.bin','launcher.bin','demand_loader.sym','boss_preview.bin','boss_preview.sym','gateway.bin','gateway.sym','irq.bin','irq.sym']:shutil.copy2(SRC/f,OUT/f)
 gateway=bytearray((OUT/'gateway.bin').read_bytes())
 assert gateway[0x81:0x84]==bytes.fromhex('cd37fb')
 gateway[0x81:0x84]=bytes.fromhex('cd8609')
 (OUT/'gateway.bin').write_bytes(gateway)
 (OUT/'manifest.json').write_text(json.dumps(dict(status='r55 candidate',regions=records,projectile_engine_bytes=len(engine)),indent=2))
 print('r55 independent projectile engine',len(engine),'gateway',len(gate),'hit handoff',len(hits))
if __name__=='__main__':main()
