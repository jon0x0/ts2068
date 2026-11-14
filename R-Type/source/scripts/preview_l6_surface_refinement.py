from pathlib import Path
import sys,json,hashlib,itertools
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from boss_motion_assets_r60 import PALETTE
OUT=ROOT/'build/graphics/l6_surface_refinement';OUT.mkdir(parents=True,exist_ok=True)
SRC=ROOT/'build/graphics/l6_assembly_review';HEAD=ROOT/'build/graphics/l6_corrected_sources'
BAYER=(np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])+.5)/16
LINES=(np.array([[0,2,1,3],[8,10,9,11],[4,6,5,7],[12,14,13,15]])+.5)/16
reports=[]
def image(a):return Image.fromarray(PALETTE[a].astype('uint8'))
def save(stem,a):
 assert a.min()>=0 and a.max()<=7 and a.shape[1]%8==0
 assert all(len(set(row[x:x+8]))<=2 for row in a for x in range(0,a.shape[1],8))
 np.save(OUT/(stem+'.npy'),a);im=image(a);im.save(OUT/(stem+'.png'));return im

def gif(stem,frames):
 fs=[im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST)for im in frames];fs[0].save(OUT/(stem+'.gif'),save_all=True,append_images=fs[1:],duration=280,loop=0,disposal=2)

def ordered(rgb,alpha,classes=None,gray=None,redmask=None,pattern=LINES):
 h,w=alpha.shape;out=np.zeros((h,w),np.uint8)
 for y in range(h):
  for x in range(0,w,8):
   vis=alpha[y,x:x+8];row=rgb[y,x:x+8];rm=redmask[y,x:x+8]if redmask is not None else np.zeros(8,bool)
   if not vis.any():continue
   if gray is not None and gray[y,x:x+8].sum()>=4 and not rm.any():candidates=[(0,7)]
   else:
    colors=list(range(1,8))
    if redmask is not None and not rm.any():colors=[c for c in colors if c not in [2,3]]
    if classes is not None:
     c=classes[y,x:x+8][vis];dominant=int(np.bincount(c,minlength=5).argmax())
     if dominant==1:colors=[1,5,7] # pistons: blue/cyan/white
     elif dominant==2:colors=[5,6,7] # housing: cyan/yellow/white
     elif dominant==3:colors=[7] # tubing: black/white
     if dominant==3:candidates=[(0,7)]
     else:candidates=list(itertools.combinations([0]+colors if not vis.all()else colors,2))
    else:candidates=list(itertools.combinations([0]+colors if not vis.all()else colors,2))
    if not vis.all():candidates=[v for v in candidates if 0 in v]
   best=None
   for p,q in candidates:
    vp=PALETTE[p].astype(float);vq=PALETTE[q].astype(float);v=vq-vp;coverage=np.clip(((row-vp)*v).sum(1)/(v*v).sum(),0,1);t=np.array([pattern[y%4,(x+i)%4]for i in range(8)]);sel=coverage>t;vals=np.where(sel,q,p).astype(np.uint8)
    if redmask is not None:
     wrong=np.isin(vals,[2,3])&~rm;vals[wrong]=q if q not in[2,3]else p
    vals[~vis]=0;err=((PALETTE[vals].astype(float)-row)**2).sum(1);err[~vis]=0
    # Preserve real red accents without allowing scattered invented red pixels.
    if redmask is not None:err[rm]*=2
    score=float(err.sum())
    if best is None or score<best[0]:best=(score,vals)
   assert best is not None
   out[y,x:x+8]=best[1]
 return out

