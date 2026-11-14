from pathlib import Path
import subprocess,json,shutil,hashlib
from build_rocket_fix import code
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/material_game_r49'
def main():
 source=ROOT/'build/fullgame/compiled_game_r48';OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(source/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True)
 asm=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';r=subprocess.run([str(asm),f'--raw={OUT/"compositor.bin"}',f'--sym={OUT/"compositor.sym"}',str(ROOT/'src/bellmite_material_compositor.asm')],cwd=ROOT,capture_output=True,text=True);(OUT/'assembly.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stdout+r.stderr;engine=(OUT/'compositor.bin').read_bytes()
 low_source="""        ORG $0D00
        RET
        POP AF
        LD A,(DE)
        AND A
        JP Z,$8F0B
        CP $80
        JR C,fallback
        CP $DC
        JR NC,fallback
        LD ($5C82),A
        LD A,($8EB1)
        LD ($5C81),A
        DI
        LD A,$19
        OUT ($F4),A
        CALL $88EB
        LD A,9
        OUT ($F4),A
        EI
        JP NC,fallback
        OR A
        RET
fallback:
        LD A,(DE)
        AND A
        JP $8EDA
        ASSERT $ == $0D2F
        XOR A
        LD ($5C82),A
        LD A,($7A9C)
        LD (DE),A
        LD A,($8EB1)
        LD ($5C81),A
        JP $FD08
        ASSERT $ == $0D40
"""
 (OUT/'gate.asm').write_text(low_source);r=subprocess.run([str(asm),f'--raw={OUT/"gate.bin"}',str(OUT/'gate.asm')],cwd=ROOT,capture_output=True,text=True);assert not r.returncode,r.stdout+r.stderr;low=(OUT/'gate.bin').read_bytes();assert len(low)==64
 records=[]
 for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
  b=bytearray((source/f'{name}_region.bin').read_bytes())
  if n==5:
   b[0xd00:0xd40]=low;b[0x14f4:0x14f8]=bytes.fromhex('f3 c3 2f 0d')
   b[0x88eb:0x8c00]=bytes([255])*(0x8c00-0x88eb);b[0x88eb:0x88eb+len(engine)]=engine
  assert len(b)==65536;(OUT/f'{name}_region.bin').write_bytes(b);tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP';(OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{p:02X}',b[p*8192:(p+1)*8192],p)for p in range(8)));records.append(dict(file=tap,level=n,sha256=hashlib.sha256(b).hexdigest()))
 for f in ['launcher.bin','demand_loader.sym','boss_preview.bin','boss_preview.sym','overlay.bin','overlay.sym','gateway.bin','gateway.sym','irq.bin','irq.sym','native_level5.bin','enemy_palette.bin']:shutil.copy2(source/f,OUT/f)
 native=bytearray((source/'native_level5.bin').read_bytes());stage=(OUT/'level05_region.bin').read_bytes();native[0xc000:0xf87c]=stage[0xa000:0xd87c];(OUT/'native_level5.bin').write_bytes(native)
 (OUT/'manifest.json').write_text(json.dumps(dict(status='Compiled Bellmite/pixel gameplay candidate; validation pending',regions=records,compositor_bytes=len(engine),precompiled_row_pair_bytes=1536,selected_game_keys_preserved=True),indent=2));print('Compiled game',len(engine))
if __name__=='__main__':main()

