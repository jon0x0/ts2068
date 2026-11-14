from pathlib import Path
import sys,json,itertools
import numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import decode,PALETTE,LAYOUTS
O=R/'build/graphics/r64_native_fit';O.mkdir(parents=True,exist_ok=True)
# The fixed mount already exists in the level. Keep only the moving right component.
for ident,state in [(140,2),(141,1),(142,0),(143,8),(144,6),(145,5)]:
 a=np.load(R/f'build/graphics/l6_light_fill/magenta_{state}.npy');a=np.array(Image.fromarray(a).crop((24,0,48,32)).resize((16,32),Image.Resampling.NEAREST));
 for y in range(32):
  for x in [0,8]:
   row=a[y,x:x+8].copy();cs=sorted(set(map(int,row)))
   if len(cs)>2:
    candidates=[v for v in itertools.combinations(cs,2) if 0 not in cs or v[0]==0];best=None
    for p,q in candidates:
     dp=((PALETTE[row]-PALETTE[p])**2).sum(1);dq=((PALETTE[row]-PALETTE[q])**2).sum(1);v=np.where(dq<dp,q,p);cost=np.minimum(dp,dq);cost[np.isin(row,[2,3,7])]*=3;score=cost.sum()
     if best is None or score<best[0]:best=(score,v)
    a[y,x:x+8]=best[1]
 np.save(O/f'L6_{ident}.npy',a);Image.fromarray(PALETTE[a].astype('uint8')).save(O/f'L6_{ident}.png')
BAYER=(np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])+.5)/16
ids=list(range(11,23))+list(range(25,33))+list(range(36,41));records=[];new={}
for i in ids:
 old,_,_=decode(7,i)
 if not old.size:continue
 h,w=old.shape;target=old.copy();yy,xx=np.indices(old.shape);solid=old!=0
 if 18<=i<=22:
  a=np.load(R/f'build/graphics/l6_ordered_machinery/head_darker_{[0,1,2,3,1][i-18]}.npy');target=np.array(Image.fromarray(a).resize((w,h),Image.Resampling.NEAREST))
 else:
  # Preserve the native shape and animation; material shading replaces flat colour bands.
  for y in range(h):
   for x in range(w):
    c=int(old[y,x])
    if c==0:continue
    rowxs=np.where(solid[y])[0];colys=np.where(solid[:,x])[0];edge=x<=rowxs.min()+1 or y<=colys.min()+1
    if 14<=i<=17: # walker: blue armour, white/cyan gun/legs, yellow small accents
     if c==6:target[y,x]=7 if edge and y<h*.55 else 5 if x<w*.6 else 1
     elif c==3:target[y,x]=7 if edge else 5 if x<w*.55 else 1
     elif c==7:target[y,x]=7 if edge else 5
    elif c==7:target[y,x]=7 if edge else 5 if x<w*.65 else 1
    elif c==5:target[y,x]=5 if edge else 1
    elif c==6:target[y,x]=7 if edge else 6 if x<w*.65 else 4
    elif c==3:target[y,x]=5 if edge else 1
    elif c==2:target[y,x]=6 if edge else 2
  # Small warm armour highlights, not whole horizontal stripes.
  if 14<=i<=17:target[(old==6)&(yy<h*.3)&(xx>w*.6)&((xx+yy)%5==0)]=6
 arr=np.zeros_like(target)
 for y in range(h):
  for x in range(0,w,8):
   row=target[y,x:x+8];cs=sorted(set(map(int,row)))
   if len(cs)<=2:arr[y,x:x+8]=row;continue
   choices=[(p,q) for p,q in itertools.combinations(cs,2) if 0 not in cs or p==0];rgb=PALETTE[row].astype(float);best=None
   for p,q in choices:
    vp=PALETTE[p].astype(float);vq=PALETTE[q].astype(float);v=vq-vp;t=np.clip(((rgb-vp)*v).sum(1)/(v*v).sum(),0,1);a=np.where(t>BAYER[y%4,np.arange(x,x+8)%4],q,p);a[row==0]=0;err=((PALETTE[a]-rgb)**2).sum()
    if best is None or err<best[0]:best=(err,a)
   arr[y,x:x+8]=best[1]
 # Native blank 8x8 cells stay blank, preserving variable-length source storage.
 b=(R/'build/fullgame/l6_selected_r63/level07_region.bin').read_bytes();mem=bytes(0xc000)+b[0xa000:0xe000];desc=LAYOUTS[6]['enemies'][i-1];p=desc['pointer']
 for cy in range(h//8):
  for cx in range(w//8):
   tag=mem[p]
   if tag==54:arr[cy*8:cy*8+8,cx*8:cx*8+8]=0;p+=1
   else:p+=9
 np.save(O/f'L7_{i}.npy',arr);Image.fromarray(PALETTE[arr].astype('uint8')).save(O/f'L7_{i}.png');new[i]=arr;records.append({'id':i,'size':[w,h],'source':'Approved darker arcade head, reduced to native geometry' if 18<=i<=22 else 'Native silhouette/animation, authored ECM material highlights; not a verified arcade replacement'})
sheet=Image.new('RGB',(800,150*((len(new)+3)//4)),(18,18,18));d=ImageDraw.Draw(sheet)
for k,(i,a) in enumerate(new.items()):
 x=k%4*200;y=k//4*150;old=decode(7,i)[0];d.text((x+3,y+3),f'#{i} old / ECM',fill='white');sheet.paste(Image.fromarray(PALETTE[old].astype('uint8')).resize((old.shape[1]*3,old.shape[0]*3),Image.Resampling.NEAREST),(x+3,y+24));sheet.paste(Image.fromarray(PALETTE[a].astype('uint8')).resize((a.shape[1]*3,a.shape[0]*3),Image.Resampling.NEAREST),(x+80,y+24))
sheet.save(O/'L7_comparison.png');(O/'manifest.json').write_text(json.dumps(records,indent=2));print('L7',len(new),'frames; L6 six native-footprint piston states')
