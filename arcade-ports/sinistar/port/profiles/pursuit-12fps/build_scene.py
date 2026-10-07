from pathlib import Path
import hashlib,json,subprocess
import build
ROOT=Path(__file__).resolve().parents[1]
def main():
    build.main()
    banks={n:bytearray([255]*8192) for n in [0,1,2,3,4,5,6,7]}
    cursor={n:0 for n in [0,1,2,3,5,6,7]}
    def allocate(data,order):
        bank=next(n for n in order if cursor[n]+len(data)<=8192)
        ptr=bank*8192+cursor[bank]
        banks[bank][cursor[bank]:cursor[bank]+len(data)]=data
        cursor[bank]+=len(data)
        return f' DB {16 if bank==3 else 16|(1<<bank)}\n DW {0xe000+ptr-0x6000 if bank==3 else ptr}\n'
    faceptr=[];face_sizes=[]
    for phase in range(8):
        data=(ROOT.parent/f'assets/face-00-{phase}.bin').read_bytes()
        assert len(data)==1092
        code=bytearray()
        for row in range(52):
            for x in range(7):
                mask,bits,color=data[(row*7+x)*3:(row*7+x+1)*3]
                if mask!=255:
                    if mask==0:code.extend([0x36,bits])
                    else:code.extend([0x7e,0xe6,mask,0xf6,bits,0x77])
                    code.extend([0x3e,color,0x12])
                code.extend([0x2c,0x1c])
            if row!=51:code.extend([0xcd,0x83,0x7b])
        code.append(0xc9)
        face_sizes.append(len(code));faceptr.append(allocate(code,[0,1,2,7]))
    assert cursor[3]==0
    pointers=[]
    for heading in range(32):
        for phase in range(8):
            data=(ROOT.parent/f'assets/ship-{heading:02d}-{phase}.bin').read_bytes()
            assert len(data)==108
            pointers.append(allocate(data,[5,6,0,1,2,7,3]))
    assert cursor[3]<=0xb00, 'HOME asset spill must end before generated writes'
    (ROOT/'build/face-pointers.asm').write_text(''.join(faceptr))
    (ROOT/'build/sprite-pointers.asm').write_text(''.join(pointers))
    loops=[]
    for kind in ['clear','scan']:
        loops.append(kind+'_table:')
        loops.append(' DW '+','.join(kind+'_'+str(n) for n in range(33)))
        for n in range(32,0,-1):
            loops.append(kind+'_'+str(n)+':')
            if kind=='clear':loops.extend([' ld (hl),0',' ld (de),a',' inc l',' inc e'])
            else:
                loops.extend([' ld a,(de)',' xor (hl)',f' jr z,scan_skip_{n}',' ld a,(hl)',' push de',' exx',' pop de',' ld (hl),$21',' inc hl',' ld (hl),e',' inc hl',' ld (hl),d',' inc hl',' ld (hl),$36',' inc hl',' ld (hl),a',' inc hl',' exx',f'scan_skip_{n}:',' inc l',' inc e'])
        loops.extend([kind+'_0:',' ret'])
    (ROOT/'build/scene-loops.asm').write_text('\n'.join(loops)+'\n')
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
    manifest=dict(stage='optimized direct pursuit; ROM face blitters; no controls',face_code_bytes=face_sizes,dck_sha256=hashlib.sha256(dck).hexdigest(),sprite_bytes=cursor,source_commit=build.PIN,star_count=len(stars),star_motion='shared rounded camera delta; white palette; deterministic toroidal wrap')
    (ROOT/'build/scene-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(manifest)
if __name__=='__main__':main()
