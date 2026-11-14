from pathlib import Path
import sys
from PIL import Image,ImageDraw
sys.path.insert(0,'scripts');from build_reviewed_r72 import frames
R=Path.cwd();O=R/'build/graphics/l1_machinery_r83';O.mkdir(exist_ok=True);names=['l3_pods_ecm_r82','l2_rpc_r67','l5_effects_fast_r59'];sheet=Image.new('RGB',(700,480));dr=ImageDraw.Draw(sheet)
for j,name in enumerate(names):
 p=R/'build/fullgame'/name/'level01_region.bin'
 if not p.exists():continue
 b=p.read_bytes();d=frames(b,1)[7];print(name,d['w'],d['h'],d['ptr']);im=Image.new('RGB',(d['w']*8,d['h']*8));pix=im.load()
 for k,(ptr,t,raw)in enumerate(d['cells']):
  if t==54:continue
  cy,cx=divmod(k,d['w'])
  for y in range(8):
   a=b[0x2000+(t&127)*8+y];v=255 if a&64 else 205
   for x in range(8):
    c=(a&7)if raw[1+y]&(128>>x)else(a>>3)&7;pix[cx*8+x,cy*8+y]=(v if c&2 else 0,v if c&4 else 0,v if c&1 else 0)
 im.save(O/(name+'.png'));sheet.paste(im.resize((im.width*2,im.height*2)),(j*230,30));dr.text((j*230,5),name,fill='white')
sheet.save(O/'baseline.png')
