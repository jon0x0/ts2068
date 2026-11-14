from pathlib import Path
import sys,json,shutil,numpy as np
from PIL import Image
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from walker_review_r85 import current,PAL
V=R/'build/graphics/walker_review_r85';B=R/'build/graphics/walker_runtime_r86';O=R/'build/graphics/walker_restore_r87';O.mkdir(exist_ok=True);shutil.copytree(B,O,dirs_exist_ok=True);m=json.loads((B/'inputs.json').read_text());norm=np.array(PAL[:8],int)
def idx(im):
 a=np.array(im.convert('RGB')).astype(int);return ((a[:,:,None,:]-norm[None,None,:,:])**2).sum(3).argmin(2).astype('uint8')
def encode(name,a):
 h,w=a.shape;bits=np.zeros((h,w//8),np.uint8);attrs=np.zeros_like(bits)
 for y in range(h):
  for cx in range(w//8):
   row=a[y,cx*8:cx*8+8];cs=sorted(set(map(int,row)));assert len(cs)<=2,(name,y,cx,cs);p,q=(cs[0],cs[-1]);bits[y,cx]=sum(128>>k for k,v in enumerate(row)if v==q)if p!=q else 0;attrs[y,cx]=(p<<3)|q
 (O/(name+'.bits')).write_bytes(bits.tobytes());(O/(name+'.attrs')).write_bytes(attrs.tobytes());Image.fromarray(norm[a].astype('uint8')).save(O/(name+'.png'))
def fourth(a):
 b=a.copy();h,w=b.shape;cut=h*2//3;old=b[cut:].copy();b[cut:]=0;b[cut:,:w//2-1]=old[:,1:w//2];b[cut:,w//2+1:]=old[:,w//2:-1]
 # Local leg shifts may merge a cell: choose its dominant nonblack ink, keep silhouette.
 for y in range(cut,h):
  for x in range(0,w,8):
   row=b[y,x:x+8];cs=set(map(int,row))
   if len(cs)>2:
    vis=row!=0;counts=np.bincount(row[vis],minlength=8);row[vis]=int(counts.argmax())
 return b
for g in m['groups']:
 n,key=g['level'],g['key'];aa=[a for a in m['assets']if a['level']==n and a['key']==key];ims=[]
 if key in['yellow','exhaust']:continue
 if key=='small':
  ims=[np.load(R/f'build/graphics/small_walker_highlights/blue_{i}.npy')for i in[21,22,23]];ims.append(fourth(ims[1]))
 elif key.startswith('raise'):ims=[np.load(R/f'build/graphics/small_walker_highlights/blue_{24+int(key[-1])}.npy')]
 elif key=='head':
  ims=[np.load(R/f'build/graphics/l6_surface_refinement/head_deeper_{k}.npy')for k in range(4)]if n==6 else[idx(current(7,i)[0])for i in[18,19,20,22]]
 elif key=='large':ims=[idx(current(1,i)[0])for i in range(201,205)]
 elif key=='round':
  ids=g['original'];ims=[idx(Image.open(V/f'L{n}_round_{i}_source.png'))for i in ids];ims=(ims+[fourth(ims[1])])[:4]if len(ims)==3 else ims
 elif key.startswith('ground'):
  # Preserve full original geometry rather than returning to missing-body r84 cache data.
  ims=[]
  for a in aa:
   im=Image.open(B/(a['name']+'_source.png')).convert('RGBA');v=np.array(im);arr=np.where(v[:,:,3]>=112,7,0).astype('uint8');ims.append(arr)
 else:raise AssertionError(key)
 assert len(ims)==len(aa),(n,key)
 for a,im in zip(aa,ims):assert list(im.shape[::-1])==a['size'];encode(a['name'],im)
for a in m['assets']:
 if a['key']in['yellow','exhaust']:
  for suf in['.bits','.attrs']:assert (O/(a['name']+suf)).read_bytes()==(B/(a['name']+suf)).read_bytes()
(O/'restoration.json').write_text(json.dumps(dict(approved_blue_source='small_walker_highlights/blue_21..25.npy',head32_source='l6_surface_refinement/head_deeper_0..3.npy',head24_source='r84 native L7 descriptors18/19/20/22',approved_yellow_exhaust_unchanged=True,no_global_RPC_reconversion=True),indent=2))
