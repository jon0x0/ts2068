from pathlib import Path

import sys,json

import numpy as np

from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))

from build_graphics import decode_roms,palette_ram,fit_pairs,quantize

from decode_arcade_objects import render

from boss_motion_assets_r60 import decode,PALETTE

from preview_enemy_sierra import convert

OUT=ROOT/'build/graphics/l6_corrected_sources';OUT.mkdir(parents=True,exist_ok=True)

SP,_=decode_roms();records=[]

def preview(source,size,gamma=1.35,blue_metal=False):
 if not blue_metal:
  im,bits,attrs=convert(source,size,np.ones((size[1],size[0]),bool),gamma,1.4,hsv=True);attrs&=63
  return np.where(bits,np.repeat(attrs&7,8,axis=1),np.repeat((attrs>>3)&7,8,axis=1))
 rgba=np.array(source.convert('RGBA').resize(size,Image.Resampling.LANCZOS));alpha=rgba[:,:,3]>=96;rgb=rgba[:,:,:3].astype(float)
 if blue_metal:
  r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2];body=alpha&(np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b])<80)&(g>=r)&(b>=r);lum=rgb.mean(2)
  for test,color in [(lum<100,(0,0,205)),((lum>=100)&(lum<175),(0,205,205)),(lum>=175,(205,205,205))]:rgb[body&test]=color
 else:rgb=np.round(205*np.clip(rgb/255,0,1)**(1/gamma))
 rgb[~alpha]=0;h,w=alpha.shape;pairs=np.zeros((h,w//8,2),dtype=np.int16);pairs[:,:,1]=1;partial=np.zeros((h,w//8),bool)
 # Opaque material cells use two nonblack colours; edge cells preserve the
 # exact silhouette, rather than inventing black dithering holes in surfaces.
 for y in range(h):
  for cx in range(w//8):
   mask=alpha[y,cx*8:cx*8+8];row=rgb[y,cx*8:cx*8+8]
   if not mask.any():continue
   if not mask.all():
    partial[y,cx]=True;cost=((row[mask,None,:]-PALETTE[None,1:,:])**2).sum(2).sum(0);pairs[y,cx]=[0,1+int(cost.argmin())]
   else:
    best=None
    for p in range(1,8):
     for q in range(p+1,8):
      err=np.minimum(((row-PALETTE[p])**2).sum(1),((row-PALETTE[q])**2).sum(1)).sum()
      if best is None or err<best[0]:best=(err,p,q)
    pairs[y,cx]=best[1:]
 bits,attrs,_=quantize(Image.fromarray(np.clip(rgb,0,255).astype('uint8')),pairs=pairs)
 for y,cx in zip(*np.where(partial)):bits[y,cx*8:cx*8+8]=alpha[y,cx*8:cx*8+8]
 bits[~alpha]=0;pixels=np.where(bits,np.repeat(attrs&7,8,axis=1),np.repeat((attrs>>3)&7,8,axis=1))
 assert np.array_equal(pixels!=0,alpha),'Opaque material lost to black dithering'
 return pixels

def save_pixels(stem,a):

 assert a.shape[1]%8==0

 assert all(len(set(row[x:x+8]))<=2 for row in a for x in range(0,a.shape[1],8))

 im=Image.fromarray(PALETTE[a].astype('uint8'));im.save(OUT/(stem+'.png'));np.save(OUT/(stem+'.npy'),a);return im



def enlarged(im,n=4):return im.resize((im.width*n,im.height*n),Image.Resampling.NEAREST)

def gif(name,frames):

 fs=[enlarged(im)for im in frames];fs[0].save(OUT/name,save_all=True,append_images=fs[1:],duration=280,loop=0,disposal=2)

# The spherical, two-legged ROM cels, not explosion family2758.

pal=palette_ram(ROOT/'build/fullgame/arcade_reference/frame048000_palette_sprite.bin')[80:96]

walk={24:[],32:[]};arcade=[];current=[]

for i,code in enumerate([224,226,228,230]):

 a=np.block([[SP[code],SP[code+8]],[SP[code+1],SP[code+9]]]);rgba=np.concatenate([pal[a],np.where(a[:,:,None],255,0)],2).astype('uint8');source=Image.fromarray(rgba);source.save(OUT/f'walker_arcade_{code}.png');arcade.append(source)

 current.append(Image.fromarray(PALETTE[decode(6,5+i)[0]].astype('uint8')))

 for size in [24,32]:walk[size].append(save_pixels(f'walker_{size}_{5+i}',preview(source,(size,size),blue_metal=True)))

 records.append({'native_id':5+i,'arcade_code':code,'source_palette_frame':48000,'palette':5,'geometry':'Shared32x32sourcecanvas, aspect-preserving24x24 or32x32, baseline unchanged','mapping':'Corrected walking-cel proposal; source and native cycles shown for review'})

for name,frames in [('walker_arcade.gif',arcade),('walker_current.gif',current),('walker_24.gif',walk[24]),('walker_32.gif',walk[32])]:gif(name,frames)

sheet=Image.new('RGB',(800,4*190),(18,18,18));d=ImageDraw.Draw(sheet)

for i in range(4):

 for j,(title,im)in enumerate(zip(['ARCADE WALK CEL','CURRENT24x24','NEW24x24','NEW32x32 (1.33x)'],[arcade[i],current[i],walk[24][i],walk[32][i]])):

  x=j*200;y=i*190;d.text((x+3,y+3),f'#{5+i} {title}',fill='white');im=enlarged(im);sheet.paste(im.convert('RGB'),(x+3,y+30))

sheet.save(OUT/'walker_comparison.png')

# Reassemble both genuine32x64 objects; alpha occupies only48rows.

rows=render(48300,SP)[1];pair=Image.new('RGBA',(64,64))

for code,x in [(320,0),(324,32)]:pair.alpha_composite(next(im for meta,im in rows if meta['code']==code),(x,0))

pair.save(OUT/'turret_arcade_full.png');raw=np.array(pair)[:48].copy();original=raw[:,:,:3].copy()

glass=(original[:,:,2]>=original[:,:,0])&(original[:,:,1]>original[:,:,0])&(original[:,:,0]>=70)&(raw[:,:,3]>0)

# Restrict glass to the two source windows; frames/caps remain source-derived.

roi=np.zeros(glass.shape,bool);roi[:22,34:56]=True;roi[30:,34:56]=True;glass&=roi

lights={16:[],24:[]};counts=[]

for state,ident in enumerate([14,15,16,17]):

 src=raw.copy();on_top=bool(state&1);on_bottom=bool(state&2)

 for width in [16,24]:

  # Geometry crop, no alpha-bbox fit:48source rows always fill32 output rows.

  left=40 if width==16 else 28;crop=Image.fromarray(src).crop((left,0,64,48));a=preview(crop,(width,32))
  # Authored rounded glazing fits its own8-pixel column. Edge scanlines
  # use black plus one colour; opaque scanlines can use two glass shades.
  for top,on in [(3,on_top),(22,on_bottom)]:
   x=width-8
   masks=[0x3c,0x7e,0xff,0xff,0xff,0xff,0x7e,0x3c]
   for yy,mask in enumerate(masks):
    for xx in range(8):
     if not mask&(128>>xx):a[top+yy,x+xx]=0;continue
     if yy<2:c=7 if on else 5
     elif yy<4:c=(7 if xx<3 else 5)if on else(5 if xx<3 else 1)
     elif yy<6:c=(7 if xx==2 and yy==4 else 5)if on else(5 if xx==2 and yy==4 else 1)
     else:c=5 if on else 1
     a[top+yy,x+xx]=c
  im=save_pixels(f'turret_{width}_{ident}',a);lights[width].append(im);counts.append({'id':ident,'size':[width,32],'colors':len(set(map(int,a.flat)))-int(0 in a),'top_on':on_top,'bottom_on':on_bottom,'crop':[left,0,64,48]})

# Light toggles must not repaint unrelated housing pixels or the other dome.
for width in [16,24]:
 arrays=[np.load(OUT/f'turret_{width}_{i}.npy')for i in range(14,18)];top=np.zeros((32,width),bool);bottom=top.copy();top[3:11,width-8:]=True;bottom[22:30,width-8:]=True
 assert np.any(arrays[1]!=arrays[0]) and np.any(arrays[2]!=arrays[0])
 assert not np.any((arrays[1]!=arrays[0])&~top)
 assert not np.any((arrays[2]!=arrays[0])&~bottom)
 both=arrays[0].copy();both[top]=arrays[1][top];both[bottom]=arrays[2][bottom];assert np.array_equal(arrays[3],both)
 assert len({a.tobytes()for a in arrays})==4
for width in [16,24]:gif(f'turret_{width}.gif',[lights[width][i]for i in [0,1,3,2]])

old=[Image.fromarray(PALETTE[decode(6,i)[0]].astype('uint8'))for i in range(14,18)];gif('turret_current.gif',[old[i]for i in [0,1,3,2]])

sheet=Image.new('RGB',(800,4*190),(18,18,18));d=ImageDraw.Draw(sheet)

for i in range(4):

 ims=[pair.crop((28,0,64,48)),old[i],lights[16][i],lights[24][i]]

 for j,(title,im)in enumerate(zip(['ARCADE GEOMETRY','CURRENT16x32','NEW16x32','NEW24x32 (1.5x width)'],ims)):

  x=j*200;y=i*190;d.text((x+3,y+3),f'#{14+i} {title}',fill='white');d.text((x+3,y+17),['BOTH OFF','UPPER ON','LOWER ON','BOTH ON'][i],fill='cyan');im=enlarged(im,3 if j==0 else 4);sheet.paste(im.convert('RGB'),(x+3,y+36))

sheet.save(OUT/'turret_comparison.png')

# Keep the unresolved head family visible without inventing a new arcade match.

head=[Image.fromarray(PALETTE[decode(6,i)[0]].astype('uint8'))for i in range(9,14)];gif('unmatched_head_current.gif',head)

(OUT/'validation.json').write_text(json.dumps({'asset_preview_only':True,'legal_8x1_pairs':True,'walker_opaque_material_silhouette_preserved':True,'turret_lights_independent_housing_unchanged':True,'turret_glazing':'Authored rounded dome lights in isolated8-pixel columns; housing from arcade objects320/324','walkers':records,'turrets':counts,'turret_source_bbox':pair.getbbox(),'unmatched':[9,10,11,12,13],'animation_timing':'Illustrative280ms/pose; not native timing or performance','runtime_images_unchanged':True},indent=2))

(OUT/'index.html').write_text('''<meta charset=utf-8><title>Corrected L6 walker and turret proposals</title><style>body{background:#151515;color:white;font:18px system-ui;max-width:1200px;margin:24px auto;padding:16px}img{image-rendering:pixelated;max-width:100%}.row{display:flex;gap:32px;align-items:end;flex-wrap:wrap}figure{margin:8px}figcaption{margin-bottom:12px}a{color:cyan}</style><h1>Corrected level6 comparisons</h1><p>The previous #5 arcade explosion was an incorrect match and is withdrawn. No game files have been changed by these previews.</p><h2>#5-8: walker, four genuine walking cels</h2><p>Arcade ROM224/226/228/230, one shared source canvas and baseline. Native24x24 and a modest32x32 alternative (1.33x); scale before Sierra Lite. Blue/cyan shadows keep opaque head surfaces solid; transparent edges preserve the source silhouette. The source sequence is shown explicitly for identity review.</p><div class=row><figure><figcaption>Arcade walking cels</figcaption><img src=walker_arcade.gif></figure><figure><figcaption>Current24x24</figcaption><img src=walker_current.gif></figure><figure><figcaption>New24x24</figcaption><img src=walker_24.gif></figure><figure><figcaption>New32x32</figcaption><img src=walker_32.gif></figure></div><img src=walker_comparison.png><h2>#9-13: previous match withdrawn</h2><p>The earlier2850-family comparison is not a verified match for this silhouette. Current native sequence below; no replacement is selected yet.</p><img src=unmatched_head_current.gif><h2>#14-17: full-height turret and independent dome lights</h2><p>The old source crop was32x48 and was fitted to16x24 inside the16x32 box, shrinking it by25% vertically. These proposals fill32rows. The wider24x32 version exposes more of the actual machinery while retaining aspect and height. Arcade-derived housing now has authored rounded glass domes in separate8-pixel columns, with blue/cyan shading and white lit highlights. Upper and lower lights have four distinct states. No changes to collision geometry are implied.</p><div class=row><figure><figcaption>Current16x32</figcaption><img src=turret_current.gif></figure><figure><figcaption>New16x32</figcaption><img src=turret_16.gif></figure><figure><figcaption>New24x32</figcaption><img src=turret_24.gif></figure></div><img src=turret_comparison.png><p>Asset proposals only. GIF timing and light-state ordering are illustrative, not measured gameplay. All output cells obey normal-colour8x1 pairs. See<a href=validation.json>validation/provenance</a>.</p>''')

print(json.dumps({'turret_colors':counts,'walker_codes':[224,226,228,230]}))

