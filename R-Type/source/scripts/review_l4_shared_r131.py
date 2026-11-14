from pathlib import Path
import json,hashlib,zipfile
import numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();P=R/'build/fullgame/l2_star_guard_r130';O=R/'build/graphics/l4_shared_review_r131';O.mkdir(parents=True,exist_ok=True)
lay=json.loads((R/'build/fullgame/foundation/manifest.json').read_text())['levels'];walk=json.loads((P/'walker_runtime.json').read_text());regions={n:(P/f'level{n:02d}_region.bin').read_bytes()for n in[1,4]}
def native(n,i,original=False):
 m=(R/f'build/fullgame/foundation/level{n:02d}_live.bin').read_bytes()if original else bytes(0xc000)+regions[n][0xa000:0xe000];at=lay[n-1]['enemy_descriptors_start']+(i-1)*4;w,h=m[at:at+2];pos=int.from_bytes(m[at+2:at+4],'little');im=np.zeros((h*8,w*8),np.uint8);bitmap=[]
 for c in range(w*h):
  tag=m[pos];pos+=1;bits=bytes(8)if tag==54 else m[pos:pos+8];pos+=0 if tag==54 else 8;bitmap.extend(bits)
  for y,b in enumerate(bits):
   a=tag if original else regions[n][0x2000+(tag&127)*8+y]
   for x in range(8):im[(c//w)*8+y,(c%w)*8+x]=(a&7)if b&(128>>x)else((a>>3)&7)
 return im,(w,h,bytes(bitmap))
def runtime(n,key,frame):
 w=next(v for v in walk if v['level']==n);a=next(v for v in w['assets']if v['key']==key and v['frame']==frame);raw=(P/f'L{n}_runtime_art.bin').read_bytes();base=w['assets'][0]['pointer'];v=raw[a['pointer']-base:a['pointer']-base+a['bytes']];ww,hh=a['size'];p=np.frombuffer(v,np.uint8).reshape(ww//8,hh,2);im=np.zeros((hh,ww),np.uint8)
 for x in range(ww//8):
  for y in range(hh):
   b,t=p[x,y]
   for k in range(8):im[y,x*8+k]=(t&7)if b&(128>>k)else((t>>3)&7)
 return im,v,a
pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)],np.uint8)
rows=[('White ghost: L4 19-21 = L1 35-37','ghost32',[19,20,21],None),('White/magenta: L4 5-9 = L6 9-13','shell32',[6,7,8,9],None),('Yellow round walker: L4 28-31 = L1 53-56','round',[28,29,30,31],'round')]
sheet=Image.new('RGB',(1100,660),(18,22,28));d=ImageDraw.Draw(sheet);report=[]
for row,(label,key,ids,oldkey)in enumerate(rows):
 y=row*220;d.text((12,y+7),label,fill='white');d.text((12,y+30),'Current L4',fill='white');d.text((540,y+30),'Previously approved ECM (exact saved bytes)',fill='white')
 for k,i in enumerate(ids):
  old=runtime(4,oldkey,k)[0]if oldkey else native(4,i)[0];new,v,a=runtime(1,key,k)
  for x,img in [(12+k*126,old),(540+k*135,new)]:sheet.paste(Image.fromarray(pal[img]).resize((img.shape[1]*4,img.shape[0]*4),Image.Resampling.NEAREST),(x,y+60))
  if key=='ghost32':assert native(4,i,True)[1]==native(1,35+k,True)[1]
  if key=='shell32':assert native(4,i,True)[1]==native(1,30+k,True)[1]
  if key=='round':assert native(4,i,True)[1]==native(1,53+k,True)[1];assert v==zipfile.ZipFile(R/'convref/rtype-l1-walker-snake-assets.zip').read(f'walker/frame_{k:02d}.pairs.bin')
  report.append(dict(L4=i,source_level=1,key=key,frame=k,size=a['size'],sha256=hashlib.sha256(v).hexdigest(),native_bitmap_identity=True))
sheet.save(O/'confirmed_families.png');(O/'matches.json').write_text(json.dumps(report,indent=2));print(O)
