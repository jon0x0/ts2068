"""Arcade scene/object sources adapted to the native boss cell layouts."""
from pathlib import Path
import json,sys,collections
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_graphics import decode_roms,palette_ram,fit_pairs,quantize,PALETTE
from decode_arcade_objects import render
CAP=ROOT/'build/fullgame/arcade_reference'
def scene(frame,box,warm=False):
 im=Image.open(CAP/f'frame{frame:06d}.png').convert('RGB').crop(box);a=np.asarray(im);rgb=a.astype(int);alpha=a.max(2)>12
 if warm:alpha&=(rgb[:,:,0]>rgb[:,:,2]+12)&(rgb[:,:,1]>rgb[:,:,2]+5)
 return Image.fromarray(np.concatenate([a,np.where(alpha[:,:,None],255,0).astype('uint8')],axis=2),'RGBA')
def objects(frame,colour,box=None,codes=None):
 _,rows=render(frame,SPRITES);im=Image.new('RGBA',(384,256))
 for d,tile in reversed(rows):
  if d['colour']==colour and (codes is None or d['code']in codes):im.alpha_composite(tile,(d['x'],d['y']))
 if box:im=im.crop(box)
 bbox=im.getbbox();assert bbox,(frame,colour,box,codes)
 return im.crop(bbox)
def resized(image,w,h):return image.resize((w,h),Image.Resampling.LANCZOS)
def build_sources():
 sources={n:{}for n in range(1,9)}
 sources[1][8]=scene(10200,(104,16,264,212))
 mouth=objects(10200,2,codes={946});tail=objects(10200,1,box=(0,115,100,180))
 for ident in [9,11,12]:sources[1][ident]=mouth
 for ident in [16,17,18,19]:sources[1][ident]=tail
 left=scene(16800,(48,88,104,136),True);right=scene(16800,(336,40,384,96),True)
 for ident,im in zip([3,4,5,6],[left,right,right.transpose(Image.Transpose.FLIP_LEFT_RIGHT),left.transpose(Image.Transpose.FLIP_LEFT_RIGHT)]):sources[2][ident]=im
 ship=Image.open(ROOT/'build/fullgame/arcade_objects/giant_ship_panorama.png').convert('RGBA').crop((0,45,570,215));ship=resized(ship,368,104)
 for i,ident in enumerate(range(41,87)):sources[3][ident]=ship.crop((i*8,0,i*8+8,104))
 turret=objects(26400,13,box=(60,80,132,126));sources[3][40]=turret
 for ident in range(101,107):sources[3][ident]=objects(26400,7,box=(200,55,320,200))
 side=objects(36600,11,box=(275,30,383,110));front=objects(36600,11,box=(35,110,142,212))
 sources[4].update({25:side,26:side,27:front})
 sources[5][8]=objects(44700,7,box=(88,68,158,138))
 cells=[objects(44700,6,codes={code})for code in [2964,2966,2976]]
 # Extract one genuine32x32 cel from each object family, not the full cloud.
 _,rows=render(44700,SPRITES)
 cells=[next(tile for d,tile in rows if d['code']==code and d['colour']==6)for code in [2964,2966,2976]]
 for ident in range(9,27):sources[5][ident]=cells[(ident-9)%len(cells)]
 boxes=[objects(54000,7,box=box)for box in [(26,94,90,158),(242,82,306,146),(178,178,242,242)]]
 for ident in range(18,26):sources[6][ident]=boxes[(ident-18)%3]
 for ident in range(26,34):sources[6][ident]=boxes[(ident-26)%3].crop((0,48,64,64))
 body=objects(57900,7,box=(90,90,230,148));head=objects(57900,4,box=(58,90,98,132))
 sources[7].update({49:head,50:body,51:head,52:body,53:body,54:body})
 for ident,frame in zip(range(42,47),[71100,71700,72300,72900,73500]):sources[8][ident]=scene(frame,(320,88,384,152))
 return sources
