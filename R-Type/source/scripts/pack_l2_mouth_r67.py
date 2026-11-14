from pathlib import Path
import numpy as np,collections,json
from PIL import Image
R=Path.cwd();O=R/'build/graphics/l2_actors_r67';B=R/'build/graphics/l2_integrated_r67'
pal=np.array([[0,0,0],[1,0,206],[207,1,0],[207,1,206],[0,207,21],[1,207,207],[207,207,21],[207,207,207],[96,96,96],[2,0,253],[255,2,1],[255,2,253],[0,255,28],[2,255,255],[255,255,29],[255,255,255]],float)
rows=[(B/'palette.bin').read_bytes()[i:i+8]for i in range(0,896,8)];keys={}
for i,k in enumerate(rows):keys.setdefault(k,i)
imgs=[];attrs=[];count=collections.Counter()
for n in range(4):
 a=np.frombuffer((O/f'M{n}.attrs').read_bytes(),np.uint8).reshape(24,4);bits=np.frombuffer((O/f'M{n}.bits').read_bytes(),np.uint8).reshape(24,4);im=np.zeros((24,32),np.uint8)
 for y in range(24):
  for x in range(4):
   t=int(a[y,x]);p=(t>>3&7)+(8 if t&64 else 0);q=(t&7)+(8 if t&64 else 0)
   for k in range(8):im[y,x*8+k]=q if bits[y,x]&(128>>k)else p
 for y in range(0,24,8):
  for x in range(4):count[a[y:y+8,x].tobytes()]+=1
 imgs.append(im);attrs.append(a)
for k,n in count.most_common():
 if k not in keys and len(rows)<128:keys[k]=len(rows);rows.append(k)
def fit(im,k):
 a=np.frombuffer(k,np.uint8);p=((a>>3)&7)+((a>>6)&1)*8;q=(a&7)+((a>>6)&1)*8;col=pal[im];bits=((col-pal[q][:,None])**2).sum(2)<((col-pal[p][:,None])**2).sum(2);black=im==0
 if any(black[y].any()and p[y]!=0 and q[y]!=0 for y in range(8)):return None
 if any((~black[y]).any()and p[y]==0 and q[y]==0 for y in range(8)):return None
 bits[black]=np.broadcast_to((q==0)&(p!=0),im.shape)[black];bits[(~black)&(p[:,None]==0)]=True;bits[(~black)&(q[:,None]==0)]=False
 out=np.where(bits,q[:,None],p[:,None]);return float(((pal[out]-col)**2).sum()),bits,out
raw=bytearray();errors=[];contact=Image.new('RGB',(512,96))
for n,im in enumerate(imgs):
 out=np.zeros_like(im);start=len(raw)
 for y in range(0,24,8):
  for x in range(4):
   block=im[y:y+8,x*8:x*8+8];best=None
   for k,i in keys.items():
    f=fit(block,k)
    if f is not None and(best is None or f[0]<best[0]):best=(*f,i)
   assert best is not None
   score,bits,result,i=best;raw.append(0x80|i);raw.extend(np.packbits(bits,axis=1).tobytes());out[y:y+8,x*8:x*8+8]=result
 errors.append(float(np.abs(pal[out]-pal[im]).mean()));Image.fromarray(pal[out].astype('uint8')).resize((128,96),Image.Resampling.NEAREST).save(O/f'M{n}_installed.png');contact.paste(Image.open(O/f'M{n}_installed.png'),(n*128,0))
assert len(raw)==432
(O/'mouths.bin').write_bytes(raw);(O/'palette.bin').write_bytes(b''.join(rows));contact.save(O/'mouth_contact.png');(O/'packing.json').write_text(json.dumps({'bytes':len(raw),'palette_rows':len(rows),'RGB_mean_errors':errors,'native_origin':[152,64],'native_size':[32,24],'arcade_frames':[17400,17700,18000,18300]},indent=2));print(errors)
