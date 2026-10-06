"""Build exact scripted ECM frames and assess a precomputed XOR stream."""
from pathlib import Path
import math,json,random,zlib
import numpy as np
from prepare_assets import extract,pack
ROOT=Path(__file__).resolve().parents[1]
N=384
def sprites():
    faces,ships=extract();result={}
    for kind,frames,width in [('face',faces,7),('ship',ships,3)]:
        for i,a in enumerate(frames):
            for phase in range(8):
                p=ROOT/f'assets/{kind}-{i:02}-{phase}.bin'
                if not p.exists():p.write_bytes(pack(a,phase,width)[0])
                result[kind,i,phase]=np.frombuffer(p.read_bytes(),np.uint8).reshape(len(a),width,3)
    return result
def main():
    sp=sprites();audio=json.loads((ROOT/'assets/audio.json').read_text())
    mouths=[[0]*1+[1]*4+[2]*14+[1]*6+[0]*13+[1]*8+[0]*6+[1]*3+[2]*5+[1]*13+[0]*13,
            [0]*1+[2]*5+[1]*11+[2]*12+[1]*24+[0]*1]
    rng=random.Random(1983)
    stars=[(rng.randrange(256),rng.randrange(8,184),i%3,[7,5,1][i%3]) for i in range(24)]
    frames=[];meta=[];events={45:0,240:1}
    for t in range(N):
        angle=t*2*math.pi/N
        bx=round(104+68*math.sin(angle));by=round(80+35*math.sin(2*angle+.4))
        px=round(122+98*math.sin(angle+.95));py=round(92+62*math.sin(2*angle+1.2))
        dx=98*math.cos(angle+.95);dy=124*math.cos(2*angle+1.2)
        heading=round(math.atan2(dx,-dy)*32/(2*math.pi))%32
        mouth=0
        for start,clip in events.items():
            tick=t-start
            if 0<=tick<audio[clip]['count']:
                timing=mouths[clip];mouth=timing[min(len(timing)-1,tick*len(timing)//audio[clip]['count'])]
        pixels=np.zeros((192,32),np.uint8);attrs=np.full((192,32),7,np.uint8)
        for x,y,depth,color in stars:
            # Closed camera orbit gives a seamless parallax loop.
            speed=[1,.5,.25][depth]
            sx=round(x-95*speed*math.sin(angle+.95))%256
            sy=8+round(y-8-55*speed*math.sin(2*angle+1.2))%176
            pixels[sy,sx//8]|=128>>(sx&7);attrs[sy,sx//8]=color
        for kind,pose,x,y,w in [('face',mouth,bx,by,7),('ship',heading,px,py,3)]:
            spr=sp[kind,pose,x%8];h=len(spr);mask,bits,col=spr.transpose(2,0,1)
            area=pixels[y:y+h,x//8:x//8+w];ac=attrs[y:y+h,x//8:x//8+w]
            area[:]=(area&mask)|bits;ac[mask!=255]=col[mask!=255]
        frames.append(np.stack([pixels,attrs]))
        meta.append(dict(face=[bx,by,mouth],ship=[px,py,heading],event=events.get(t,255)))
    # Each record: length, screen address, XOR bytes. Zero length ends a frame.
    streams=[]
    for t,frame in enumerate(frames):
        delta=frame^frames[t-1];out=bytearray()
        for y in range(192):
            for plane in range(2):
                row=delta[plane,y];nz=np.flatnonzero(row)
                if not len(nz):continue
                lo=int(nz[0]);hi=int(nz[-1])+1
                address=(0x4000 if plane==0 else 0x6000)+((y&192)<<5)+((y&7)<<8)+((y&56)<<2)+lo
                out.extend([hi-lo,address&255,address>>8]);out.extend(row[lo:hi])
        out.append(0);streams.append(bytes(out))
    allbytes=b''.join(streams)
    (ROOT/'build/scene.frames').write_bytes(b''.join(f.tobytes() for f in frames))
    (ROOT/'build/scene.delta').write_bytes(allbytes)
    (ROOT/'build/scene.json').write_text(json.dumps(dict(frames=N,metadata=meta,lengths=list(map(len,streams)))))
    print('raw delta',len(allbytes),'zlib',len(zlib.compress(allbytes,9)),'max frame',max(map(len,streams)),flush=True)
if __name__=='__main__':main()
