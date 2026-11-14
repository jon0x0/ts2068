"""Detail/composition alternatives at captured native boss positions, offline."""
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from build_graphics import PALETTE,PAIRS,unpack
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/graphics/bellmite_detail_feedback'

def legal(rgb,visible):
    h,w,_=rgb.shape;blocks=rgb.reshape(h,w//8,8,3).reshape(-1,8,3).astype(float);mask=visible.reshape(-1,8)
    best=np.full(len(blocks),np.inf);chosen=np.zeros((len(blocks),2),np.uint8)
    for p,q in PAIRS:
        # Empty/transparent pixels stay actual black, no bright-black paper.
        valid=np.ones(len(blocks),bool)
        if p!=0:valid&=mask.all(1)
        if p%8==0:valid&=~mask.all(1)
        e=np.minimum(((blocks-PALETTE[p])**2).sum(2),((blocks-PALETTE[q])**2).sum(2)).sum(1)
        if p%8==0:e=(((blocks-PALETTE[q])**2).sum(2)*mask).sum(1)
        take=valid&(e<best);best[take]=e[take];chosen[take]=[p,q]
    p=PALETTE[chosen[:,0]];q=PALETTE[chosen[:,1]];bits=((blocks-q[:,None])**2).sum(2)<((blocks-p[:,None])**2).sum(2)
    edge=chosen[:,0]%8==0;bits[edge]=mask[edge]
    result=np.where(bits[:,:,None],q[:,None],p[:,None]).astype(np.uint8).reshape(h,w,3)
    assert not result[~visible].any()
    assert result[visible].any(1).all(),'Black pixel inside composed silhouette'
    for row in result.reshape(-1,8,3):assert len(set(map(tuple,row)))<=2
    return Image.fromarray(result)

def material(src,style):
    a=np.asarray(src.convert('RGBA'));rgb=a[:,:,:3].astype(float);mask=a[:,:,3]>=128
    l=(rgb*np.array([.2126,.7152,.0722])).sum(2)/255
    red=(rgb[:,:,0]>rgb[:,:,1]*1.25)&(rgb[:,:,0]>rgb[:,:,2]*1.25)&mask
    # Source brightness supplies actual folds, nodes and highlights; do not invent noise.
    if style=='A':colours=[4,6,7];thresholds=[.40,.62]
    elif style=='B':colours=[1,4,5,7];thresholds=[.25,.44,.65]
    else:colours=[4,5,7];thresholds=[.40,.64]
    indices=np.array(colours)[np.digitize(l,thresholds)];indices[red]=2;indices[red&(rgb.max(2)>175)]=6
    pixels=PALETTE[indices].astype('uint8');pixels[~mask]=0
    return Image.fromarray(np.dstack([pixels,mask.astype('uint8')*255]),'RGBA')

def main():
    OUT.mkdir(parents=True,exist_ok=True);capture=ROOT/'build/fullgame/bellmite_orbs_r44'
    frames={};sources=[Image.open(ROOT/f'build/fullgame/converted/level05/descriptor{i:03d}_arcade.png').convert('RGBA')for i in [9,10,11]]
    labels={'A':'A: warm green, source highlights','B':'B: deep shadows, sculpted surface','C':'C: green/cyan, restrained highlights'}
    page=['<meta charset="utf-8"><title>Bellmite detail and overlap review</title><style>body{background:#151515;color:white;font:17px sans-serif}img{max-width:100%;image-rendering:pixelated}</style><h1>Bellmite: detail and overlap review</h1><p>These are OFFLINE alternatives at captured game positions, not a new cartridge. Sphere layer only: mechanical core omitted for this comparison. Whole-sphere masks are composed in draw-priority order before choosing each final legal 8×1 pair. No error-diffusion stippling. The original arcade brightness pattern guides folds and highlights. No black inside the composed silhouette; option B uses dark blue for deeper shadows. Partial edge rows use one visible ink to preserve a solid outline.</p>']
    gallery=Image.new('RGB',(960,3*208),(12,12,12));draw=ImageDraw.Draw(gallery)
    for row,style in enumerate(labels):
        canvas=Image.new('RGBA',(256,160))
        commands=json.loads((capture/'sample_200.commands.json').read_text())
        for command in reversed(commands):
            if command['pointer']not in [0xf3f1,0xf481,0xf511]:continue
            cel=material(sources[[0xf3f1,0xf481,0xf511].index(command['pointer'])],style)
            if command['entry']in [0x8dd3,0x8e29]:cel=cel.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            if command['entry']in [0x8d65,0x8e29]:cel=cel.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            y=command['y'];y=y if y<128 else y-256
            canvas.alpha_composite(cel,(command['x']*8,y*8))
        array=np.asarray(canvas);mask=array[:,:,3]>0;image=legal(array[:,:,:3],mask);image.save(OUT/f'composition_{style}.png')
        source=material(sources[0],style);a=np.asarray(source);single=legal(a[:,:,:3],a[:,:,3]>0);single.save(OUT/f'sphere_{style}.png')
        draw.text((5,row*208+4),labels[style],fill='white');gallery.paste(single.resize((160,160),Image.Resampling.NEAREST),(5,row*208+26));gallery.paste(image.resize((768,480),Image.Resampling.NEAREST).crop((170,0,938,480)).resize((640,160),Image.Resampling.NEAREST),(185,row*208+26))
        page.append(f'<h2>{labels[style]}</h2><img width="160" src="sphere_{style}.png"> <img width="768" src="composition_{style}.png">')
    page.append('<h2>Current r44, actual emulator capture</h2><p>For comparison: the rectangular cuts remain in this current native renderer.</p><img width="768" src="current.png">')
    b=(capture/'sample_200.home.bin').read_bytes();unpack(b[0x4000:0x5800],b[0x6000:0x7800]).save(OUT/'current.png')
    (OUT/'index.html').write_text('\n'.join(page),encoding='utf-8');(OUT/'manifest.json').write_text(json.dumps(dict(status='Offline feedback alternatives, not a native compositing fix',styles=labels,native_sample_update=200,order='First drawn component has priority; composed back-to-front',black_interior=False),indent=2));print(OUT/'index.html')
if __name__=='__main__':main()
