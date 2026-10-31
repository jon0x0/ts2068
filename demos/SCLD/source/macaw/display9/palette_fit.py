"""Eight updates per line with register-preloaded, shared new attributes."""
from pathlib import Path
import argparse,itertools,json,struct,zlib
import numpy as np
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parent
# Match Retro Pixel Converter's Timex palette, including BRIGHT dark gray.
PALETTE=np.array([(0,0,0),(1,0,206),(207,1,0),(207,1,206),(0,207,21),(1,207,207),(207,207,21),(207,207,207),
                  (96,96,96),(2,0,253),(255,2,1),(255,2,253),(0,255,28),(2,255,255),(255,255,29),(255,255,255)],dtype=np.uint8)
def linear(v):return np.where(v<=.04045,v/12.92,((v+.055)/1.055)**2.4)
PAL=linear(PALETTE.astype(float)/255)
PAIRS=np.array([(a+bright,b+bright) for bright in (0,8) for a,b in itertools.combinations_with_replacement(range(8),2)])
ATTR=np.array([(a&7)|((b&7)<<3)|(64 if a>=8 else 0) for a,b in PAIRS],dtype=np.uint8)
DUAL=np.array(list(itertools.combinations_with_replacement(range(len(PAIRS)),2)))
def row(y):return ((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
def pair_errors(pixels):
    # Fit the linear-light color segment, including the mixtures a spatial
    # dither can render, rather than selecting pairs by nearest solid colors.
    a=PAL[PAIRS[:,0]];delta=PAL[PAIRS[:,1]]-a;norm=(delta*delta).sum(axis=-1)
    dots=np.einsum('...pc,kc->...pk',pixels,delta)-(a*delta).sum(axis=-1)
    blend=np.clip(dots/np.maximum(norm,1e-20),0,1)
    dist=((pixels[...,None,:]-a)**2).sum(axis=-1)
    errors=np.maximum(0,dist-2*blend*dots+blend*blend*norm).sum(axis=-2)
    return errors
def pair_fit(pixels):
    errors=pair_errors(pixels);idx=errors.argmin(axis=-1)
    return idx,np.take_along_axis(errors,idx[...,None],axis=-1)[...,0]
