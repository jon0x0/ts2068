"""Extract original arcade pixels; convert to legal TS2068 ECM sprites."""
from pathlib import Path
import re, json, sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parents[1]/'speech2ay'))
from tsaudio.codecs import encode

def extract():
    text=(ROOT/'references/IMAGE.ASM').read_text()
    mem=[]; labels={}; descriptors={}
    for line in text.splitlines():
        line=line.split(';')[0]
        m=re.match(r'^(\w+)\s+',line)
        if m: labels[m[1]]=len(mem)
        if 'FCB' in line:
            vals=line.split('FCB')[1].strip().split(',')
            mem.extend(int(v.strip()[1:],16) if v.strip().startswith('$') else int(v.strip()) for v in vals)
        if m and 'FDB' in line:
            d=re.search(r'FDB\s+\$([0-9A-F]+),(\w+)',line)
            if d: descriptors[m[1]]=(int(d[1],16)>>8,int(d[1],16)&255,d[2])
    def piece(name,mirror=False,animated=False):
        h,w,label=descriptors[name]; pos=labels[label]; a=np.zeros((h*2,w),dtype=np.uint8)
        for x in range(w):
            # MODSINI walks backwards through right pieces; animation reflects at center.
            col=(min(x,w-1-x) if animated else -x if mirror else x)
            for y in range(h):
                v=mem[pos+col*h+y];a[y*2,x]=v>>4;a[y*2+1,x]=v&15
        return a
    table=(ROOT/'references/SAMTABLE.ASM').read_text().split('PIECETB FDB')[1].split('PIECEND')[0]
    pieces=re.findall(r'(\w+),([0-9A-F]{4})',table)
    base=np.zeros((52,49),dtype=np.uint8)
    for name,offset in pieces:
        y,x=int(offset[:2],16),int(offset[2:],16)
        p=piece(name,mirror=name.endswith('R'))
        h,w=p.shape
        area=base[y:y+h,x:x+w]; p=p[:area.shape[0],:area.shape[1]]; area[p!=0]=p[p!=0]
    faces=[]
    for mouth in ['AMOUT1','AMOUT3','AMOUT2']:
        a=base.copy()
        for name,y,x in [(mouth,6,12),('AEYE1',26,12)]:
            p=piece(name,animated=True);h,w=p.shape
            a[y:y+h,x:x+w]=p
        faces.append(np.flipud(a))
    ships=[]
    dims=re.findall(r'\$([0-9A-F]{4}),IPLAY(\d+),',text.split('RADIX   10')[0])
    for size,n in dims:
        h,w=int(size[:2],16),int(size[2:],16)
        descriptors['ship']=(h,w,'IPLAY'+n)
        p=np.flipud(piece('ship')); a=np.zeros((12,12),np.uint8)
        a[(12-p.shape[0])//2:(12-p.shape[0])//2+p.shape[0],(12-p.shape[1])//2:(12-p.shape[1])//2+p.shape[1]]=p
        ships.append(a)
    return faces,ships

ARCADE=[0o000,0o377,0o277,0o256,0o255,0o244,0o232,0,0,0o311,0o120,0o113,0o005,0o007,0o007,0o067]
RGB=np.array([[(v&7)*255/7,((v>>3)&7)*255/7,((v>>6)&3)*85] for v in ARCADE])
PALETTE=np.array([[205*((i>>1)&1),205*((i>>2)&1),205*(i&1)] for i in range(8)]+[[255*((i>>1)&1),255*((i>>2)&1),255*(i&1)] for i in range(8)])

def pack(a,phase,width):
    padded=np.zeros((a.shape[0],width*8),np.uint8);padded[:,phase:phase+a.shape[1]]=a
    out=bytearray();preview=np.zeros((*padded.shape,3),np.uint8)
    for y,row in enumerate(padded):
        for x in range(width):
            indices=row[x*8:x*8+8]; pixels=RGB[indices];best=None
            # Normal luminance keeps black truly black on the TS2068 analog model.
            for bright in range(1):
                for paper in range(8):
                    for ink in range(paper+1,8):
                        if (paper,ink) not in [(0,7),(0,2),(2,7),(0,6),(6,7),(0,1),(1,7)]:continue
                        colors=PALETTE[[bright*8+paper,bright*8+ink]]
                        errors=((pixels[:,None,:]-colors[None,:,:])**2).sum(axis=2)
                        # Preserve black exterior and tiny features; no smoothing or scaling.
                        v=colors[1]-colors[0]; t=np.clip(((pixels-colors[0])*v).sum(axis=1)/(v*v).sum(),0,1)
                        thresholds=(np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])[y%4,(np.arange(8)+x*8-phase)%4]+0.5)/16
                        choice=(t>thresholds).astype(int)
                        score=((pixels-(colors[0]+t[:,None]*v))**2).sum()+0.12*errors.min(axis=1).sum()
                        if np.any(indices==0) and paper!=0:score+=1e8
                        if best is None or score<best[0]:best=(score,bright,paper,ink,choice,colors)
            _,bright,paper,ink,choice,colors=best
            bits=sum(int(v)<<(7-i) for i,v in enumerate(choice));attr=bright*64+paper*8+ink
            mask=sum(int(v==0)<<(7-i) for i,v in enumerate(indices))
            out.extend([mask,bits,attr]);preview[y,x*8:x*8+8]=colors[choice]
    return bytes(out),Image.fromarray(preview)

def main():
    faces,ships=extract();sheet=Image.new('RGB',(49*3,52))
    for i,a in enumerate(faces):sheet.paste(Image.fromarray(RGB[a].astype('uint8')),(i*49,0))
    sheet.resize((588,208),Image.Resampling.NEAREST).save(ROOT/'assets/arcade-faces.png')
    blobs=[];meta=[]
    for kind,frames,width in [('face',faces,7),('ship',ships,3)]:
        for i,a in enumerate(frames):
            for phase in range(8):
                raw,im=pack(a,phase,width)
                path=f'{kind}-{i:02}-{phase}.bin';(ROOT/'assets'/path).write_bytes(raw)
                meta.append(dict(kind=kind,frame=i,phase=phase,width=width,height=len(a),file=path,size=len(raw)))
                if kind=='face' and phase==0:im.resize((224,208),Image.Resampling.NEAREST).save(ROOT/f'assets/ecm-face-{i}.png')
    (ROOT/'assets/sprites.json').write_text(json.dumps(meta,indent=2))
    print(len(ships),'original headings, eight pixel phases; speech is prepared separately.')
if __name__=='__main__':main()