head_frames={};head_stats=[]
for strength,label in [(.55,'fine'),(.8,'deeper')]:
 frames=[]
 for i,code in enumerate([224,226,228,230]):
  rgba=np.array(Image.open(HEAD/f'walker_arcade_{code}.png').convert('RGBA'));rgb=rgba[:,:,:3].astype(float);vis=rgba[:,:,3]>=96;r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2];lum=rgb.mean(2)
  red=(r>g*1.4)&(r>b*1.2)&vis
  base=np.load(SRC/f'head32_pose{i}.npy');target=PALETTE[base].astype(float)
  # Use source geometry for red, not colours invented by pair fitting.
  stray=np.isin(base,[2,3])&~red;target[stray]=(205,205,205);target[red]=(205,0,0)
  neutral=vis&((rgb.max(2)-rgb.min(2))<80)&(g>=r)&(b>=r)
  mid=neutral&(lum>75)&(lum<190)&(np.indices(vis.shape)[0]<25)
  shade=np.minimum(205,lum*strength+205*(1-strength));target[mid]=np.repeat(shade[:,:,None],3,2)[mid]
  gray=np.zeros(vis.shape,bool)
  for y in range(32):
   for x in range(0,32,8):
    if mid[y,x:x+8].sum()>=4 and not red[y,x:x+8].any() and np.count_nonzero(vis[y,x:x+8]&~neutral[y,x:x+8])<=1:gray[y,x:x+8]=True
  arr=ordered(target,vis,gray=gray,redmask=red,pattern=BAYER)
  assert not np.any(np.isin(arr,[2,3])&~red)
  addedblack=int(np.count_nonzero((arr==0)&vis&gray));assert addedblack>0
  frames.append(save(f'head_{label}_{i}',arr));head_stats.append({'style':label,'code':code,'gray_black_pixels':addedblack,'red_pixels':int(np.isin(arr,[2,3]).sum()),'invented_red_pixels':0})
 head_frames[label]=frames;gif('head_'+label,frames)

pairs=[(320,324),(1476,336),(1488,340)];machine={};machine_stats=[]
for style,pattern in [('horizontal',LINES),('ordered',BAYER)]:
 frames=[]
 for i,(left,right)in enumerate(pairs):
  source=Image.open(SRC/f'arcade_pair_{left}_{right}.png').convert('RGBA');fit=source.resize((43,32),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',(48,32));canvas.alpha_composite(fit,(2,0));a=np.array(canvas);rgb=a[:,:,:3].astype(float);r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2];vis=(a[:,:,3]>=96)&(rgb.max(2)>10);lum=rgb.mean(2);xx,yy=np.meshgrid(np.arange(48),np.arange(32));sx=(xx-2)/43*64;sy=yy/32*48
  tube=(sx<18)&vis
  warm=(r>.7*g)&(g>.7*r)&(b<.7*g)&vis&~tube
  tip=(sx>=54)&vis&((r>1.35*g)|(b>1.35*g))&~warm
  piston=(sx>=34)&(sx<57)&((sy<22)|(sy>=29))&vis&~warm&~tip&~tube
  body=vis&~tube&~piston&~tip
  cls=np.zeros(vis.shape,np.uint8);cls[piston]=1;cls[body]=2;cls[tube]=3;cls[tip]=4
  target=np.zeros_like(rgb)
  # Gray tubing uses actual white/black ordered coverage, normal black only.
  shade=np.clip(lum*1.25+30,50,205);target[tube]=np.repeat(shade[:,:,None],3,2)[tube]
  for mask,color in [(piston&(lum<110),(0,0,205)),(piston&(lum>=110)&(lum<185),(0,205,205)),(piston&(lum>=185),(205,205,205)),(body&(lum<85),(0,205,205)),(body&(lum>=85)&(lum<185),(205,205,0)),(body&(lum>=185),(205,205,205)),(tip&(lum<90),(205,0,0)),(tip&(lum>=90)&(lum<165),(205,0,205)),(tip&(lum>=165),(205,205,205))]:target[mask]=color
  arr=ordered(target,vis,classes=cls,pattern=pattern)
  frames.append(save(f'machine_{style}_{i}',arr));machine_stats.append({'style':style,'codes':[left,right],'colors':sorted(set(map(int,arr.flat))),'piston_pixels':int(piston.sum()),'tube_pixels':int(tube.sum()),'tip_pixels':int(tip.sum())})
 machine[style]=frames;gif('machine_'+style,[frames[j]for j in [0,1,2,1]])

sheet=Image.new('RGB',(1000,4*190),(18,18,18));d=ImageDraw.Draw(sheet)
for i,code in enumerate([224,226,228,230]):
 images=[Image.open(HEAD/f'walker_arcade_{code}.png'),Image.open(SRC/f'head32_pose{i}.png'),head_frames['fine'][i],head_frames['deeper'][i]]
 for col,(title,im)in enumerate(zip(['ARCADE SOURCE','PREVIOUS32x32','FINE GRAY / CLEAN RED','DEEPER GRAY / CLEAN RED'],images)):
  x=col*250;y=i*190;d.text((x+4,y+3),title,fill='white');im=im.resize((128,128),Image.Resampling.NEAREST);sheet.paste(im.convert('RGB'),(x+4,y+28))
sheet.save(OUT/'head_comparison.png')
sheet=Image.new('RGB',(1150,3*220),(18,18,18));d=ImageDraw.Draw(sheet)
for i,(left,right)in enumerate(pairs):
 images=[Image.open(SRC/f'arcade_pair_{left}_{right}.png'),Image.open(SRC/f'assembly_48x32_pose{i}.png'),machine['horizontal'][i],machine['ordered'][i]]
 for col,(title,im)in enumerate(zip(['ORIGINAL PAIRED POSE','PREVIOUS ACTUAL PAIRED','HORIZONTAL SHADING','FINER ORDERED'],images)):
  x=col*285;y=i*220;d.text((x+4,y+3),title,fill='white');d.text((x+4,y+17),f'{left}+{right}',fill='gray');im=im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST);sheet.paste(im.convert('RGB'),(x+4,y+38))
