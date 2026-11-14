"""Offline L2 organic boss ECM comparison; no gameplay patches."""
from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw
R=Path.cwd(); O=R/'build/graphics/l2_organic_sierra'; O.mkdir(exist_ok=True)
PAL=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)],float)
W,H=160,88
source=Image.open(R/'build/fullgame/arcade_reference/frame017400.png').convert('RGB')
a=np.array(source); r,g,b=a.astype(int).transpose(2,0,1)
mask=((r>b+7)&(g>b+7))|((r>g+18)&(r>b+7))
mask[:96]=False; mask[240:]=False; mask[:,:55]=False; mask[:,329:]=False
for _ in range(2):
 n=sum(np.roll(np.roll(mask,dy,0),dx,1)for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)])
 mask|=(n>=3)&(a.max(2)>180)&(r>=b)
poly=Image.new('1',source.size)
ImageDraw.Draw(poly).polygon([(112,96),(156,96),(170,114),(208,114),(232,96),(270,96),(268,156),(264,184),(309,183),(326,207),(302,234),(270,240),(109,240),(74,233),(60,216),(62,195),(95,183),(123,187),(125,155)],fill=1)
mask &= np.array(poly,dtype=bool)
body=Image.fromarray(np.dstack([a,np.where(mask,255,0).astype('uint8')]),'RGBA').crop((55,96,329,240))
body=body.crop(body.getbbox()); body.save(O/'arcade_body.png'); source.save(O/'arcade_context.png')
body.thumbnail((W,H),Image.Resampling.LANCZOS)
canvas=Image.new('RGBA',(W,H)); canvas.alpha_composite(body,((W-body.width)//2,H-body.height)); canvas.save(O/'scaled_source.png')
mask=np.array(canvas)[:,:,3]>=112
ALL=[(p,q)for p in range(8)for q in range(p+1,8)]
def convert(gamma,saturation,vector):
 src=np.array(canvas)[:,:,:3].astype(float)
 flesh=(src[:,:,2]>.78*src[:,:,1])&(src[:,:,0]>=src[:,:,1])&mask
 hsv=np.array(canvas.convert('RGB').convert('HSV')); mult=np.where(flesh,1.1,saturation)
 hsv[:,:,1]=np.minimum(hsv[:,:,1].astype(float)*mult,255).astype('uint8')
 rgb=np.round(205*(np.array(Image.fromarray(hsv,'HSV').convert('RGB'),float)/255)**(1/gamma)); rgb[~mask]=0
 pairs=np.zeros((H,W//8,2),np.uint8)
 for y in range(H):
  for x in range(0,W,8):
   cell=rgb[y,x:x+8]; visible=mask[y,x:x+8]
   if not visible.any():continue
   choices=[v for v in ALL if visible.all()or v[0]==0]
   pink=np.count_nonzero(flesh[y,x:x+8]&visible)>np.count_nonzero(visible)//2
   if vector:
    allowed=[(0,2),(0,7),(2,7)]if pink else[(0,6),(0,7),(6,7)]
    choices=[v for v in choices if v in allowed]
   if visible.all()and np.mean(cell@np.array([.21,.72,.07]))>90 and(not vector or pink):choices=[v for v in choices if v[0]!=0]
   def cost(v):return np.minimum(((cell-PAL[v[0]])**2).sum(1),((cell-PAL[v[1]])**2).sum(1)).sum()
   pairs[y,x//8]=min(choices,key=cost)
 bits=np.zeros((H,W),np.uint8);work=rgb.copy();coverage=np.zeros((H,W),float)
 if not vector:
  for y in range(H):
   for x in range(W):
    p,q=PAL[pairs[y,x//8]];v=q-p;coverage[y,x]=np.clip((rgb[y,x]-p)@v/max(1,v@v),0,1)
 for y in range(H):
  direction=-1 if y&1 else 1
  for x in(range(W-1,-1,-1)if direction<0 else range(W)):
   if not mask[y,x]:continue
   p,q=PAL[pairs[y,x//8]]
   if vector:
    value=int(((work[y,x]-q)**2).sum()<((work[y,x]-p)**2).sum());error=work[y,x]-(q if value else p)
   else:value=int(coverage[y,x]>=.5);error=coverage[y,x]-value
   bits[y,x]=value
   for dx,dy,weight in[(direction,0,.5),(-direction,1,.25),(0,1,.25)]:
    xx,yy=x+dx,y+dy
    if 0<=xx<W and yy<H and mask[yy,xx]and(not vector or flesh[yy,xx]==flesh[y,x]):
     if vector:work[yy,xx]+=error*weight
     else:coverage[yy,xx]+=error*weight
 attrs=(pairs[:,:,0]<<3)|pairs[:,:,1]
 rgb=np.where(bits[:,:,None],np.repeat(PAL[attrs&7],8,1),np.repeat(PAL[(attrs>>3)&7],8,1)).astype('uint8')
 assert not rgb[~mask].any()and not(attrs&192).any()
 for y in range(H):
  for x in range(0,W,8):assert len(set(map(tuple,rgb[y,x:x+8])))<=2
 return rgb,bits,attrs
profiles=[('A','Deep material shading',1.35,2.5,True),('B','Pink flesh / bronze ribs',1.8,3.5,True),('C','Bright material shading',2.2,4.5,True),('D','Coverage / unrestricted palette',1.8,3.5,False)]
records=[];sheet=Image.new('RGB',(960,650),(16,16,16));draw=ImageDraw.Draw(sheet)
scene=np.array(Image.open(R/'build/fullgame/startup_r66/ordinary_L2_col66.png').convert('RGB').resize((256,192),Image.Resampling.NEAREST));scene[64:160,56:256]=0
for n,(id,title,gamma,sat,vector)in enumerate(profiles):
 rgb,bits,attrs=convert(gamma,sat,vector);im=Image.fromarray(rgb);im.save(O/f'{id}.png')
 np.save(O/f'{id}.npy',np.argmin(((rgb[:,:,None,:].astype(float)-PAL)**2).sum(3),2).astype('uint8'))
 packed=np.packbits(bits,axis=1).tobytes();(O/f'{id}.bits').write_bytes(packed);(O/f'{id}.attrs').write_bytes(attrs.tobytes())
 # Reconstruct exported bytes independently; do not validate only working arrays.
 rb=np.unpackbits(np.frombuffer(packed,np.uint8).reshape(H,W//8),axis=1)
 ra=np.frombuffer((O/f'{id}.attrs').read_bytes(),np.uint8).reshape(H,W//8)
 rec=np.where(rb[:,:,None],np.repeat(PAL[ra&7],8,1),np.repeat(PAL[(ra>>3)&7],8,1)).astype('uint8');assert np.array_equal(rec,rgb)
 x=n%2*480;y=n//2*325;draw.text((x+8,y+8),f'{id}: {title}, gamma {gamma}',fill='white');sheet.paste(im.resize((480,264),Image.Resampling.NEAREST),(x,y+35))
 v=scene.copy();v[72:160,96:256]=rgb;Image.fromarray(v).resize((768,576),Image.Resampling.NEAREST).save(O/f'{id}_scene.png')
 records.append(dict(id=id,title=title,gamma=gamma,saturation=sat,flesh_saturation=1.1,material_pairs=vector,diffusion='serpentine RGB Sierra Lite'if vector else'serpentine scalar-coverage Sierra Lite',size=[W,H],bitmap_bytes=len(packed),attribute_bytes=attrs.size,unique_pairs=len(np.unique(attrs)),black_is_normal=True,all_8x1_cells_legal=True,export_reconstructed_exactly=True))
sheet.save(O/'comparison.png')
sections=[]
for r in records:
 id=r['id'];sections.append(f'<section><h2>{id}: {r["title"]}</h2><p>Gamma {r["gamma"]}; rib saturation {r["saturation"]}; {r["diffusion"]}.</p><img class="body" src="{id}.png"><details><summary>Offline scene composition</summary><img width="768" src="{id}_scene.png"></details></section>')
page='''<!doctype html><meta charset="utf-8"><title>L2 organic boss Sierra Lite</title><style>body{background:#161616;color:#eee;font:17px system-ui;max-width:1100px;margin:30px auto}img{image-rendering:pixelated;max-width:100%}.body{width:640px}section{border-top:1px solid #555;padding:12px 0}</style><h1>L2 organic boss: arcade-derived ECM shading</h1><p>Complete arcade body from frame17400; isolated and proportionally scaled before conversion into a160x88 canvas. Openings stay black. All cells use legal8x1 pairs and normal0..7 colours; no BRIGHT black or background diffusion.</p><p>A-C protect the pink tissue hue at1.1x saturation and separate flesh/rib palette choices. D compares unrestricted pairs and scalar coverage diffusion. Source masking uses warm colours and a coarse silhouette guide; inspect the source below for any contour loss.</p><p><strong>Asset previews only, not installed in r66.</strong> Scene compositions show appearance and size, not collision compatibility or scrolling performance. Native tile mapping, animated-mouth integration and scenery synchronization still require work.</p><h2>Your RPC reference</h2><img width="691" src="rpc_reference.png"><h2>Arcade reference</h2><img width="768" src="arcade_context.png"><h2>Isolated source at target scale</h2><img class="body" src="scaled_source.png">'''+''.join(sections)
(O/'index.html').write_text(page,encoding='utf-8')
(O/'manifest.json').write_text(json.dumps(dict(source_frame=17400,source_crop=[55,96,329,240],target=[W,H],source_mask='warm body vs blue cave plus coarse silhouette and neighbouring highlights',profiles=records,material_policy='pink tissue hue protected; red-white flesh pairs; yellow-white/dark rib pairs',status='offline asset preview; no playable/hardware/performance claim'),indent=2),encoding='utf-8')
print(O/'index.html')
