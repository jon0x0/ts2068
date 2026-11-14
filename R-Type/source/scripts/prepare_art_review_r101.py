from pathlib import Path
import sys,json,numpy as np,base64,shutil
from PIL import Image,ImageFilter
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));import walker_review_r85 as old
old.B=R/'build/releases/r100'
O=R/'build/graphics/l2_art_review_r101';O.mkdir(exist_ok=True);profiles=[];records=[]
PAL=np.array(old.PAL,np.uint8)
def add(key,im,size,settings=None,**extra):
 im=im.convert('RGBA');im.thumbnail(size,Image.Resampling.LANCZOS);can=Image.new('RGBA',size);can.alpha_composite(im,((size[0]-im.width)//2,size[1]-im.height));a=np.array(can);mask=(a[:,:,3]>=112)&(a[:,:,:3].max(2)>0);rgb=a[:,:,:3].copy();rgb[~mask]=0;can.save(O/f'{key}_source.png');(O/f'{key}.rgb').write_bytes(rgb.tobytes());(O/f'{key}.mask').write_bytes(mask.astype('uint8').tobytes());profiles.append(dict(id=key,size=key,w=size[0],h=size[1],bright=True,strategy='segment-coverage',settings=settings or dict(brightness=44,contrast=54,saturation=71,gamma=.98),**extra))
def actual(n,key):
 meta=next(v for v in json.loads((R/'build/releases/r100/walker_runtime.json').read_text())if v['level']==n);raw=(R/f'build/releases/r100/L{n}_runtime_art.bin').read_bytes();base=meta['assets'][0]['pointer'];ims=[]
 for a in meta['assets']:
  if a['key']!=key:continue
  w,h=a['size'];b=raw[a['pointer']-base:a['pointer']-base+a['bytes']];idx=np.zeros((h,w),np.uint8)
  for x in range(w//8):
   for y in range(h):
    bits,t=b[(x*h+y)*2:(x*h+y)*2+2];bank=8 if t&64 else 0
    for k in range(8):idx[y,x*8+k]=((t&7)if bits&(128>>k)else(t>>3)&7)+bank
  im=Image.fromarray(PAL[idx]);im.save(O/f'L{n}_{key}_current_{len(ims)}.png');ims.append(im)
 return ims
actual(1,'small');actual(1,'large');actual(3,'exhaust')
jobs=json.loads((R/'build/graphics/walker_choice_r90/choice_jobs.json').read_text())
for k in range(4):
 p=jobs[k]['profile'];rgb=np.frombuffer(base64.b64decode(p['raw']),np.uint8).reshape(24,32,3);mask=np.frombuffer(base64.b64decode(p['mask']),np.uint8).reshape(24,32);im=Image.fromarray(np.concatenate([rgb,mask[:,:,None]*255],2));add(f'walker_A_{k}',im,(32,24),dict(brightness=49,contrast=60,saturation=80,gamma=1.2))
 add(f'walker_B_{k}',Image.open(R/f'build/graphics/walker_runtime_r86/L1_small_{k}_source.png'),(32,24),dict(brightness=49,contrast=65,saturation=85,gamma=1.15))
for i in [3,4]:
 im,kind=old.current(2,i);im.save(O/f'L2_{i}_current.png');src=Image.open(R/f'build/graphics/l2_geometry_review_r66/{i}_isolated_source.png');add(f'L2_{i}_rpc',src,im.size);add(f'L2_{i}_detail',src,im.size,dict(brightness=49,contrast=60,saturation=85,gamma=1.2))
# Actual screen geometry. Convert material lighting, not a resized terrain strip.
b=(O/'L2_16.home.bin').read_bytes();idx=np.zeros((192,256),np.uint8)
for y in range(192):
 at=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
 for x in range(32):
  t=b[0x6000+at+x];bits=b[0x4000+at+x]
  for k in range(8):idx[y,x*8+k]=(t&7)if bits&(128>>k)else(t>>3)&7
mask=(idx>0);mask[155:]=False;mask&=np.isin(idx,[6]) # authored terrain only, exclude sprites/HUD
arc=Image.open(R/'build/graphics/l2_geometry_review_r66/arcade_reference.png').convert('RGB');arc.save(O/'arcade_reference.png')
for name,colors,allowed in [('olive',[(70,60,35),(139,126,79),(238,222,171)],[4,6,7]),('organic',[(85,22,30),(205,65,73),(255,219,208)],[2,3,7])]:
 a=np.zeros((160,256,4),np.uint8)
 for y in range(155):
  xs=np.flatnonzero(mask[y]);groups=[]
  for x in xs:
   if not groups or x-groups[-1][-1]>8:groups.append([int(x)])
   else:groups[-1].append(int(x))
  for g in groups:
   l,r=g[0],g[-1];centre=(l+r)/2;radius=max((r-l+1)/2,1)
   for x in g:
    curve=np.sqrt(max(0,1-((x-centre)/radius)**2));rib=(.14 if (y%8)<2 else 0);light=np.clip(.18+.6*curve+rib,0,1);v=np.array(colors[0])*(1-light)+np.array(colors[2])*light;a[y,x,:3]=v;a[y,x,3]=255
 add('terrain_'+name,Image.fromarray(a),(256,160),dict(brightness=50,contrast=50,saturation=50,gamma=1.0),coherent=True,allowedInk=allowed)
# Plume candidates inspired by the supplied rocket photograph: blue/white nozzle, warm outer tail.
for k in range(4):
 a=np.zeros((16,48,4),np.uint8)
 for y in range(16):
  for x in range(40):
   t=x/39;radius=1.1+4.6*t;dy=abs(y-7.5);wave=.25*np.sin(x*.8+k*1.5)
   if dy>radius+wave:continue
   core=dy<max(.6,radius*.42);rgb=([230,245,255]if t>.7 else[100,165,255])if core and t>.4 else ([255,225,110]if core else[230,55,15]);a[y,x]=[*rgb,255]
 cur=np.array(Image.open(O/f'L3_exhaust_current_{k}.png').convert('RGBA'));a[:,40:48]=cur[:,40:48];a[:,40:48,3]=np.where(cur[:,40:48,:3].max(2)>0,255,0)
 add(f'exhaust_{k}',Image.fromarray(a),(48,16),dict(brightness=50,contrast=50,saturation=50,gamma=1.0))
(O/'inputs.json').write_text(json.dumps(dict(profiles=profiles),indent=2))
s=(R/'scripts/convert_walkers_rpc_r85.mjs').read_text().replace('build/graphics/walker_review_r85','build/graphics/l2_art_review_r101')
needle=" const result=new Float32Array(n*3);"
coherent="""
 if(p.coherent){for(let y=0;y<p.h;y++){const xs=[];for(let x=0;x<p.w;x++)if(mask[y*p.w+x])xs.push(x);const groups=[];for(const x of xs){if(!groups.length||x-groups.at(-1).at(-1)>8)groups.push([x]);else groups.at(-1).push(x);}for(const g of groups){let best=Infinity,chosen=0;for(const ink of p.allowedInk){let error=0;const c=palettes[0][ink];for(const x of g){const k=(y*p.w+x)*3;error+=(work[k]-c[0])**2+(work[k+1]-c[1])**2+(work[k+2]-c[2])**2;}if(error<best){best=error;chosen=ink;}}for(let bx=Math.floor(g[0]/8);bx<=Math.floor(g.at(-1)/8);bx++){attrs[y*p.w/8+bx]=chosen;colors[y][bx]=[palettes[0][chosen],palettes[0][0]];}}}}
"""
assert needle in s;s=s.replace(needle,coherent+needle);(R/'scripts/convert_art_review_r101.mjs').write_text(s)
print('Prepared',len(profiles),'proposals; no game or release files changed.')

