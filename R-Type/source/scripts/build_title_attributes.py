"""Arcade-derived chrome title colours, preserving native logo bitmap."""
from pathlib import Path
import numpy as np
from PIL import Image
from build_graphics import quantize,pack,screen_offset
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/ecm_native';im=Image.open(ROOT/'build/graphics/arcade_title_reference.png').convert('RGB');rgb=np.asarray(im,dtype=float);l=(rgb*np.array([.2126,.7152,.0722])).sum(2,keepdims=True)
 for name,source in [('preserve',im),('chroma',Image.fromarray(np.clip(l+2.5*(rgb-l),0,255).astype('uint8')))]:
  bits,attrs,preview=quantize(source,black=True);pix,atr=pack(bits,attrs);preview.save(out/f'title_{name}_source.png')
  data=b''.join(atr[screen_offset(y)+1:screen_offset(y)+31] for y in range(100,144));enc=bytearray();i=0
  while i<len(data):
   n=1
   while i+n<len(data) and data[i+n]==data[i] and n<255:n+=1
   enc+=bytes([n,data[i]]);i+=n
  (out/f'title_{name}_attributes.rle').write_bytes(enc)
  if name=='chroma':assert len(enc)<=0x4e0,len(enc)
if __name__=='__main__':main()
