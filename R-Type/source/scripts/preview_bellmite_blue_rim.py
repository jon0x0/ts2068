"""Top/right dark-blue rim with explicit 8x1 feasibility checks, offline."""
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from preview_bellmite_rims import ROOT,highlight
from preview_bellmite_detail import legal
OUT=ROOT/'build/graphics/bellmite_blue_rim_feedback'

def blue_rim(source,strict,align=False):
    a=np.asarray(highlight(source,'D'));mask=(a[:,:,3]>0).copy();base=np.asarray(legal(a[:,:,:3],mask)).copy();adjusted=0
    if align:
        # On selected rows, a one-pixel expansion puts the right rim at a byte
        # boundary. The cell can then contain body+blue without black as a third.
        for y in range(mask.shape[0]):
            xs=np.flatnonzero(mask[y])
            if not len(xs):continue
            right=xs[-1]
            if right%8!=6 or right+1>=mask.shape[1]:continue
            x=right//8*8;proposal=np.minimum(base[y,x:x+8],205).copy();proposal[-1]=[0,0,205]
            if len(set(map(tuple,proposal)))<=2:
                base[y,x:x+8]=proposal;mask[y,right+1]=True;adjusted+=1
    wanted=np.zeros(mask.shape,bool)
    for x in range(mask.shape[1]):
        ys=np.flatnonzero(mask[:,x])
        if len(ys):wanted[ys[0],x]=True
    for y in range(mask.shape[0]):
        xs=np.flatnonzero(mask[y])
        if len(xs):wanted[y,xs[-1]]=True
    used=np.zeros_like(mask)
    for y in range(mask.shape[0]):
        for x in range(0,mask.shape[1],8):
            sl=slice(x,x+8);rim=wanted[y,sl]
            if not rim.any():continue
            cell=base[y,sl].copy();normal=np.minimum(cell,205);normal[rim]=[0,0,205]
            if len(set(map(tuple,normal)))<=2:
                base[y,sl]=normal;used[y,sl]=rim
            elif not strict:
                # Force blue, exposing the edge-cell tradeoff. Transparent rows
                # require black+blue, so adjacent body pixels become blue too.
                visible=mask[y,sl]
                if not visible.all():normal[:]=0;normal[visible]=[0,0,205]
                else:
                    body=normal[~rim];colours,counts=np.unique(body,axis=0,return_counts=True);dominant=colours[np.argmax(counts)];normal[:]=dominant;normal[rim]=[0,0,205]
                base[y,sl]=normal;used[y,sl]=rim
    for cell in base.reshape(-1,8,3):assert len(set(map(tuple,cell)))<=2
    assert not base[~mask].any();assert base[mask].any(1).all()
    return Image.fromarray(np.dstack([base,mask.astype('uint8')*255]),'RGBA'),dict(requested_pixels=int(wanted.sum()),blue_rim_pixels=int(used.sum()),rejected_pixels=int((wanted&~used).sum()),outline_rows_expanded_one_pixel=adjusted)

def main():
    OUT.mkdir(parents=True,exist_ok=True);sources=[Image.open(ROOT/f'build/fullgame/converted/level05/descriptor{i:03d}_arcade.png').convert('RGBA')for i in [9,10,11]]
    labels={'D':'Baseline: bright rim','F':'Continuous top/right blue (colour spill)','G':'Cell-safe top/right blue (selective)','H':'Planned edge: selected rows widened 1px','J':'Dark-blue edges instead of white'}
    sheet=Image.new('RGB',(850,950),(12,12,12));draw=ImageDraw.Draw(sheet);report=[]
    page=['<meta charset="utf-8"><title>Bellmite top/right blue rim</title><style>body{background:#151515;color:white;font:17px sans-serif}img{max-width:100%;image-rendering:pixelated}</style><h1>Dark-blue top and right edges</h1><p>D is the bright-rim baseline. F forces blue around the top/right: boundary cells sometimes have to turn adjoining body pixels blue because black background plus body plus blue would require three colours. G keeps only legal one-pixel blue segments and leaves the conflicting areas unchanged. Adding dark blue also requires normal brightness in that cell. These are offline alternatives, not a game release.</p><img src="spheres.png">']
    for row,(style,label)in enumerate(labels.items()):
        draw.text((5,row*190+5),label,fill='white')
        cels=[]
        for i,source in enumerate(sources):
            if style=='D':
                a=np.asarray(highlight(source,'D'));cel=Image.fromarray(np.dstack([np.asarray(legal(a[:,:,:3],a[:,:,3]>0)),a[:,:,3]]),'RGBA');stats={}
            else:
                cel,stats=blue_rim(source,style in ['G','H','J'],style in ['H','J'])
                if style=='J':
                    a=np.array(cel);visible=a[:,:,3]>0
                    eroded=np.asarray(Image.fromarray(visible.astype('uint8')*255).filter(ImageFilter.MinFilter(3)))>0
                    edge=visible&~eroded
                    white=(a[:,:,:3].min(2)>180)&edge
                    a[white,:3]=[0,0,205]
                    # Re-plan shared-cell colours after replacing residual white edge pixels.
                    fitted=np.asarray(legal(a[:,:,:3],visible));cel=Image.fromarray(np.dstack([fitted,a[:,:,3]]),'RGBA')
            cel.save(OUT/f'{style}_sphere{i}.png');im=Image.new('RGB',cel.size);im.paste(cel,mask=cel.getchannel('A'));sheet.paste(im.resize((160,160),Image.Resampling.NEAREST),(245+i*195,row*190+25));cels.append(cel);report.append(dict(style=style,cel=i,**stats))
        canvas=Image.new('RGBA',(256,160))
        for command in reversed(json.loads((ROOT/'build/fullgame/bellmite_orbs_r44/sample_200.commands.json').read_text())):
            if command['pointer']not in [0xf3f1,0xf481,0xf511]:continue
            cel=cels[[0xf3f1,0xf481,0xf511].index(command['pointer'])]
            if command['entry']in [0x8dd3,0x8e29]:cel=cel.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            if command['entry']in [0x8d65,0x8e29]:cel=cel.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            y=command['y']if command['y']<128 else command['y']-256;canvas.alpha_composite(cel,(command['x']*8,y*8))
        a=np.asarray(canvas);legal(a[:,:,:3],a[:,:,3]>0).save(OUT/f'{style}_group.png');page.append(f'<h2>{label}</h2><img width="768" src="{style}_group.png">')
    page.insert(2,'<p>H tests deliberate edge planning: selected rows widen by one pixel to place the right edge on a byte boundary, only when body+blue remain a legal pair. This changes the silhouette slightly; the other variants preserve it.</p>')
    sheet.save(OUT/'spheres.png');(OUT/'index.html').write_text('\n'.join(page),encoding='utf-8');(OUT/'manifest.json').write_text(json.dumps(dict(status='Offline blue-rim alternatives',records=report),indent=2));print(OUT/'index.html');print(report)
if __name__=='__main__':main()
