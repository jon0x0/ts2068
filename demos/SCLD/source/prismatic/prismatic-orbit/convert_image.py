"""Image conversion constrained to the native seven-update-per-line schedule."""
from pathlib import Path
import argparse,itertools,json,struct,zlib
import numpy as np
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parent
# Match Retro Pixel Converter's Timex palette, including BRIGHT dark gray.
PALETTE=np.array([(0,0,0),(1,0,206),(207,1,0),(207,1,206),(0,207,21),(1,207,207),(207,207,21),(207,207,207),
                  (96,96,96),(2,0,253),(255,2,1),(255,2,253),(0,255,28),(2,255,255),(255,255,29),(255,255,255)],dtype=np.uint8)
def linear(v):return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
PAL=linear(PALETTE.astype(float)/255)
PAIRS=np.array([(a+bright,b+bright) for bright in (0,8) for a,b in itertools.combinations_with_replacement(range(8),2)])
ATTR=np.array([(a&7)|((b&7)<<3)|(64 if a>=8 else 0) for a,b in PAIRS],dtype=np.uint8)
COMBOS=np.array([[c+4*i for i,c in enumerate(cs)] for cs in itertools.combinations(range(8),7)])
def row(y):return ((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
def pair_fit(pixels):
    # Fit the linear-light color segment, including the mixtures a spatial
    # dither can render, rather than selecting pairs by nearest solid colors.
    a=PAL[PAIRS[:,0]];delta=PAL[PAIRS[:,1]]-a;norm=(delta*delta).sum(axis=-1)
    dots=np.einsum('...pc,kc->...pk',pixels,delta)-(a*delta).sum(axis=-1)
    blend=np.clip(dots/np.maximum(norm,1e-20),0,1)
    dist=((pixels[...,None,:]-a)**2).sum(axis=-1)
    errors=np.maximum(0,dist-2*blend*dots+blend*blend*norm).sum(axis=-2)
    idx=errors.argmin(axis=-1)
    return idx,np.take_along_axis(errors,idx[...,None],axis=-1)[...,0]
def read_reference(path):
    data=Path(path).read_bytes();blocks=[];at=0
    while at<len(data):
        n=struct.unpack_from('<H',data,at)[0];b=data[at+2:at+2+n];at+=n+2
        assert len(b)==n and n>=2 and np.bitwise_xor.reduce(np.frombuffer(b,dtype=np.uint8))==0,'Invalid TAP block/checksum'
        blocks.append(b)
    assert at==len(data) and len(blocks)==4,'Expected two CODE header/data pairs'
    planes={}
    for h,b in zip(blocks[::2],blocks[1::2]):
        assert h[0]==0 and h[1]==3 and len(b)==6146 and b[0]==255,'Expected ECM CODE blocks'
        planes[struct.unpack_from('<H',h,14)[0]]=b[1:-1]
    bitmap,attrs=planes[0x4000],planes[0x6000];assert not any(a&128 for a in attrs),'FLASH attributes unsupported in comparison'
    indices=np.empty((192,256),np.uint8);bits=np.empty_like(indices);attributes=np.empty((192,32),np.uint8)
    for y in range(192):
        for c in range(32):
            k=row(y)+c;a=attrs[k];attributes[y,c]=a
            for b in range(8):
                on=bool(bitmap[k]&(128>>b));bits[y,c*8+b]=on;indices[y,c*8+b]=((a&7) if on else ((a>>3)&7))+(8 if a&64 else 0)
    return bitmap,attrs,indices,bits,attributes
def convert(path,method='floyd',strength=1.0,fit='contain',reference=None):
    src=Image.open(path).convert('RGB')
    if fit=='contain':
        sized=ImageOps.contain(src,(256,192),Image.Resampling.LANCZOS)
        image=Image.new('RGB',(256,192));image.paste(sized,((256-sized.width)//2,(192-sized.height)//2))
    elif fit=='crop':image=ImageOps.fit(src,(256,192),Image.Resampling.LANCZOS)
    else:image=src.resize((256,192),Image.Resampling.LANCZOS)
    rgb=linear(np.asarray(image).astype(float)/255);cells=rgb.reshape(192,32,8,3)
    ref=read_reference(reference) if reference else None
    original_rgb=rgb.copy()
    if ref:
        # Preserve the supplied conversion's local color/brightness grade,
        # while recovering sub-cell variation from the original photograph.
        reference_cells=PAL[ref[2]].reshape(192,32,8,3)
        cells=np.clip(cells+reference_cells.mean(axis=2,keepdims=True)-cells.mean(axis=2,keepdims=True),0,1)
        rgb=cells.reshape(192,256,3)
    base,baseerr=pair_fit(cells);halves,halferr=pair_fit(cells.reshape(192,32,2,4,3))
    gains=np.maximum(0,baseerr-halferr.sum(axis=-1))
    choices=COMBOS[gains[:,COMBOS].sum(axis=-1).argmax(axis=-1)]
    result={};pred={}
    for dynamic in (False,True):
        attr0=(ref[4].copy() if ref else ATTR[base].copy());attr1=attr0.copy();pairs0=base.copy();pairs1=base.copy()
        selected=np.zeros((192,32),bool)
        if dynamic:
            for y in range(192):
                for c in choices[y]:
                    selected[y,c]=True
                    pairs0[y,c]=halves[y,c,0];pairs1[y,c]=halves[y,c,1]
                    attr0[y,c]=ATTR[pairs0[y,c]];attr1[y,c]=ATTR[pairs1[y,c]]
        work=rgb.copy();bits=np.zeros((192,256),np.uint8);indices=np.zeros_like(bits)
        for y in range(192):
            reverse=(y&1)==1 and method in ('floyd','atkinson');direction=-1 if reverse else 1
            for x in (range(255,-1,-1) if reverse else range(256)):
                c=x//8;pi=pairs0[y,c] if x%8<4 else pairs1[y,c];ink,paper=PAIRS[pi]
                value=work[y,x].copy()
                if method=='bayer':
                    bayer=((0,8,2,10),(12,4,14,6),(3,11,1,9),(15,7,13,5))
                    delta=PAL[ink]-PAL[paper];blend=float((value-PAL[paper])@delta)/max(float(delta@delta),1e-20)
                    threshold=.5+strength*((bayer[y%4][x%4]+.5)/16-.5)
                    on=blend>threshold
                else:on=((value-PAL[ink])**2).sum()<((value-PAL[paper])**2).sum()
                color=ink if on else paper
                if ref and not selected[y,c]:on=bool(ref[3][y,x]);color=int(ref[2][y,x])
                bits[y,x]=on;indices[y,x]=color
                if method not in ('floyd','atkinson'):continue
                if ref and not selected[y,c]:continue
                error=(value-PAL[color])*strength
                fan=[(direction,0,7/16),(-direction,1,3/16),(0,1,5/16),(direction,1,1/16)] if method=='floyd' else [(direction,0,1/8),(2*direction,0,1/8),(-direction,1,1/8),(0,1,1/8),(direction,1,1/8),(0,2,1/8)]
                for dx,dy,weight in fan:
                    xx=x+dx;yy=y+dy
                    if 0<=xx<256 and yy<192 and (not ref or selected[yy,xx//8]):work[yy,xx]+=error*weight
        bitmap=bytearray(6144);attrs=bytearray(6144)
        for y in range(192):
            for c in range(32):
                k=row(y)+c;bitmap[k]=sum((128>>b) for b in range(8) if bits[y,c*8+b]);attrs[k]=int(attr0[y,c])
        name='dynamic' if dynamic else 'ecm';result[name]=(bitmap,attrs)
        (ROOT/(name+'-bitmap.bin')).write_bytes(bitmap);(ROOT/(name+'-attributes.bin')).write_bytes(attrs)
        Image.fromarray(PALETTE[indices]).resize((768,576),Image.Resampling.NEAREST).save(ROOT/(name+'-preview.png'))
        pred[name]=indices;np.save(ROOT/(name+'-indices.npy'),indices)
        if dynamic:
            schedule=[dict(columns=[int(c) for c in choices[y]],old=[int(attr0[y,c]) for c in choices[y]],new=[int(attr1[y,c]) for c in choices[y]]) for y in range(192)]
            (ROOT/'schedule.json').write_text(json.dumps(schedule,indent=2))
            records=bytes(v for s in schedule for key in ('columns','old','new') for v in s[key])
            payload=bytes(bitmap)+bytes(attrs)+records
            header=struct.pack('<4sBBBBHHHHIIII',b'TDEC',2,7,1,['none','floyd','atkinson','bayer'].index(method),256,192,192,4,6144,6144,len(records),zlib.crc32(payload))
            (ROOT/'image.tdec').write_bytes(header+payload)
    mse={name:float(((PAL[index]-rgb)**2).mean()) for name,index in pred.items()}
    def averaged(v):return v.reshape(96,2,128,2,3).mean(axis=(1,3))
    averaged_mse={name:float(((averaged(PAL[index])-averaged(rgb))**2).mean()) for name,index in pred.items()}
    enhanced=sum(len(set(pred['dynamic'][y,c*8:c*8+8]))>2 for y in range(192) for c in choices[y])
    image.save(ROOT/'scaled-input.png')
    report=dict(source=Path(path).name,referenceTap=Path(reference).name if reference else None,referenceToneMatching='per-cell mean color matched; photograph supplies sub-cell variation' if ref else None,unchangedOutsideScheduledCells=bool(ref),width=256,height=192,fit=fit,dither=method,ditherStrength=strength,pairSearch='linear-light segment coverage',scheduledCells=1344,totalCells=6144,cellsWithMoreThanTwoColors=int(enhanced),errorMetricTarget='reference-tone-matched photograph' if ref else 'photograph',linearRgbMse=mse,averaged2x2LinearRgbMse=averaged_mse,relativeAveragedMseReduction=1-averaged_mse['dynamic']/averaged_mse['ecm'],palette='Retro Pixel Converter Timex palette; BRIGHT black is gray',schedule='seven cells per row, columns 0..31, separation at least five cells',hardwareVerified=False)
    (ROOT/'conversion.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('image');p.add_argument('--reference',help='Existing ECM image TAP to preserve outside scheduled cells');p.add_argument('--dither',choices=['floyd','atkinson','bayer','none'],default='floyd');p.add_argument('--strength',type=float,default=1.0);p.add_argument('--fit',choices=['contain','crop','stretch'],default='contain');a=p.parse_args();convert(a.image,a.dither,a.strength,a.fit,a.reference)
