"""A separate ten-change, four-colors-per-cell density test."""
from pathlib import Path
import json,struct,zlib
import numpy as np
from PIL import Image,ImageDraw
from convert_image import COLUMNS,SPLITS,pack
from palette_fit import row,PALETTE
ROOT=Path(__file__).resolve().parent
out=ROOT/'variants/prover';out.mkdir(parents=True,exist_ok=True)
im=Image.new('1',(256,192));draw=ImageDraw.Draw(im)
draw.text((10,8),'TIMEX DYNAMIC ECM',fill=1)
draw.text((10,25),'10 CHANGES PER TEST LINE',fill=1)
draw.text((10,42),'4 COLORS PER 8x1 CELL',fill=1)
draw.text((10,148),'64 CONSECUTIVE TEST LINES',fill=1)
draw.text((10,168),'SPACE: STANDARD ECM / DYNAMIC',fill=1)
bits=np.array(im,dtype=np.uint8);attrs=np.full((192,32),7,dtype=np.uint8)
selected=np.zeros((192,10),bool);selected[64:128]=True
schedule=[]
new_values=[1|(6<<3)|64,3|(5<<3)|64,2|(4<<3),1|(7<<3)]
for y in range(192):
 s=dict(columns=[],splits=[],slots=[],old=[],new=[])
 if 64<=y<128:
  for i,(c,cut) in enumerate(zip(COLUMNS,SPLITS)):
   new=new_values[(i+(y-64)//16)%4]
   used={new&7,(new>>3)&7};remaining=[k for k in range(8) if k not in used]
   ink=remaining[(i+y)%len(remaining)];paper=remaining[(i+y+2)%len(remaining)]
   old=ink|(paper<<3)|(64 if y&8 else 0)
   attrs[y,c]=old;bits[y,c*8:c*8+8]=np.arange(8)%2
   for k,v in [('columns',int(c)),('splits',int(cut)),('slots',i),('old',old),('new',new)]:s[k].append(v)
 schedule.append(s)
bitmap=bytearray(6144);plane=bytearray(6144)
for y in range(192):
 for c in range(32):
  k=row(y)+c;bitmap[k]=sum(128>>b for b in range(8) if bits[y,c*8+b]);plane[k]=int(attrs[y,c])
for name in ['ecm','dynamic']:
 (out/(name+'-bitmap.bin')).write_bytes(bitmap);(out/(name+'-attributes.bin')).write_bytes(plane)
 idx=np.empty((192,256),np.uint8)
 for y in range(192):
  for x in range(256):
   c=x//8;a=int(attrs[y,c]);s=schedule[y]
   if name=='dynamic' and c in s['columns']:
    i=s['columns'].index(c)
    if x%8>=s['splits'][i]:a=s['new'][i]
   idx[y,x]=((a&7) if bits[y,x] else ((a>>3)&7))+(8 if a&64 else 0)
 np.save(out/(name+'-indices.npy'),idx)
 Image.fromarray(PALETTE[idx]).resize((768,576),Image.Resampling.NEAREST).save(out/(name+'-preview.png'))
 if name=='dynamic':
  assert all(len(set(idx[y,c*8:c*8+8]))==4 for y in range(64,128) for c in COLUMNS)
(out/'schedule.json').write_text(json.dumps(schedule));(out/'restore-plan.json').write_text(json.dumps(pack(selected)))
(out/'conversion.json').write_text(json.dumps(dict(prover=True,cellsWithMoreThanTwoColors=640,maxMulticolorCellsPerRow=10,actualWrites=640,maxWritesPerRow=10,hardwareVerified=False)))
metadata=dict(profile='adaptive-10',version=4,width=256,height=192,schedule=schedule)
records=json.dumps(metadata,separators=(',',':')).encode();payload=bytes(bitmap)+bytes(plane)+records
(out/'image.tdec').write_bytes(struct.pack('<4sB3xIIII',b'TDEC',4,6144,6144,len(records),zlib.crc32(payload))+payload)
print('Generated 640 four-color cells: ten on each of 64 consecutive scanlines.')
