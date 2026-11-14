from pathlib import Path
import subprocess,json,shutil,hashlib
from build_rocket_fix import code
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/compiled_game_r48'
def main():
 source=ROOT/'build/fullgame/pixel_game_r47';OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(source/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True)
 asm=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';r=subprocess.run([str(asm),f'--raw={OUT/"compositor.bin"}',f'--sym={OUT/"compositor.sym"}',str(ROOT/'src/bellmite_compiled.asm')],cwd=ROOT,capture_output=True,text=True);(OUT/'assembly.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stdout+r.stderr;engine=(OUT/'compositor.bin').read_bytes();records=[]
 for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
  b=bytearray((source/f'{name}_region.bin').read_bytes())
  if n==5:
   pairs=bytearray();flipped=bytearray();palette=bytes(b[0x8c00:0x8d80]);assert len(palette)==384
   for cell in range(48):
    for y in range(8):
     px=b[0xd3f1+cell*9+1+y];attr=palette[cell*8+y];pairs+=bytes([px,attr]);flipped+=bytes([int(f'{px:08b}'[::-1],2),attr])
   assert len(pairs)==len(flipped)==768
   b[0x88eb:0x8c00]=bytes([255])*(0x8c00-0x88eb);b[0x88eb:0x88eb+len(engine)]=engine;b[0x8c00:0x8f00]=pairs;b[0x8f00:0x8f10]=bytes(16);b[0xf380:0xf680]=flipped
   assert all(v in (5,255) for v in b[0xd30:0xd3a]);b[0xd30:0xd3a]=bytes.fromhex('f3 3a b1 8e 32 81 5c c3 08 fd')
   assert b[0x14f4:0x14f8]==bytes.fromhex('f3 c3 08 fd');b[0x14f4:0x14f8]=bytes.fromhex('c3 30 0d 00')
  assert len(b)==65536;(OUT/f'{name}_region.bin').write_bytes(b);tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP';(OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{p:02X}',b[p*8192:(p+1)*8192],p)for p in range(8)));records.append(dict(file=tap,level=n,sha256=hashlib.sha256(b).hexdigest()))
 for f in ['launcher.bin','demand_loader.sym','boss_preview.bin','boss_preview.sym','overlay.bin','overlay.sym','gateway.bin','gateway.sym','irq.bin','irq.sym','native_level5.bin','enemy_palette.bin']:shutil.copy2(source/f,OUT/f)
 native=bytearray((source/'native_level5.bin').read_bytes());stage=(OUT/'level05_region.bin').read_bytes();native[0xc000:0xf87c]=stage[0xa000:0xd87c];(OUT/'native_level5.bin').write_bytes(native)
 (OUT/'manifest.json').write_text(json.dumps(dict(status='Compiled Bellmite/pixel gameplay candidate; validation pending',regions=records,compositor_bytes=len(engine),precompiled_row_pair_bytes=1536,selected_game_keys_preserved=True),indent=2));print('Compiled game',len(engine))
if __name__=='__main__':main()

