"""Natural-colour 8x1 ECM: fixed ordered shading, no gray bright-black."""
import numpy as np
from PIL import Image

PALETTE=np.array([[0,0,0],[0,0,205],[205,0,0],[205,0,205],
 [0,205,0],[0,205,205],[205,205,0],[205,205,205],
 [96,96,96],[2,0,253],[255,2,1],[255,2,253],
 [0,255,28],[2,255,255],[255,255,29],[255,255,255]],dtype=np.uint8)
def linear(rgb):
 v=np.asarray(rgb,dtype=np.float32)/255
 return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
# A perceptual working space avoids very sparse black/white mixtures in dark
# photographed material. Dither density should preserve visible midtone detail.
PERCEPTUAL_POWER=.65
PAL=linear(PALETTE)**PERCEPTUAL_POWER
# Canonical orientation avoids gratuitous paper/ink swaps. Exclude colour
# zero in BRIGHT cells: that entry is gray in this TS2068 preview palette.
CAND=[]
for bright in (0,1):
 for paper in range(8):
  for ink in range(paper,8):
   if bright and (paper==0 or ink==0):continue
   CAND.append((bright*64+paper*8+ink,paper+bright*8,ink+bright*8))
ATTR=np.array([c[0] for c in CAND],dtype=np.uint8)
PAPER=PAL[[c[1] for c in CAND]];INK=PAL[[c[2] for c in CAND]]
AXIS=INK-PAPER;DEN=(AXIS**2).sum(axis=1)
BAYER=np.array([[0,32,8,40,2,34,10,42],[48,16,56,24,50,18,58,26],
 [12,44,4,36,14,46,6,38],[60,28,52,20,62,30,54,22],
 [3,35,11,43,1,33,9,41],[51,19,59,27,49,17,57,25],
 [15,47,7,39,13,45,5,37],[63,31,55,23,61,29,53,21]],dtype=np.float32)

def quantize(rgb,previous=None,saturation=1.15,gamma=1.1):
 h,w,_=rgb.shape;assert w%8==0
 source=linear(rgb)
 luma=source@np.array([.2126,.7152,.0722],dtype=np.float32)
 source=np.clip(np.maximum(luma[:,:,None]+(source-luma[:,:,None])*saturation,0)**(1/gamma),0,1)
 source=source**PERCEPTUAL_POWER
 cells=source.reshape(h*(w//8),8,3)
 numerator=((cells[:,:,None,:]-PAPER[None,None,:,:])*AXIS[None,None,:,:]).sum(axis=3)
 projection=np.divide(numerator,DEN[None,None,:],out=np.zeros_like(numerator),where=DEN[None,None,:]>1e-9).clip(0,1)
 closest=PAPER[None,None,:,:]+projection[:,:,:,None]*AXIS[None,None,:,:]
 errors=((cells[:,:,None,:]-closest)**2).sum(axis=(1,3))
 # Small texture cost prevents arbitrary long colour segments on flat cells;
 # segment fitting still preserves intermediate shading through spatial mix.
 errors+=.04*(projection*(1-projection)*DEN[None,None,:]).sum(axis=1)
 if previous is not None:
  old=np.frombuffer(previous[len(previous)//2:],dtype=np.uint8)
  errors+=.002*(ATTR[None,:]!=old[:,None])
 chosen=errors.argmin(axis=1)
 coverage=projection[np.arange(len(chosen))[:,None],np.arange(8)[None,:],chosen[:,None]]
 threshold=np.tile((BAYER+.5)/64,(int(np.ceil(h/8)),int(np.ceil(w/8))))[:h,:w].reshape(-1,8)
 bits=coverage>threshold
 bitmap=(bits*(1<<np.arange(7,-1,-1))).sum(axis=1).astype(np.uint8)
 attrs=ATTR[chosen]
 assert not np.any(((attrs&64)!=0)&(((attrs&7)==0)|(((attrs>>3)&7)==0)))
 return bitmap.tobytes()+attrs.tobytes()

def preview(raw,w,h,scale=1):
 plane=w*h//8;bitmap=np.frombuffer(raw[:plane],dtype=np.uint8)
 attrs=np.frombuffer(raw[plane:],dtype=np.uint8)
 ink=(attrs&7)+(attrs>>6)*8;paper=((attrs>>3)&7)+(attrs>>6)*8
 bits=((bitmap[:,None]>>np.arange(7,-1,-1))&1).astype(bool)
 rgb=PALETTE[np.where(bits,ink[:,None],paper[:,None])].reshape(h,w,3)
 im=Image.fromarray(rgb)
 return im.resize((w*scale,h*scale),Image.Resampling.NEAREST)
