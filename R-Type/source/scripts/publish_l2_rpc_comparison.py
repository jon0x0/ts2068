from pathlib import Path
import json,numpy as np,shutil
from PIL import Image
R=Path.cwd();O=R/'build/graphics/l2_rpc_settings';m=json.loads((O/'manifest.json').read_text());normal=np.array([[0,0,0],[1,0,206],[207,1,0],[207,1,206],[0,207,21],[1,207,207],[207,207,21],[207,207,207]],np.uint8);bright=np.array([[96,96,96],[2,0,253],[255,2,1],[255,2,253],[0,255,28],[2,255,255],[255,255,29],[255,255,255]],np.uint8);palette=np.stack([normal,bright]);rows=[]
for p in m['profiles']:
 id,w,h=p['id'],p['w'],p['h'];bits=np.frombuffer((O/f'{id}.bits').read_bytes(),np.uint8).reshape(h,w//8);attrs=np.frombuffer((O/f'{id}.attrs').read_bytes(),np.uint8).reshape(h,w//8);pix=np.unpackbits(bits,axis=1);bank=np.repeat((attrs>>6)&1,8,1);idx=np.where(pix,np.repeat(attrs&7,8,1),np.repeat((attrs>>3)&7,8,1));rgb=palette[bank,idx];expected=np.frombuffer((O/f'{id}.rgb').read_bytes(),np.uint8).reshape(h,w,3);assert np.array_equal(rgb,expected)
 mask=np.frombuffer((O/f'{p["size"]}.mask').read_bytes(),np.uint8).reshape(h,w).astype(bool);assert not rgb[~mask].any()and not pix[~mask].any();assert not((attrs&64).astype(bool)&(((attrs&7)==0)|(((attrs>>3)&7)==0))).any();np.save(O/f'{id}.indices.npy',(idx+bank*8).astype('uint8'))
 base=bytearray((R/'build/fullgame/startup_r66/ordinary_L2_col66.home.bin').read_bytes());x0=96 if w==160 else 64;y0=160-h
 def offset(y,x):return ((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|x
 for y in range(min(64,y0),160):
  for x in range(7,32):base[0x4000+offset(y,x)]=0;base[0x6000+offset(y,x)]=0
 for y in range(h):
  for x in range(w//8):base[0x4000+offset(y+y0,x+x0//8)]=bits[y,x];base[0x6000+offset(y+y0,x+x0//8)]=attrs[y,x]
 frame=np.zeros((192,256,3),np.uint8)
 for y in range(192):
  for x in range(32):
   k=offset(y,x);a=base[0x6000+k];v=base[0x4000+k]
   for j in range(8):frame[y,x*8+j]=palette[(a>>6)&1,(a&7)if v&(128>>j)else(a>>3)&7]
 Image.fromarray(frame).resize((768,576),Image.Resampling.NEAREST).save(O/f'{id}_scene.png');(O/f'{id}_scene.ecm').write_bytes(base[0x4000:0x5800]+base[0x6000:0x7800])
 rows.append(f'<section><h2>{id}: {p["name"]}</h2><p>{w}x{h}, {p["strategy"]}; Sierra Lite serpentine. Bitmap+attributes {len(bits.tobytes())+len(attrs.tobytes())} bytes, plus preserve mask.</p><img class="body" src="{id}.png"><details><summary>Offline scene composition</summary><img src="{id}_scene.png"></details></section>')
shutil.copy2(R/'build/graphics/l2_organic_sierra/A.png',O/'previous_A.png')
page='''<!doctype html><meta charset="utf-8"><title>L2 boss - supplied RPC settings</title><style>body{background:#171717;color:#eee;font:17px system-ui;max-width:1100px;margin:30px auto}img{image-rendering:pixelated;max-width:100%}.body{width:640px}section{border-top:1px solid #555;padding:12px 0}a{color:cyan}</style><h1>L2 boss using your RPC settings</h1><p><b>Brightness44, contrast54, saturation71, gamma0.98.</b> The local RPC source maps these to -0.12, 1.08, 1.42 and0.98, applied in linear light. Uses actual extracted RPC adjustment, palette-search and Sierra Lite routines; no flesh/rib palette restrictions or gamma lift. Black stays normal black. BRIGHT is retained only in pairs containing two nonblack colours.</p><p>These are not claimed pixel-identical to your screenshot: exact source/crop/output dimensions and colour strategy were not supplied. A-C use RPC's default segment-coverage search; D shows per-block search. Perceptual/GS refinement not applied. Alpha masking stops background diffusion. Native-sized160x88 and larger192x104 versions are shown.</p><p><strong>Artwork previews, not a playable build.</strong> Bright-interior pairs need support through the game's cached renderer; geometry/collision/tile/animation integration remains separate. Scene images clear the old boss region and show an offline composition, not evidence of gameplay or speed.</p><h2>Your reference and settings</h2><img src="rpc_reference.png"><img src="rpc_settings.png"><h2>Previous A for comparison</h2><img class="body" src="previous_A.png">'''+''.join(rows)
(O/'index.html').write_text(page,encoding='utf-8');print('4 exported assets independently reconstructed; black pixels/masks verified; scene exports built')
