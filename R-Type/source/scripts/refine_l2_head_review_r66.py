from pathlib import Path
import sys,numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from decode_arcade_objects import render
from preview_enemy_sierra import convert
O=R/'build/graphics/l2_geometry_review_r66';_,rows=render(16800)
contact=Image.new('RGB',(1000,420),(16,16,16));dr=ImageDraw.Draw(contact)
for k,(i,code)in enumerate([(3,2470),(4,2464)]):
 tile=next(im for d,im in rows if d['code']==code);tile.save(O/f'{i}_isolated_source.png')
 for j,(label,im)in enumerate([('Spectrum',Image.open(O/f'{i}_spectrum.png')),('Current',Image.open(O/f'{i}_current.png')),('Arcade32',tile)]):
  dr.text((j*200,k*210),f'#{i} {label}',fill='white');contact.paste(im.convert('RGB').resize((im.width*4,im.height*4),Image.Resampling.NEAREST),(j*200,k*210+24))
 for j,size in enumerate([32,40]):
  canvas=Image.new('RGBA',(40,40));scaled=tile.resize((size,size),Image.Resampling.LANCZOS);canvas.alpha_composite(scaled,((40-size)//2,(40-size)//2));im,_,_=convert(canvas,(40,40),np.ones((40,40),bool),1.8,2,hsv=True);im=Image.fromarray(np.minimum(np.asarray(im),205).astype('uint8'));im.save(O/f'{i}_isolated_{size}.png');dr.text((600+j*200,k*210),f'Isolated head {size}px',fill='white');contact.paste(im.resize((160,160),Image.Resampling.NEAREST),(600+j*200,k*210+24))
contact.save(O/'isolated_heads.png')
p=O/'index.html';s=p.read_text()
if '<table>' in s:
 a=s.index('<table>');z=s.index('</table>',a)+8;s=s[:a]+'<h2>Corrected isolated arcade objects</h2><p>The screenshot crop included a second neck object and cave background. These alternatives use only the decoded head objects (codes2470/2464, palette6), retaining original40x40 native storage. Compare32px and40px head detail. No playable replacement yet.</p><img src="isolated_heads.png">'+s[z:];p.write_text(s)
