"""Level-five material-aware ECM alternatives, offline only."""
import json
import numpy as np
from PIL import Image,ImageDraw
from preview_enemy_sierra import ROOT,decode,convert
from build_graphics import PALETTE,quantize
OUT=ROOT/'build/graphics/level5_material_trials'

def material(source,size,gamma,body,bright):
    source=source.convert('RGBA');ratio=min(size[0]/source.width,size[1]/source.height)
    source=source.resize((round(source.width*ratio),round(source.height*ratio)),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',size);canvas.alpha_composite(source,((size[0]-source.width)//2,(size[1]-source.height)//2))
    a=np.asarray(canvas);visible=a[:,:,3]>=96;rgb=a[:,:,:3].astype(float)
    red=(rgb[:,:,0]>rgb[:,:,1]*1.25)&(rgb[:,:,0]>rgb[:,:,2]*1.25)&visible
    # Material hues are authored from the arcade's muted green body / red nodes.
    luminance=(rgb*np.array([.2126,.7152,.0722])).sum(2)/255
    luminance=luminance**(1/gamma)
    tint=np.array([.38,1,.35])if body==4 else np.array([.45,1,.85])
    target=np.clip(luminance[:,:,None]*255*tint,0,255)
    target[red]=np.stack([luminance[red]*255,luminance[red]*55,luminance[red]*25],axis=1)
    target[~visible]=0
    h,w=visible.shape;pairs=np.zeros((h,w//8,2),np.uint8)
    for y in range(h):
        for x in range(w//8):
            sl=slice(x*8,x*8+8);v=visible[y,sl];r=red[y,sl];offset=8 if bright else 0
            if not v.all():pair=(0,2 if r.sum()>v.sum()/2 else body)
            elif r.any():pair=(2,body)
            elif luminance[y,sl].mean()>.48:pair=(body,7)
            else:pair=(0,body)
            pairs[y,x]=np.array(pair)+offset
    bits,attrs,_=quantize(Image.fromarray(target.astype(np.uint8)),pairs=pairs,dither='sierra');bits[~visible]=0
    p=np.repeat(PALETTE[pairs[:,:,0]],8,axis=1);q=np.repeat(PALETTE[pairs[:,:,1]],8,axis=1)
    image=Image.fromarray(np.where(bits[:,:,None],q,p).astype('uint8'))
    assert not np.asarray(image)[~visible].any();assert not(attrs&128).any()
    return image,bits,attrs

def main():
    OUT.mkdir(parents=True,exist_ok=True);folder=ROOT/'build/fullgame/converted/level05'
    meta=json.loads((folder/'manifest.json').read_text());foundation=json.loads((ROOT/'build/fullgame/foundation/manifest.json').read_text())['levels'][4]
    descs={v['id']:v for v in foundation['enemies']};descs.update({v['id']:v for v in meta['descriptors']})
    raw=(folder/'enemy_graphics.bin').read_bytes();dictionary=(folder/'enemy_palette.bin').read_bytes();records=[]
    page=['<meta charset="utf-8"><title>Level 5 colour alternatives</title><style>body{background:#151515;color:white;font:16px sans-serif}img{max-width:100%;image-rendering:pixelated}</style><h1>Level 5: green body, red details</h1><p>Arcade source and current artwork shown first. Options 1/2 retain source hues with lower gamma; 3–6 explicitly preserve a green or turquoise body and red nodes using legal 8×1 pairs. Sierra Lite after scaling. Preview only: palettes are not yet reduced to the game dictionary; sizes/collisions/performance are not integrated.</p>']
    labels=['1 Source / gamma 1.0','2 Source / gamma 1.35','3 Green / subdued','4 Green / bright','5 Turquoise / subdued','6 Turquoise / bright']
    for ident in [8,9,10,11]:
        src=Image.open(folder/f'descriptor{ident:03d}_arcade.png').convert('RGBA');current,_=decode(descs[ident],raw,dictionary)
        sheet=Image.new('RGB',(1440,4*230),(12,12,12));draw=ImageDraw.Draw(sheet)
        for i,(label,im)in enumerate([('ARCADE SOURCE',src),('CURRENT GAME',current)]):
            preview=im.convert('RGB');preview.thumbnail((220,190),Image.Resampling.NEAREST)
            factor=max(1,min(4,220//preview.width,190//preview.height));preview=preview.resize((preview.width*factor,preview.height*factor),Image.Resampling.NEAREST)
            draw.text((i*240+5,5),label,fill='white');sheet.paste(preview,(i*240+5,30))
        for row,scale in enumerate([1,1.3,1.5],1):
            box=tuple(round(v*scale)for v in current.size);size=tuple((v+7)//8*8 for v in box)
            ratio=min(box[0]/src.width,box[1]/src.height);scaled=src.resize((round(src.width*ratio),round(src.height*ratio)),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',size);canvas.alpha_composite(scaled,((size[0]-scaled.width)//2,(size[1]-scaled.height)//2))
            for col,label in enumerate(labels):
                if col<2:im,bits,attrs=convert(canvas,size,np.ones((size[1],size[0]),bool),1 if col==0 else 1.35,1.3,False,True)
                else:im,bits,attrs=material(canvas,size,1.15,4 if col<4 else 5,col%2==1)
                stem=f'cel{ident:03d}_{scale}_option{col+1}';im.save(OUT/f'{stem}.png');(OUT/f'{stem}.bits').write_bytes(np.packbits(bits,axis=1).tobytes());(OUT/f'{stem}.attrs').write_bytes(attrs.tobytes())
                x=col*240+5;y=row*230;draw.text((x,y+5),label,fill='white');draw.text((x,y+23),f'{scale}x / {size[0]}x{size[1]} storage',fill='white');factor=max(1,min(4,225//size[0],170//size[1]));sheet.paste(im.resize((size[0]*factor,size[1]*factor),Image.Resampling.NEAREST),(x,y+48))
                records.append(dict(descriptor=ident,scale=scale,option=col+1,size=size,file=stem+'.png',colours=len(set(im.getdata()))))
        name=f'cel{ident:03d}.png';sheet.save(OUT/name);page.append(f'<h2>Level 5 #{ident}</h2><img src="{name}">')
    (OUT/'index.html').write_text('\n'.join(page),encoding='utf-8');(OUT/'manifest.json').write_text(json.dumps(dict(status='Offline choices; no playable release changed',records=records),indent=2));print('Generated',len(records),'alternatives:',OUT)
if __name__=='__main__':main()
