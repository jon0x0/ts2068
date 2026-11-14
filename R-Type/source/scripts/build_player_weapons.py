from pathlib import Path
import subprocess,shutil,json,hashlib
from build_rocket_fix import code
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'build/fullgame/boss_speed_r53';OUT=ROOT/'build/fullgame/player_weapons_r54'
def main():
 OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(SRC/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True)
 def asm(name,file):
  r=subprocess.run([str(ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={OUT/(name+".bin")}',f'--sym={OUT/(name+".sym")}',str(ROOT/file)],capture_output=True,text=True,cwd=ROOT);assert not r.returncode,r.stdout+r.stderr;return(OUT/(name+'.bin')).read_bytes()
 engine=asm('overlay','src/game_pixel_overlay_masked.asm');damage=asm('player_damage','src/player_damage.asm');assert len(engine)<=0x980
 steps=[(a,asm(n,'src/'+n+'.asm'))for a,n in [(0x19e3,'projectile_swept_step'),(0x9b6,'projectile_swept_check'),(0x1e20,'projectile_swept_next'),(0x190,'projectile_swept_return')]]
 records=[]
 for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
  b=bytearray((SRC/f'{name}_region.bin').read_bytes());assert not any(b[0xf080:0xf100]);b[0xe400:0xed80]=bytes([255])*0x980;b[0xe400:0xe400+len(engine)]=engine;b[0xf080:0xf080+len(damage)]=damage
  for at,payload in steps:
   assert all(v==255 for v in b[at:at+len(payload)]);b[at:at+len(payload)]=payload
  if name=='boot':
   assert b[0x5dba:0x5dbd]==bytes.fromhex('cdd1c3');b[0x5dba:0x5dbd]=bytes.fromhex('cde319');assert b[0x5dbd]==0xf5;b[0x5dbe:0x5dc1]=bytes.fromhex('c3ca9d')
  (OUT/f'{name}_region.bin').write_bytes(b);tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP';(OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{p:02X}',b[p*8192:(p+1)*8192],p)for p in range(8)));records.append(dict(file=tap,level=n,sha256=hashlib.sha256(b).hexdigest()))
 for f in ['launcher.bin','demand_loader.sym','boss_preview.bin','boss_preview.sym','gateway.bin','gateway.sym','irq.bin','irq.sym']:shutil.copy2(SRC/f,OUT/f)
 (OUT/'manifest.json').write_text(json.dumps(dict(status='r54 candidate',regions=records,overlay_bytes=len(engine),damage_bytes=len(damage)),indent=2));print(len(engine),len(damage))
if __name__=='__main__':main()
