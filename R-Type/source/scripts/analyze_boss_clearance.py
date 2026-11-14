from pathlib import Path
from PIL import Image,ImageDraw
import json,collections
ROOT=Path('.');out=ROOT/'build/fullgame/fast_boss_r51';ph=(ROOT/'build/diagnostics/pixel_movement_trial/ship_phases.bin').read_bytes();ship=[]
for y in range(8):
 row=0
 for x in range(32):
  if ph[768+64+y*4+x//8]&(128>>(x&7)):row|=1<<x
 ship.append(row)
pal=[((255 if i&8 else 205)if i&2 else 0,(255 if i&8 else 205)if i&4 else 0,(255 if i&8 else 205)if i&1 else 0)for i in range(16)];report=[];sheet=Image.new('RGB',(1536,610));draw=ImageDraw.Draw(sheet)
for n,variant in enumerate(['responsive_game_r50','compact_boss_r51']):
 b=(out/(variant+'_composition.bin')).read_bytes();im=Image.new('RGB',(256,192));px=im.load();occupied=[]
 for y in range(192):
  at=((y&192)<<5)|((y&7)<<8)|((y&56)<<2);row=0
  for x in range(256):
   a=b[6144+at+x//8];c=(a&7)if b[at+x//8]&(128>>(x&7))else((a>>3)&7);px[x,y]=pal[c+(8 if a&64 else 0)]
   if c:row|=1<<x
  occupied.append(row)
 valid={(x,y)for y in range(153)for x in range(8,225)if not any(occupied[y+r]&(ship[r]<<x)for r in range(8))};queue=collections.deque((8,y)for y in range(153)if(8,y)in valid);seen=set(queue)
 while queue:
  x,y=queue.popleft()
  for q in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
   if q in valid and q not in seen:seen.add(q);queue.append(q)
 rec=dict(variant=variant,occupied_boss_pixels=sum(r.bit_count()for r in occupied[:160]),safe_player_positions=len(valid),left_to_right_path=any(x==224 for x,y in seen),reachable_safe_positions=len(seen),scope='Captured25actor arrangement only; source phase mask/pixel coverage; excludes projectiles, terrain, timing and actual playthrough');report.append(rec);print(rec);im.resize((768,576),Image.Resampling.NEAREST).save(out/(variant+'_preview.png'));draw.text((n*768+5,5),'r50 32px spheres /96px core'if n==0 else'r51 24px spheres /80px core',fill='white');sheet.paste(im.resize((768,576),Image.Resampling.NEAREST),(n*768,28))
sheet.save(out/'size_comparison.png');(out/'clearance_analysis.json').write_text(json.dumps(report,indent=2))
