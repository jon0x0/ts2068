from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np
R=Path.cwd();O=R/'build/graphics/walker_runtime_r86';m=json.loads((O/'inputs.json').read_text());pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)],np.uint8);page=['<!doctype html><meta charset=utf-8><title>R-Type r86 integrated walkers and exhaust</title><style>body{background:#10161e;color:#e4eff9;font:17px system-ui;max-width:1100px;margin:24px auto;padding:16px}img{image-rendering:pixelated;max-width:100%}.row{display:flex;gap:24px;flex-wrap:wrap}section{border-top:1px solid #567;padding:20px 0}</style><h1>r86: integrated walker animation and exhaust</h1><p>These are the exact converted assets installed in the playable build. GIF timing is illustrative180ms/pose, not a measured game frame rate. Four distinct walking poses are selected per actor; native movement scripts and hitbox dimensions retained. Weapon-raising poses remain separate. Arrowed yellow bot is L3 native94, distinct from Before31.</p><p>Arcade-derived small walkers use1570/1572/1574 plus an authored intermediate leg pose; the previously tested1576 tile was rejected. Large walkers use four earlier arcade cels. Walking heads use224/226/228/230. Round walkers and yellow94 use explicitly AI-assisted Spectrum-derived concepts, not claimed arcade matches. Exhaust is a reference-based AI artwork pass, scaled before RPC. RPC settings are identical within each animation family.</p>']
for a in m['assets']:
 w,h=a['size'];attrs=np.frombuffer((O/(a['name']+'.attrs')).read_bytes(),np.uint8).reshape(h,w//8);bits=np.unpackbits(np.frombuffer((O/(a['name']+'.bits')).read_bytes(),np.uint8)).reshape(h,w);idx=np.where(bits,np.repeat(attrs&7,8,1),np.repeat((attrs>>3)&7,8,1));Image.fromarray(pal[idx]).save(O/(a['name']+'.png'))
selected=[(3,'round'),(3,'yellow'),(3,'exhaust'),(1,'small'),(1,'large'),(6,'head')];sheet=Image.new('RGB',(800,len(selected)*150),(15,21,28));d=ImageDraw.Draw(sheet)
for row,(n,key)in enumerate(selected):
 aa=[a for a in m['assets']if a['level']==n and a['key']==key]
 for a in aa:
  im=Image.open(O/(a['name']+'.png'));sheet.paste(im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST),(a['frame']*200+5,row*150+30))
 d.text((5,row*150+4),f'L{n} {key}: '+str(len(aa))+' poses',fill='white')
sheet.save(O/'integrated_artwork.png')
for g in m['groups']:
 aa=[a for a in m['assets']if a['level']==g['level']and a['key']==g['key']];frames=[]
 for a in aa:
  im=Image.open(O/(a['name']+'.png'));can=Image.new('RGB',(64,48));can.paste(im,((64-im.width)//2,48-im.height));frames.append(can.resize((384,288),Image.Resampling.NEAREST))
 name=f'L{g["level"]}_{g["key"]}';frames[0].save(O/f'{name}.gif',save_all=True,append_images=frames[1:],duration=180,loop=0,disposal=2);page.append(f'<section><h2>{name}</h2><p>Native IDs '+str(g['original'])+f'; footprint {g["size"]}; {len(aa)} poses.</p><img src="{name}.gif"><div class=row>')
 for a in aa:page.append(f'<figure><figcaption>Pose {a["frame"]+1}</figcaption><img width="{a["size"][0]*4}" height="{a["size"][1]*4}" src="{a["name"]}.png"></figure>')
 page.append('</div></section>')
(O/'index.html').write_text('\n'.join(page),encoding='utf-8')
