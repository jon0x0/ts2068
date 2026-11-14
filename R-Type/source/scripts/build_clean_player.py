"""Remove stale unowned scenery from the independent player copy footprint."""
from pathlib import Path
import shutil,subprocess,json,hashlib
from build_rocket_fix import code
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'build/fullgame/projectile_clock_r55'
OUT=ROOT/'build/fullgame/clean_player_r56'
def main():
 OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(SRC/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True)
 r=subprocess.run([str(ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={OUT/"overlay.bin"}',f'--sym={OUT/"overlay.sym"}',str(ROOT/'src/game_pixel_overlay_clean.asm')],cwd=ROOT,capture_output=True,text=True)
 assert r.returncode==0,r.stdout+r.stderr
 engine=(OUT/'overlay.bin').read_bytes();assert len(engine)<=0x980
 records=[]
 for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
  b=bytearray((SRC/f'{name}_region.bin').read_bytes())
  b[0xe400:0xed80]=bytes([255])*0x980;b[0xe400:0xe400+len(engine)]=engine
  (OUT/f'{name}_region.bin').write_bytes(b)
  tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP'
  (OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{p:02X}',b[p*8192:(p+1)*8192],p)for p in range(8)))
  records.append(dict(file=tap,level=n,sha256=hashlib.sha256(b).hexdigest()))
 for file in ['launcher.bin','demand_loader.sym','boss_preview.bin','boss_preview.sym','gateway.bin','gateway.sym','irq.bin','irq.sym','player_damage.bin','projectile_clock.bin','projectile_clock.sym']:
  shutil.copy2(SRC/file,OUT/file)
 (OUT/'manifest.json').write_text(json.dumps(dict(status='r56 candidate',overlay_bytes=len(engine),regions=records),indent=2))
 print('r56 player renderer',len(engine),'bytes; independent projectiles retained')
if __name__=='__main__':main()
