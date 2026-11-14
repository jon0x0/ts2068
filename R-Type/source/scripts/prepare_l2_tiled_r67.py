from pathlib import Path
import sys,json,collections
import numpy as np
from PIL import Image
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import pack,unpack
O=R/'build/graphics/l2_integrated_r67';O.mkdir(exist_ok=True)
b=(R/'build/fullgame/startup_r66/level02_region.bin').read_bytes();src=np.load(R/'build/graphics/l2_rpc_settings/C.indices.npy');pal=np.array([[0,0,0],[1,0,206],[207,1,0],[207,1,206],[0,207,21],[1,207,207],[207,207,21],[207,207,207],[96,96,96],[2,0,253],[255,2,1],[255,2,253],[0,255,28],[2,255,255],[255,255,29],[255,255,255]],float)
attrs=np.frombuffer((R/'build/graphics/l2_rpc_settings/C.attrs').read_bytes(),np.uint8).reshape(104,24);priority=collections.Counter(attrs[y:y+8,x].tobytes()for y in range(0,104,8)for x in range(24));palette_rows=[bytes(b[0x2000+i*8:0x2008+i*8])for i in range(16)];keys={}
for i,k in enumerate(palette_rows):keys.setdefault(k,i)
for k,n in priority.most_common():
 if k not in keys and len(palette_rows)<112:keys[k]=len(palette_rows);palette_rows.append(k)
# Match missing row patterns while preserving every black/source-nonblack pixel.
def fit(block,k):
 aa=np.frombuffer(k,np.uint8);p=((aa>>3)&7)+((aa>>6)&1)*8;q=(aa&7)+((aa>>6)&1)*8;col=pal[block];dp=((col-pal[p][:,None])**2).sum(2);dq=((col-pal[q][:,None])**2).sum(2);bits=dq<dp
 black=block==0;nonblack=~black
 if any(black[y].any()and p[y]!=0 and q[y]!=0 for y in range(8)):return None
 if any(nonblack[y].any()and p[y]==0 and q[y]==0 for y in range(8)):return None
 bits[black]=np.broadcast_to((q==0)&(p!=0),block.shape)[black];bits[nonblack&(np.broadcast_to(p[:,None]==0,block.shape))]=True;bits[nonblack&(np.broadcast_to(q[:,None]==0,block.shape))]=False
 im=np.where(bits,q[:,None],p[:,None]);return float(((pal[im]-col)**2).sum()),bits,im
field_bits=np.zeros((160,32),np.uint8);field_tags=np.zeros((20,32),np.uint8);field_indices=np.zeros((160,256),np.uint8);approximated=0;exact=0
for y in range(0,104,8):
 for x in range(24):
  block=src[y:y+8,x*8:x*8+8];key=attrs[y:y+8,x].tobytes();opts=[(key,keys[key])]if key in keys else list(keys.items());best=None
  for k,id in opts:
   result=fit(block,k)
   if result is not None and(best is None or result[0]<best[0]):best=(*result,k,id)
  assert best is not None
  score,bits,im,k,id=best;yy=y+56;xx=x+8;field_bits[yy:yy+8,xx]=np.packbits(bits,axis=1).ravel();field_tags[yy//8,xx]=(id+0x90) if id>=16 else id;field_indices[yy:yy+8,xx*8:xx*8+8]=im;approximated+=score>0;exact+=score==0
rows=[];payload=bytearray();world=np.zeros((8,5),np.uint8);base=0xd442
for ty in range(1,5):
 for tx in range(8):
  pix=field_bits[ty*32:ty*32+32,tx*4:tx*4+4]
  if not pix.any():continue
  raw=bytearray()
  for cy in range(4):
   for cx in range(4):raw.append(field_tags[ty*4+cy,tx*4+cx]);raw.extend(pix[cy*8:cy*8+8,cx].tobytes())
  compressed=pack(raw);assert unpack(compressed)==raw;ident=19+len(rows);world[tx,ty]=ident;rows.append(dict(id=ident,tx=tx,ty=ty,pointer=base+len(payload),bytes=len(compressed)));payload.extend(compressed)
print([(r["id"],r["bytes"])for r in rows]);assert len(payload)<=0x870,len(payload)
(O/'body_tiles.lz').write_bytes(payload);(O/'palette.bin').write_bytes(b''.join(palette_rows));(O/'map_patch.bin').write_bytes(world.tobytes());np.save(O/'world_indices.npy',field_indices)
Image.fromarray(pal[field_indices].astype('uint8')).resize((768,480),Image.Resampling.NEAREST).save(O/'tiled_body.png');actual=field_indices[56:160,64:256];error=float(np.mean(np.abs(pal[actual]-pal[src])));Image.fromarray(pal[actual].astype('uint8')).resize((768,416),Image.Resampling.NEAREST).save(O/'body.png')
(O/'manifest.json').write_text(json.dumps({'tiles':rows,'compressed_bytes':len(payload),'palette_rows':len(palette_rows),'exact_cells':exact,'approximate_cells':approximated,'mean_absolute_RGB_error':error,'target':[192,104],'map_columns':[56,63],'image_origin_at_stop':[64,56],'transparent_geometry_preserved':True},indent=2));print('tiles',len(rows),'compressed',len(payload),'palette exact/approx',exact,approximated,'RGB mean error',error)
