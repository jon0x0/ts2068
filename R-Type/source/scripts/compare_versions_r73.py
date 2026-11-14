from pathlib import Path
import json,numpy as np,html
from PIL import Image,ImageDraw
R=Path.cwd();O=R/'build/graphics/version_comparison_r73';versions=['r67','r72','r73'];folders=['l2_rpc_r67','reviewed_r72','terrain_restore_r73'];pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205),(0,0,0),(0,0,255),(255,0,0),(255,0,255),(0,255,0),(0,255,255),(255,255,0),(255,255,255)],np.uint8)
layouts=json.loads((R/'build/fullgame/foundation/manifest.json').read_text())['levels']
def native(b,n,i):
 m=bytes(0xc000)+b[0xa000:0xe000];at=layouts[n-1]['enemy_descriptors_start']+(i-1)*4;w,h=m[at:at+2];p=int.from_bytes(m[at+2:at+4],'little');out=np.zeros((h*8,w*8),np.uint8)
 for cy in range(h):
  for cx in range(w):
   tag=m[p];p+=1
   if tag==54:continue
   for y in range(8):
    a=b[0x2000+(tag&127)*8+y];bank=8 if a&64 else 0
    for x in range(8):out[cy*8+y,cx*8+x]=((a&7)if m[p+y]&(128>>x)else(a>>3)&7)+bank
   p+=8
 return Image.fromarray(pal[out])
parts=['''<!doctype html><meta charset="utf-8"><title>R-Type r67 / r72 / r73 comparison</title><style>body{background:#171b22;color:#eee;font:16px system-ui;margin:24px}a{color:#8ddfff}.row{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}img{max-width:100%;image-rendering:pixelated;background:black}article{padding:18px 0;border-bottom:1px solid #576070}h3{margin:6px 0}button,select{font:inherit}p{max-width:1000px}</style><h1>r67 / r72 / r73</h1><p>r67: previous game. r72: reviewed artwork integration. r73: restored previous terrain, retained enemy upgrades. These are actual decoded assets and scripted ECM gameplay captures, not arcade-source proposals. Gameplay scenes use the same double-B preview route and post-jump update 110; actor timing can differ with artwork cost. They are not hardware captures or a scrolling-clash benchmark.</p><p>L1: r72 reused shared palette rows; r73 restores every palette row and fits four upgraded enemy streams to existing pairs. L2: r73 restores previous body/terrain, including the boss body. L3: r73 restores all previous strips and palettes. L4/L5 terrain did not change. L4/L6/L8 reviewed enemies remain in r73; L5/L7 remain r67-identical.</p>''']
summary=[]
for n in range(1,9):
 bs=[(R/'build/fullgame'/f/f'level{n:02d}_region.bin').read_bytes()for f in folders]
 summary.append({'level':n,'r67_to_r72_changed_bytes':sum(a!=b for a,b in zip(bs[0],bs[1])),'r67_to_r73_changed_bytes':sum(a!=b for a,b in zip(bs[0],bs[2])),'r72_to_r73_changed_bytes':sum(a!=b for a,b in zip(bs[1],bs[2]))})
 if n<=5:
  parts.append(f'<article><h2>Level {n}: gameplay and terrain</h2><div class="row">')
  for v in versions:
   parts.append(f'<div><h3>{v}</h3><img src="{v}/scene_L{n}_110.png"></div>')
  parts.append('</div></article>')
for n,i in [(1,8),(1,9),(3,42),(3,47),(3,61),(3,72)]:
 parts.append(f'<article><h2>L{n} native artwork #{i}</h2><div class="row">')
 for v,f in zip(versions,folders):
  im=native((R/'build/fullgame'/f/f'level{n:02d}_region.bin').read_bytes(),n,i);p=O/v/f'asset_L{n}_{i}.png';im.save(p);parts.append(f'<div><h3>{v}: {im.width} x {im.height}</h3><img style="width:{im.width*3}px" src="{v}/{p.name}"></div>')
 parts.append('</div></article>')
parts.append('<p>Changed-byte counts include compressed storage and relocation, so they are not unique graphics sizes or quality measurements.</p><pre>'+html.escape(json.dumps(summary,indent=2))+'</pre>')
(O/'index.html').write_text(''.join(parts),encoding='utf-8');(O/'binary_comparison.json').write_text(json.dumps(summary,indent=2))
print('Comparison page and exact native assets generated')
