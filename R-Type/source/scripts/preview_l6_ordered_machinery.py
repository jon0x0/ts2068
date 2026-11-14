from pathlib import Path
import ast,sys,json,hashlib,itertools
import numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'))
from boss_motion_assets_r60 import PALETTE
S=R/'build/graphics/l6_assembly_review';P=R/'build/graphics/l6_surface_refinement';O=R/'build/graphics/l6_ordered_machinery';O.mkdir(parents=True,exist_ok=True)
B=(np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])+.5)/16
BAR=(np.array([[1,1,3,3],[13,13,15,15],[5,5,7,7],[9,9,11,11]])+.5)/16
ns={'np':np,'PALETTE':PALETTE,'itertools':itertools,'LINES':BAR}
tree=ast.parse((R/'scripts/preview_l6_surface_refinement.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='ordered'],type_ignores=[]),'<helpers>','exec'),ns)
def save(name,a):
 assert a.min()>=0 and a.max()<=7
 assert all(len(set(row[x:x+8]))<=2 for row in a for x in range(0,a.shape[1],8))
 np.save(O/(name+'.npy'),a);im=Image.fromarray(PALETTE[a].astype('uint8'));im.save(O/(name+'.png'));return im
def gif(name,fs):
 fs=[f.resize((f.width*5,f.height*5),Image.Resampling.NEAREST) for f in fs];fs[0].save(O/(name+'.gif'),save_all=True,append_images=fs[1:],duration=280,loop=0,disposal=2)
heads=[];stats=[]
for i,c in enumerate([224,226,228,230]):
 src=np.array(Image.open(R/f'build/graphics/l6_corrected_sources/walker_arcade_{c}.png').convert('RGBA')).astype(float);rgb=src[:,:,:3];r,g,b=rgb.transpose(2,0,1);vis=src[:,:,3]>=96;lum=rgb.mean(2);red=(r>g*1.4)&(r>b*1.2)&vis
 base=np.load(P/f'head_deeper_{i}.npy');target=PALETTE[base].astype(float);neutral=vis&((rgb.max(2)-rgb.min(2))<80)&(g>=r)&(b>=r);mid=neutral&(lum>75)&(lum<190)&(np.indices(vis.shape)[0]<25);gray=np.zeros(vis.shape,bool)
 for y in range(32):
  for x in range(0,32,8):
   if mid[y,x:x+8].sum()>=4 and not red[y,x:x+8].any() and np.count_nonzero(vis[y,x:x+8]&~neutral[y,x:x+8])<=1:gray[y,x:x+8]=True
 shade=np.clip(lum*.9+205*.1-8,0,205);target[mid]=np.repeat(shade[:,:,None],3,2)[mid]
 a=ns['ordered'](target,vis,gray=gray,redmask=red,pattern=B);assert not np.any(np.isin(a,[2,3])&~red);heads.append(save(f'head_darker_{i}',a));stats.append({'code':c,'previous_gray_black':int(((base==0)&vis&gray).sum()),'new_gray_black':int(((a==0)&vis&gray).sum())})
gif('head_darker',heads)
pairs=[(320,324),(1476,336),(1488,340)];machines={};lights=[]
for style,pattern in [('bars',BAR),('ordered',B)]:
 frames=[]
 for i,(l,r) in enumerate(pairs):
  src=Image.open(S/f'arcade_pair_{l}_{r}.png').convert('RGBA').resize((43,32),Image.Resampling.LANCZOS);can=Image.new('RGBA',(48,32));can.alpha_composite(src,(2,0));v=np.array(can);rgb=v[:,:,:3].astype(float);vis=v[:,:,3]>=96;rr,gg,bb=rgb.transpose(2,0,1);y,x=np.indices(vis.shape);sx=(x-2)*64/43
  red=vis&(rr>gg*1.4)&(rr>bb*1.05);domes=red&(sx>=54);side=red&~domes
  # Preserve original material and dark structural bars; no region-wide flat recolour.
  target=np.clip((rgb/255)**(1/1.35)*205,0,205);warm=(gg>.7*rr)&(rr>.7*gg)&(bb<gg*.65)&vis
  target[warm,0]=np.clip(target[warm,0]*1.12,0,205);target[warm,1]=np.clip(target[warm,1]*1.12,0,205)
  target[red]=(205,0,0)
  # Source lightness controls white/red coverage, producing pink without magenta fill.
  shine=np.clip((rgb.mean(2)-70)/120,.12,.72);target[domes,1]=205*shine[domes];target[domes,2]=205*shine[domes]
  out=np.zeros((32,48),np.uint8)
  for yy in range(32):
   for xx in range(0,48,8):
    mask=vis[yy,xx:xx+8];row=target[yy,xx:xx+8];rm=red[yy,xx:xx+8];dm=domes[yy,xx:xx+8]
    if not mask.any():continue
    cand=list(itertools.combinations([0,1,2,5,6,7],2))
    if rm.any():cand=[(0,2),(2,7),(0,7),(0,6),(6,7),(5,7)]
    if not mask.all():cand=[p for p in cand if 0 in p]
    best=None
    for p,q in cand:
     vp=PALETTE[p].astype(float);vq=PALETTE[q].astype(float);vec=vq-vp;coverage=np.clip(((row-vp)*vec).sum(1)/(vec*vec).sum(),0,1);threshold=pattern[yy%4,np.arange(xx,xx+8)%4];a=np.where(coverage>threshold,q,p).astype(np.uint8);a[~mask]=0
     if p==2 or q==2:a[(a==2)&~rm]=q if p==2 else p
     error=((PALETTE[a].astype(float)-row)**2).sum(1);error[~mask]=0;error[rm]*=3
     score=error.sum()
     if best is None or score<best[0]:best=(score,a)
    out[yy,xx:xx+8]=best[1]
  frames.append(save(f'machine_{style}_{i}',out))
  if style=='bars':lights.append({'pair':[l,r],'source_side_red_pixels':int(side.sum()),'source_dome_red_pixels':int(domes.sum()),'output_red_pixels':int((out==2).sum())})
 machines[style]=frames;gif('machine_'+style,[frames[j] for j in [0,1,2,1]])
# Source-state comparison keeps actual light changes; no invented flashing timing.
sheet=Image.new('RGB',(1080,600),(18,18,18));d=ImageDraw.Draw(sheet)
for i,(l,r) in enumerate(pairs):
 ims=[Image.open(S/f'arcade_pair_{l}_{r}.png'),Image.open(S/f'assembly_48x32_pose{i}.png'),machines['bars'][i],machines['ordered'][i]]
 for j,(label,im) in enumerate(zip(['ARCADE PAIRED SOURCE','PREVIOUS ACTUAL PAIRED','STRUCTURAL BARS','ORDERED SHADING'],ims)):
  d.text((j*270+5,i*200+5),label,fill='white');im=im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST);sheet.paste(im.convert('RGB'),(j*270+5,i*200+28))
sheet.save(O/'machinery_comparison.png')
sheet=Image.new('RGB',(560,640),(18,18,18));d=ImageDraw.Draw(sheet)
for i in range(4):
 for j,(label,im) in enumerate([('PREVIOUS DEEPER',Image.open(P/f'head_deeper_{i}.png')),('SLIGHTLY DARKER',heads[i])]):
  d.text((j*280+5,i*160+3),label,fill='white');sheet.paste(im.resize((128,128),Image.Resampling.NEAREST),(j*280+5,i*160+23))
sheet.save(O/'head_comparison.png')
sha=hashlib.sha256((R/'build/fullgame/force_loading_r62/RType_TS2068_r62.zip').read_bytes()).hexdigest();assert sha=='e3e067696e54563880e59ad2fa6974340a2c56d497f56e4c6b0fdf2515f69574'
(O/'validation.json').write_text(json.dumps({'preview_only':True,'legal_frames':10,'heads':stats,'lights':lights,'source_pose_cycle':[0,1,2,1],'light_states':'Source poses only, independent blink cadence not established','normal_black_only':True,'runtime_sha256':sha},indent=2))
(O/'index.html').write_text('''<meta charset="utf-8"><title>L6 structural shading refinement</title><style>body{background:#151515;color:white;font:18px system-ui;max-width:1150px;margin:24px auto}img{max-width:100%;image-rendering:pixelated}.row{display:flex;gap:40px}a{color:cyan}</style><h1>L6: darker gray and machinery detail</h1><h2>#9-13: slightly darker gray, 32x32</h2><img src="head_darker.gif"><details><summary>Compare with previous deeper gray</summary><img src="head_comparison.png"></details><h2>#14 family: structural bars and ordered shading</h2><p>Reconverted from the actual paired arcade poses, preserving the original dark support bars and material shading instead of flat region recolouring. Stronger red domes use ordered white highlights for pink shading. Small side-light accents follow the source poses; independent blink timing is not yet established.</p><div class="row"><figure><figcaption>Structural bars</figcaption><img src="machine_bars.gif"></figure><figure><figcaption>Ordered shading</figcaption><img src="machine_ordered.gif"></figure></div><img src="machinery_comparison.png"><p>Asset previews only. Three actual paired source poses; illustrative animation timing. Normal black throughout. Playable build unchanged. <a href="validation.json">Validation</a>.</p>''',encoding='utf-8')
print(json.dumps({'heads':stats,'lights':lights}))
