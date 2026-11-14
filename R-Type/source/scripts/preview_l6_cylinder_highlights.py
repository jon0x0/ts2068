from pathlib import Path
import sys,itertools,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'))
from boss_motion_assets_r60 import PALETTE
S=R/'build/graphics/l6_assembly_review';O=R/'build/graphics/l6_cylinder_highlights';O.mkdir(parents=True,exist_ok=True)
B=(np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])+.5)/16
pairs=[(320,324),(1476,336),(1488,340)];allframes={};report=[]
for style in ['cyan_rim','cyan_metal']:
 fs=[]
 for i,(l,r) in enumerate(pairs):
  src=Image.open(S/f'arcade_pair_{l}_{r}.png').convert('RGBA').resize((43,32),Image.Resampling.NEAREST);can=Image.new('RGBA',(48,32));can.alpha_composite(src,(2,0));a=np.array(can);rgb=a[:,:,:3].astype(float);vis=a[:,:,3]>127;rr,gg,bb=rgb.transpose(2,0,1);y,x=np.indices(vis.shape);sx=(x-2)*64/43;sy=y*48/32
  warm=(gg>.7*rr)&(rr>.7*gg)&(bb<gg*.65)&vis
  cylinder=(sx>=14)&(sx<38)&(((sy>=2)&(sy<21))|((sy>=29)&(sy<47)))&vis
  red=(rr>gg*1.4)&(rr>bb*1.05)&vis
  lum=rgb.mean(2);target=np.clip((rgb/255)**(1/1.2)*205,0,205)
  # Keep source silhouette and horizontal end-cap boundaries; recolour only cylinder material.
  rel=np.where(sy<24,sy-2,sy-29)
  rim=cylinder&((rel<4)|(rel>=16))&~red
  if style=='cyan_rim':
   target[rim&(lum>85)]=(0,205,205)
   target[cylinder&warm&(rel>=12)&(lum<140)]=(0,0,150)
  else:
   mask=cylinder&warm;target[mask&(lum<100)]=(0,0,155);target[mask&(lum>=100)&(lum<185)]=(0,170,170);target[mask&(lum>=185)]=(205,205,205)
  target[red]=(205,0,0)
  dome=red&(sx>=54);bright=np.clip((lum-70)/120,.15,.65);target[dome,1]=205*bright[dome];target[dome,2]=205*bright[dome]
  # Explicit dark source strokes carry geometry and may not turn into coloured fill.
  dark=vis&(rgb.max(2)<60)
  out=np.zeros(vis.shape,np.uint8)
  for yy in range(32):
   for xx in range(0,48,8):
    m=vis[yy,xx:xx+8];row=target[yy,xx:xx+8];rm=red[yy,xx:xx+8];dk=dark[yy,xx:xx+8]
    if not m.any():continue
    cand=list(itertools.combinations([0,1,2,5,6,7],2))
    if not m.all() or dk.any():cand=[p for p in cand if 0 in p]
    best=None
    for p,q in cand:
     vp=PALETTE[p].astype(float);vq=PALETTE[q].astype(float);v=vq-vp;t=np.clip(((row-vp)*v).sum(1)/(v*v).sum(),0,1)
     # Mostly nearest colour retains narrow mechanical edges; ordered mixing only midtones.
     threshold=.5+(B[yy%4,np.arange(xx,xx+8)%4]-.5)*.45
     val=np.where(t>threshold,q,p).astype(np.uint8);val[~m]=0
     if 0 in [p,q]:val[dk]=0
     if 2 in [p,q]:val[(val==2)&~rm]=q if p==2 else p
     err=((PALETTE[val].astype(float)-row)**2).sum(1);err[~m]=0;err[rm]*=2
     # Source dark strokes and light outlines have stronger visual weight.
     err[dk]*=4;err[m&(rgb[yy,xx:xx+8].min(1)>190)]*=2
     score=err.sum()
     if best is None or score<best[0]:best=(score,val)
    out[yy,xx:xx+8]=best[1]
  assert all(len(set(row[z:z+8]))<=2 for row in out for z in range(0,48,8));assert not np.any(out[~vis]);assert np.all(out[dark]==0)
  np.save(O/f'{style}_{i}.npy',out);im=Image.fromarray(PALETTE[out].astype('uint8'));im.save(O/f'{style}_{i}.png');fs.append(im)
  report.append({'style':style,'pair':[l,r],'dark_source_strokes':int(dark.sum()),'retained_dark_strokes':int(((out==0)&dark).sum())})
 allframes[style]=fs;gif=[fs[j].resize((240,160),Image.Resampling.NEAREST) for j in [0,1,2,1]];gif[0].save(O/f'{style}.gif',save_all=True,append_images=gif[1:],duration=280,loop=0,disposal=2)
sheet=Image.new('RGB',(1080,660),(18,18,18));d=ImageDraw.Draw(sheet)
for i,(l,r) in enumerate(pairs):
 ims=[Image.open(S/f'arcade_pair_{l}_{r}.png'),Image.open(S/f'assembly_48x32_pose{i}.png'),allframes['cyan_rim'][i],allframes['cyan_metal'][i]]
 for j,(label,im) in enumerate(zip(['ARCADE SOURCE','EARLIER PAIRED REFERENCE','A: CYAN CYLINDER RIMS','B: COOL CYLINDER METAL'],ims)):
  d.text((j*270+4,i*220+5),label,fill='white');sheet.paste(im.convert('RGB').resize((im.width*3,im.height*3),Image.Resampling.NEAREST),(j*270+4,i*220+30))
sheet.save(O/'comparison.png')
sha=hashlib.sha256((R/'build/fullgame/force_loading_r62/RType_TS2068_r62.zip').read_bytes()).hexdigest();assert sha=='e3e067696e54563880e59ad2fa6974340a2c56d497f56e4c6b0fdf2515f69574'
(O/'validation.json').write_text(json.dumps({'preview_only':True,'legal_frames':6,'source_stroke_checks':report,'runtime_sha256':sha},indent=2))
(O/'index.html').write_text('''<meta charset=utf-8><title>L6 cylinder shape and highlights</title><style>body{background:#151515;color:white;font:18px system-ui;max-width:1150px;margin:24px auto}img{max-width:100%;image-rendering:pixelated}.row{display:flex;gap:40px}a{color:cyan}</style><h1>Cylinder shape and highlight alternatives</h1><p>A keeps yellow cylinder faces with cyan rim highlights and blue lower shadows. B uses cool cyan/white cylinder metal against the yellow support structure. Both retain dark source strokes explicitly and use less dithering along mechanical edges. Nearest source scaling avoids blurred boundaries. Full paired source, same 43x32 fit in 48x32 storage.</p><div class=row><figure><figcaption>A: cyan rims</figcaption><img src=cyan_rim.gif></figure><figure><figcaption>B: cool metal</figcaption><img src=cyan_metal.gif></figure></div><img src=comparison.png><p>Asset previews only; game unchanged. Actual three source poses, illustrative 280ms timing. Independent side-light timing remains pending. <a href=validation.json>Validation</a>.</p>''',encoding='utf-8')
print(json.dumps(report))
