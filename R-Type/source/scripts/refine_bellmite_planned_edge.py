"""Small legal contour touch-ups to the approved planned-edge treatment."""
import json
import numpy as np
from PIL import Image,ImageDraw
from preview_bellmite_blue_rim import ROOT,blue_rim
from preview_bellmite_detail import legal
OUT=ROOT/'build/graphics/bellmite_planned_edge_refined'

def refine(source):
    before,stats=blue_rim(source,True,True);a=np.array(before);mask=(a[:,:,3]>0).copy();rgb=a[:,:,:3];wanted=np.zeros(mask.shape,bool);trimmed=0
    for y in range(32):
        xs=np.flatnonzero(mask[y])
        if not len(xs):continue
        right=xs[-1]
        if right%8!=1 or tuple(rgb[y,right])in[(205,0,0),(255,0,0),(205,205,0),(255,255,0)]:continue
        if np.all(rgb[y,right]==[0,0,205]):continue
        # A two-pixel tip in a transparent byte needs three colours for a blue
        # rim. Trim only its outer pixel: one blue tip + black is then exact.
        mask[y,right]=False;a[y,right]=0;rgb[y,right-1]=[0,0,205];trimmed+=1
    for x in range(32):
        ys=np.flatnonzero(mask[:,x])
        if len(ys):wanted[ys[0],x]=True
    for y in range(32):
        xs=np.flatnonzero(mask[y])
        if len(xs):wanted[y,xs[-1]]=True
    blue=np.array([0,0,205]);touched=0;added=0
    for y in range(32):
        for x in range(0,32,8):
            target=wanted[y,x:x+8];visible=mask[y,x:x+8]
            if not target.any():continue
            original=rgb[y,x:x+8].copy();proposal=np.minimum(original,205);proposal[target]=blue
            colours,counts=np.unique(proposal,axis=0,return_counts=True)
            if len(colours)<=2:
                rgb[y,x:x+8]=proposal;continue
            if not visible.all():continue # black + body + rim cannot be represented
            nonblue=~np.all(proposal==blue,axis=1)
            colours,counts=np.unique(proposal[nonblue],axis=0,return_counts=True)
            if len(colours)!=2:continue
            small=int(np.argmin(counts));major=int(np.argmax(counts))
            if counts[small]!=1:continue
            minority=colours[small]
            if tuple(minority)in[(205,0,0),(205,205,0)]:continue # preserve red nodes and warm highlights
            at=np.all(proposal==minority,axis=1)
            if tuple(minority)==(205,205,205)and not np.any(at&target):continue # preserve interior whites
            proposal[at]=colours[major]
            assert len(set(map(tuple,proposal)))<=2
            added+=int((target&~np.all(original==blue,axis=1)).sum());touched+=1;rgb[y,x:x+8]=proposal
    assert int((np.asarray(before)[:,:,3]!=a[:,:,3]).sum())==trimmed
    for cell in rgb.reshape(-1,8,3):assert len(set(map(tuple,cell)))<=2
    return before,Image.fromarray(a,'RGBA'),dict(**stats,extra_rim_pixels=added+trimmed,one_pixel_body_touchups=touched,contour_rows_trimmed_one_pixel=trimmed)

def main():
    OUT.mkdir(parents=True,exist_ok=True);sources=[Image.open(ROOT/f'build/fullgame/converted/level05/descriptor{i:03d}_arcade.png').convert('RGBA')for i in [9,10,11]]
    sheet=Image.new('RGB',(780,400),(12,12,12));draw=ImageDraw.Draw(sheet);records=[];cels={'H':[],'K':[]}
    for i,source in enumerate(sources):
        old,new,stats=refine(source);records.append(dict(cel=i,**stats))
        for row,(label,im)in enumerate([('H: approved planned edge',old),('K: local contour refinement',new)]):
            key='H'if row==0 else'K';cels[key].append(im);im.save(OUT/f'{key}_sphere{i}.png');black=Image.new('RGB',(32,32));black.paste(im,mask=im.getchannel('A'));sheet.paste(black.resize((160,160),Image.Resampling.NEAREST),(i*245+20,row*200+30));draw.text((i*245+20,row*200+7),f'{label} / cel{i+1}',fill='white')
    sheet.save(OUT/'comparison.png')
    page=['<meta charset="utf-8"><title>Planned-edge refinement</title><style>body{background:#151515;color:white;font:17px sans-serif}img{max-width:100%;image-rendering:pixelated}</style><h1>Approved planned edge, local refinement</h1><p>H retained as the baseline. K trims one outer pixel on selected right-contour rows so a narrow blue tip can share a cell with black without spreading into the body. Red nodes and warm highlights are protected. Other changes are limited to legal two-colour cells. These are small silhouette touch-ups, not a wider blue outline. Offline only; no new game release or runtime performance claim.</p><img src="comparison.png">']
    for style,images in cels.items():
        canvas=Image.new('RGBA',(256,160))
        for command in reversed(json.loads((ROOT/'build/fullgame/bellmite_orbs_r44/sample_200.commands.json').read_text())):
            if command['pointer']not in [0xf3f1,0xf481,0xf511]:continue
            cel=images[[0xf3f1,0xf481,0xf511].index(command['pointer'])]
            if command['entry']in[0x8dd3,0x8e29]:cel=cel.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            if command['entry']in[0x8d65,0x8e29]:cel=cel.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            y=command['y']if command['y']<128 else command['y']-256;canvas.alpha_composite(cel,(command['x']*8,y*8))
        a=np.asarray(canvas);legal(a[:,:,:3],a[:,:,3]>0).save(OUT/f'{style}_group.png');page.append(f'<h2>{style}: sphere layer at captured game positions</h2><img width="768" src="{style}_group.png">')
    (OUT/'index.html').write_text('\n'.join(page),encoding='utf-8');(OUT/'manifest.json').write_text(json.dumps(dict(status='Offline local refinements',records=records),indent=2));print(records)
if __name__=='__main__':main()
