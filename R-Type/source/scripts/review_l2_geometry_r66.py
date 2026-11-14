from pathlib import Path
import sys,json,html
import numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));import boss_motion_assets_r60 as a
from preview_enemy_sierra import convert
from build_graphics import PALETTE
O=R/'build/graphics/l2_geometry_review_r66';O.mkdir(exist_ok=True)
l=a.LAYOUTS[1];mem=bytes(16384)+(R/'build/fullgame/foundation/level02.raw').read_bytes()
def spectrum(i):
 d=l['enemies'][i-1];p=d['pointer'];im=np.zeros((d['height']*8,d['width']*8),np.uint8)
 for cy in range(d['height']):
  for cx in range(d['width']):
   tag=mem[p];p+=1
   if tag==54:continue
   bits=np.unpackbits(np.frombuffer(mem[p:p+8],np.uint8)).reshape(8,8);im[cy*8:cy*8+8,cx*8:cx*8+8]=np.where(bits,(tag&7),((tag>>3)&7));p+=8
 return Image.fromarray(PALETTE[im].astype('uint8'))
source=Image.open(R/'build/fullgame/arcade_reference/frame016800.png').convert('RGB');source.save(O/'arcade_reference.png')
rows=[];contact=Image.new('RGB',(1000,4*190),(16,16,16));dr=ImageDraw.Draw(contact)
for k,i in enumerate([3,4,25,41]):
 old=spectrum(i);cur=Image.fromarray(a.PALETTE[a.decode(2,i)[0]].astype('uint8'));old.save(O/f'{i}_spectrum.png');cur.save(O/f'{i}_current.png')
 dr.text((0,k*190),f'L2 #{i}: Spectrum / current / arcade crop',fill='white')
 for x,im in [(0,old),(230,cur)]:contact.paste(im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST),(x,k*190+24))
 crop=source.crop((48,88,104,136)if i==3 else(336,40,384,96)if i==4 else(125,45,155,75)if i==25 else(254,158,294,190));crop.save(O/f'{i}_source.png');contact.paste(crop.resize((crop.width*3,crop.height*3),Image.Resampling.NEAREST),(460,k*190+24))
 if i in [3,4]:
  box=(48,100,88,140)if i==3 else(340,54,384,96);tight=source.crop(box).convert('RGBA');v=np.array(tight);v[:,:,3]=np.where(v[:,:,:3].max(2)>45,255,0);tight=Image.fromarray(v,'RGBA');tight.thumbnail((40,40),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',(40,40));canvas.alpha_composite(tight,((40-tight.width)//2,(40-tight.height)//2));preview,_,_=convert(canvas,(40,40),np.ones((40,40),bool),1.8,2,hsv=True);preview.save(O/f'{i}_tight_trial.png');contact.paste(preview.resize((160,160),Image.Resampling.NEAREST),(760,k*190+24))
 rows.append(f'<tr><td>#{i}</td><td><img src="{i}_spectrum.png"></td><td><img src="{i}_current.png"></td><td><img src="{i}_source.png"></td><td>'+ (f'<img src="{i}_tight_trial.png">'if i in[3,4]else'Identification/reference only')+'</td></tr>')
contact.save(O/'comparison.png')
# Full native-v-current inventory, not an unsupported claim of arcade matches.
audit=[];atlas=Image.new('RGB',(1000,6*150),(16,16,16));dr=ImageDraw.Draw(atlas)
for j,d in enumerate(l['enemies']):
 i=d['id'];cur=Image.fromarray(a.PALETTE[a.decode(2,i)[0]].astype('uint8'));old=spectrum(i);x=j%8*125;y=j//8*150
 if y+150>atlas.height:
  n=Image.new('RGB',(1000,y+150),(16,16,16));n.paste(atlas,(0,0));atlas=n;dr=ImageDraw.Draw(atlas)
 dr.text((x,y),f'#{i} Spectrum/current',fill='white');old.thumbnail((55,110),Image.Resampling.NEAREST);cur.thumbnail((55,110),Image.Resampling.NEAREST);atlas.paste(old,(x,y+20));atlas.paste(cur,(x+60,y+20));cs=set(map(tuple,np.asarray(cur).reshape(-1,3)));cs.discard((0,0,0));audit.append({'id':i,'native_size':[d['width']*8,d['height']*8],'nonblack_colours':len(cs),'low_colour_review':0<len(cs)<=3})
atlas.save(O/'inventory.png');(O/'inventory.json').write_text(json.dumps(audit,indent=2))
(O/'index.html').write_text('<meta charset="utf-8"><title>L2 geometry and boss review</title><style>body{background:#171717;color:white;font:16px sans-serif}img{image-rendering:pixelated}td img{width:160px;max-height:220px;object-fit:contain}td{padding:10px}</style><h1>L2 geometry review</h1><p>Offline comparison only. No graphics replaced in r66. Spectrum geometry is shown at the same pixel scale. The existing arcade worm crop includes neighbouring body; tight-crop trials retain a 40x40 storage box without stretching. Body #25 and boss-mouth #41 require their own matching; these source crops are reference, not confirmed final replacements.</p><table><tr><th>ID</th><th>Spectrum</th><th>Current</th><th>Arcade reference crop</th><th>Tight head trial</th></tr>'+''.join(rows)+'</table><h2>Arcade context</h2><img width="768" src="arcade_reference.png"><h2>All native/current frames</h2><img src="inventory.png">')
print(O/'index.html')
