"""Offline legal ECM material variants; B is the approved r61 selection."""
from pathlib import Path
import sys,json,itertools
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,'scripts');from boss_motion_assets_r60 import PALETTE
SRC=Path('build/graphics/small_walker_comparison');OUT=Path('build/graphics/small_walker_highlights');OUT.mkdir(parents=True,exist_ok=True)
styles=[('steel','A - Steel highlights'),('blue','B - Blue armour'),('warm','C - Warm metal accents')]
allrows=[]
for style,title in styles:
 for ident in range(21,26):
  base=np.load(SRC/f'{ident}_proposed.npy');h,w=base.shape;mask=base!=0;wanted=base.copy();weight=np.ones((h,w),float)
  for y,x in zip(*np.where(mask)):
   c=int(base[y,x]);top=y==0 or not mask[y-1,x];bottom=y==h-1 or not mask[y+1,x];left=x==0 or not mask[y,x-1];right=x==w-1 or not mask[y,x+1]
   if c==5:
    if y<h*.48 or ident>=24 and y<h*.7:
     # Raised barrel ribs, bevel glints and a dark lower face.
     if top and (x%8 in [1,2,3,4,5] or c==7):wanted[y,x]=7;weight[y,x]=3
     elif bottom:wanted[y,x]=1
     elif c==7:wanted[y,x]=7 if x%7 in [0,1] else 5
     elif style=='blue':wanted[y,x]=1 if bottom or (y+2<h and not mask[y+2,x]) else 5
     else:wanted[y,x]=5
     if style=='warm' and x%8==2 and top:wanted[y,x]=6;weight[y,x]=1.7
    else:
     # Exposed leg struts catch light; inner joints stay dark.
     if top or left and x%3==0:wanted[y,x]=7 if style!='warm' else 6;weight[y,x]=2
     elif bottom or right:wanted[y,x]=1
     else:wanted[y,x]=5 if style!='blue' else 1
   elif c==6:wanted[y,x]=6
  pixels=np.zeros_like(base);attrs=np.zeros((h,w//8),np.uint8)
  for y in range(h):
   for cx in range(w//8):
    sl=slice(cx*8,cx*8+8);visible=mask[y,sl];target=PALETTE[wanted[y,sl]];weights=weight[y,sl];best=None
    for p,q in itertools.combinations(range(8),2):
     if not visible.all() and p!=0:continue
     dist=((target[:,None,:]-PALETTE[[p,q]][None,:,:])**2).sum(2);choice=dist.argmin(1);cost=float((dist.min(1)*weights).sum())
     if best is None or cost<best[0]:best=(cost,p,q,choice)
    _,p,q,choice=best;row=np.array([p,q],np.uint8)[choice];row[~visible]=0;pixels[y,sl]=row;attrs[y,cx]=(p<<3)|q
  assert all(len(set(row[x:x+8]))<=2 for row in pixels for x in range(0,w,8));assert not pixels[~mask].any();assert not (attrs&0xc0).any()
  np.save(OUT/f'{style}_{ident}.npy',pixels);Image.fromarray(PALETTE[pixels].astype(np.uint8)).save(OUT/f'{style}_{ident}.png')
 frames=[Image.open(OUT/f'{style}_{i}.png').resize((256,192),Image.Resampling.NEAREST)for i in [21,22,23,22]];frames[0].save(OUT/f'{style}.gif',save_all=True,append_images=frames[1:],duration=360,loop=0,disposal=2)
 rows=[Image.open(OUT/f'{style}_{i}.png')for i in range(21,26)];allrows.append((title,rows))
can=Image.new('RGB',(1000,720),'#111');d=ImageDraw.Draw(can)
allrows.insert(0,('Corrected arcade conversion - baseline',[Image.open(SRC/f'{i}_proposed.png')for i in range(21,26)]))
for r,(title,ims)in enumerate(allrows):
 y=r*180;d.text((8,y+4),title,fill='white')
 for j,im in enumerate(ims):can.paste(im.resize((im.width*5,im.height*5),Image.Resampling.NEAREST),(j*200+10,y+35))
can.save(OUT/'comparison.png')
html='<meta charset="utf-8"><title>Walker highlight trials</title><style>body{background:#111;color:white;font:18px system-ui;margin:24px}main{display:flex;gap:24px;flex-wrap:wrap}img{image-rendering:pixelated;max-width:100%}p{max-width:1000px}</style><h1>Walker shading and highlight trials</h1><p>More deliberate barrel bevels, bright ribs, shaded undersides and illuminated leg struts. A favours steel/cyan, B deeper blue armour, C warm metallic accents. These are offline pixel-art material treatments of the corrected arcade-derived poses, not new game builds. All15 variant frames use legal normal-black8x1 pairs; silhouette is preserved. Identical illustrative animation timing, not gameplay FPS.</p><main><section><h2>Baseline</h2><img src="../small_walker_comparison/proposed_walk.gif"></section>'
for style,title in styles:html+=f'<section><h2>{title}</h2><img src="{style}.gif"></section>'
html+='</main><h2>All poses</h2><img src="comparison.png">';(OUT/'index.html').write_text(html);(OUT/'validation.json').write_text(json.dumps(dict(passed=True,frames=15,legal_pairs=True,normal_black=True,transparent_silhouette_preserved=True,game_changed=False),indent=2))
