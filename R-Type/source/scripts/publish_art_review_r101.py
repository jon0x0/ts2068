from pathlib import Path
import json,numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();O=R/'build/graphics/l2_art_review_r101';j=json.loads((O/'inputs.json').read_text());checks=[]
for p in j['profiles']:
 w,h=p['w'],p['h'];rgb=np.frombuffer((O/f'{p["id"]}.rgb').read_bytes(),np.uint8).reshape(h,w,3);at=np.frombuffer((O/f'{p["id"]}.attrs').read_bytes(),np.uint8);mask=np.frombuffer((O/f'{p["id"]}.mask').read_bytes(),np.uint8).reshape(h,w)
 assert not(at&128).any();assert not np.any(((at&64)>0)&(((at&7)==0)|(((at>>3)&7)==0)));assert not rgb[mask==0].any()
 for y in range(h):
  for x in range(0,w,8):assert len(np.unique(rgb[y,x:x+8],axis=0))<=2
 Image.fromarray(rgb).save(O/f'{p["id"]}.png');checks.append(p['id'])
for variant in ['A','B']:
 ims=[Image.open(O/f'walker_{variant}_{k}.png').resize((256,192),Image.Resampling.NEAREST)for k in range(4)];ims[0].save(O/f'walker_{variant}.gif',save_all=True,append_images=ims[1:],duration=180,loop=0,disposal=2)
ims=[Image.open(O/f'L1_small_current_{k}.png').resize((256,192),Image.Resampling.NEAREST)for k in range(4)];ims[0].save(O/'walker_current.gif',save_all=True,append_images=ims[1:],duration=180,loop=0,disposal=2)
for name in ['current','new']:
 ims=[Image.open(O/(f'L3_exhaust_current_{k}.png'if name=='current'else f'exhaust_{k}.png')).resize((384,128),Image.Resampling.NEAREST)for k in range(4)];ims[0].save(O/f'exhaust_{name}.gif',save_all=True,append_images=ims[1:],duration=110,loop=0,disposal=2)
scene=np.array(Image.open(O/'current_scene.png').resize((256,192),Image.Resampling.NEAREST));terrain=[]
for name in ['olive','organic']:
 rgb=np.array(Image.open(O/f'terrain_{name}.png'));mask=np.frombuffer((O/f'terrain_{name}.mask').read_bytes(),np.uint8).reshape(160,256)>0;im=scene.copy();im[:160][mask]=rgb[mask];Image.fromarray(im).resize((768,576),Image.Resampling.NEAREST).save(O/f'scene_{name}.png')
 frames=[]
 for phase in range(8):
  moved=np.roll(rgb,-phase,axis=1)
  for y in range(160):
   for x in range(0,256,8):assert len(np.unique(moved[y,x:x+8],axis=0))<=2,('scroll clash',name,phase,y,x)
  canvas=im.copy();canvas[:160]=np.roll(im[:160],-phase,axis=1);frames.append(Image.fromarray(canvas).resize((768,576),Image.Resampling.NEAREST))
 frames[0].save(O/f'scroll_{name}.gif',save_all=True,append_images=frames[1:],duration=110,loop=0,disposal=2);terrain.append(dict(name=name,scroll_phases=8,legal_8x1=True))
page=['<!doctype html><meta charset="utf-8"><title>L1 walker and L2 arcade shading review</title><style>body{background:#10151c;color:#eee;font:17px system-ui;margin:24px auto;max-width:1250px;padding:16px}img{image-rendering:pixelated;max-width:100%}.row{display:flex;gap:18px;flex-wrap:wrap}figure{margin:8px}h2{border-top:1px solid #567;padding-top:22px}figcaption{max-width:350px}</style><h1>Artwork review against actual r100</h1><p>Offline proposals only: the stable r100 release is unchanged. All sprite variants use actual Retro Pixel Converter CPU adjustments and serpentine Sierra Lite, shared across every frame in a family. Normal black, no flash or bright-black pairs. Preview animation timings are illustrative, not game performance.</p><h2>L1 small walker:32x24 / four poses</h2><p>The large walker stays unchanged. A refines the currently installed gun-walker source. B returns to the earlier arcade-derived blue-armour walker. B source uses arcade1570/1572/1574 with an authored intermediate pose; A is the earlier redrawn gun-walker, not original arcade art.</p><div class=row>']
for name,label in [('current','Current r100'),('A','A - current shape, clearer metal/blue shading'),('B','B - earlier arcade blue-armour shape')]:page.append(f'<figure><img src="walker_{name}.gif"><figcaption>{label}</figcaption></figure>')
page+=['</div><h2>L2 terrain: existing r100 geometry, arcade-informed material shading</h2><p>This retains the existing bitmap silhouette/holes and full256x160playfield dimensions. It is a shading study, not a replacement terrain strip or an installed game. Olive/ivory and organic red/cream material directions reference the arcade surfaces shown below. Arcade geometry has not been substituted. Both use a common horizontal pair until a run of at least8blackpixels allows a transition. Eight horizontal subpixel scroll phases pass the legal8x1colour check on the terrain layer. This conservative policy still produces some horizontal banding: consider that tradeoff before installation.</p><img width="768" src="arcade_reference.png"><div class=row>']
for key,label in [('current_scene','Current r100'),('scene_olive','A - olive / ivory'),('scene_organic','B - organic red / cream')]:page.append(f'<figure><img width="600" src="{key}.png"><figcaption>{label}</figcaption></figure>')
page+=['</div><details><summary>Illustrative scrolling checks</summary><img src="scroll_olive.gif"><img src="scroll_organic.gif"></details><h2>L2 head sprites: corrected isolated arcade source</h2><p>Same40x40storage. These remain review proposals: earlier instructions held3-6pending evaluation. The known withdrawn neck-containing crops are not used.</p>']
for i in [3,4]:
 page.append(f'<h3>Descriptor{i}</h3><div class=row>')
 for key,label in [(f'L2_{i}_current','Current r100'),(f'L2_{i}_rpc','RPC44/54/71/gamma0.98'),(f'L2_{i}_detail','RPC49/60/85/gamma1.2')]:page.append(f'<figure><img width="240" src="{key}.png"><figcaption>{label}</figcaption></figure>')
 page.append('</div>')
page+=['<h2>Large L3 rocket exhaust:48x16 / four poses</h2><p>Current installed asset versus an authored study of the supplied rocket photograph: white/blue near the nozzle, warmer red/yellow at the far tail. Nozzle remains at the right; plume points left. This is a reference-inspired ECM drawing, not extracted arcade graphics.</p><div class=row><figure><img src="exhaust_current.gif"><figcaption>Current r100</figcaption></figure><figure><img src="exhaust_new.gif"><figcaption>Reference-inspired proposal</figcaption></figure></div><p>The small player-ship flame is a separate path: r100 only recolours its existing two-pixel flare. A larger plume will require a separate geometry review.</p>']
(O/'index.html').write_text('\n'.join(page),encoding='utf-8');(O/'validation.json').write_text(json.dumps(dict(passed=True,converted_profiles=len(checks),terrain=terrain,status='offline proposals, not installed',stable_release_unchanged=True),indent=2));print('Validated',len(checks),'profiles; terrain2x8scrollphases pass.')
