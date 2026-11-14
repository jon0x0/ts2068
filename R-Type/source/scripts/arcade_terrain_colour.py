"""Arcade-warm row palette with vertical chroma error diffusion."""
import numpy as np
from build_graphics import PALETTE
def row_pairs(samples):
 colours=PALETTE.astype(float);inks=[2,6,7,14,15];error=np.zeros(3);chosen=[]
 for y in range(16):
  row=samples[y];mask=np.max(row,axis=1)>45;active=row[mask]
  if not len(active):chosen.append([8,15]);continue
  # Robust surface colour ignores black sky/holes. Diffuse chroma between rows
  # instead of letting black/white coverage absorb every warm arcade shade.
  target=np.mean(active,axis=0);desired=target+error*.8;best=None
  for ink in inks:
   rgb=colours[ink];coverage=np.clip(np.dot(desired,rgb)/max(np.dot(rgb,rgb),1),.15,1)
   estimate=rgb*coverage;cost=np.sum((desired-estimate)**2)+250*(1-coverage)**2
   if best is None or cost<best[0]:best=(cost,ink,estimate)
  _,ink,estimate=best;error=np.clip(desired-estimate,-100,100);chosen.append([8 if ink>=8 else 0,ink])
 a=np.array(chosen+chosen[::-1],dtype=np.uint8);return np.repeat(a[:,None,:],4,axis=1)
