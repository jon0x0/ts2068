from pathlib import Path
import sys,json
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack
LAY=json.loads((R/'build/fullgame/foundation/manifest.json').read_text())['levels'];PAL=[(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)];PAL+= [(0,0,0),(0,0,255),(255,0,0),(255,0,255),(0,255,0),(0,255,255),(255,255,0),(255,255,255)]
B=R/'build/fullgame/l1_machinery_r84';O=R/'build/graphics/walker_review_r85';O.mkdir(exist_ok=True)
def current(n,i):
 b=(B/f'level{n:02d}_region.bin').read_bytes()
 if n!=5:
  for at in range(0xe350,0xe3f0,11):
   if b[at]==0:break
   if b[at]!=i:continue
   w=b[at+1]&0x6f;h=b[at+2]*8;ptr=int.from_bytes(b[at+3:at+5],'little')
   if ptr>=0xc000:
    cache=b[0xdc50:0xdf50];off=cache.find(bytes.fromhex('dd21'),0x200);tab=int.from_bytes(cache[off+2:off+4],'little');raw=None
    for k in range(b[tab]):
     source=int.from_bytes(b[tab+1+k*4:tab+3+k*4],'little');dest=int.from_bytes(b[tab+3+k*4:tab+5+k*4],'little');v=unpack(b[source:]);needed=(w+(0 if b[at+1]&128 else 1))*h*2
     if dest<=ptr and ptr+needed<=dest+len(v):raw=v[ptr-dest:ptr-dest+needed];break
    assert raw is not None,(n,i,ptr)
   else:raw=unpack(b[ptr:])
   im=Image.new('RGB',(w*8,h));p=im.load()
   for x in range(w):
    for y in range(h):
     bits,a=raw[(x*h+y)*2:(x*h+y)*2+2];bank=8 if a&64 else 0
     for k in range(8):p[x*8+k,y]=PAL[((a&7)if bits&(128>>k)else(a>>3)&7)+bank]
   return im,'compiled'
 m=bytes(0xc000)+b[0xa000:0xe000];at=LAY[n-1]['enemy_descriptors_start']+(i-1)*4;w,h=m[at:at+2];ptr=int.from_bytes(m[at+2:at+4],'little');im=Image.new('RGB',(w*8,h*8));p=im.load()
 for cy in range(h):
  for cx in range(w):
   t=m[ptr];ptr+=1
   if t==54:continue
   for y in range(8):
    a=b[0x2000+(t&127)*8+y];bank=8 if a&64 else 0
    for x in range(8):p[cx*8+x,cy*8+y]=PAL[((a&7)if m[ptr+y]&(128>>x)else(a>>3)&7)+bank]
   ptr+=8
 return im,'native'
def main():
 for n in range(1,9):
  ims=[]
  for i in range(7,LAY[n-1]['enemy_descriptors']+1):
   try:
    im,kind=current(n,i)
    if im.width and im.height and im.width<=64 and im.height<=48:ims.append((i,im,kind));im.save(O/f'L{n}_{i:03d}_current.png')
   except Exception:continue
  sh=Image.new('RGB',(1000,((len(ims)+9)//10)*115),(16,20,24));d=ImageDraw.Draw(sh)
  for j,(i,im,kind)in enumerate(ims):
   x=j%10*100;y=j//10*115;d.text((x,y),str(i)+' '+kind,fill='white');im=im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST);im.thumbnail((98,95),Image.Resampling.NEAREST);sh.paste(im,(x,y+17))
  sh.save(O/f'L{n}_contact.png')
if __name__=='__main__':main()