sheet.save(OUT/'machinery_comparison.png')
archive=ROOT/'build/fullgame/force_loading_r62/RType_TS2068_r62.zip';sha=hashlib.sha256(archive.read_bytes()).hexdigest();assert sha=='e3e067696e54563880e59ad2fa6974340a2c56d497f56e4c6b0fdf2515f69574'
(OUT/'validation.json').write_text(json.dumps({'preview_only':True,'head_size':[32,32],'heads':head_stats,'machinery':machine_stats,'machine_storage':[48,32],'machine_fitted_source':[43,32],'source_poses':pairs,'ordered_patterns_fixed_object_coordinates':True,'normal_black_only':True,'pistons_not_lamps':True,'legal8x1':True,'runtime_unchanged_sha256':sha,'animation':'Illustrative280ms; exactsourceposes0/1/2/1, not nativeFPS'},indent=2))
(OUT/'index.html').write_text('''<meta charset=utf-8><title>L6 surface and piston refinement</title><style>body{background:#151515;color:white;font:18px system-ui;max-width:1250px;margin:24px auto;padding:16px}img{max-width:100%;image-rendering:pixelated}.row{display:flex;gap:36px;flex-wrap:wrap}a{color:cyan}</style><h1>L6: gray shading and actual piston motion</h1><h2>#9-13:32x32 retained</h2><p>Red output is restricted to the source red-accent pixels. The gray middle now uses controlled black/white ordered dithering. Fine and deeper gray alternatives are shown; blue/cyan shadows remain elsewhere. Exact mapping of four arcade poses to five native poses is still pending.</p><div class=row><figure><figcaption>Fine gray</figcaption><img src=head_fine.gif></figure><figure><figcaption>Deeper gray</figcaption><img src=head_deeper.gif></figure></div><img src=head_comparison.png><h2>#14 family: actual paired piston poses</h2><p>The three original paired poses are converted together in their 0-1-2-1 sequence. Piston motion is preserved; no fake lamp-on/off frames. Pistons use white/cyan/blue; housing uses yellow/cyan/white; tubing uses white/normal black; dome tips retain richer red/magenta/white highlights. Normal black avoids the hardware bright-black trail issue.</p><p>The horizontal option clusters ordered shading into scanlines. The finer option uses a fixed Bayer pattern. Both stay anchored to object coordinates, with no random dithering. Storage 48x32, source fitted 43x32.</p><div class=row><figure><figcaption>Horizontal shading</figcaption><img src=machine_horizontal.gif></figure><figure><figcaption>Finer ordered</figcaption><img src=machine_ordered.gif></figure></div><img src=machinery_comparison.png><p>Asset review only; game files unchanged. <a href=validation.json>Validation and source details</a>.</p>''',encoding='utf-8')
print(json.dumps({'heads':head_stats,'machinery':machine_stats}))
