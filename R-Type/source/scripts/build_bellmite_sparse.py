"""Approved planned-edge assets and stage-five masked retained composition."""
import json,shutil,subprocess,hashlib,re
from pathlib import Path
from build_rocket_fix import code
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/bellmite_sparse_r46'

def main():
    source=ROOT/'build/fullgame/bellmite_orbs_r44';OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(source/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True)
    assembler=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
    def assemble(name,text):
        p=OUT/f'{name}.asm';p.write_text(text);r=subprocess.run([str(assembler),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],cwd=ROOT,capture_output=True,text=True);p.with_suffix('.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stdout+r.stderr;return p.with_suffix('.bin').read_bytes()
    engine=assemble('compositor',(ROOT/'src/bellmite_sparse.asm').read_text())
    lookup=assemble('gate_wrapper',"""        ORG $5BAA
        PUSH AF
        LD A,($0D70)
        CP '5'
        JP Z,$0D01
        POP AF
        LD A,(DE)
        AND A
        JP Z,$8F0B
        JP $8EDA
        ASSERT $ <= $5BE0
""")
    low=assemble('gate_stage5',"""        ORG $0D00
        RET
        POP AF
        LD A,(DE)
        AND A
        JP Z,$8F0B
        CP $80
        JR C,fallback
        CP $DC
        JR NC,fallback
        LD A,H
        CP $EF
        JR C,fallback
        LD A,($8EB1)
        LD ($5C81),A
        DI
        LD A,$19
        OUT ($F4),A
        CALL $88EB
        LD A,9
        OUT ($F4),A
        EI
        OR A
        RET
fallback:
        LD A,(DE)
        AND A
        JP $8EDA
        ASSERT $ <= $0D40
""")
    paint=assemble('paint_wrapper','''        ORG $FD08
        LD A,$19
        OUT ($F4),A
        CALL $88EE
        PUSH AF
        LD A,9
        OUT ($F4),A
        POP AF
        EI
        RET C
        PUSH BC
        LD A,($7A9C)
        JP $14F8
        ASSERT $ <= $FD20
''')
    import numpy as np
    from PIL import Image
    from build_graphics import PALETTE,PAIRS
    sphere_colours=bytearray();sphere_pixels=[]
    for cel in range(3):
        rgba=np.asarray(Image.open(ROOT/f'build/graphics/bellmite_blue_rim_feedback/H_sphere{cel}.png').convert('RGBA'))
        frame=bytearray()
        for cy in range(4):
            for cx in range(4):
                tile=rgba[cy*8:cy*8+8,cx*8:cx*8+8];bits=[]
                for row in tile:
                    rgb=np.where((row[:,3]>=128)[:,None],row[:,:3],0)
                    matches=[]
                    for paper,ink in PAIRS:
                        pb=np.all(rgb==PALETTE[paper],axis=1);ib=np.all(rgb==PALETTE[ink],axis=1)
                        if np.all(pb|ib):matches.append((paper,ink,ib))
                    assert matches,'H asset is not exact ECM'
                    paper,ink,ib=matches[0]
                    attr=(paper%8)*8+(ink%8)+(64 if paper>=8 else 0)
                    assert not (attr&64 and (paper%8==0 or ink%8==0))
                    sphere_colours.append(attr);bits.append(int(np.packbits(ib)[0]))
                frame.append(0);frame+=bytes(bits)
        assert len(frame)==144;sphere_pixels.append(frame)
    records=[]
    for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
        b=bytearray((source/f'{name}_region.bin').read_bytes())
        b[0xfbaa:0xfbaa+len(lookup)]=lookup
        if name=='boot':
            assert b[0x4ed6:0x4eda]==bytes.fromhex('1a a7 28 31');b[0x4ed6:0x4eda]=bytes.fromhex('c3 aa 5b 00')
            b[0xdd08:0xdd08+len(paint)]=paint
        if n==5:
            b[0x88eb:0x88eb+len(engine)]=engine
            b[0x8c00:0x8c00+len(sphere_colours)]=sphere_colours
            for cel,pixels in enumerate(sphere_pixels):
                for cell in range(16):
                    pos=0xd3f1+cel*144+cell*9
                    b[pos+1:pos+9]=pixels[cell*9+1:cell*9+9]
            b[0xd00:0xd00+len(low)]=low
            assert b[0x14f4:0x14f8]==bytes.fromhex('c5 3a 9c 7a');b[0x14f4:0x14f8]=bytes.fromhex('f3 c3 08 fd')
        (OUT/f'{name}_region.bin').write_bytes(b);tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP';(OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{p:02X}',b[p*8192:(p+1)*8192],p)for p in range(8)));records.append(dict(file=tap,level=n,sha256=hashlib.sha256(b).hexdigest()))
    for file in ['launcher.bin','demand_loader.sym','native_level5.bin','enemy_palette.bin','boss_preview.bin','boss_preview.sym']:shutil.copy2(source/file,OUT/file)
    (OUT/'manifest.json').write_text(json.dumps(dict(status='Unreleased native compositor experiment: approved H assets packed; visual/performance and full regression gates incomplete',regions=records,engine_bytes=len(engine)),indent=2));print('compositor bytes',len(engine),'low',len(low),'paint',len(paint))
if __name__=='__main__':main()
