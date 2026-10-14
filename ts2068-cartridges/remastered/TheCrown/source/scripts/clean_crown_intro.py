"""Suppress unsupported and isolated ECM changes while preserving motion/glints.

The locked source sequence remains the reference. Filtering acts on paired
8x1 bitmap/attribute cells; it never blurs artwork or changes the key pose.
"""
from pathlib import Path
from collections import Counter
import json
import sys
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/tsvideocodec'))
from svd_ecm import ECMFrame, screen_offset
from polish_crown_title import polish


def components(mask):
    seen=np.zeros_like(mask,dtype=bool)
    groups=[]
    for y,x in np.argwhere(mask):
        if seen[y,x]: continue
        todo=[(int(y),int(x))];seen[y,x]=True;group=[]
        while todo:
            yy,xx=todo.pop();group.append((yy,xx))
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    ny,nx=yy+dy,xx+dx
                    if 0<=ny<192 and 0<=nx<32 and mask[ny,nx] and not seen[ny,nx]:
                        seen[ny,nx]=True;todo.append((ny,nx))
        groups.append(group)
    return groups


def dilate(mask):
    padded=np.pad(mask,1)
    return np.logical_or.reduce([padded[dy:dy+192,dx:dx+32] for dy in range(3) for dx in range(3)])


