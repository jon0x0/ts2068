"""Offline walker-family artwork review. Arcade sources are distinguished from native refinements."""
from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageFilter
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from walker_review_r85 import current,LAY,PAL
from build_reviewed_r72 import frames
from build_graphics import decode_roms,palette_ram
O=R/'build/graphics/walker_review_r85';sp,_=decode_roms();profiles=[];records=[]
def fit(im,size):
 im=im.convert('RGBA');ratio=min(size[0]/im.width,size[1]/im.height);im=im.resize((max(1,round(im.width*ratio)),max(1,round(im.height*ratio))),Image.Resampling.LANCZOS);out=Image.new('RGBA',size);out.alpha_composite(im,((size[0]-im.width)//2,size[1]-im.height));return out
def native_early(n,i):
 if n==3 and i>=101:
  b=(R/'build/fullgame/foundation/level03_live.bin').read_bytes();at=LAY[n-1]['enemy_descriptors_start']+(i-1)*4;w,h=b[at:at+2];p=int.from_bytes(b[at+2:at+4],'little');im=Image.new('RGBA',(w*8,h*8));pix=im.load()
  for cy in range(h):
   for cx in range(w):
    t=b[p];p+=1
    if t==54:continue
    for y in range(8):
     for x in range(8):
      if b[p+y]&(128>>x):pix[cx*8+x,cy*8+y]=(190,210,230,255)
    p+=8
  return im
 b=(R/f'build/fullgame/l5_effects_fast_r59/level{n:02d}_region.bin').read_bytes();d=frames(b,n)[i-1];im=Image.new('RGBA',(d['w']*8,d['h']*8));p=im.load()
 for k,(ptr,t,raw)in enumerate(d['cells']):
  if t==54:continue
  cy,cx=divmod(k,d['w'])
  for y in range(8):
   a=b[0x2000+(t&127)*8+y]
   for x in range(8):
    c=(a&7)if raw[1+y]&(128>>x)else(a>>3)&7
    if c:p[cx*8+x,cy*8+y]=(*PAL[c],255)
 return im
def material(im,kind='metal'):
 a=np.array(im.convert('RGBA'));rgb=a[:,:,:3].astype(float);h,w=rgb.shape[:2];mask=(a[:,:,3]>96)&(rgb.max(2)>0)
 # Fill isolated one-pixel pepper holes, not open joints, eye sockets or leg gaps.
 pad=np.pad(mask,1);neigh=sum(pad[dy:dy+h,dx:dx+w].astype(int)for dy in range(3)for dx in range(3)if(dy,dx)!=(1,1));filled=mask|((~mask)&(neigh>=7))
 blur=np.array(Image.fromarray(filled.astype('uint8')*255).filter(ImageFilter.GaussianBlur(1.1)),float)/255
 gy,gx=np.gradient(blur);y,x=np.indices(mask.shape);lum=np.clip(.72+.18*(1-y/max(h-1,1))+.8*(-gx-gy),.16,1)
 # Local surface lighting follows bevels/limbs, not repeating scanline bands.
 glint=(gy>.1)&filled;lum[glint]=np.minimum(1,lum[glint]+.24)
 color=np.zeros_like(rgb);color[:]=np.array([80,180,224])[None,None,:]*lum[:,:,None]
 high=lum>.75;color[high]=np.array([220,240,250])*lum[high,None]
 red=(rgb[:,:,0]>rgb[:,:,1]*1.5)&(rgb[:,:,0]>rgb[:,:,2]*1.4)&mask
 gold=(rgb[:,:,0]>rgb[:,:,2]*1.7)&(rgb[:,:,1]>rgb[:,:,2]*1.5)&mask
 if kind=='round':
  gold&=y<h*.30
 if kind=='yellow':gold&=(y<h*.45)|(x>w*.72)
 color[gold]=np.array([245,180,45])*lum[gold,None];color[red]=np.array([255,40,35])*.85
 color[~filled]=0;return Image.fromarray(np.concatenate([color.clip(0,255).astype('uint8'),np.where(filled[:,:,None],255,0).astype('uint8')],2))
pal1=palette_ram(R/'build/fullgame/arcade_reference/frame004200_palette_sprite.bin')[64:80]
def small(k):
 code=[1570,1572,1574,1600,1602][k];a=np.block([[sp[code],sp[code+8]],[sp[code+1],sp[code+9]]]);im=Image.fromarray(np.concatenate([pal1[a],np.where(a[:,:,None],255,0)],2).astype('uint8'));return im.crop((0,7,32,32))if k<3 else im.crop(im.getbbox())
heads=Image.open(R/'build/graphics/l6_assembly_review/head_arcade.gif')
groups=[('L1_small',1,list(range(21,26)),'arcade_small','Verified walking/raising-gun poses: arcade1570/1572/1574/1600/1602'),('L1_large',1,list(range(201,205)),'arcade_large','Four arcade-derived source cels from the existing large-walker extraction'),('L1_round',1,list(range(53,57)),'round','Native silhouette refinement; arcade identity unverified'),('L3_round',3,list(range(31,34)),'round','Before31: native silhouette refinement; arcade identity unverified'),('L3_yellow',3,[94],'yellow','Arrowed elongated yellow bot: native94,32x16; arcade identity unverified'),('L3_ground',3,list(range(101,107)),'ground','Restore pre-r72 full walker geometry; arcade identity unverified'),('L4_small',4,list(range(14,19)),'arcade_small','Same small-walker family as L1; native pose order retained'),('L4_round',4,list(range(28,32)),'round','Native silhouette refinement; arcade identity unverified'),('L6_round',6,list(range(5,9)),'round','Correct native yellow walker, not the previously withdrawn explosion match'),('L6_head',6,list(range(9,14)),'arcade_head','Arcade224/226/228/230: separate white walking-head family, accepted32x32 footprint'),('L7_round',7,list(range(11,14)),'round','Native silhouette refinement; arcade identity unverified'),('L7_head',7,list(range(18,23)),'arcade_head','Shared walking-head family;24x24 native footprint'),('L7_small',7,list(range(25,30)),'arcade_small','Same small-walker family as L1; native pose order retained')]
for family,n,ids,kind,provenance in groups:
 rec=dict(family=family,level=n,ids=ids,kind=kind,provenance=provenance,frames=[])
 for k,i in enumerate(ids):
  cur,_=current(n,i);size=cur.size;cur.save(O/f'{family}_{i}_current.png')
  if kind=='arcade_small':src=small(k)
  elif kind=='arcade_large':src=Image.open(R/f'build/graphics/enemy_upgrades_r60/{i}_arcade.png').convert('RGBA')
  elif kind=='arcade_head':heads.seek([0,1,2,3,0][k]);src=heads.convert('RGBA')
  else:src=native_early(n,i)
  src=fit(src,size);src.save(O/f'{family}_{i}_source.png')
  # A retains source colours; B gives local bevel highlights and blue armour.
  art=material(src,kind)
  for variant,image in [('A',src),('B',art)]:
   key=f'{family}_{i}_{variant}';image.save(O/f'{key}_input.png');a=np.array(image);mask=(a[:,:,3]>=112)&(a[:,:,:3].max(2)>0);rgb=a[:,:,:3].copy();rgb[~mask]=0;(O/f'{key}.rgb').write_bytes(rgb.tobytes());(O/f'{key}.mask').write_bytes(mask.astype('uint8').tobytes());profiles.append(dict(id=key,size=key,w=size[0],h=size[1],bright=True,strategy='segment-coverage'))
  rec['frames'].append(dict(id=i,size=size,key=f'{family}_{i}'))
 records.append(rec)
(O/'inputs.json').write_text(json.dumps(dict(records=records,profiles=profiles),indent=2))
s=(R/'scripts/convert_l2_actors_r67.mjs').read_text();s=s.replace('build/graphics/l2_actors_r67','build/graphics/walker_review_r85');start=s.index('const profiles=');end=s.index('const reports=',start);s=s[:start]+"const profiles=JSON.parse(fs.readFileSync(path.join(out,'inputs.json'),'utf8')).profiles;\n"+s[end:];s=s.replace('brightness:44*.02-1,contrast:54*.02,saturation:71*.02,gamma:.98','brightness:49*.02-1,contrast:65*.02,saturation:78*.02,gamma:1.13').replace('brightness:44,contrast:54,saturation:71,gamma:.98','brightness:49,contrast:65,saturation:78,gamma:1.13').replace('brightness:-.12,contrast:1.08,saturation:1.42,gamma:.98','brightness:-.02,contrast:1.3,saturation:1.56,gamma:1.13');s=s.replace("for(const p of profiles){const raw=","for(const p of profiles){const st=p.settings||{brightness:49,contrast:65,saturation:78,gamma:1.13};const raw=").replace('brightness:49*.02-1,contrast:65*.02,saturation:78*.02,gamma:1.13','brightness:st.brightness*.02-1,contrast:st.contrast*.02,saturation:st.saturation*.02,gamma:st.gamma').replace('settings:{brightness:49,contrast:65,saturation:78,gamma:1.13},parameters:{brightness:-.02,contrast:1.3,saturation:1.56,gamma:1.13}','settings:st,parameters:{brightness:st.brightness*.02-1,contrast:st.contrast*.02,saturation:st.saturation*.02,gamma:st.gamma}');(R/'scripts/convert_walkers_rpc_r85.mjs').write_text(s)
print(len(records),'families',sum(len(r['frames'])for r in records),'frames',len(profiles),'conversions')
