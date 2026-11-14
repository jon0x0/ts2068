"""Offline group-composition experiment; not a gameplay renderer replacement."""
import json
import numpy as np
from PIL import Image,ImageDraw
from preview_enemy_sierra import ROOT,decode
from build_graphics import unpack,quantize
OUT=ROOT/'build/diagnostics/level5_overlap'

def main():
    report=json.loads((OUT/'result.json').read_text());folder=ROOT/'build/fullgame/converted/level05'
    meta=json.loads((folder/'manifest.json').read_text());descs={d['id']:d for d in meta['descriptors']};raw=(folder/'enemy_graphics.bin').read_bytes();dictionary=(folder/'enemy_palette.bin').read_bytes()
    frames=[]
    for offset in list(range(-16,33,8))+list(range(24,-17,-8)):
        canvas=Image.new('RGB',(80,56))
        for ident,x,y in [(9,20,16),(10,20+offset,24)]:
            current,_=decode(descs[ident],raw,dictionary)
            alpha=Image.open(folder/f'descriptor{ident:03d}_arcade.png').convert('RGBA').resize(current.size,Image.Resampling.LANCZOS).getchannel('A').point(lambda a:255 if a>=96 else 0)
            canvas.paste(current,(x,y),alpha)
        # Select one legal pair AFTER composition so overlapping parts do not
        # independently repaint the shared cell's colours.
        bits,attrs,preview=quantize(canvas,dither='sierra')
        assert not(attrs&128).any()
        frame=Image.new('RGB',(480,370),(12,12,12));draw=ImageDraw.Draw(frame)
        draw.text((8,8),'OFFLINE MASKED GROUP + FINAL ECM QUANTIZATION',fill='white')
        frame.paste(preview.resize((480,336),Image.Resampling.NEAREST),(0,30));frames.append(frame)
    frames[0].save(OUT/'group_composition.gif',save_all=True,append_images=frames[1:],duration=160,loop=0)
    proof=Image.new('RGB',(768,220));draw=ImageDraw.Draw(proof)
    for col,(name,label)in enumerate([('first','First part'),('second_alone','Second part alone'),('overlap','Actual native overlap')]):
        b=(OUT/f'{name}.home.bin').read_bytes();im=unpack(b[0x4000:0x5800],b[0x6000:0x7800]).crop((48,48,128,104)).resize((240,168),Image.Resampling.NEAREST);proof.paste(im,(col*256,24));draw.text((col*256+4,5),label,fill='white')
    proof.save(OUT/'native_overlap.png')
    (OUT/'index.html').write_text('<meta charset="utf-8"><title>Level 5 compositing investigation</title><style>body{background:#151515;color:white;font:16px sans-serif}img{image-rendering:pixelated;max-width:100%}</style><h1>Native cell-priority overlap</h1><p>Actual Z80 test: '+str(report['missingForegroundPixels'])+' pixels from the second component are suppressed by the first component’s cell ownership. Earlier pixels erased: '+str(report['erasedEarlierPixels'])+'. This reproduces the cell-level mechanism, not the exact reported animation frame.</p><img src="native_overlap.png"><h2>Alternative: compose the whole group, then choose ECM pairs</h2><p>Offline experiment only. Alpha masks preserve overlapping shapes; each final 8×1 area receives one legal pair after composition. No CPU/frame-rate or playable integration claim. Current assets still have harsh colour compromises.</p><img src="group_composition.gif">',encoding='utf-8')
    print(OUT/'index.html')
if __name__=='__main__':main()
