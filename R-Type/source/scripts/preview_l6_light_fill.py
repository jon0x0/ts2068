from pathlib import Path
import sys,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'))
from boss_motion_assets_r60 import PALETTE
S=R/'build/graphics/l6_flash_sources';P=R/'build/graphics/l6_cylinder_flash';O=R/'build/graphics/l6_light_fill';O.mkdir(parents=True,exist_ok=True)
m=json.loads((S/'manifest.json').read_text());seq=m['sequence'];frames={};checks=[]
for style in ['red','magenta']:
 fs=[]
 for i,u in enumerate(m['unique']):
  base=np.load(P/f'cyan_rim_{i}.npy');im=Image.open(S/f'arcade_pair_{i}_0.png').resize((43,32),Image.Resampling.NEAREST);can=Image.new('RGBA',(48,32));can.alpha_composite(im,(2,0));v=np.array(can).astype(float);rr,gg,bb=v[:,:,:3].transpose(2,0,1);vis=v[:,:,3]>127;y,x=np.indices(vis.shape);sx=(x-2)*64/43
  dome=vis&(sx>=54)&(rr>gg*1.4)&(rr>bb*1.05)
  # Earlier than original bright phase: source red132 starts ON, dim107 stays OFF.
  level=float(np.median(rr[dome])) if dome.any() else 0;lit=level>=145
  out=base.copy();hi=np.zeros(dome.shape,bool)
  if lit:
   ys,xs=np.where(dome);top=int(ys.min());bottom=int(ys.max())
   # Place a tiny persistent white glint on its own scanline to avoid a third colour.
   hy=top;hx=int(np.where(dome[hy])[0].max());hi[hy,hx]=True
   for yy in range(32):
    for xx in range(0,48,8):
     dm=dome[yy,xx:xx+8];hm=hi[yy,xx:xx+8]
     if not dm.any():continue
     cell=out[yy,xx:xx+8].copy();vm=vis[yy,xx:xx+8]
     if hm.any():
      cell[:]=0;cell[hm]=7
     else:
      ink=3 if style=='magenta' and yy>=top+int((bottom-top+1)*.70) else 2
      # Full red fill; shared-cell metal follows red/white when no black is required.
      if vm.all() and not np.any(cell==0):cell[:]=7;cell[dm]=ink
      else:cell[:]=0;cell[dm]=ink
     out[yy,xx:xx+8]=cell
  assert all(len(set(row[z:z+8]))<=2 for row in out for z in range(0,48,8));assert not np.any(out[~vis])
  # Cells untouched by the dome remain byte-identical, preserving side-lamp flashing.
  touched=np.zeros(dome.shape,bool)
  for yy in range(32):
   for xx in range(0,48,8):
    if dome[yy,xx:xx+8].any() and lit:touched[yy,xx:xx+8]=True
  assert np.array_equal(out[~touched],base[~touched])
  if not lit:assert np.array_equal(out,base)
  np.save(O/f'{style}_{i}.npy',out);pic=Image.fromarray(PALETTE[out].astype('uint8'));pic.save(O/f'{style}_{i}.png');fs.append(pic);checks.append({'style':style,'state':i,'source_median_red':level,'on':lit,'dome_pixels':int(dome.sum()),'red_fill':int(((out==2)&dome).sum()),'magenta_fill':int(((out==3)&dome).sum()),'highlight':int(hi.sum())})
 assert any(c['on'] for c in checks if c['style']==style) and any(not c['on'] for c in checks if c['style']==style)
 frames[style]=fs;gif=[fs[i].resize((288,192),Image.Resampling.NEAREST) for i in seq];dur=[(round((i+1)*4/55.017606*100)-round(i*4/55.017606*100))*10 for i in range(len(seq))];gif[0].save(O/f'{style}.gif',save_all=True,append_images=gif[1:],duration=dur,loop=0,disposal=2)
sheet=Image.new('RGB',(800,600),(18,18,18));d=ImageDraw.Draw(sheet)
for row,i in enumerate([0,4,8]):
 for col,(label,im) in enumerate([('PREVIOUS CYAN RIMS',Image.open(P/f'cyan_rim_{i}.png')),('QUICK RED FILL',frames['red'][i]),('RED + LOWER MAGENTA',frames['magenta'][i])]):
  d.text((col*265+4,row*200+5),label,fill='white');sheet.paste(im.resize((240,160),Image.Resampling.NEAREST),(col*265+4,row*200+28))
sheet.save(O/'comparison.png')
sha=hashlib.sha256((R/'build/fullgame/force_loading_r62/RType_TS2068_r62.zip').read_bytes()).hexdigest();assert sha=='e3e067696e54563880e59ad2fa6974340a2c56d497f56e4c6b0fdf2515f69574'
(O/'validation.json').write_text(json.dumps({'asset_preview_only':True,'accepted_style':'cyan rims','head':'darker32x32 accepted','threshold':145,'off_state_unchanged':True,'outside_dome_cells_unchanged':True,'legal_frames':30,'checks':checks,'runtime_sha256':sha},indent=2))
(O/'index.html').write_text('''<meta charset=utf-8><title>Quick red light and cyan rims</title><style>body{background:#151515;color:white;font:18px system-ui;max-width:1100px;margin:24px auto}img{max-width:100%;image-rendering:pixelated}.row{display:flex;gap:35px}a{color:cyan}</style><h1>Cyan rims: quicker, fuller red light</h1><p>Cyan rims retained. The light switches fully on earlier in the palette ramp, keeping the existing off image. Solid red fill replaces the sparse lit texture; a small upper-right white glint occupies a separate scanline to stay legal in ECM. Compare red alone with lower magenta shading. Side-light flashing and untouched machinery cells remain unchanged.</p><div class=row><figure><figcaption>Quick red fill</figcaption><img src=red.gif></figure><figure><figcaption>Red with lower magenta</figcaption><img src=magenta.gif></figure></div><img src=comparison.png><p>Asset preview only; game unchanged. <a href=validation.json>Validation</a>.</p>''',encoding='utf-8')
print(json.dumps(checks[:15]))
