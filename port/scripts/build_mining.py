"""Native mining integration fixture; leaves pursuit and saved demos intact."""
from pathlib import Path
import sys,re,json,hashlib,subprocess
import build as kernel_build
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parent/'scripts'))
from prepare_assets import pack as pack_uncached,RGB
from PIL import Image

def pack(a,phase,width):
    import prepare_assets
    cache=ROOT/'build/packed-cache';cache.mkdir(exist_ok=True)
    key=hashlib.sha256(a.tobytes()+str((a.shape,phase,width)).encode()+prepare_assets.RGB.tobytes()+Path(prepare_assets.__file__).read_bytes()).hexdigest()
    file=cache/(key+'.bin')
    if not file.exists():file.write_bytes(pack_uncached(a,phase,width)[0])
    return file.read_bytes(),None

def main():
    kernel_build.main()
    out=ROOT/'build';out.mkdir(exist_ok=True)
    source_table=(ROOT/'reference/original/SAM/SAMTABLE.SRC').read_text().split('SCIVELT\tFCB',1)[1].split('ESCIVEL',1)[0]
    pairs=[(-1,0)]+[tuple(map(int,m)) for m in re.findall(r'FCB\s+(-?\d+),(-?\d+)',source_table)]
    assert len(pairs)==9
    speeds=[(round(vs*128*256/304),round(-vl*64*112/256)) for vl,vs in pairs]
    (out/'world-bank-speeds.asm').write_text('wb_rock_speeds:\n'+''.join(f' DB {x},{y}\n' for x,y in speeds)+'wb_rock_speeds4:\n'+''.join(f' DW {x*4},{y*4}\n' for x,y in speeds))
    (out/'effect-rock-speeds.asm').write_text(' DB '+','.join(str(v) for pair in speeds for v in pair)+'\n')
    (out/'world-speeds.asm').write_text('rock_speeds:\n'+''.join(f' DB {x},{y}\n' for x,y in speeds))

    # Fixed-width compare/emit kernels: no per-cell loop or emitter call.
    # Entry addresses and Spectrum scanline offsets are computed offline.
    kernels=['span_entries:', ' DW '+','.join(f'span_{n}' for n in range(1,33))]
    for n in range(32,0,-1):
        kernels += [f'span_{n}:', ' ld a,(de)', ' xor (hl)', f' jp z,span_same_{n}',
                    ' ld a,(hl)', ' push de', ' push af', f'span_same_{n}:', ' dec l', ' dec e']
    kernels += [' jp stream_after_span']
    kernels += ['publish_records:', ' ld hl,$fffe',' ld de,($7bb2)',' or a',' sbc hl,de',' srl h',' rr l',' srl h',' rr l',' ld a,h',' or l',' ret z',
                ' ld a,l',' and 31',' ld c,a',' DUP 5',' srl h',' rr l',' EDUP',' ld b,l',' ld a,c',' or a',' jr z,pub_exact',' inc b','pub_exact:',
                ' add a,a',' ld l,a',' ld h,0',' ld de,pub_entries',' add hl,de',' ld e,(hl)',' inc hl',' ld d,(hl)',' ex de,hl',
                ' ld ($7bb4),sp',' ld sp,($7bb2)',' jp (hl)','pub_block:']
    for n in range(32,0,-1):kernels += [f'pub_{n}:',' pop de',' pop hl',' ld (hl),d']
    kernels += [' djnz pub_block',' ld sp,($7bb4)',' ret','pub_entries:',' DW pub_32,'+','.join(f'pub_{n}' for n in range(1,32))]
    kernels += [ ' INCLUDE "../src/controls.asm"', ' INCLUDE "assembly-lengths.asm"', ' INCLUDE "../src/player-impact.asm"', ' INCLUDE "../src/explosion-shift4.asm"', ' ALIGN 256', 'scanline_low:',
                ' DB '+'\n DB '.join(','.join(str((y&56)<<2) for y in range(start,start+128)) for start in (0,128)), 'scanline_high:',
                ' DB '+'\n DB '.join(','.join(str((y&7)|((y&192)>>3)) for y in range(start,start+128)) for start in (0,128))]
    kernels += ['clear_entries:', ' DW '+','.join(f'clear_{n}' for n in range(1,8))]
    for n in range(7,0,-1):kernels += [f'clear_{n}:',' ld (hl),0',' ld (de),a',' inc l',' inc e']
    kernels += [' ret']
    (out/'render-kernels.asm').write_text('\n'.join(kernels)+'\n',encoding='utf-8')
    speedtext=(ROOT/'reference/original/WITT/STBLSBOM.SRC').read_text(encoding='utf-8')
    rows=[(kernel_build.number(d),kernel_build.number(v),int(a)) for d,v,a in re.findall(r'fdb\s+\(([^)]+)\),\(([^)]+)\),asrd([0-7])',speedtext,re.I)]
    assert len(rows)==8
    (out/'sinibomb-speeds.asm').write_text('bomb_speeds:\n'+''.join(f' DW {d},{v}\n DB {a}\n' for d,v,a in rows),encoding='utf-8')
    text=(ROOT/'reference/original/SAM/IMAGE.SRC').read_text()
    def original(label,h,w,end="2$"):
        block=text.split(label+'\tFDB',1)[1].split('1$\tFCB',1)[1].split(end+'\tFCB',1)[0]
        data=bytes(int(n,16) for n in re.findall(r'\$([0-9A-F]{2})',block))
        assert len(data)==h*w,(label,len(data),h*w)
        a=np.zeros((h*2,w),np.uint8)
        for x in range(w):
            for y in range(h):a[y*2,x]=data[x*h+y]>>4;a[y*2+1,x]=data[x*h+y]&15
        return np.flipud(a)
    rocks=[original('IPLAN'+str(i+1),h,w) for i,(h,w) in enumerate([(14,26),(13,24),(10,18),(12,27),(16,28)])]
    rock=rocks[0];crystal=original('ICRYSTA',2,2);worker=original('IWORKER',6,10,'101$')
    # Read the pinned arcade descriptors and column-major image bytes.
    mem=[]; labels={}; desc={}; scope=""
    for line in text.splitlines():
        label=re.match(r'^(\w+\$?)\s+',line)
        if label:
            if not label[1].endswith('$'):scope=label[1]
            labels[scope+':'+label[1] if label[1].endswith('$') else label[1]]=len(mem)
        if 'FCB' in line:
            mem.extend(int(v.strip()[1:],16) if v.strip().startswith('$') else int(v.strip()) for v in line.split('FCB',1)[1].split(',') if v.strip())
        if label:
            m=re.search(r'FDB\s+([0-9A-F]{4}),(\w+\$?)',line)
            if m:desc[label[1]]=(int(m[1][:2],16),int(m[1][2:],16),scope+':'+m[2] if m[2].endswith('$') else m[2])
    table=(ROOT/'reference/original/SAM/SAMTABLE.SRC').read_text(encoding='utf-8').split('PIECETB\tFDB',1)[1].split('PIECEND',1)[0]
    order=re.findall(r'(\w+),([0-9A-F]{4})',table)
    assert len(order)==20
    canvas=np.zeros((52,49),np.uint8);assemblies=[];targets=[]
    for name,offset in order:
        h,w,label=desc[name];pos=labels[label];y,x=int(offset[:2],16),int(offset[2:],16)
        for col in range(w):
            for row in range(h*2):
                value=mem[pos+(-col if name.endswith('R') else col)*h+row//2]
                value=(value>>(4 if row%2==0 else 0))&15
                if y+row<52 and x+col<49 and value:canvas[y+row,x+col]=value
        assemblies.append(np.flipud(canvas.copy()))
        targets.append((192+x,80+max(0,52-y-h*2)))
    # ADDPIEC.SUBPIEC backs up from ALIVE through the twelve outer entries.
    damage=[]
    for name,offset in reversed(order[:12]):
        height,width,_=desc[name];y,x=int(offset[:2],16),int(offset[2:],16)
        damage.append(dict(name=name,x=x,y=max(0,52-y-height*2),width=width,height=min(height*2,52-y)))
    (out/'damage-pieces.json').write_text(json.dumps(damage,indent=2))
    (out/'damage-pieces.asm').write_text('damage_pieces:\n'+''.join(f" DB {r['x']},{r['y']},{r['width']},{r['height']}\n" for r in damage))
    import prepare_assets
    # PCRAM+$0e cycles through packed red intensities 7,3,0 in ANISINI.
    prepare_assets.RGB=np.vstack([RGB,[[255,0,0],[3*255/7,0,0],[0,0,0]]])
    waking=[]
    for eye in range(3):
        for mouth in ['AMOUT1','AMOUT3','AMOUT2']:
            a=canvas.copy()
            for name,oy,is_eye in [(mouth,6,False),(f'AEYE{eye+1}',26,True)]:
                h,w,label=desc[name];pos=labels[label]
                for x in range(w):
                    for y in range(h*2):
                        v=mem[pos+min(x,w-1-x)*h+y//2]
                        value=(v>>(4 if y%2==0 else 0))&15
                        a[oy+y,12+x]=16+eye if is_eye and value==14 else value
            waking.append(np.flipud(a))
    speech=(ROOT/'reference/original/WITT/ANISINI.SRC').read_text(encoding='utf-8')
    block=speech.split('TABLE\tAniSC2',1)[1].split('ENDTBL',1)[0]
    pairs=re.findall(r'(Shut|Open|Wide|EOA),([0-9]+\.?)',block)
    sequence=[({'Shut':0,'Open':1,'Wide':2,'EOA':255}[m],int(t.rstrip('.'),10 if t.endswith('.') else 16)) for m,t in pairs]
    (out/'awakening-sequence.json').write_text(json.dumps(sequence),encoding='utf-8')
    (out/'awakening-sequence.asm').write_text('awakening_sequence:\n'+''.join(f' DB {m},{t}\n' for m,t in sequence),encoding='utf-8')
    (out/'assembly-order.json').write_text(json.dumps(dict(order=[n for n,o in order],targets=targets),indent=2),encoding='utf-8')
    (out/'assembly-targets.asm').write_text('assembly_targets:\n'+''.join(f' DB {x},{y}\n' for x,y in targets),encoding='utf-8')
    Image.fromarray(RGB[rock].astype('uint8')).resize((208,224),Image.Resampling.NEAREST).save(out/'mining-arcade-rock.png')
    banks={n:bytearray([255]*8192) for n in range(8)};cursor={n:0 for n in banks if n!=4}
    def face_planes(raw,phase):
        out=bytearray()
        for row in range(52):
            pixels=bytearray();attrs=bytearray()
            for col in range(7):
                i=(row*7+col)*3
                mask=((raw[i]>>phase)|((raw[i-3] if col else 255)<<(8-phase)))&255
                bits=((raw[i+1]>>phase)|((raw[i-2] if col else 0)<<(8-phase)))&255
                pixels.append(bits if mask!=255 else 0)
                attrs.append(raw[i+2] if mask!=255 else 7)
            out.extend(pixels);out.extend(attrs)
        return out
    import mining_transitions
    pose_planes=[face_planes(pack(a,0,7)[0],0) for a in waking]
    for eye in range(3):
        for mouth in (1,2):
            assert all(33<=i//14<=45 for i,(a,b) in enumerate(zip(pose_planes[eye*3],pose_planes[eye*3+mouth])) if a!=b)
    pose_planes += [face_planes(pack(waking[eye*3],0,7)[0],phase) for eye in range(3) for phase in range(1,8)]
    # Stationary eye-only repair is valid for every generated fine phase.
    for phase in range(8):
        frames=[pose_planes[e*3] if phase==0 else pose_planes[9+e*7+phase-1] for e in range(3)]
        for a in frames:
            for b in frames:
                assert all(12<=i//14<=25 for i,(x,y) in enumerate(zip(a,b)) if x!=y)
    face_tables,fast_report,fast_alloc=mining_transitions.build(out,banks,cursor,pose_planes)
    face_slots=list(face_tables)
    # Unused tail of boot-only DOCK3 -> unused HOME tail after fast cache.
    sfx_report=json.loads((ROOT.parent/'assets/sfx-manifest.json').read_text())
    sfx_payload=bytearray();sfx_clips=['sfx_clips:']
    for effect in sfx_report['effects']:
        data=(ROOT.parent/f"assets/sfx-{effect['name']}.packed").read_bytes()
        sfx_clips += [f" DB {effect['frames']}",f" DW {0x5c40+len(sfx_payload)}"]
        sfx_payload.extend(data)
    assert len(sfx_payload)<=0x240 and cursor[3]+len(sfx_payload)<=8192 # 5E80..5E8D: roar state
    assert fast_report['boot_cache_windows'][-1][3]<=0x340
    source=0x6000+cursor[3]
    banks[3][cursor[3]:cursor[3]+len(sfx_payload)]=sfx_payload;cursor[3]+=len(sfx_payload)
    impact=(ROOT.parent/'assets/sfx-player-impact-real.packed').read_bytes()
    assert len(impact)==90
    sfx_clips += [' DB 30', ' DW player_impact_data']
    sfx_report['player_impact']=dict(bytes=90,frames=30,storage='resident DOCK4',chain='existing explosion after thirty audio refreshes',source='RemingtonGunshot.wav by fastson, CC BY 3.0; noise-only AY fit')
    (out/'sfx-clips.asm').write_text('\n'.join(sfx_clips)+'\n')
    (out/'sfx-cache-init.asm').write_text(f" ld a,$18\n out ($f4),a\n ld hl,{source}\n ld de,$5c40\n ld bc,{len(sfx_payload)}\n ldir\n ld a,$10\n out ($f4),a\n xor a\n ld ($5860),a\n ld ($5861),a\n ld ($5862),a\n ld ($5865),a\n ld ($5867),a\n ld ($5868),a\n ld ($586a),a\n ld ($586b),a\n ld ($586c),a\n ld ($586d),a\n ld ($586e),a\n ld ($586f),a\n inc a\n ld ($5866),a\n")

    from collections import Counter
    ship_raw=[(ROOT.parent/f'assets/ship-{h:02}-{phase}.bin').read_bytes() for h in range(32) for phase in range(8)]
    small_raw=[pack(rock,phase,5)[0] for phase in range(8)]
    # Boot-only triple dictionary: preserve the exact eight raw rock caches.
    rock_raw=b''.join(small_raw)
    rock_dict=list(dict.fromkeys(rock_raw[i:i+3] for i in range(0,len(rock_raw),3)))
    assert len(rock_dict)<=256
    rock_codes=bytes(rock_dict.index(rock_raw[i:i+3]) for i in range(0,len(rock_raw),3))
    rock_packed=b''.join(rock_dict)+rock_codes
    banks[3][:len(rock_packed)]=rock_packed
    roar_address=0x6000+len(rock_packed)
    # Position-independent row programs: HL=bitmap, DE=attributes. All
    # programs are in DOCK2, leaving resident code, stack and shadows visible.
    rock_rows={};rock_tables=[]
    def rock_alloc(data):
        address=0x4000+cursor[2]
        assert cursor[2]+len(data)<=8192
        banks[2][cursor[2]:cursor[2]+len(data)]=data;cursor[2]+=len(data)
        return address
    # Share identical instruction tails while retaining compiled row drawing.
    row_code={};tail_counts=Counter()
    for raw in small_raw:
        for y in range(28):
            row=bytes(raw[y*15:y*15+15])
            if row in row_code:continue
            chunks=[];known_a=None
            for x in range(5):
                mask,bits,attr=row[x*3:x*3+3];code=bytearray()
                if mask!=255:
                    code.extend([0x36,bits] if mask==0 else [0x7e,0xe6,mask,0xf6,bits,0x77])
                    # Opaque stores preserve A; reuse the previous cell's
                    # attribute instead of loading the same constant again.
                    if mask!=0:known_a=None
                    if known_a!=attr:code.extend([0x3e,attr])
                    code.append(0x12);known_a=attr
                code.extend([0x2c,0x1c] if x!=4 else [0xc9]);chunks.append(bytes(code))
            row_code[row]=b''.join(chunks)
            for x in range(1,5):tail_counts[b''.join(chunks[x:])]+=1
    # Merge instruction-aligned suffixes across both rows and shared tails.
    # This preserves compiled drawing; it only replaces duplicate ROM tails.
    programs=[];row_ids={}
    for row,code in row_code.items():
        seq=[];pos=0
        while pos<len(code):
            size=2 if code[pos] in (0x36,0xe6,0xf6,0x3e) else 1
            seq.append(bytes(code[pos:pos+size]));pos+=size
        row_ids[row]=len(programs);programs.append(tuple(seq))
    size=lambda seq:sum(len(x) if isinstance(x,bytes) else 3 for x in seq)
    while True:
        candidates={}
        for ident,seq in enumerate(programs):
            for at in range(len(seq)):
                tail=seq[at:]
                if size(tail)>3:candidates.setdefault(tail,[]).append((ident,at))
        best=None;gain=0
        for tail,matches in candidates.items():
            existing=next((ident for ident,at in matches if at==0),None)
            saving=(len(matches)-(existing is not None))*(size(tail)-3)-(0 if existing is not None else size(tail))
            if saving>gain:best=(tail,matches,existing);gain=saving
        if best is None:break
        tail,matches,target=best
        if target is None:target=len(programs);programs.append(tail)
        for ident,at in matches:
            if ident!=target:programs[ident]=programs[ident][:at]+(target,)
    addresses=[];pos=0x4000+cursor[2]
    for seq in programs:addresses.append(pos);pos+=size(seq)
    for seq in programs:
        rock_alloc(b''.join(x if isinstance(x,bytes) else bytes([0xc3,addresses[x]&255,addresses[x]>>8]) for x in seq))
    rock_rows={row:addresses[ident] for row,ident in row_ids.items()}
    for raw in small_raw:
        table=[rock_rows[bytes(raw[y*15:y*15+15])] for y in range(28)]
        rock_tables.append(rock_alloc(b''.join(v.to_bytes(2,'little') for v in table)))
    rock_program_table=rock_alloc(b''.join(v.to_bytes(2,'little') for v in rock_tables))
    compiled_rock_bytes=cursor[2]
    render_extension=0x4000+cursor[2]
    render_capacity=1120
    cursor[2]+=render_capacity
    (out/'incremental-origin.asm').write_text(f'render_extension EQU {render_extension}\n')
    (out/'rock-programs.asm').write_text(f'rock_programs EQU {rock_program_table}\n')
    small_raw += [pack(a,phase,w)[0] for a,w in [(crystal,2),(worker,3),(np.ones((2,2),np.uint8),2)] for phase in range(8)]
    frequencies=Counter(bytes(raw[i:i+3]) for raw in ship_raw+small_raw for i in range(0,len(raw),3) if raw[i]!=255)
    dictionary=[t for t,n in frequencies.most_common(255)]
    indices={t:i for i,t in enumerate(dictionary)}
    dictionary_source=fast_alloc(b''.join(dictionary))
    with (out/'fast-tables.asm').open('a') as f:f.write(f'ship_dictionary_source EQU {dictionary_source}\n')
    # Reserve the largest indivisible payload before packing small sprites.
    voice_names=['beware-i-live','i-am-sinistar','sinistar-roar','i-hunger','beware-coward','run-coward','run-run-run','i-hunger-coward']
    voice_payloads=[(ROOT.parent/f'assets/{name}.ay').read_bytes() for name in voice_names]
    packed_voices=[]
    for voice_index,payload in enumerate(voice_payloads):
        if voice_index==2:
            # Exact fourteen-register frame deltas. First frame defines every register.
            previous=bytes([254])*14; delta=bytearray()
            for at in range(0,len(payload),14):
                row=payload[at:at+14]
                mask=sum(1<<r for r in range(14) if row[r]!=previous[r])
                delta.extend(mask.to_bytes(2,'little'))
                delta.extend(row[r] for r in range(14) if mask&(1<<r))
                previous=row
            packed_voices.append(bytes(delta))
            continue
        packed=bytearray()
        for i in range(0,len(payload),14):
            r=payload[i:i+14]
            assert len(r)==14 and (r[11],r[12],r[13])==(1,0,255)
            assert r[6]==5 if r[7]!=52 else (r[6]==r[4] and r[5]==0 and 1<=r[6]<=31)
            assert r[1]<8 and r[3]<4 and r[5]<2 and r[7] in (31,56,52)
            assert all(r[n]<16 for n in [8,9,10])
            packed.extend([r[0],r[2],r[4],r[1]|(r[3]<<3)|(r[5]<<5)|((r[7]==31)<<6)|((r[7]==52)<<7),r[8]|(r[9]<<4),r[10]])
        paired=bytearray()
        for i in range(0,len(packed),12):
            pair=packed[i:i+12]
            paired.extend(pair[:5]);paired.append(pair[5]|((pair[11] if len(pair)==12 else 0)<<4))
            if len(pair)==12:paired.extend(pair[6:11])
        packed_voices.append(bytes(paired))
    speech_payload=b''.join(packed_voices)
    extension_address=0xc000
    extension_capacity=6000
    (out/'world-origin.asm').write_text(f'world_extension EQU {extension_address}\n')
    cursor[6]=extension_capacity
    voice_locations=[]
    for voice_index,payload in enumerate(packed_voices):
        if voice_index==2:
            bank=3;address=roar_address
            banks[3][address-0x6000:address-0x6000+len(payload)]=payload
            voice_locations.append((bank,address))
            continue
        bank=next((n for n in (6,5,0,1) if cursor[n]+len(payload)<=8192),None)
        assert bank is not None,('speech capacity',cursor)
        address=bank*8192+cursor[bank]
        banks[bank][cursor[bank]:cursor[bank]+len(payload)]=payload;cursor[bank]+=len(payload)
        voice_locations.append((bank,address))
    pointers=[];metadata=[]
    def compress(raw):
        count=len(raw)//3;flags=bytearray((count+7)//8);payload=bytearray()
        assert count<=255
        for cell in range(count):
            triple=bytes(raw[cell*3:cell*3+3])
            if triple[0]!=255:
                flags[cell//8]|=1<<(cell%8)
                if triple in indices:payload.append(indices[triple])
                else:payload.append(255);payload.extend(triple)
        return bytes([count])+flags+payload
    def add(data,kind,index,stored=None):
        compressed=kind in ['ship','worker','crystal','bullet','sinibomb']
        payload=compress(data) if compressed else (data if stored is None else stored)
        if kind=='rock':
            # Reuse the boot-copied HOME windows formerly holding horizontal
            # transition templates. Clipped rocks keep raw data without decode.
            dest,source,slot=(0xa000,0,index) if index<4 else ((0xc300,1680,index-4) if index<7 else (0x5900,2940,0))
            address=dest+slot*420;offset=source+slot*420
            # Expanded from the lossless boot dictionary into these HOME addresses.
            bank=3;mapping=0x10
        elif kind in ['awakening','face_phase']:
            assert len(payload)==728
            address=face_slots.pop(0);bank=address//8192
            mapping=0x93
        elif kind=='speech':
            bank,address=voice_locations[index];mapping=16|(1<<bank)
        else:
            bank=next((n for n in cursor if n!=3 and (kind!='ship' or n!=6) and cursor[n]+len(payload)<=8192),None)
            assert bank is not None,(kind,index,len(payload),cursor)
            offset=cursor[bank];cursor[bank]+=len(payload)
            address=bank*8192+offset;banks[bank][offset:offset+len(payload)]=payload
            mapping=16|(1<<bank)
        if kind!='speech' or index==0:pointers.append(f' DB {mapping|(8 if compressed else 0)}\n DW {address}\n')
        if bank==5 and kind!='speech': assert (len(payload) if kind=='assembly' else len(data))<=384, 'DC80 stage must end before assembly color cache DE00'
        metadata.append(dict(kind=kind,index=index,bank=bank,address=address,data=list(data)))
    for heading in range(32):
        for phase in range(8):
            raw=(ROOT.parent/f'assets/ship-{heading:02}-{phase}.bin').read_bytes()
            flags=bytearray(5);payload=bytearray()
            for cell in range(36):
                triple=raw[cell*3:cell*3+3]
                if triple[0]!=255:
                    flags[cell//8]|=1<<(cell%8)
                    if triple in indices:payload.append(indices[triple])
                    else:payload.append(255);payload.extend(triple)
            add(raw,'ship',heading*8+phase,flags+payload)
    for kind,a,width in [('rock',rock,5),('crystal',crystal,2),('bullet',np.ones((2,2),np.uint8),2),('worker',worker,3)]:
        for phase in range(8):add(pack(a,phase,width)[0],kind,phase)
    lengths=[];previous=bytes([255,0,1])*364
    for index,a in enumerate(assemblies):
        raw=pack(a,0,7)[0];encoded=bytearray()
        assert all(raw[i]==255 and raw[i+1]==0 for i in range(0,21,3)), 'Cached assembly row zero must be transparent'
        mask_pairs=set()
        for y in range(52):
            prior=255
            for mask in raw[y*21:(y+1)*21:3]:
                mask_pairs.add((prior&127,mask));prior=mask
        assert len(mask_pairs)<=100, ('Assembly mask dictionary overflow',index,len(mask_pairs))
        last=0
        for i in range(0,len(raw),3):
            if raw[i:i+3]!=previous[i:i+3]:
                delta=i//3-last;attr=[7,15,23,2,55].index(raw[i+2])
                encoded.append((attr<<5)|min(delta,31))
                if delta>=31:encoded.extend(i.to_bytes(2,'little'))
                encoded.extend(raw[i:i+2]);last=i//3
        encoded.append(255)
        assert len(encoded)<=2048
        add(raw,'assembly',index,encoded);lengths.append(len(encoded));previous=raw
    (out/'assembly-lengths.asm').write_text('assembly_lengths:\n DW '+','.join(map(str,lengths))+'\n',encoding='utf-8')
    for index,a in enumerate(waking):
        raw=pack(a,0,7)[0];add(raw,'awakening',index,face_planes(raw,0))
    block=text.split('ISBOMB\tFDB',1)[1].split('2$\tFCB',1)[1].split('3$\tFCB',1)[0]
    raw=bytes(int(v,16) for v in re.findall(r'\$([0-9A-F]{2})',block));assert len(raw)==15
    bomb=np.flipud(np.array([[(raw[x*3+y//2]>>(4 if y%2==0 else 0))&15 for x in range(5)] for y in range(6)],dtype=np.uint8))
    for phase in range(8):
        raw=bytearray(pack(bomb,phase,2)[0])
        # Preserve the arcade bitmap; improve contrast on the small ECM screen.
        for i in range(0,len(raw),3):
            if raw[i]!=255:raw[i+2]=0x46 if i//6 in (2,3) else 0x47
        add(bytes(raw),'sinibomb',phase)
    for index,payload in enumerate(voice_payloads):add(payload,'speech',index)
    (out/'speech-source.asm').write_text('speech_bank EQU $50\nspeech_frames EQU 125\n',encoding='utf-8')
    speech_tables=[f'wb_awakening_ticks EQU {sum(t for m,t in sequence if m!=255)}','wb_speech_clips:']
    for payload,(bank,address) in zip(voice_payloads,voice_locations):
        speech_tables.extend([f' DB {len(payload)//14},{0x50|(1<<bank)}',f' DW {address}'])
    speech_tables+=['wb_mouth_tables:',' DW '+','.join(f'wb_mouth_{n}' for n in [2,1,8,3,4,5,6,7])]
    for n in range(1,9):
        block=speech.split(f'TABLE\tAniSC{n}',1)[1].split('ENDTBL',1)[0]
        pairs=re.findall(r'(Shut|Open|Wide|EOA),([0-9]+\.?)',block)
        speech_tables.append(f'wb_mouth_{n}:')
        speech_tables.extend(f" DB {dict(Shut=0,Open=1,Wide=2,EOA=255)[m]},{int(t.rstrip('.'),10 if t.endswith('.') else 16)}" for m,t in pairs)
    (out/'taunt-tables.asm').write_text('\n'.join(speech_tables)+'\n')
    # Shut-mouth pursuit: seven further phases for each eyebrow pose.
    for eye in range(3):
        raw=pack(waking[eye*3],0,7)[0]
        for phase in range(1,8):add(face_planes(raw,phase),'face_phase',eye*7+phase-1)
    assert not face_slots
    # Original IEXPLO column-major frames, centered using descriptor offsets.
    explosion_block=text.split('IEXPLO\tFDB',1)[1].split('* null image',1)[0]
    explosion_dictionary=[];explosion_indices=[];explosion_meta=[]
    for frame,(height,width) in enumerate([(12,19),(13,19),(13,20),(13,20)]):
        block=explosion_block.split(f'{frame+1}$\tFCB',1)[1].split(f'{frame+2}$\tFCB',1)[0]
        source=bytes(int(v,16) for v in re.findall(r'\$([0-9A-F]{2})',block))
        assert len(source)==height*width
        canvas=np.zeros((26,20),np.uint8)
        for x in range(width):
            for y in range(height*2):canvas[13-height+y,x]=(source[x*height+y//2]>>(4 if y%2==0 else 0))&15
        canvas=np.flipud(canvas)
        raw=pack(canvas,0,3)[0];codes=[]
        for at in range(0,len(raw),3):
            triple=raw[at:at+3]
            if triple not in explosion_dictionary:explosion_dictionary.append(triple)
            codes.append(explosion_dictionary.index(triple))
        explosion_indices.append(codes)
        padded=b''.join(raw[y*9:y*9+9]+bytes([255,0,1]) for y in range(26))
        explosion_meta.append(dict(kind='arcade-explosion',index=frame,data=list(padded),arcade_pixels=canvas.tolist()))
    assert len(explosion_dictionary)<256
    lines=['fx_explosion_pointers:',' DW '+','.join(f'fx_exp_{n}' for n in range(4))]
    for frame,codes in enumerate(explosion_indices):lines += [f'fx_exp_{frame}:',' DB '+','.join(map(str,codes))]
    lines += ['fx_explosion_dictionary:']+[' DB '+','.join(str(v) for v in t) for t in explosion_dictionary]
    (out/'explosion-art.asm').write_text('\n'.join(lines)+'\n')
    metadata.extend(explosion_meta)
    (out/'mining-pointers.asm').write_text(''.join(pointers))
    (out/'mining-assets.json').write_text(json.dumps(metadata))
    effects_origin=0xe000+cursor[7]
    effects_capacity=8192-cursor[7]
    (out/'effects-origin.asm').write_text(f'effects_origin EQU {effects_origin}\n')
    # Filled diameter-98 disc: per-scanline half widths; ECM rounds edges to cells.
    import math
    (out/'ring-points.asm').write_text('ring_spans:\n'+''.join(f' DB {math.isqrt(2401-y*y)},{math.isqrt(1600-y*y) if abs(y)<=40 else 255}\n' for y in range(-49,50)))
    (out/'ring-phases.asm').write_text('inc_ring_tables:\n'+''.join(' DB '+','.join(str(math.isqrt(r*r-y*y)) if y<=r else '255' for y in range(50))+'\n' for r in (43,45,47)))
    font_source=(ROOT/'src/end-screen.asm').read_text().split('we_font:')[1].split('we_lost:')[0]
    glyphs=[[int(v.strip().replace('$','0x'),0) for v in line.split('DB ')[1].split(',')] for line in font_source.splitlines() if 'DB ' in line]
    font=dict(zip(' AEFGIMNORSTUVWY',glyphs));font['D']=[0xf0,0x88,0x88,0x88,0x88,0x88,0xf0]
    font['B']=[0xf0,0x88,0x88,0xf0,0x88,0x88,0xf0]
    font['C']=[0x70,0x88,0x80,0x80,0x80,0x88,0x70]
    notice=[];notice_rows=[]
    for label,msg in [('mode_on_text','FAST MODE ON '),('mode_off_text','FAST MODE OFF'),('mode_bounce_on','BOUNCE ON    '),('mode_bounce_off','BOUNCE OFF   ')]:
        notice_rows.append((label,[font[ch][row] for row in range(7) for ch in msg]))
    notice_dictionary=list(dict.fromkeys(v for _,rows in notice_rows for v in rows))
    assert len(notice_dictionary)<=16
    for label,rows in notice_rows:
        notice.append(label+':')
        # Pad each 13-cell row independently; the unused low nibble is skipped.
        for row in range(7):
            indices=[notice_dictionary.index(v) for v in rows[row*13:row*13+13]]+[0]
            notice.append(' DB '+','.join(str(indices[i]*16+indices[i+1]) for i in range(0,14,2)))
    notice+=['mode_byte_table:',' DB '+','.join(map(str,notice_dictionary))]
    (out/'mode-notice.asm').write_text('\n'.join(notice)+'\n')
    exe=ROOT.parent/'tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
    import title_screen
    rock_decoder_address=roar_address+len(packed_voices[2])
    decoder=f''' ORG {rock_decoder_address}
rock_decode:
 ld a,(hl)
 inc hl
 push hl
 push bc
 ld l,a
 ld h,0
 ld c,a
 ld b,0
 add hl,hl
 add hl,bc
 ld bc,$6000
 add hl,bc
 pop bc
 ldi
 ldi
 ldi
 pop hl
 jp pe,rock_decode
 ret
'''
    (out/'rock-boot.asm').write_text(decoder)
    subprocess.run([str(exe),'--dirbol','--raw=build/rock-boot.bin','build/rock-boot.asm'],cwd=ROOT,check=True)
    rock_decoder=(out/'rock-boot.bin').read_bytes()
    assert rock_decoder_address+len(rock_decoder)<=0x6000+3360
    banks[3][rock_decoder_address-0x6000:rock_decoder_address-0x6000+len(rock_decoder)]=rock_decoder
    init=[' ld sp,$b7ff',' ld a,$18',' out ($f4),a']
    for dest,size,offset in [(0xa000,1680,0),(0xc300,1260,1680),(0x5900,420,2940)]:
        init += [f' ld hl,{0x6000+len(rock_dict)*3+offset//3}',f' ld de,{dest}',f' ld bc,{size}',f' call {rock_decoder_address}']
    init += [' ld a,$10',' out ($f4),a',' ld sp,$7fff']
    (out/'fast-cache-init.asm').write_text('\n'.join(init)+'\n')
    title_address,title_length=title_screen.build(ROOT,banks,cursor)
    font_address=rock_decoder_address+len(rock_decoder)
    font=(out/'frontend-font.bin').read_bytes()
    assert font_address+len(font)<=0x6d20
    banks[3][font_address-0x6000:font_address-0x6000+len(font)]=font
    offsets=json.loads((out/'frontend-font-offsets.json').read_text())
    (out/'frontend-font.asm').write_text(f'front_font EQU {font_address}\n'+''.join(f'front_{n} EQU {font_address+v}\n' for n,v in offsets.items()))
    boot_address=title_address+title_length+600
    with (out/'title-origin.asm').open('a') as f:f.write(f'boot_source EQU {boot_address}\n')
    subprocess.run([str(exe),'--dirbol','--raw=build/mining-bank4.bin','--sym=build/mining-symbols.txt','src/mining-scene.asm'],cwd=ROOT,check=True)
    banks[4][:]=(out/'mining-bank4.bin').read_bytes();assert all(len(b)==8192 for b in banks.values())
    symbols=dict(re.findall(r'^(\w+): EQU (0x[0-9A-F]+)',(out/'mining-symbols.txt').read_text(),re.M))
    (out/'world-equ.asm').write_text(''.join(f'{n} EQU {v}\n' for n,v in symbols.items()))
    subprocess.run([str(exe),'--dirbol','--raw=build/assembly-cache.bin','--sym=build/assembly-cache-symbols.txt','src/assembly-cache.asm'],cwd=ROOT,check=True)
    assembly_cache=(out/'assembly-cache.bin').read_bytes();assert len(assembly_cache)<=1792
    banks[3][3360:3360+len(assembly_cache)]=assembly_cache
    help_data=(out/'frontend-help.bin').read_bytes()
    assert len(assembly_cache)+len(help_data)<=1792
    help_address=0x6000+3360+len(assembly_cache)
    banks[3][help_address-0x6000:help_address-0x6000+len(help_data)]=help_data
    with (out/'frontend-font.asm').open('a') as f:f.write(f'front_mining_help EQU {help_address}\n')
    cache_symbols=dict(re.findall(r'^(\w+): EQU (0x[0-9A-F]+)',(out/'assembly-cache-symbols.txt').read_text(),re.M))
    (out/'assembly-home-init.asm').write_text(f" ld a,$18\n out ($f4),a\n ld hl,{cache_symbols['ac_home_source']}\n ld de,$df70\n ld bc,{cache_symbols['ac_home_length']}\n ldir\n ld a,$10\n out ($f4),a\n")
    subprocess.run([str(exe),'--dirbol','--raw=build/incremental.bin','--sym=build/incremental-symbols.txt','src/incremental.asm'],cwd=ROOT,check=True)
    incremental=(out/'incremental.bin').read_bytes();assert len(incremental)<=render_capacity
    banks[2][render_extension-0x4000:render_extension-0x4000+len(incremental)]=incremental
    subprocess.run([str(exe),'--dirbol','--raw=build/world-bank.bin','--sym=build/world-bank-symbols.txt','src/world-bank.asm'],cwd=ROOT,check=True)
    extension=(out/'world-bank.bin').read_bytes()
    assert len(extension)<=extension_capacity
    banks[6][extension_address-0xc000:extension_address-0xc000+len(extension)]=extension
    with (out/'mining-symbols.txt').open('a') as f:
        f.write('\n'+''.join(line+'\n' for line in (out/'world-bank-symbols.txt').read_text().splitlines() if line.startswith(('wb','wp','ww','ws','fp_','speech_unpack','radar_','stars_'))))
    with (out/'mining-symbols.txt').open('a') as f:
        f.write('\n'+''.join(line+'\n' for line in (out/'incremental-symbols.txt').read_text().splitlines() if line.startswith('inc_')))
    with (out/'mining-symbols.txt').open('a') as f:
        f.write('\n'+''.join(line+'\n' for line in (out/'assembly-cache-symbols.txt').read_text().splitlines() if line.startswith('ac_')))
    (out/'title-equ.asm').write_text(f'title_source EQU {title_address}\ntitle_return EQU {symbols["title_return"]}\noffset EQU {symbols["offset"]}\nstart EQU {symbols["start"]}\ntitle_boot EQU {symbols["title_boot"]}\neffects_origin EQU {effects_origin}\n')
    subprocess.run([str(exe),'--dirbol','--raw=build/title.bin','--sym=build/title-symbols.txt','src/title.asm'],cwd=ROOT,check=True)
    title_symbols=dict(re.findall(r'^(\w+): EQU (0x[0-9A-F]+)',(out/'title-symbols.txt').read_text(),re.M))
    (out/'frontend-world-equ.asm').write_text(''.join(line+'\n' for line in (out/'world-bank-symbols.txt').read_text().splitlines() if line.startswith(('wb_delta:', 'wb_get:'))))
    (out/'frontend-title-equ.asm').write_text(''.join(f'{n} EQU {title_symbols[n]}\n' for n in ['front_title','front_firing_help','front_sinistar_help']))
    subprocess.run([str(exe),'--dirbol','--raw=build/effects.bin','--sym=build/effects-symbols.txt','src/effects.asm'],cwd=ROOT,check=True)
    effects=(out/'effects.bin').read_bytes();assert len(effects)<=effects_capacity,(len(effects),effects_capacity)
    banks[7][effects_origin-0xe000:effects_origin-0xe000+len(effects)]=effects
    cursor[7]+=len(effects)
    with (out/'mining-symbols.txt').open('a') as f:
        f.write('\n'+''.join(line+'\n' for line in (out/'effects-symbols.txt').read_text().splitlines() if line.startswith(('ring_','mode_','fx_','front_'))))
    subprocess.run([str(exe),'--dirbol','--raw=build/title.bin','--sym=build/title-symbols.txt','src/title.asm'],cwd=ROOT,check=True)
    title=(out/'title.bin').read_bytes()
    assert cursor[3]+len(title)<=8192, 'Title exceeds boot bank'
    assert len(title)<=title_length+600
    banks[3][cursor[3]:cursor[3]+len(title)]=title
    (out/'boot-equ.asm').write_text(''.join(f'{n} EQU {v}\n' for n,v in symbols.items()))
    home_symbols=dict(re.findall(r'^(\w+): EQU (0x[0-9A-F]+)',(out/'mining-symbols.txt').read_text(),re.M))
    (out/'home-render-equ.asm').write_text(''.join(f'{n} EQU {v}\n' for n,v in home_symbols.items()))
    subprocess.run([str(exe),'--dirbol','--raw=build/home-render.bin','--sym=build/home-render-symbols.txt','src/home-render.asm'],cwd=ROOT,check=True)
    home_render=(out/'home-render.bin').read_bytes()
    assert len(home_render)<=0x170
    # Fixed boot-bank tail; copied after the raw rock cache, before interrupts.
    helper_source=0x8000-len(home_render)
    banks[3][helper_source-0x6000:]=home_render
    (out/'home-render-init.asm').write_text(f' ld a,$18\n out ($f4),a\n ld hl,{helper_source}\n ld de,$a690\n ld bc,{len(home_render)}\n ldir\n ld a,$10\n out ($f4),a\n')
    subprocess.run([str(exe),'--dirbol','--raw=build/roar-mixer.bin','--sym=build/roar-mixer-symbols.txt','src/roar-mixer.asm'],cwd=ROOT,check=True)
    roar_mixer=(out/'roar-mixer.bin').read_bytes()
    helper_source-=len(roar_mixer)
    banks[3][helper_source-0x6000:helper_source-0x6000+len(roar_mixer)]=roar_mixer
    (out/'roar-init.asm').write_text(f' ld a,$18\n out ($f4),a\n ld hl,{helper_source}\n ld de,$bc00\n ld bc,{len(roar_mixer)}\n ldir\n ld a,$10\n out ($f4),a\n ld hl,$bc00\n ld de,$7f60\n ld bc,{len(roar_mixer)}\n ldir\n')
    with (out/'mining-symbols.txt').open('a') as f:
        f.write('\n'+''.join(line+'\n' for line in (out/'home-render-symbols.txt').read_text().splitlines() if line.startswith(('hp_','wpp_','pc_','pd_','population_end:'))))
    subprocess.run([str(exe),'--dirbol','--raw=build/boot.bin','src/boot.asm'],cwd=ROOT,check=True)
    boot=(out/'boot.bin').read_bytes()
    assert len(boot)<=1024 and boot_address+len(boot)<=helper_source
    banks[3][boot_address-0x6000:boot_address-0x6000+len(boot)]=boot
    cursor[3]=boot_address-0x6000+len(boot)
    boot_tail_free=helper_source-(0x6000+cursor[3])
    cursor[3]=8192 # Helpers occupy the tail, with a checked gap after boot.
    with (out/'mining-symbols.txt').open('a') as f:
        f.write('\n'+''.join(line+'\n' for line in (out/'title-symbols.txt').read_text().splitlines() if line.startswith('title_') or (line.startswith('front_') and title_address<=int(line.split('0x')[1],16)<boot_address)))
    dck=bytes([0]+[2 if n in banks else 0 for n in range(8)])+b''.join(banks[n] for n in sorted(banks))
    (out/'sinistar-mining.dck').write_bytes(dck)
    (out/'sinistar-mining.bin').write_bytes(b''.join(banks.get(n,bytes([255]*8192)) for n in range(8)))
    report=dict(stage='native playable fixed-screen prototype',dck_sha256=hashlib.sha256(dck).hexdigest(),sprite_bytes=cursor,source_sha256={f:hashlib.sha256((ROOT/'reference/original'/f).read_bytes()).hexdigest() for f in ['SAM/SCANNER.SRC','SAM/EXECJNK.SRC','SAM/IMAGE.SRC','FALS/N1ALL.SRC','FALS/N1SYM.EQU','WITT/WORKER.SRC','WITT/COLLISIO.SRC','SAM/ADDPIEC.SRC','SAM/SAMTABLE.SRC','WITT/ANISINI.SRC','WITT/CHASE.SRC','WITT/VELOCITY.SRC','WITT/SINIBOMB.SRC','WITT/STBLSBOM.SRC','WITT/STBLSINI.SRC','WITT/SINI.SRC','WITT/THINK.SRC','WITT/SUBPART.SRC']})
    report['incremental_rendering'] = dict(bank=2,origin=render_extension,bytes=len(incremental),capacity=render_capacity,scratch='HOME 7BA0-7BAB',stationary_face='dirty spans and eye rows 12-25',restoration='old rectangle minus new opaque face')
    report['compiled_planetoids'] = dict(rows=len(rock_rows), bytes=compiled_rock_bytes, mapping=0x14)
    report['roar_mixer'] = dict(address=0x7f60,bytes=len(roar_mixer),stack_boundary=0x7fd0,boot_source=helper_source,impact_refreshes=12)
    report['speech_storage'] = dict(format='paired ordinary speech; fourteen-register deltas for edited roar',raw_bytes=sum(map(len,voice_payloads)),stored_bytes=len(speech_payload),roar_bytes=len(packed_voices[2]),roar_address=roar_address,world_code_bytes=len(extension),world_code_capacity=extension_capacity)
    report['rock_boot_storage'] = dict(raw_bytes=len(rock_raw),stored_bytes=len(rock_packed),decoder_bytes=len(rock_decoder),dictionary_entries=len(rock_dict),runtime_graphics_unchanged=True)
    report['sfx'] = sfx_report
    prior_audio={x['name']:x for x in json.loads((ROOT.parent/'assets/audio.json').read_text())}
    report['voices'] = {name:json.loads((ROOT.parent/f'assets/{name}.json').read_text()) if (ROOT.parent/f'assets/{name}.json').exists() else prior_audio[name] for name in voice_names}
    report['speech'] = json.loads((ROOT.parent/'assets/beware-i-live.json').read_text())
    report['face_atlas'] = dict(poses=30,shared_padded_rows=fast_report['rows'],banks=[0,1,7],runtime_shift=False)
    report['fast_transitions'] = {k:v for k,v in fast_report.items() if k!='cases'}
    report['packed_publication'] = dict(record_bytes=4, direction='descending stack build, top-down publication', changed_only=True)
    report['retained_planetoids'] = dict(projection_bytes=9, previous='HOME 5B00-5B98', flags='HOME 5BA0-5BB0', repair='dirty rows of unchanged fully visible rocks')
    report['home_render_helpers'] = dict(address=0xa690,bytes=len(home_render),capacity=0x170,boot_source=0x8000-len(home_render),boot_tail_free=boot_tail_free,flags='HOME 5BCA-5BCE',covered_player_default=False,covered_stars_default=True)
    report['stage'] = 'native playable scrolling-world milestone'
    report['ship_storage'] = 'cell count, occupancy mask, common-triple indices with literal escapes; HOME c000 dictionary and 7c00 cache'
    report['world'] = dict(size=[512,512],viewport=[256,112],camera='adapted dead zone',stars=10,planetoids=18,types=[10,2,2,2,2],planetoid_art='shared IPLAN1',radar=[64,16],radar_scale=[8,32],secondary_motion_groups=4)
    report['face_atlas']['runtime_shift'] = 'opening-mouth camera phases only; assembly uses RAM phase caches'
    report['assembly_cache'] = dict(sets=2,phases=8,ram='HOME 8000-9FFF',bytes_per_set=4096,bitmap_bytes=2856,bitmap_phase_bytes=357,transparent_row_zero_omitted=True,overlap_rows_offset=2856,mask_indices_offset=2912,mask_patterns_offset=3276,mask_pattern_capacity=100,mask_count_offset=4095,state='HOME 5BD0-5C23',normalized_colors='HOME DE00-DF6B',selected_mask_lookup='HOME BF00-BF63, retained until phase/stage change or bank-6 staging',row_mask_scratch='HOME BF80-BF86',home_helpers='HOME DF70-DFFE',dirty_rows='HOME BE00-BE33 and BE40-BE73',code_bank=3,code_bytes=len(assembly_cache),code_capacity=1792,rows_per_build_call=1,calls_per_picture=2,pictures_per_stage=26,rows_per_draw_call=13,composition='dirty-cell intersection only; masked on object overlap, direct elsewhere',culling='object bounds fully inside opaque assembly mask')
    report['world']['radar_refresh_ticks'] = 24
    report['world']['hidden_sprite_staging'] = False
    (out/'mining-scene-manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':main()
