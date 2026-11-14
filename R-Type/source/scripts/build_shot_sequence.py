from pathlib import Path
import subprocess,shutil,json,hashlib
from build_rocket_fix import code
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'build/fullgame/clean_player_r56';OUT=ROOT/'build/fullgame/shot_sequence_r57'
def main():
 OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(SRC/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True)
 def asm(name,file,defines=''):
  source=OUT/(name+'.asm');source.write_text(defines+(ROOT/file).read_text())
  r=subprocess.run([str(ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={OUT/(name+".bin")}',f'--sym={OUT/(name+".sym")}',str(source)],cwd=ROOT,capture_output=True,text=True)
  assert r.returncode==0,r.stdout+r.stderr
  return (OUT/(name+'.bin')).read_bytes()
 player=asm('overlay','src/game_pixel_overlay_fire_latest.asm');engine=asm('projectile_clock','src/projectile_continuous.asm')
 assert len(player)<=2432 and len(engine)<=640
 defines=f'ENGINE_LENGTH EQU {len(engine)}\nGATEWAY EQU $9501\n'
 gateway=asm('projectile_gateway','src/projectile_gateway_restore.asm',defines);assert len(gateway)==96
 irq=asm('irq','src/game_pixel_irq_serial.asm');irq_exit=asm('irq_exit','src/boss_irq_exit_serial.asm')
 guards=[(a,asm('irq_guard'+str(i),'src/irq_source_guard.asm',f'SECTION EQU {i}\n'))for i,a in enumerate([0x8e2,0x911])]
 hooks=[(a,asm('projectile_hook'+str(i),'src/projectile_continuous_hooks.asm',defines+f'SECTION EQU {i}\n'))for i,a in enumerate([0x1928,0xfd4,0xf70,0x986,0x9de7,0x1a91,0x19fc])]
 records=[]
 for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
  b=bytearray((SRC/f'{name}_region.bin').read_bytes());b[0xe400:0xed80]=bytes([255])*2432;b[0xe400:0xe400+len(player)]=player
  for at,payload in guards:
   assert all(v==255 for v in b[at:at+len(payload)])
   b[at:at+len(payload)]=payload
  b[0x971:0x971+len(irq_exit)]=irq_exit;b[0xfd20:0xfd48]=irq
  b[0xf100:0xf380]=bytes(640);b[0xf100:0xf100+len(engine)]=engine
  for at,payload in hooks:
   if at<0x9000:b[at:at+len(payload)]=payload
  if name=='boot':
   b[0xdd20:0xdd48]=irq
   b[0x54f9:0x54f9+len(gateway)]=gateway
   for at,payload in hooks:
    if at>=0x9000:b[at-0x4000:at-0x4000+len(payload)]=payload
  (OUT/f'{name}_region.bin').write_bytes(b);tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP'
  (OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{p:02X}',b[p*8192:(p+1)*8192],p)for p in range(8)))
  records.append(dict(file=tap,level=n,sha256=hashlib.sha256(b).hexdigest()))
 for file in ['launcher.bin','demand_loader.sym','boss_preview.bin','boss_preview.sym','gateway.bin','gateway.sym','player_damage.bin']:
  shutil.copy2(SRC/file,OUT/file)
 (OUT/'manifest.json').write_text(json.dumps(dict(status='r57 candidate',overlay_bytes=len(player),projectile_bytes=len(engine),regions=records),indent=2))
 print('r57',len(player),'player bytes;',len(engine),'projectile bytes')
if __name__=='__main__':main()
