from pathlib import Path
import hashlib,json,subprocess
import build
ROOT=Path(__file__).resolve().parents[1]
def main():
    build.main()
    banks={n:bytearray([255]*8192) for n in [0,1,4,5,6,7]}
    cursor={n:0 for n in [0,1,5,6]};pointers=[]
    for heading in range(32):
        for phase in range(8):
            data=(ROOT.parent/f'assets/ship-{heading:02d}-{phase}.bin').read_bytes()
            assert len(data)==108
            bank=next(n for n in cursor if cursor[n]+108<=8192)
            ptr=bank*8192+cursor[bank]
            banks[bank][cursor[bank]:cursor[bank]+108]=data;cursor[bank]+=108
            pointers.append(f' DB {16|(1<<bank)}\n DW {ptr}\n')
    faceptr=[]
    facecursor={7:0,6:cursor[6]}
    for phase in range(8):
        data=(ROOT.parent/f'assets/face-00-{phase}.bin').read_bytes()
        assert len(data)==1092
        bank=next(n for n in facecursor if facecursor[n]+len(data)<=8192)
        ptr=bank*8192+facecursor[bank]
        banks[bank][facecursor[bank]:facecursor[bank]+len(data)]=data
        facecursor[bank]+=len(data)
        faceptr.append(f' DB {16|(1<<bank)}\n DW {ptr}\n')
    (ROOT/'build/face-pointers.asm').write_text(''.join(faceptr))
    (ROOT/'build/sprite-pointers.asm').write_text(''.join(pointers))
    # Original NSTARS=$0A. Deterministic initial positions for repeatable tests.
    stars=[((i*73+19)%256,(i*47+11)%192) for i in range(10)]
    data=bytearray(6144)
    for x,y in stars:data[((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|(x>>3)]|=128>>(x&7)
    (ROOT/'build/starfield.bin').write_bytes(data)
    (ROOT/'build/star-seeds.json').write_text(json.dumps(stars)+'\n')
    (ROOT/'build/star-seeds.asm').write_text(''.join(f' DB {x},{y}\n DW {((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|(x>>3)}\n DB {128>>(x&7)}\n' for x,y in stars))
    (ROOT/'build/star-init.asm').write_text(''.join(f' ld a,{b}\n ld (${0xe000+i:04x}),a\n' for i,b in enumerate(data) if b))
    exe=ROOT.parent/'tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
    subprocess.run([str(exe),'--dirbol','--raw=build/scene-bank4.bin','--sym=build/scene-symbols.txt','src/scene.asm'],cwd=ROOT,check=True)
    banks[4][:]=(ROOT/'build/scene-bank4.bin').read_bytes()
    assert all(len(b)==8192 for b in banks.values())
    flat=b''.join(banks.get(n,bytes([255]*8192)) for n in range(8))
    dck=bytes([0]+[2 if n in banks else 0 for n in range(8)])+b''.join(banks[n] for n in sorted(banks))
    (ROOT/'build/sinistar-pursuit.dck').write_bytes(dck)
    (ROOT/'build/sinistar-pursuit.bin').write_bytes(flat)
    manifest=dict(stage='direct pursuit experiment; dynamic compositor; no controls',dck_sha256=hashlib.sha256(dck).hexdigest(),sprite_bytes=cursor,source_commit=build.PIN,star_count=len(stars),star_motion='shared rounded camera delta; white palette; deterministic toroidal wrap')
    (ROOT/'build/scene-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(manifest)
if __name__=='__main__':main()
