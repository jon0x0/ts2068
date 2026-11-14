"""Read Fuse FMF raster rectangles for regression evidence (no sound playback)."""
from pathlib import Path
import sys,zlib,json
import numpy as np
from PIL import Image
from build_graphics import PALETTE
def read(path):
 raw=Path(path).read_bytes();assert raw[:6]==b'FMF_V1';data=zlib.decompressobj().decompress(raw[16:])if raw[7]==90 else raw[16:];pos=0;frames=0;mode=chr(raw[9]);pix=np.zeros((240,40),dtype='uint8');atr=np.zeros_like(pix);saved=[]
 def plane(n):
  nonlocal pos
  out=[];last=None
  while len(out)<n:
   v=data[pos];pos+=1;out.append(v)
   if v==last:
    count=data[pos];pos+=1;out.extend([v]*count);last=None
   else:last=v
  assert len(out)==n
  return np.array(out,dtype='uint8')
 def save():
  if mode=='R':return
  bits=np.unpackbits(pix,axis=1);a=np.repeat(atr,8,axis=1);br=np.where(a&64,8,0);rgb=PALETTE[np.where(bits,(a&7)+br,((a>>3)&7)+br)].astype('uint8');target=Path(path).with_suffix(f'.frame{frames}.png');Image.fromarray(rgb).resize((640,480),Image.Resampling.NEAREST).save(target);saved.append(str(target))
 while pos<len(data):
  c=chr(data[pos]);pos+=1
  if c=='$':
   x=data[pos];y=int.from_bytes(data[pos+1:pos+3],'little');w=data[pos+3];h=int.from_bytes(data[pos+4:pos+6],'little');pos+=6;pix[y:y+h,x:x+w]=plane(w*h).reshape(h,w);atr[y:y+h,x:x+w]=plane(w*h).reshape(h,w)
   if mode=='R':plane(w*h)
  elif c=='N':
   if frames in [800,820,850,900,950,999]:save()
   frames+=1;mode=chr(data[pos+1]);pos+=3
  elif c=='S':
   encoding=chr(data[pos]);channels=2 if data[pos+3]==83 else 1;n=int.from_bytes(data[pos+4:pos+6],'little')+1;pos+=6+n*channels*(2 if encoding=='P'else 1)
  elif c=='X':break
  else:raise ValueError((c,pos))
 save();print(json.dumps(dict(frames=frames,files=saved)))
if __name__=='__main__':read(sys.argv[1])

