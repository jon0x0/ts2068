"""Deep-shadow Bellmite with source-guided organic rim highlights, offline."""
import json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from preview_bellmite_detail import ROOT,material,legal
OUT=ROOT/'build/graphics/bellmite_rim_feedback'

def highlight(source,style):
    base=material(source,'B');rgba=np.array(base);original=np.asarray(source);mask=rgba[:,:,3]>0
    eroded=np.asarray(Image.fromarray(mask.astype('uint8')*255).filter(ImageFilter.MinFilter(3)))>0
    inside=np.asarray(Image.fromarray(mask.astype('uint8')*255).filter(ImageFilter.MinFilter(5)))>0
    rim=mask&~eroded;inner=eroded&~inside
    up=np.zeros_like(mask);up[1:]=mask[:-1];left=np.zeros_like(mask);left[:,1:]=mask[:,:-1]
    lit=rim&(~up|~left)
    brightness=(original[:,:,:3]*np.array([.2126,.7152,.0722])).sum(2)/255
    red=(original[:,:,0]>original[:,:,1]*1.25)&(original[:,:,0]>original[:,:,2]*1.25)
    if style=='D':
        rgba[lit&(brightness>.27)&~red,:3]=[255,255,255]
        rgba[inner&(brightness>.42)&~red,:3]=[0,255,255]
    elif style=='E':
        rgba[rim&~red,:3]=[0,255,255]
        rgba[lit&~red,:3]=[255,255,255]
        rgba[inner&(brightness>.38)&~red,:3]=[0,255,255]
    return Image.fromarray(rgba,'RGBA')

def main():
    OUT.mkdir(parents=True,exist_ok=True);capture=ROOT/'build/fullgame/bellmite_orbs_r44'
    sources=[Image.open(ROOT/f'build/fullgame/converted/level05/descriptor{i:03d}_arcade.png').convert('RGBA')for i in [9,10,11]]
    labels={'B':'Approved deep shadows','D':'Source-guided rim / darker lower edge','E':'Stronger cyan rim / white upper edge'}
    sheet=Image.new('RGB',(800,3*190),(12,12,12));draw=ImageDraw.Draw(sheet)
    page=['<meta charset="utf-8"><title>Bellmite rim highlights</title><style>body{background:#151515;color:white;font:17px sans-serif}img{max-width:100%;image-rendering:pixelated}</style><h1>Deep shadows with organic edge highlights</h1><p>Approved B retained as the baseline. D adds a selective one-pixel white upper/left rim guided by arcade brightness, with cyan inner highlights. E has a stronger cyan outline. Red nodes and source silhouette retained. Each final 8×1 pair is chosen after composition. Offline previews only; no new cartridge or speed claim.</p><img src="spheres.png">']
    for row,(style,label)in enumerate(labels.items()):
        draw.text((5,row*190+5),label,fill='white')
        for i,src in enumerate(sources):
            rgba=highlight(src,style);a=np.asarray(rgba);single=legal(a[:,:,:3],a[:,:,3]>0);single.save(OUT/f'{style}_sphere{i}.png');sheet.paste(single.resize((160,160),Image.Resampling.NEAREST),(i*190+210,row*190+24))
        canvas=Image.new('RGBA',(256,160))
        for command in reversed(json.loads((capture/'sample_200.commands.json').read_text())):
            if command['pointer']not in [0xf3f1,0xf481,0xf511]:continue
            rgba=highlight(sources[[0xf3f1,0xf481,0xf511].index(command['pointer'])],style)
            if command['entry']in [0x8dd3,0x8e29]:rgba=rgba.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            if command['entry']in [0x8d65,0x8e29]:rgba=rgba.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            y=command['y']if command['y']<128 else command['y']-256;canvas.alpha_composite(rgba,(command['x']*8,y*8))
        a=np.asarray(canvas);legal(a[:,:,:3],a[:,:,3]>0).save(OUT/f'{style}_group.png');page.append(f'<h2>{label}</h2><img width="768" src="{style}_group.png">')
    sheet.save(OUT/'spheres.png');(OUT/'index.html').write_text('\n'.join(page),encoding='utf-8');(OUT/'manifest.json').write_text(json.dumps(dict(status='Offline rim alternatives; approved base B retained',styles=labels,source_frame=44700,native_integration=False),indent=2));print(OUT/'index.html')
if __name__=='__main__':main()
