"""Offline, native-size ECM alternatives. Does not modify playable releases."""
from pathlib import Path
import json, html
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
from build_graphics import PALETTE, fit_pairs, quantize

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/graphics/enemy_sierra_trials'

def decode(d, raw, dictionary):
    pixels = np.zeros((d['height']*8,d['width']*8,3), dtype=np.uint8)
    opaque = np.zeros(pixels.shape[:2], dtype=bool)
    p = d['pointer']-0xc4ce
    for y in range(d['height']):
        for x in range(d['width']):
            a=raw[p]
            if a==54:
                p+=1
                continue
            row=np.frombuffer(dictionary[(a&127)*8:(a&127)*8+8],dtype=np.uint8)
            br=np.where(row&64,8,0)
            bits=np.unpackbits(np.frombuffer(raw[p+1:p+9],dtype=np.uint8)).reshape(8,8)
            colours=np.where(bits,(row&7)[:,None]+br[:,None],((row>>3)&7)[:,None]+br[:,None])
            pixels[y*8:y*8+8,x*8:x*8+8]=PALETTE[colours]
            opaque[y*8:y*8+8,x*8:x*8+8]=True
            p+=9
    return Image.fromarray(pixels),opaque

def convert(source,size,mask,gamma,saturation,coherent=False,hsv=False):
    # Scale before colour enhancement and error diffusion, never afterwards.
    im=source.convert('RGBA').resize(size,Image.Resampling.LANCZOS)
    alpha=np.asarray(im)[:,:,3]>=96
    rgb=im.convert('RGB')
    if hsv:
        channels=np.array(rgb.convert('HSV'))
        channels[:,:,1]=np.minimum(255,channels[:,:,1].astype(float)*saturation).astype(np.uint8)
        rgb=Image.fromarray(channels,'HSV').convert('RGB')
    else: rgb=ImageEnhance.Color(rgb).enhance(saturation)
    values=np.asarray(rgb,dtype=float)/255
    values=np.round(255*values**(1/gamma)).astype(np.uint8)
    visible=alpha&mask
    values[~visible]=0
    pairs=fit_pairs(values.astype(float),mode='row' if coherent else 'cell')
    edge=fit_pairs(values.astype(float),mode='row' if coherent else 'cell',black=True)
    holes=(~visible).reshape(size[1],size[0]//8,8).any(2)
    if coherent: holes[:]=holes.any(1)[:,None]
    pairs[holes]=edge[holes]
    bits,attrs,_=quantize(Image.fromarray(values),pairs=pairs,dither='sierra')
    bits[~visible]=0
    p=np.repeat(PALETTE[pairs[:,:,0]],8,axis=1)
    q=np.repeat(PALETTE[pairs[:,:,1]],8,axis=1)
    preview=Image.fromarray(np.where(bits[:,:,None],q,p).astype(np.uint8))
    assert not (attrs&128).any()
    assert not np.asarray(preview)[~visible].any(), 'Transparent pixels must remain black'
    return preview,bits,attrs

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    foundation=json.loads((ROOT/'build/fullgame/foundation/manifest.json').read_text())['levels']
    profiles=[('A',1.8,4.5,False,False),('B',2.4,4.5,False,False),('C',2.4,4.5,True,False),('D',1.8,2.0,False,True),('E',2.4,2.0,False,True)]
    records=[];page=['<meta charset="utf-8"><title>Enemy ECM Sierra Lite trials</title><style>body{background:#181818;color:white;font:16px sans-serif}img{image-rendering:pixelated;max-width:100%}td{padding:12px;vertical-align:top}a{color:cyan}</style><h1>Native-size enemy ECM comparisons</h1><p>Arcade source → current playable art → A gamma 1.8 → B gamma 2.4 → C gamma 2.4, row coherent. Saturation 4.5 in A/B/C. All candidates use Sierra Lite after scaling. Preview only: no playable assets replaced. Candidate colours are not yet reduced to the shared 127-row dictionary.</p>']
    for layout in foundation:
        n=layout['level'];folder=ROOT/f'build/fullgame/converted/level{n:02d}'
        meta=json.loads((folder/'manifest.json').read_text());raw=(folder/'enemy_graphics.bin').read_bytes();dictionary=(folder/'enemy_palette.bin').read_bytes()
        descs={d['id']:d for d in layout['enemies']};descs.update({d['id']:d for d in meta['descriptors']})
        # Representative distinct components rather than every repeated ship strip.
        ids={1:[8,9,16],2:[3,4],3:[40,60,101],4:[25,27],5:[8,9,10,11],6:[18,19,20,26],7:[49,50],8:[42,43,44]}[n]
        sheet=Image.new('RGB',(1680,len(ids)*180),(12,12,12));draw=ImageDraw.Draw(sheet)
        for i,ident in enumerate(ids):
            source=Image.open(folder/f'descriptor{ident:03d}_arcade.png')
            current,mask=decode(descs[ident],raw,dictionary);images=[source,current]
            rec=dict(level=n,descriptor=ident,native_size=current.size,profiles=[])
            for label,g,s,c,hsv in profiles:
                image,bits,attrs=convert(source,current.size,mask,g,s,c,hsv)
                stem=f'L{n}_{ident:03d}_{label}'
                image.save(OUT/f'{stem}.png');(OUT/f'{stem}.bits').write_bytes(np.packbits(bits,axis=1).tobytes());(OUT/f'{stem}.attrs').write_bytes(attrs.tobytes())
                rec['profiles'].append(dict(name=label,gamma=g,saturation=s,hue_preserving=hsv,row_coherent=c,bitmap_bytes=bits.size//8,attribute_bytes=attrs.size,unique_rows=len(set(attrs[y:y+8,x].tobytes() for y in range(0,attrs.shape[0],8) for x in range(attrs.shape[1])))))
                images.append(image)
            for col,(label,im) in enumerate(zip(['ARCADE SOURCE','CURRENT','A: GAMMA 1.8','B: GAMMA 2.4','C: ROW COHERENT','D: HSV / GAMMA 1.8','E: HSV / GAMMA 2.4'],images)):
                draw.text((col*240+4,i*180+4),f'L{n} #{ident} {label}',fill='white')
                if col==0: im=im.convert('RGB')
                factor=max(1,min(4,220//im.width,150//im.height))
                im=im.resize((im.width*factor,im.height*factor),Image.Resampling.NEAREST)
                if im.width>230 or im.height>150:im.thumbnail((230,150),Image.Resampling.NEAREST)
                sheet.paste(im,(col*240+4,i*180+24))
            records.append(rec)
        name=f'level{n:02d}.png';sheet.save(OUT/name);page.append(f'<h2>Level {n}</h2><img src="{name}">')
    (OUT/'manifest.json').write_text(json.dumps(dict(status='Offline alternatives; no runtime performance claim',records=records),indent=2))
    page.insert(2,'<p>D/E preserve hue using HSV saturation ×2, then gamma 1.8/2.4. These are explicit experimental settings, not claimed equivalent to Retro Image Converter controls.</p>')
    (OUT/'index.html').write_text('\n'.join(page),encoding='utf-8')
    print(json.dumps(dict(comparisons=len(records),candidates=len(records)*len(profiles),output=str(OUT))))

if __name__=='__main__':main()
