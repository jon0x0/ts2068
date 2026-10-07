"""Build pre-shifted sprites and scripted sparse deltas for a 60-Hz cartridge."""
from pathlib import Path
import json,math,struct,subprocess,hashlib,random,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main():
    sys.path.insert(0,str(ROOT.parents[1]/'speech2ay'))
    from tsaudio.assembly import runtime
    rt=runtime().split('; dac5:')[0]
    rt=rt[rt.index('audio_init:'):].replace(' out ($ff),a\n','')
    (ROOT/'build/audio.asm').write_text(rt)
    banks={i:bytearray([255])*8192 for i in range(8)};used={i:0 for i in banks};used[4]=4096
    def allocate(data,choices=(0,1,5,6,7)):
        bank=next(i for i in choices if used[i]+len(data)<=8192)
        ptr=8192*bank+used[bank];banks[bank][used[bank]:used[bank]+len(data)]=data;used[bank]+=len(data)
        return bank,ptr
    aud=json.loads((ROOT/'assets/audio.json').read_text());audio=b'';constants=[]
    for i,a in enumerate(aud):
        constants += [f'AUDIO{i} EQU ${0xf000+len(audio):04x}',f'COUNT{i} EQU {a["count"]}']
        audio+=(ROOT/f'assets/{a["name"]}.ay').read_bytes()
    banks[2][:len(audio)]=audio;used[2]=len(audio);constants.append(f'AUDIO_SIZE EQU {len(audio)}')
    entries={};images={}
    for kind,count,phases,w,h,pady in [('face',3,range(8),7,52,2),('ship',32,range(8),3,12,2)]:
        for pose in range(count):
            for phase in phases:
                src=np.fromfile(ROOT/f'assets/{kind}-{pose:02}-{phase}.bin',np.uint8).reshape(h,w,3)
                data=src[:,:,1].tobytes()
                bank,ptr=allocate(data)
                entries[kind,pose,phase]=(bank,ptr);images[str(ptr)]=dict(kind=kind,pose=pose,phase=phase,w=w,h=h)
    N=256;records=[];metadata=[]
    mouths=[[0]*1+[1]*4+[2]*14+[1]*6+[0]*13+[1]*8+[0]*6+[1]*3+[2]*5+[1]*13+[0]*13,[0]*1+[2]*5+[1]*11+[2]*12+[1]*24+[0]*1]
    events={30:0,160:1}
    for t in range(N):
        angle=t*2*math.pi/N
        bx=round(100+52*math.sin(angle));by=round(84-12*math.sin(2*angle))
        px=round(122+102*math.cos(angle));py=round(90+80*math.sin(angle))
        dx=-102*math.sin(angle);dy=80*math.cos(angle)
        heading=round(math.atan2(dx,-dy)*32/(2*math.pi))%32;mouth=0
        for start,clip in events.items():
            tick=t-start
            if 0<=tick<aud[clip]['count']:
                timing=mouths[clip];mouth=timing[tick*len(timing)//aud[clip]['count']]
        rectangles=[];record=bytearray()
        for kind,pose,x,y,w,h,pady in [('face',mouth,bx,by,7,52,0),('ship',heading,px,py,3,12,0)]:
            bank,ptr=entries[kind,pose,x%8];xx=x//8;yy=y-pady
            assert 0<=xx<=32-w and 0<=yy<=192-h
            record+=bytes([xx,yy,w,h,16|(1<<bank)])+struct.pack('<H',ptr)
            rectangles.append((xx,yy,w,h))
        a,b=rectangles
        assert a[0]+a[2]<=b[0] or b[0]+b[2]<=a[0] or a[1]+a[3]<=b[1] or b[1]+b[3]<=a[1], (t,a,b)
        record+=bytes([events.get(t,255),int(t<N//2)]);records.append(record)
        metadata.append(dict(face=[bx,by,mouth],ship=[px,py,heading],rectangles=rectangles,event=events.get(t,255)))
    # Sparse color deltas carry absolute display addresses. Empty streams are shared.
    attr_cache={};boot=[]
    for kind,w,h in [('face',7,52),('ship',3,12)]:
        layers=[]
        for frame in metadata:
            x,y,pose=frame[kind]
            src=np.fromfile(ROOT/f'assets/{kind}-{pose:02}-{x%8}.bin',np.uint8).reshape(h,w,3)
            a=np.zeros((192,32),np.uint8)
            a[y:y+h,x//8:x//8+w]=np.where(src[:,:,0]!=255,src[:,:,2]^7,0)
            layers.append(a)
        for y,x in np.argwhere(layers[-1]):
            addr=0x6000+((int(y)&192)<<5)+((int(y)&7)<<8)+((int(y)&56)<<2)+int(x)
            boot += [f' ld hl,${addr:04x}',f' ld (hl),{int(layers[-1][y,x])^7}']
        for t in range(N):
            delta=layers[t]^layers[t-1];ys,xs=np.nonzero(delta)
            ox=int(xs.min()) if len(xs) else 0;oy=int(ys.min()) if len(ys) else 0
            data=bytearray([len(ys)])
            for y,x in zip(ys,xs):
                addr=0x6000+((int(y)&192)<<5)+((int(y)&7)<<8)+((int(y)&56)<<2)+int(x)
                data.extend([addr&255,addr>>8,int(delta[y,x])])
            key=bytes(data)
            if key not in attr_cache:attr_cache[key]=allocate(key,(2,5,6,7,0,1,4))
            bank,ptr=attr_cache[key]
            records[t]+=bytes([16|(1<<bank)])+struct.pack('<H',ptr)+bytes([ox,oy])
    (ROOT/'build/initial-attributes.asm').write_text('\n'.join(boot))
    rng=random.Random(1983)
    stars=[(rng.randrange(256),8+i*10,[0,1,3][i%3],7) for i in range(18)]
    positions=[[x,y] for x,y,_,_ in stars];star_layers=[];full_pixels=[]
    for t,frame in enumerate(metadata):
        layer=np.zeros((192,32),np.uint8);star_positions=[]
        def protected(x,y):
            return any(rx<=x//8<rx+w and ry<=y<ry+h for rx,ry,w,h in frame['rectangles'])
        for i,((x,y),(_,_,mask,_)) in enumerate(zip(positions,stars)):
            if not (t&mask):x=(x+(1 if t<N//2 else -1))%256
            if not (t&15):y=(y+(1 if t<N//2 else -1))%192
            positions[i]=[x,y];star_positions.append([x,y])
            if not protected(x,y):layer[y,x//8]|=128>>(x&7)
        star_layers.append(layer);frame['stars']=star_positions
        full=layer.copy()
        for kind,w,h in [('face',7,52),('ship',3,12)]:
            x,y,pose=frame[kind]
            source=np.fromfile(ROOT/f'assets/{kind}-{pose:02}-{x%8}.bin',np.uint8).reshape(h,w,3)
            full[y:y+h,x//8:x//8+w]=source[:,:,1]
        full_pixels.append(full)
    assert positions==[[x,y] for x,y,_,_ in stars]
    for y,x in np.argwhere(star_layers[-1]):
        addr=0x4000+((int(y)&192)<<5)+((int(y)&7)<<8)+((int(y)&56)<<2)+int(x)
        boot += [f' ld hl,${addr:04x}',f' ld (hl),{int(star_layers[-1][y,x])}']
    (ROOT/'build/initial-attributes.asm').write_text('\n'.join(boot))
    # Absolute color operations remove repeated address and rectangle scans.
    star_bytes=0
    for t,frame in enumerate(metadata):
        delta=star_layers[t]^full_pixels[t-1];ops=bytearray()
        for y,x in np.argwhere(delta):
            if any(rx<=x<rx+w and ry<=y<ry+h for rx,ry,w,h in frame['rectangles']):continue
            addr=0x4000+((int(y)&192)<<5)+((int(y)&7)<<8)+((int(y)&56)<<2)+int(x)
            ops.extend([addr&255,addr>>8,int(delta[y,x])])
        data=bytes([len(ops)//3])+ops;assert len(ops)<256
        bank,ptr=allocate(data,(2,5,6,7,0,1,4));star_bytes+=len(data)
        records[t]+=bytes([16|(1<<bank)])+struct.pack('<H',ptr)+bytes(3)
    seq=b''.join(records);assert all(len(r)==32 for r in records)
    (ROOT/'build/sequence.bin').write_bytes(seq)
    banks[3][:8192]=seq[:8192];used[3]=8192
    (ROOT/'build/sequence-tail.bin').write_bytes(seq[8192:])
    constants += [f'SEQUENCE_END EQU ${0xa000+len(seq):04x}',f'SEQUENCE_SIZE EQU {len(seq)}',f'SEQUENCE_FRAMES EQU {N}']
    (ROOT/'build/constants.asm').write_text('\n'.join(constants)+'\n')
    # Fixed-width unrolled loops consume only changed destination bytes.
    loops=[]
    for width in [3,7]:
        loops += [f'copy{width}:']
        for n in range(width):
            loops += [' ld a,(de)',' xor (hl)',f' jr z,copy{width}_{n}',' ld a,(hl)',' ld (de),a',f'copy{width}_{n}:',' inc hl',' inc e']
        loops += [' ret']
    (ROOT/'build/fast-copy.asm').write_text('\n'.join(loops))
    (ROOT/'build/stars.asm').write_text(''.join(' DB '+','.join(map(str,[x,y,0,0,mask,color,0,0]))+'\n' for x,y,mask,color in stars))
    exe=ROOT/'tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
    subprocess.run([str(exe),'--dirbol','--raw=build/bank4.bin','--sym=build/symbols.txt','src/demo.asm'],cwd=ROOT,check=True)
    code=(ROOT/'build/bank4.bin').read_bytes();assert len(code)<=4096;banks[4][:len(code)]=code
    raw=b''.join(banks.values());dck=bytes([0]+[2]*8)+raw
    for bank,data in banks.items():(ROOT/f'build/bank{bank}.bin').write_bytes(data)
    (ROOT/'build/sinistar.dck').write_bytes(dck);(ROOT/'build/sinistar-picorom.bin').write_bytes(raw)
    (ROOT/'build/fast-scene.json').write_text(json.dumps(dict(metadata=metadata,stars=stars,images=images)))
    (ROOT/'build/manifest.json').write_text(json.dumps(dict(used=used,sequence_frames=N,target_fps=3528000/58688,loop_seconds=N*58688/3528000,audio=aud,sha256=hashlib.sha256(dck).hexdigest()),indent=2))
    print('ROM use',used,'total',sum(used.values()),'star deltas',star_bytes,flush=True)
if __name__=='__main__':main()




