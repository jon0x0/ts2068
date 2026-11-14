"""Instance-specific8x1-compatible groups over the actual535-byte level map."""
import json
import numpy as np

def build(root,out,b,patch):
 start=int.from_bytes(b[0xc4bc:0xc4be],'little');stop=int.from_bytes(b[0xc4b4:0xc4b6],'little');w=b[start:stop]
 assert len(w)==535 and max(c&63 for c in w)==21
 tiles=[]
 for t in range(22):
  im=np.zeros((32,32),dtype='uint8')
  for cy in range(4):
   for cx in range(4):
    p=t*144+(cy*4+cx)*9;im[cy*8:cy*8+8,cx*8:cx*8+8]=np.unpackbits(np.frombuffer(patch[p+1:p+9],dtype='uint8')).reshape(8,8)
  tiles.append(im)
 cols=[]
 for c in range(len(w)//5):
  ims=[]
  for row in range(5):
   code=w[c*5+row];im=tiles[code&63]
   if code&64:im=im[:,::-1]
   if code&128:im=im[::-1]
   ims.append(im)
  cols.append(np.concatenate(ims,axis=0))
 world=np.concatenate(cols,axis=1);width=world.shape[1]//8;styles=np.zeros((20,width),dtype='uint8');groups=[]
 for row in range(20):
  parent=list(range(width))
  def find(x):
   while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
   return x
  for y in range(row*8,row*8+8):
   xs=np.flatnonzero(world[y]);a,c=xs[:-1],xs[1:];close=c-a<=9
   for left,right in set(zip(a[close]//8,c[close]//8)):parent[find(int(left))]=find(int(right))
  active=np.flatnonzero(world[row*8:row*8+8].reshape(8,width,8).any((0,2)));components={}
  for x in active:components.setdefault(find(int(x)),[]).append(int(x))
  for j,g in enumerate(sorted(components.values(),key=lambda g:g[0])):
   style=(j+row//2)&1;styles[row,g]=style;groups.append(dict(row=row,start=g[0],end=g[-1],style=style))
 masks=[sum(int(styles[y,x])<<y for y in range(20))for x in range(width)];runs=[]
 for x,mask in enumerate(masks):
  if not runs or runs[-1][1]!=mask:runs.append([x,mask])
 data=bytearray()
 for i,(_,mask) in enumerate(runs):data+=(runs[i+1][0] if i+1<len(runs) else width).to_bytes(2,'little')+mask.to_bytes(3,'little')
 data+=bytes.fromhex('ff ff 00 00 00');assert len(data)<=440
 (out/'terrain_group_runs.bin').write_bytes(data);np.save(out/'terrain_group_styles.npy',styles)
 report=dict(map_start=start,map_end=stop,map_columns=107,byte_columns=width,groups=groups,runs=runs,table_bytes=len(data),rule='Each8-row band connects foreground cells whose scanline gaps are at most8 pixels; separate level instances are not unified. Alternate warm/cool arrangements per independent group. Continuous geometry retains a compatible palette.')
 (out/'terrain_groups.json').write_text(json.dumps(report,indent=2));return report
