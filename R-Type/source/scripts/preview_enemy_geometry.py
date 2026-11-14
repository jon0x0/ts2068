"""Review corrected arcade component extraction before changing collision geometry."""
import json
import numpy as np
from PIL import Image, ImageDraw
from preview_enemy_sierra import ROOT, convert

OUT=ROOT/'build/graphics/enemy_geometry_trials'

def components(im):
    a=np.asarray(im.convert('RGBA'))[:,:,3]>0
    seen=np.zeros(a.shape,bool);result=[]
    for y,x in zip(*np.where(a)):
        if seen[y,x]:continue
        todo=[(y,x)];seen[y,x]=True;points=[]
        while todo:
            yy,xx=todo.pop();points.append((yy,xx))
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    ny,nx=yy+dy,xx+dx
                    if 0<=ny<a.shape[0] and 0<=nx<a.shape[1] and a[ny,nx] and not seen[ny,nx]:
                        seen[ny,nx]=True;todo.append((ny,nx))
        if len(points)<16:continue
        ys,xs=zip(*points);box=tuple(map(int,(min(xs),min(ys),max(xs)+1,max(ys)+1)))
        isolated=np.zeros((*a.shape,4),np.uint8)
        yy,xx=zip(*points);isolated[yy,xx]=np.asarray(im.convert('RGBA'))[yy,xx]
        result.append((len(points),box,Image.fromarray(isolated).crop(box)))
    return sorted(result,key=lambda v:v[0],reverse=True)

def fit(im,size):
    scale=min(size[0]/im.width,size[1]/im.height)
    im=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',size);canvas.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2));return canvas

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    tail=Image.open(ROOT/'build/fullgame/converted/level01/descriptor016_arcade.png').convert('RGBA')
    missiles=Image.open(ROOT/'build/fullgame/converted/level03/descriptor101_arcade.png').convert('RGBA')
    parts=components(missiles);assert parts
    # Keep separate objects separate, rather than shrinking the entire formation.
    groups=[('L1 #16 tail',tail,[('whole tail, aspect fit',tail,(24,24)),('central segment',tail.crop((24,0,56,32)),(24,24)),('central segment, larger',tail.crop((24,0,56,32)),(32,32)),('whole tail, wider',tail,(48,24))]),('L3 #101',missiles,[(f'isolated object {i+1}',v[2],(32,16))for i,v in enumerate(parts[:3])]+[('largest object, taller',parts[0][2],(32,24)),('largest object, larger',parts[0][2],(48,32))])]
    page=['<meta charset="utf-8"><title>Enemy geometry corrections</title><style>body{background:#151515;color:white;font:16px sans-serif}img{image-rendering:pixelated;max-width:100%}</style><h1>Source and geometry corrections</h1><p>Preview only. Each candidate preserves source aspect ratio before Sierra Lite D conversion. Larger dimensions require renderer, animation, clipping and collision review. No game release changed.</p>'];report=[]
    for g,(name,source,variants) in enumerate(groups):
        sheet=Image.new('RGB',(len(variants)*250,310),(12,12,12));draw=ImageDraw.Draw(sheet)
        for i,(label,im,size) in enumerate(variants):
            prepared=fit(im,size);candidate,bits,attrs=convert(prepared,size,np.ones((size[1],size[0]),bool),1.8,2,False,True)
            draw.text((i*250+6,6),label,fill='white');draw.text((i*250+6,24),f'{size[0]}x{size[1]} pixels / D',fill='white')
            ref=im.copy();ref.thumbnail((180,110),Image.Resampling.NEAREST);sheet.paste(ref,(i*250+6,48),ref)
            sheet.paste(candidate.resize((size[0]*4,size[1]*4),Image.Resampling.NEAREST),(i*250+6,170))
            candidate.save(OUT/f'group{g}_option{i}.png');report.append(dict(group=name,option=i,label=label,size=size,bitmap_bytes=bits.size//8,attribute_bytes=attrs.size))
        sheet.save(OUT/f'group{g}.png');page.append(f'<h2>{name}</h2><img src="group{g}.png">')
    page.append('<p>L3 source contains multiple disconnected objects. Each isolated object above is an actual connected component, not an invented animation frame. A full animation sequence still needs temporal matching against arcade captures.</p>')
    (OUT/'index.html').write_text('\n'.join(page));(OUT/'manifest.json').write_text(json.dumps(dict(source_components=[dict(pixels=v[0],box=v[1])for v in parts],alternatives=report),indent=2));print(OUT)
    # Requested modest scale steps: content size is independent of padded cell size.
    modest=[];sheet=Image.new('RGB',(1000,620),(12,12,12));draw=ImageDraw.Draw(sheet)
    for row,(label,source,base)in enumerate([('L1 tail segment',tail.crop((24,0,56,32)),(24,24)),('L3 isolated projectile',parts[0][2],(32,16))]):
        for col,scale in enumerate([1,1.2,1.3,1.5]):
            content=tuple(round(v*scale)for v in base);padded=tuple((v+7)//8*8 for v in content)
            scaled=fit(source,content);canvas=Image.new('RGBA',padded);canvas.alpha_composite(scaled,((padded[0]-content[0])//2,(padded[1]-content[1])//2))
            candidate,bits,attrs=convert(canvas,padded,np.ones((padded[1],padded[0]),bool),1.8,2,False,True)
            x=col*250+5;y=row*310;draw.text((x,y+5),f'{label} {scale:.1f}x',fill='white');draw.text((x,y+24),f'fit box {content}, padded {padded}',fill='white')
            draw.text((x,y+43),f'{padded[0]*padded[1]//64} allocated cells',fill='white')
            sheet.paste(candidate.resize((padded[0]*4,padded[1]*4),Image.Resampling.NEAREST),(x,y+70))
            modest.append(dict(component=label,scale=scale,aspect_fit_box=content,padded_size=padded,allocated_cells=padded[0]*padded[1]//64))
    sheet.save(OUT/'modest_scales.png');(OUT/'modest_scales.json').write_text(json.dumps(modest,indent=2))
    (OUT/'modest_scales.html').write_text('<meta charset="utf-8"><title>Modest sprite size increases</title><style>body{background:#151515;color:white;font:16px sans-serif}img{max-width:100%;image-rendering:pixelated}</style><h1>1.0 / 1.2 / 1.3 / 1.5 scale comparison</h1><p>Corrected isolated arcade components, aspect preserved. Scaling occurs before Sierra Lite D. Fit box and padded ECM storage shown separately; these are artwork previews, not gameplay or speed measurements.</p><img src="modest_scales.png">')

if __name__=='__main__':main()
