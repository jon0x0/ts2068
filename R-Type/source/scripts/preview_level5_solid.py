"""Solid organic shading: no error diffusion and no black interior palettes."""
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from preview_enemy_sierra import ROOT,decode
from build_graphics import PALETTE
OUT=ROOT/'build/graphics/level5_solid_trials'

def solid(source,box,theme,highlight):
    size=tuple((v+7)//8*8 for v in box);ratio=min(box[0]/source.width,box[1]/source.height)
    scaled=source.resize((round(source.width*ratio),round(source.height*ratio)),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',size);canvas.alpha_composite(scaled,((size[0]-scaled.width)//2,(size[1]-scaled.height)//2))
    a=np.asarray(canvas);visible=a[:,:,3]>=128;rgb=a[:,:,:3].astype(float)
    red=(rgb[:,:,0]>rgb[:,:,1]*1.25)&(rgb[:,:,0]>rgb[:,:,2]*1.25)&visible
    # Smooth source illumination, preserving coherent areas rather than diffusing
    # quantization error into stippled black. Alpha remains a separate silhouette.
    lum=(rgb*np.array([.2126,.7152,.0722])).sum(2)
    lum=np.asarray(Image.fromarray(lum.astype('uint8')).filter(ImageFilter.GaussianBlur(.45))).astype(float)/255
    indices=np.zeros(visible.shape,np.uint8);attrs=np.zeros((size[1],size[0]//8),np.uint8);bits=np.zeros(visible.shape,np.uint8)
    for y in range(size[1]):
        for cx in range(size[0]//8):
            sl=slice(cx*8,cx*8+8);v=visible[y,sl];r=red[y,sl];l=lum[y,sl]
            if not v.any():continue
            if not v.all():
                # A transparent edge needs black paper; keep all visible edge
                # pixels solid, never use black to approximate their brightness.
                p=0;q=10 if r.sum()>v.sum()/2 else theme[0];choice=v.copy()
            else:
                if r.any():p,q=theme[0],10;choice=r
                else:
                    if float(l.mean())>highlight:p,q=theme[1],15;threshold=highlight+.12
                    else:p,q=theme;threshold=.40
                    choice=l>threshold
            assert p//8==q//8 or p==0
            br=64 if q>=8 else 0
            attrs[y,cx]=br|((p&7)<<3)|(q&7);bits[y,sl]=choice
            indices[y,sl]=np.where(choice,q,p)
    interior=visible.reshape(size[1],size[0]//8,8).all(2)
    assert not ((attrs[interior]>>3)&7==0).any(),'Black interior paper'
    assert not (indices[visible]%8==0).any(),'Black pixels inside silhouette'
    assert not indices[~visible].any()
    return Image.fromarray(PALETTE[indices].astype('uint8')),bits,attrs

def main():
    OUT.mkdir(parents=True,exist_ok=True);folder=ROOT/'build/fullgame/converted/level05'
    meta=json.loads((folder/'manifest.json').read_text());descs={d['id']:d for d in meta['descriptors']};raw=(folder/'enemy_graphics.bin').read_bytes();dictionary=(folder/'enemy_palette.bin').read_bytes()
    profiles=[('1 Green / yellow highlights',(12,14),.64),('2 Green / cyan highlights',(12,13),.64),('3 Cyan / white highlights',(13,15),.72),('4 Yellow / white highlights',(14,15),.72)]
    records=[];page=['<meta charset="utf-8"><title>Solid organic level 5 shading</title><style>body{background:#151515;color:white;font:16px sans-serif}img{max-width:100%;image-rendering:pixelated}</style><h1>Solid shading: no black interior dithering</h1><p>Actual arcade cels, scaled before conversion. Solid coloured shadows and highlights; no error diffusion. Black is reserved for source transparency. All candidates obey 8×1 pair and shared-brightness constraints. Preview only, not integrated gameplay or validated collision sizes.</p>']
    for ident in [9,10,11,8]:
        source=Image.open(folder/f'descriptor{ident:03d}_arcade.png').convert('RGBA');current,_=decode(descs[ident],raw,dictionary)
        sheet=Image.new('RGB',(1120,760),(12,12,12));draw=ImageDraw.Draw(sheet)
        for col,(label,image)in enumerate([('ARCADE SOURCE',source.convert('RGB')),('CURRENT',current)]):
            factor=max(1,min(4,250//image.width,190//image.height));draw.text((col*280+5,5),label,fill='white');sheet.paste(image.resize((image.width*factor,image.height*factor),Image.Resampling.NEAREST),(col*280+5,25))
        for row,scale in enumerate([1.3,1.5],1):
            box=tuple(round(v*scale)for v in current.size)
            for col,(label,theme,highlight)in enumerate(profiles):
                image,bits,attrs=solid(source,box,theme,highlight);stem=f'cel{ident:03d}_{scale}_option{col+1}';image.save(OUT/f'{stem}.png');(OUT/f'{stem}.bits').write_bytes(np.packbits(bits,axis=1).tobytes());(OUT/f'{stem}.attrs').write_bytes(attrs.tobytes())
                x=col*280+5;y=row*250;draw.text((x,y),f'{label} / {scale}x',fill='white');factor=max(1,min(5,260//image.width,210//image.height));sheet.paste(image.resize((image.width*factor,image.height*factor),Image.Resampling.NEAREST),(x,y+25));records.append(dict(descriptor=ident,scale=scale,option=col+1,size=image.size,black_interior_pixels=0,file=stem+'.png'))
        name=f'cel{ident:03d}.png';sheet.save(OUT/name);page.append(f'<h2>Level 5 #{ident}</h2><img src="{name}">')
    (OUT/'index.html').write_text('\n'.join(page),encoding='utf-8');(OUT/'manifest.json').write_text(json.dumps(dict(status='Offline solid-colour alternatives',records=records),indent=2));print(OUT/'index.html')
if __name__=='__main__':main()
