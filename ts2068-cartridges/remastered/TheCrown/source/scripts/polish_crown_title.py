"""Apply clean native reference credits and a constrained title reflection."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/tsvideocodec'))
from svd_ecm import ECMFrame, screen_offset


def credit_bitmap():
    asset=ROOT/'assets/intro/credits-bitmap.bin'
    tap=ROOT/'original/optional-credit-reference.tap'
    if tap.exists():
        raw=tap.read_bytes();offset=0;header=None;planes={}
        while offset<len(raw):
            size=int.from_bytes(raw[offset:offset+2],'little')
            block=raw[offset+2:offset+2+size];offset+=size+2
            assert len(block)==size and size
            checksum=0
            for value in block: checksum^=value
            assert checksum==0,'Reference TAP checksum mismatch'
            if size==19 and block[0]==0:
                header=(block[1],int.from_bytes(block[12:14],'little'),int.from_bytes(block[14:16],'little'))
            elif block[0]==255 and header:
                kind,length,address=header
                assert len(block[1:-1])==length
                if kind==3 and length==6144 and address in (0x4000,0x6000):
                    planes[address]=block[1:-1]
                header=None
        frame=ECMFrame(planes[0x4000],planes[0x6000])
        rgb=np.asarray(frame.render())
        # Preserve exact native glyph pixels, without colour diffusion or scaling.
        red=(rgb[169:, :, 0]>100)&(rgb[169:, :, 1]<40)&(rgb[169:, :, 2]<40)
        data=np.packbits(red,axis=1).tobytes()
        if not asset.exists() or asset.read_bytes()!=data: asset.write_bytes(data)
        provenance={'source':str(tap),'source_sha256':hashlib.sha256(raw).hexdigest(),
                    'credit_rows':[169,191],'credit_bitmap_sha256':hashlib.sha256(data).hexdigest()}
        (ROOT/'assets/intro/credits-provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    else:
        assert asset.exists(),'Restore the original thecrown.tap or its saved credit strip'
    data=asset.read_bytes()
    assert len(data)==23*32
    return data


def polish(frames):
    credits=credit_bitmap()
    rgb=np.asarray(Image.open(ROOT/'build/intro-eight-locked/source/frame_00.png').convert('RGB').resize((256,192),Image.Resampling.LANCZOS))
    letters=np.zeros((192,256),dtype=bool)
    for left,top,right,bottom in ((122,130,148,166),(146,133,172,169),(169,132,194,165),(190,131,224,166),(220,125,245,167)):
        letters[top:bottom,left:right]=True
    gold=(rgb[:,:,0]>145)&(rgb[:,:,1]>95)&(rgb[:,:,2]<140)&(rgb[:,:,0].astype(int)>1.35*rgb[:,:,2])&letters
    cells=gold.reshape(192,32,8).sum(axis=2)>=2
    candidates=np.argwhere(gold[125:137,232:245])
    assert len(candidates)
    yy,xx=max(candidates,key=lambda p:2*int(p[1])-int(p[0]))
    corner=(232+int(xx),125+int(yy))
    finished=[];details=[]
    positions=(None,128,153,179,204,230,None,None)
    for i,frame in enumerate(frames):
        bitmap=bytearray(frame.bitmap);attrs=bytearray(frame.attributes)
        lighting={'eye_glow':False,'chest_cells':0,'chin_shadow_cells':0}
        if i in (1,2):
            pose=np.asarray(Image.open(ROOT/f'build/intro-eight-locked/source/frame_{i:02d}.png').convert('RGB').resize((256,192),Image.Resampling.LANCZOS))
            region=pose[22:34,145:164].astype(int)
            candidates=np.argwhere((region[:,:,0]>150)&(region[:,:,1]>65)&(region[:,:,1]<190)&(region[:,:,2]<85))
            assert len(candidates),'Dragon eye not found'
            ey,ex=min(candidates,key=lambda p:(int(p[1])+145-153)**2+(int(p[0])+22-28)**2)
            ex,ey=145+int(ex),22+int(ey)
            for y in (ey,ey+1):
                a=screen_offset(y,ex//8);old=attrs[a]
                ink,paper=old&7,(old>>3)&7
                if ink in (6,7,2):
                    attrs[a]=64+8*paper+2
                    bitmap[a]|=128>>(ex%8)
                else:
                    attrs[a]=64+8*2+ink
                    bitmap[a]&=255^(128>>(ex%8))
            lighting['eye_glow']=True
            lighting['eye_pixel']=[ex,ey]
        if i in (0,2,7):
            # Only the upper wooden lid: preserve its grain and metal outlines.
            for y in range(85,93):
                for x in range(15,20):
                    a=screen_offset(y,x);old=attrs[a]
                    if old&7 not in (2,6) and (old>>3)&7 not in (2,6): continue
                    attrs[a]=old|64
                    lighting['chest_cells']+=attrs[a]!=old
        if i==3:
            # Two short dark-green scanlines below the returning lower jaw.
            for y in (66,67):
                a=screen_offset(y,17);old=attrs[a]
                ink,paper=old&7,(old>>3)&7
                ink=4 if ink in (6,7) else ink
                paper=4 if paper in (6,7) else paper
                attrs[a]=8*paper+ink
                lighting['chin_shadow_cells']+=attrs[a]!=old
        # The painted source's first credit line starts above the TAP strip.
        # Remove its red remnants while preserving the title's other colours.
        for y in range(164,169):
            for x in range(32):
                a=screen_offset(y,x)
                original=attrs[a];ink=original&7;paper=(original>>3)&7
                ink=0 if ink==2 else ink
                paper=0 if paper==2 else paper
                attrs[a]=(original&0xC0)+8*paper+ink
        for row in range(23):
            for x in range(32):
                a=screen_offset(169+row,x)
                bitmap[a]=credits[row*32+x];attrs[a]=2
        lit=0
        if positions[i] is not None:
            for y,x in np.argwhere(cells):
                y,x=int(y),int(x)
                local=np.flatnonzero(gold[y,8*x:8*x+8])
                distance=abs(8*x+float(local.mean())-positions[i]-0.22*(y-146))
                if distance>8: continue
                a=screen_offset(y,x);original=attrs[a]
                ink,paper=original&7,(original>>3)&7
                if ink!=6 and paper!=6: continue
                if distance<=5:
                    ink=7 if ink==6 else ink;paper=7 if paper==6 else paper
                attrs[a]=64+8*paper+ink
                lit+=attrs[a]!=original
        if i==6:
            # A small white cross and diagonal rays at the N's actual gold tip.
            cx,cy=corner
            star={(cx,cy)}
            for d in range(-3,4): star.update(((cx+d,cy),(cx,cy+d)))
            star.update((cx+dx,cy+dy) for dx,dy in ((-1,-1),(1,1),(-1,1),(1,-1)))
            visible=np.asarray(ECMFrame(bytes(bitmap),bytes(attrs)).render()).max(axis=2)>0
            by_cell={}
            for px,py in star:
                if 0<=px<256 and 0<=py<169:
                    by_cell.setdefault((py,px//8),set()).add(px%8)
            for (y,x),points in by_cell.items():
                a=screen_offset(y,x)
                on=visible[y,8*x:8*x+8].copy()
                for px in points: on[px]=True
                bitmap[a]=int(np.packbits(on)[0]);attrs[a]=71
            lit+=len(by_cell)
        result=ECMFrame(bytes(bitmap),bytes(attrs))
        # The credit band remains exactly identical throughout the loop.
        for row in range(23):
            for x in range(32):
                a=screen_offset(169+row,x)
                assert result.bitmap[a]==credits[row*32+x] and result.attributes[a]==2
        finished.append(result)
        details.append({'frame':i,'reflection_center_x':positions[i],'highlighted_cells':int(lit),'terminal_glint':i==6,'scene_lighting':lighting})
    assert finished[0].bitmap==finished[7].bitmap and finished[0].attributes==finished[7].attributes
    report={'credits':'Exact native red glyphs extracted from thecrown.tap','credit_rows':[169,191],
            'credits_sha256':hashlib.sha256(credits).hexdigest(),'credits_static':True,
            'reflection':'bright-gold halo and white specular sweep across CROWN','glint_corner':list(corner),
            'reflection_frames':details,'loop_seam_preserved':True}
    return finished,report
