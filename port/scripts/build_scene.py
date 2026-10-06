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
    phases=[(ROOT.parent/f'assets/face-00-{phase}.bin').read_bytes() for phase in range(8)]
    erase=bytearray()
    for row in range(52):
        erase.extend([0x3e,7])
        for x in range(7):
            cells=[p[(row*7+x)*3:(row*7+x+1)*3] for p in phases]
            if any(c[0]!=255 for c in cells):erase.extend([0x36,0])
            if any(c[0]!=255 and c[2]!=7 for c in cells):erase.append(0x12)
            erase.extend([0x2c,0x1c])
        if row!=51:erase.extend([0xcd,0x83,0x7b])
    erase.append(0xc9)
    (ROOT/'build/erase-pointer.asm').write_text(allocate(erase,[0,1,2,7]))
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
                    if color!=7:code.extend([0x3e,color,0x12])
                code.extend([0x2c,0x1c])
            if row!=51:code.extend([0xcd,0x83,0x7b])
        code.append(0xc9)
        face_sizes.append(len(code));faceptr.append(allocate(code,[0,1,2,7]))
    rows=json.loads((ROOT/'build/sinistar-speeds.json').read_text())
    velocity=bytearray();velocity_values=[]
    for distance in range(-512,512):
        speed=next(v for d,v,a in rows if abs(distance)>=d)
        shift=next(a for d,v,a in rows if speed>=v)
        value=(speed if distance<0 else -speed)&65535
        entry=(value,shift)
        if entry not in velocity_values:velocity_values.append(entry)
        velocity.append(velocity_values.index(entry))
    ptr=allocate(velocity,[7])
    (ROOT/'build/scene-velocity-values.asm').write_text(''.join(f' DW {value}\n DB {shift}\n' for value,shift in velocity_values))
    fields=ptr.split()
    (ROOT/'build/scene-velocity.asm').write_text(f'velocity_bank EQU {fields[1]}\nvelocity_address EQU {fields[3]}\n')
    (ROOT/'build/scene-turn.asm').write_text(''.join(' DB '+','.join(str(((i if i<128 else i-256)*127+128)//256&255) for i in range(start,start+64))+'\n' for start in range(0,256,64)))
    assert cursor[3]==0
    pointers=[]
    for heading in range(32):
        for phase in range(8):
            data=(ROOT.parent/f'assets/ship-{heading:02d}-{phase}.bin').read_bytes()
            assert len(data)==108
            pointers.append(allocate(data,[5,6,0,1,2,7,3]))
    assert cursor[3]<=0xb00, 'HOME asset spill must end before generated writes'
    # Relative sparse attribute transitions: no absolute screen address or trajectory.
    color_layers=[{(i%7,i//7):p[3*i+2] for i in range(364) if p[3*i]!=255 and p[3*i+2]!=7} for p in phases]
    bitmap_layers=[{(i%7,i//7):p[3*i+1] for i in range(364) if p[3*i]!=255} for p in phases]
    transition_streams=[];bitmap_streams=[];transition_cases=[]
    for phase in range(8):
        for dy in [-1,0,1]:
            for dx in [-1,0,1]:
                next_phase=(phase+dx)%8;byte_dx=(phase+dx)//8;base_x=min(0,byte_dx)
                old=color_layers[phase]
                new={(x+byte_dx,y+dy):v for (x,y),v in color_layers[next_phase].items()}
                changed=sorted((y,x) for x,y in old.keys()|new.keys() if old.get((x,y),7)!=new.get((x,y),7))
                ys=sorted({y for y,x in changed});stream=bytearray([len(ys)])
                for y in ys:
                    xs=[x for cy,x in changed if cy==y]
                    assert all(0<=x<8 for x in xs)
                    stream.extend([y&255,sum(1<<x for x in xs)])
                transition_streams.append(bytes(stream))
                oldbits=bitmap_layers[phase]
                newbits={(x+byte_dx,y+dy):v for (x,y),v in bitmap_layers[next_phase].items()}
                runs=[]
                for y in range(-1,53):
                    xs=[x for x in range(base_x,base_x+8) if oldbits.get((x,y),0)!=newbits.get((x,y),0)]
                    span=((max(xs)-min(xs)+1)<<4)|(min(xs)-base_x) if xs else 0
                    if runs and runs[-1][1]==span:runs[-1][0]+=1
                    else:runs.append([1,span])
                bitmap_streams.append(bytes([len(runs),*[v for run in runs for v in run]]))
                transition_cases.append(dict(phase=phase,dx=dx,dy=dy,base_x=base_x,cells=len(changed)))
    windows=[[cursor[3],0xb00,0xe000],[0xb00,0x11c0,0xb940-0xb00],[0x11c0,0x19c0,0xd800-0x11c0]]
    placement={}
    for stream in sorted(set(transition_streams+bitmap_streams),key=lambda x:(-len(x),x)):
        window=next(w for w in windows if w[0]+len(stream)<=w[1])
        off=window[0];banks[3][off:off+len(stream)]=stream;window[0]+=len(stream)
        placement[stream]=off+window[2]
    (ROOT/'build/relative-pointers.asm').write_text(''.join(f' DW {placement[colors]},{placement[bits]}\n' for colors,bits in zip(transition_streams,bitmap_streams)))
    (ROOT/'build/relative-transitions.json').write_text(json.dumps(dict(bytes=sum(map(len,placement)),cases=transition_cases,streams=[dict(address=placement[c],data=list(c),bitmap_address=placement[b],bitmap_data=list(b)) for c,b in zip(transition_streams,bitmap_streams)]),indent=2)+'\n')
    (ROOT/'build/face-pointers.asm').write_text(''.join(faceptr))
    (ROOT/'build/sprite-pointers.asm').write_text(''.join(pointers))
    (ROOT/'build/scene-costs.asm').write_text("".join(f" DW {36*n+40},{36*n+76}\n" for n in range(33)))
    (ROOT/'build/scene-deadlines.asm').write_text("".join(f" DW {(40+y)*224}\n" for y in range(192)))
    loops=[]
    for kind in ['clear','pixels']:
        limit=3 if kind=='clear' else 32
        loops.append(kind+'_table:')
        loops.append(' DW '+','.join(kind+'_'+str(n) for n in range(limit+1)))
        for n in range(limit,0,-1):
            loops.append(kind+'_'+str(n)+':')
            if kind=='clear':loops.extend([' ld (hl),0',' ld (de),a',' inc l',' inc e'])
            else:
                loops.extend([' ld a,(de)',' cp (hl)',f' jr z,pixels_skip_{n}',' ld (hl),a',f'pixels_skip_{n}:',' inc l',' inc e'])
        loops.extend([kind+'_0:',' ret'])
    loops.extend(['scan_table:',' DW '+','.join('scan_'+str(n) for n in range(33))])
    for n in range(33):
        loops.extend([f'scan_{n}:',' pop hl',' pop de',f' call pixels_{n}',' ld a,l',f' sub {n}',' ld l,a',' ld e,a',' ld a,h',' xor $20',' ld h,a',' ld a,d',' xor $60',' ld d,a',f' jp pixels_{n}'])
    loops.extend(['mono_table:',' DW '+','.join('mono_'+str(n) for n in range(33))])
    for n in range(33):
        loops.extend([f'mono_{n}:',' pop hl',' pop de',f' jp pixels_{n}'])
    loops.extend(['delta_table:',' DW '+','.join('delta_'+str(n) for n in range(33))])
    for n in range(32,0,-1):
        loops.extend([f'delta_{n}:',' ld a,(de)',' xor (hl)',' call nz,fallback_byte',' inc l',' inc e'])
    loops.extend(['delta_0:',' ret'])
    loops.extend(['star_publish:',' pop hl',' pop de',' jp pixels_1'])
    phases=[(ROOT.parent/f'assets/face-00-{phase}.bin').read_bytes() for phase in range(8)]
    # Two old/new sprite layers bound sparse color writes independently of location.
    face_colors=max(sum(p[i]!=255 and p[i+2]!=7 for i in range(0,len(p),3)) for p in phases)
    ship_colors=max(sum(d[i]!=255 and d[i+2]!=7 for i in range(0,len(d),3)) for d in [(ROOT.parent/f'assets/ship-{h:02d}-{p}.bin').read_bytes() for h in range(32) for p in range(8)])
    assert 2*(face_colors+ship_colors)*5+1<4096
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
    manifest=dict(stage='keyboard/joystick flight with scripted stun and relocatable renderer',stop_source_sha256={f:hashlib.sha256((build.UPSTREAM/f).read_bytes()).hexdigest() for f in ['WITT/SINI.SRC','WITT/SCREENCH.SRC']},face_code_bytes=face_sizes,relative_transition_bytes=sum(map(len,placement)),relative_transition_cases=len(transition_cases),relative_cache_windows={"E000-EAFF":windows[0][0]-cursor[3],"B940-BFFF":windows[1][0]-0xb00,"D800-DFFF":windows[2][0]-0x11c0},dck_sha256=hashlib.sha256(dck).hexdigest(),sprite_bytes=cursor,source_commit=build.PIN,star_count=len(stars),star_motion='shared rounded camera delta; white palette; deterministic toroidal wrap')
    (ROOT/'build/scene-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(manifest)
if __name__=='__main__':main()
