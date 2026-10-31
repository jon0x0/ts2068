"""Photographic 8x1 ECM: neutral-friendly pair fitting with fixed spatial dither.

Uses the proven V7 palette/attribute conventions, including its exclusion of
bright-black. Adds emitted-pixel chroma error to discourage false-colour gray.
No temporal frame/cell dropping; only a small attribute tie-breaking cost.
"""
import numpy as np
from full160_v7_quantizer import linear,PERCEPTUAL_POWER,PAPER,INK,AXIS,DEN,ATTR,BAYER,preview
LUMA=np.array([.2126,.7152,.0722],dtype=np.float32)
def quantize(rgb,previous=None,saturation=1.0,gamma=1.06,chroma_cost=.18):
 h,w,_=rgb.shape;assert w%8==0
 source=linear(rgb);lum=source@LUMA
 source=np.clip(np.maximum(lum[:,:,None]+(source-lum[:,:,None])*saturation,0)**(1/gamma),0,1)**PERCEPTUAL_POWER
 cells=source.reshape(-1,8,3)
 threshold=np.tile((BAYER+.5)/64,(int(np.ceil(h/8)),int(np.ceil(w/8))))[:h,:w].reshape(-1,8)
 numerator=((cells[:,:,None,:]-PAPER[None,None,:,:])*AXIS[None,None,:,:]).sum(axis=3)
 projection=np.divide(numerator,DEN[None,None,:],out=np.zeros_like(numerator),where=DEN[None,None,:]>1e-9).clip(0,1)
 closest=PAPER[None,None,:,:]+projection[:,:,:,None]*AXIS[None,None,:,:]
 errors=((cells[:,:,None,:]-closest)**2).sum(axis=(1,3))
 errors+=.06*(projection*(1-projection)*DEN[None,None,:]).sum(axis=1)
 emitted=PAPER[None,None,:,:]+(projection>threshold[:,:,None])[:,:,:,None]*AXIS[None,None,:,:]
 residual=emitted-cells[:,:,None,:]
 residual-= (residual@LUMA)[:,:,:,None]
 errors+=chroma_cost*(residual**2).sum(axis=(1,3))
 if previous is not None:
  old=np.frombuffer(previous[len(previous)//2:],dtype=np.uint8)
  errors+=.003*(ATTR[None,:]!=old[:,None])
 chosen=errors.argmin(axis=1)
 coverage=projection[np.arange(len(chosen))[:,None],np.arange(8)[None,:],chosen[:,None]]
 bits=coverage>threshold
 bitmap=(bits*(1<<np.arange(7,-1,-1))).sum(axis=1).astype(np.uint8)
 attrs=ATTR[chosen]
 assert not np.any(((attrs&64)!=0)&(((attrs&7)==0)|(((attrs>>3)&7)==0)))
 return bitmap.tobytes()+attrs.tobytes()
