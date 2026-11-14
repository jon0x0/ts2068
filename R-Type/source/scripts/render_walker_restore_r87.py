from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np
R=Path.cwd();A=R/'build/graphics/walker_runtime_r86';O=R/'build/graphics/walker_restore_r87';groups=[(1,'small'),(6,'head'),(7,'head')];sheet=Image.new('RGB',(960,480),(14,20,28));d=ImageDraw.Draw(sheet);page=['<!doctype html><meta charset=utf-8><title>r87 approved walker restoration</title><style>body{background:#111923;color:#e6edf5;font:17px system-ui;margin:24px}img{image-rendering:pixelated;max-width:100%}.row{display:flex;gap:24px;flex-wrap:wrap}section{margin:24px 0;border-top:1px solid #567;padding:20px}</style><h1>r87: approved walker artwork restored</h1><p>Blue armour uses saved blue_21..25 pixels directly, not the generic r86 material pass. Head32 uses saved deeper-gray cels; L7 head24 restores its earlier native drawings (18/19/20/22), rather than substituting the L6 preview. Three approved walking poses plus an authored leg-only fourth pose for small walkers; four original head poses. Other rejected walker replacements return to earlier geometry/art. Accepted yellow94 and reference exhaust are byte-identical to r86.</p><p>All output remains legal8x1ECM, normal black. GIF180ms is illustrative, not gameplay FPS. The saved approved artwork is NOT re-run through global RPC defaults.</p>']
for row,(n,key)in enumerate(groups):
 for col,(folder,label)in enumerate([(A,'r86 rejected'),(O,'r87 restored')]):
  frames=[]
  for k in range(4):
   im=Image.open(folder/f'L{n}_{key}_{k}.png').convert('RGB');can=Image.new('RGB',(64,48));can.paste(im,((64-im.width)//2,48-im.height));frames.append(can.resize((384,288),Image.Resampling.NEAREST))
   if k<2:sheet.paste(im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST),(col*480+k*180+8,row*160+25))
  frames[0].save(O/f'L{n}_{key}_{col}.gif',save_all=True,append_images=frames[1:],duration=180,loop=0,disposal=2);d.text((col*480+8,row*160+4),f'L{n} {key} - {label}',fill='white')
 page.append(f'<section><h2>L{n}_{key}</h2><div class=row><figure><figcaption>r86</figcaption><img src="L{n}_{key}_0.gif"></figure><figure><figcaption>Restored</figcaption><img src="L{n}_{key}_1.gif"></figure></div></section>')
sheet.save(O/'approved_restoration.png');(O/'index.html').write_text('\n'.join(page))
