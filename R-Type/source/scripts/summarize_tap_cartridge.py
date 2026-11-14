"""Summarize paired actual runtime traces and visible terrain at matched updates."""
from pathlib import Path
import json
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parents[1]; O=R/'build/cartridges/tap_comparison'
def off(x,y):return ((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|(x>>3)
def pixel(b,x,y):
 p=off(x,y); bit=(b[p]>>(7-(x&7)))&1; a=b[6144+p]; return bit,(a&7 if bit else (a>>3)&7),a
rows=[]; sheet=Image.new('RGB',(1040,8*225),'#141414');draw=ImageDraw.Draw(sheet)
for n in range(1,9):
 name=f'level{n:02d}'+('_seeded' if n==8 else '')+('_candidate' if n in [2,5] else '')
 d=O/name; c=json.loads((d/'comparison.json').read_text()); visual=[]
 for u in [32,64,120]:
  a=(d/f'tap_{u}.screen.bin').read_bytes(); b=(d/f'cart_{u}.screen.bin').read_bytes(); ao=(d/f'tap_{u}.owner.bin').read_bytes();bo=(d/f'cart_{u}.owner.bin').read_bytes(); count=bits=colors=0
  for y in range(160):
   for x in range(256):
    cell=(y//8)*32+x//8
    if ao[cell]==255 and bo[cell]==255:
     p,q=pixel(a,x,y),pixel(b,x,y);count+=1;bits+=p[0]!=q[0];colors+=p[1]!=q[1]
  visual.append(dict(update=u,terrain_pixels=count,bitmap_differences=bits,color_differences=colors))
  if u==64:
   for col,data in enumerate([a,b]):
    im=Image.new('RGB',(256,192));ip=im.load()
    for y in range(192):
     for x in range(256):
      _,ci,at=pixel(data,x,y);v=255 if at&64 else 205;ip[x,y]=(v if ci&2 else 0,v if ci&4 else 0,v if ci&1 else 0)
    sheet.paste(im.resize((512,192),Image.Resampling.NEAREST),(col*520,(n-1)*225+24))
   draw.text((4,(n-1)*225+4),f'Level {n}: TAP left / cartridge right, active update 64',fill='white')
 rows.append(dict(level=n,trace=name,passed=c['passed'],controls_match=c['controlsMatch'],matched_states=c['matchedCameraStates'],terrain=visual,tap_frames=c['tap']['framesAfterActive'],cart_frames=c['cart']['framesAfterActive'],inputs=c['inputs']))
sheet.save(O/'paired_scenes.png');(O/'summary.json').write_text(json.dumps(rows,indent=2))
boss=[]
for n in range(1,9):
 name=f'level{n:02d}_boss_seeded'+('_candidate' if n==5 else '')
 d=O/name
 if not (d/'comparison.json').exists():
  d=O/f'level{n:02d}_boss'
 j=json.loads((d/'comparison.json').read_text())
 boss.append(dict(level=n,passed=j['passed'],actor_differences=j['actorDifferenceCount'],event_differences=len(j['eventDifferences']),trace=d.name))
gate=dict(passed=all(r['passed'] and all(v['bitmap_differences']==0 and v['color_differences']==0 for v in r['terrain'])for r in rows)and all(r['passed']for r in boss),early_gameplay=rows,bosses=boss,hardware_confirmed=False,scope='120 native world updates per scenario. Controls are initialized runtime component tests. Terrain pixels only where both displayed owner maps mark terrain. Screens are captured inside the native update, so different actor draw/publication phases are not a completed-frame visual comparison. Colors compare 3-bit indices, not BRIGHT. L8 controls both ROM-sampling RNG helpers. No all-boss victory/full-game/audio tempo or hardware parity claim.')
(O/'parity_gate.json').write_text(json.dumps(gate,indent=2))
print(json.dumps([{k:r[k] for k in ['level','passed','controls_match','terrain']}for r in rows],indent=2))
