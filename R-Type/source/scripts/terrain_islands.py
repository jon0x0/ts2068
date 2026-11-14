"""Offline colour-island proof over all level-map orientations; no runtime work."""
import numpy as np
from collections import Counter

def islands(original,patches):
 end=int.from_bytes(original[0xc4bc:0xc4be],'little')
 stop=int.from_bytes(original[0xc4be:0xc4c0],'little')
 world=original[end:stop];count=len(world)//5
 tiles=[];labels=[];parent=list(range(353));anchor=352
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 def union(a,b):parent[find(a)]=find(b)
 for t in range(22):
  im=np.zeros((32,32),dtype=np.uint8);lab=np.zeros((32,32),dtype=np.int16)
  for cy in range(4):
   for cx in range(4):
    p=t*144+(cy*4+cx)*9;node=t*16+cy*4+cx
    im[cy*8:cy*8+8,cx*8:cx*8+8]=np.unpackbits(np.frombuffer(patches[p+1:p+9],dtype=np.uint8)).reshape(8,8)
    lab[cy*8:cy*8+8,cx*8:cx*8+8]=node
    if not patches[p]&128:union(node,anchor)
  tiles.append(im);labels.append(lab)
 joins=0
 for row in range(5):
  ims=[];labs=[]
  for c in range(count):
   code=world[c*5+row];t=code&63
   if t>=22:
    ims.append(np.zeros((32,32),dtype=np.uint8));labs.append(np.full((32,32),anchor,dtype=np.int16));continue
   im,lab=tiles[t],labels[t]
   if code&64:im,lab=im[:,::-1],lab[:,::-1]
   if code&128:im,lab=im[::-1],lab[::-1]
   ims.append(im);labs.append(lab)
  im=np.concatenate(ims,axis=1);lab=np.concatenate(labs,axis=1)
  for y in range(32):
   xs=np.flatnonzero(im[y]);a,b=xs[:-1],xs[1:];close=b-a<=9
   edges=np.unique(np.stack([lab[y,a[close]],lab[y,b[close]]],axis=1),axis=0)
   for a,b in edges:union(int(a),int(b));joins+=1
 occupied={t*16+cy*4+cx for t in range(22) for cy in range(4) for cx in range(4) if tiles[t][cy*8:cy*8+8,cx*8:cx*8+8].any()}
 groups=Counter(find(i) for i in occupied if find(i)!=find(anchor))
 selected={g for j,g in enumerate(sorted(groups)) if j%2==0}
 variants={i for i in occupied if find(i) in selected}
 return variants,dict(map_columns=count,joining_edges=joins,independent_groups=dict(groups),variant_cells=sorted(variants),rule='Consecutive foreground pixels with at most8 black pixels between are connected. Unchanged native cells anchor their connected component to the original palette. Mirrored map instances share source-cell nodes.')

if __name__=='__main__':
 from pathlib import Path
 r=Path(r'D:/T7_Recover/Jon/Personal/Timex/cartridgeconversion/R-Type')
 b=bytes(0x4000)+(r/'build/native/snapshot.bin').read_bytes()
 print(islands(b,(r/'build/art_assets/terrain_patches.bin').read_bytes())[1])