def build_sequence():
    original=ROOT/'build/intro-eight-locked/codec/sequence'
    source=ROOT/'build/intro-eight-locked/source'
    out=ROOT/'build/intro-eight-clean'
    sequence=out/'sequence';sequence.mkdir(parents=True,exist_ok=True)
    frames=[ECMFrame((original/f'frame_{i:05d}.pix').read_bytes(),(original/f'frame_{i:05d}.atr').read_bytes()) for i in range(8)]
    rgb=[np.asarray(Image.open(source/f'frame_{i:02d}.png').convert('RGB').resize((256,192),Image.Resampling.LANCZOS),dtype=np.int16) for i in range(8)]
    offsets=np.array([[screen_offset(y,x) for x in range(32)] for y in range(192)])
    base=frames[0]
    basepix=np.frombuffer(base.bitmap,dtype=np.uint8)[offsets]
    baseatr=np.frombuffer(base.attributes,dtype=np.uint8)[offsets]
    glints=np.zeros((192,256),dtype=bool)
    # The original chest metal/cave-edge lighting zones, scaled from 512x384.
    for x,y,r,b in ((224,174,350,183),(259,177,283,205),(225,184,237,235),(341,183,351,235),(183,55,206,73)):
        glints[y//2:(b+1)//2+1,max(0,x//2-1):min(256,(r+1)//2+2)]=True
    protected=glints.reshape(192,32,8).any(axis=2)
    cleaned=[];reports=[];heat=np.zeros((192,32),dtype=np.int16)
    for i,frame in enumerate(frames):
        pix=np.frombuffer(frame.bitmap,dtype=np.uint8)[offsets].copy()
        atr=np.frombuffer(frame.attributes,dtype=np.uint8)[offsets].copy()
        delta=np.abs(rgb[i]-rgb[0]).max(axis=2).reshape(192,32,8)
        support=(delta>=28).sum(axis=2)>=2
        # Single-cell source changes do not justify an independently animated
        # dither pattern. Keep coherent motion, then pad its edges by one cell.
        coherent=np.zeros_like(support)
        for group in components(support):
            if len(group)>=4:
                yy,xx=zip(*group);coherent[yy,xx]=True
        allowed=dilate(coherent)|protected
        allowed[121:]=False
        changed=(pix!=basepix)|(atr!=baseatr)
        reset=changed&~allowed
        pix[reset]=basepix[reset];atr[reset]=baseatr[reset]
        # Eliminate remaining small ECM islands unless they carry a deliberate
        # glint or are attached to strongly supported source motion.
        isolated=0
        for group in components((pix!=basepix)|(atr!=baseatr)):
            yy,xx=zip(*group)
            if len(group)<=3 and not protected[yy,xx].any() and not coherent[yy,xx].any():
                pix[yy,xx]=basepix[yy,xx];atr[yy,xx]=baseatr[yy,xx]
                reset[yy,xx]=True;isolated+=len(group)
        bitmap=bytearray(frame.bitmap);attrs=bytearray(frame.attributes)
        for y,x in np.argwhere(reset):
            a=int(offsets[y,x]);bitmap[a]=base.bitmap[a];attrs[a]=base.attributes[a]
        result=ECMFrame(bytes(bitmap),bytes(attrs))
        if i in (0,7):
            assert result.bitmap==frame.bitmap and result.attributes==frame.attributes
        assert np.array_equal(pix[protected],np.frombuffer(frame.bitmap,dtype=np.uint8)[offsets][protected])
        assert np.array_equal(atr[protected],np.frombuffer(frame.attributes,dtype=np.uint8)[offsets][protected])
        cleaned.append(result);heat+=reset
        remaining=(pix!=basepix)|(atr!=baseatr)
        reports.append({'frame':i,'changed_cells_before':int(changed.sum()),'changed_cells_after':int(remaining.sum()),
                        'reset_cells':int(reset.sum()),'remaining_islands_removed':isolated,
                        'small_components_before':sum(len(g)<=3 for g in components(changed)),
                        'small_components_after':sum(len(g)<=3 for g in components(remaining)),
                        'glint_cells_preserved':True})
    # A coordinate can be on a moving object yet stay still between two poses.
    # Join those source-equivalent temporal states and reuse one ECM cell pair.
    transition=[]
    for i in range(8):
        delta=np.abs(rgb[i]-rgb[i-1]).max(axis=2).reshape(192,32,8)
        support=(delta>=28).sum(axis=2)>=2
        coherent=np.zeros_like(support)
        for group in components(support):
            if len(group)>=4:
                yy,xx=zip(*group);coherent[yy,xx]=True
        transition.append(dilate(coherent)|protected)
    pix=np.array([np.frombuffer(f.bitmap,dtype=np.uint8)[offsets] for f in cleaned])
    atr=np.array([np.frombuffer(f.attributes,dtype=np.uint8)[offsets] for f in cleaned])
    temporal=0
    for y in range(192):
        for x in range(32):
            if protected[y,x]: continue
            groups=[{i} for i in range(8)]
            for i in range(8):
                if transition[i][y,x]: continue
                a=next(g for g in groups if i in g)
                b=next(g for g in groups if (i-1)%8 in g)
                if a is b: continue
                merged=a|b
                samples=np.array([rgb[j][y,8*x:8*x+8] for j in sorted(merged)])
                # Avoid merging a gradual real movement through a long chain
                # of individually small differences.
                span=(samples.max(axis=0)-samples.min(axis=0)).max(axis=1)
                if (span>=48).sum()>=2: continue
                a.update(b);groups.remove(b)
            for group in groups:
                members=sorted(group)
                if 0 in group:
                    pair=(int(basepix[y,x]),int(baseatr[y,x]))
                else:
                    pair=Counter((int(pix[j,y,x]),int(atr[j,y,x])) for j in members).most_common(1)[0][0]
                for j in members:
                    if (int(pix[j,y,x]),int(atr[j,y,x]))!=pair:
                        temporal+=1;heat[y,x]+=1
                    pix[j,y,x],atr[j,y,x]=pair
    for i,frame in enumerate(frames):
        bitmap=bytearray(frame.bitmap);attrs=bytearray(frame.attributes)
        for y in range(192):
            for x in range(32):
                a=int(offsets[y,x]);bitmap[a]=int(pix[i,y,x]);attrs[a]=int(atr[i,y,x])
        result=ECMFrame(bytes(bitmap),bytes(attrs));cleaned[i]=result
        if i in (0,7): assert result.bitmap==frame.bitmap and result.attributes==frame.attributes
        assert np.array_equal(pix[i][protected],np.frombuffer(frame.bitmap,dtype=np.uint8)[offsets][protected])
        assert np.array_equal(atr[i][protected],np.frombuffer(frame.attributes,dtype=np.uint8)[offsets][protected])
        result.write(sequence/f'frame_{i:05d}')
        result.render().save(sequence/f'frame_{i:05d}_preview.png')
        originalpix=np.frombuffer(frame.bitmap,dtype=np.uint8)[offsets]
        originalatr=np.frombuffer(frame.attributes,dtype=np.uint8)[offsets]
        reports[i]['stabilized_cell_instances']=int(((pix[i]!=originalpix)|(atr[i]!=originalatr)).sum())
        reports[i]['changed_cells_after']=int(((pix[i]!=basepix)|(atr[i]!=baseatr)).sum())
        reports[i]['small_components_after']=sum(len(g)<=3 for g in components((pix[i]!=basepix)|(atr[i]!=baseatr)))
    assert cleaned[0].bitmap==cleaned[7].bitmap and cleaned[0].attributes==cleaned[7].attributes
    cleaned,title_report=polish(cleaned)
    for i,frame in enumerate(cleaned):
        frame.write(sequence/f'frame_{i:05d}')
        frame.render().save(sequence/f'frame_{i:05d}_preview.png')
    # Intentional title reflection is applied after stationary-cell cleanup.
    report={'method':'source-supported motion, small-island suppression and temporal state locking','source_difference_threshold':28,
            'source_pixels_required':2,'minimum_source_component_cells':4,'motion_edge_padding_cells':1,
            'frames':reports,'reset_cell_instances':sum(r['reset_cells'] for r in reports),
            'temporal_corrections':temporal,'stabilized_cell_instances':sum(r['stabilized_cell_instances'] for r in reports),
            'full_resolution':True,'key_pose_unchanged':True,'exact_loop_seam':True,'glints_preserved':True}
    report['title_finish']=title_report
    (out/'stability.json').write_text(json.dumps(report,indent=2)+'\n')
    palette=cleaned[0].render().quantize(colors=256)
    gif=[f.render().quantize(palette=palette,dither=Image.Dither.NONE) for f in cleaned]
    gif[0].save(out/'the_crown_ecm_preview.gif',save_all=True,append_images=gif[1:],duration=200,loop=0,optimize=False,disposal=1)
    heatimg=np.zeros((192,256,3),dtype=np.uint8)
    heatimg[:,:,0]=np.repeat(np.minimum(heat*40,255).astype(np.uint8),8,axis=1)
    Image.fromarray(heatimg).resize((768,576),Image.Resampling.NEAREST).save(out/'removed-change-map.png')
    print(json.dumps(report,indent=2),flush=True)
    return sequence


if __name__=='__main__': build_sequence()
