from pathlib import Path
import json
from PIL import Image,ImageDraw
from render_l5_preshift import image
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'build/fullgame/boss_motion_r60';OUT=ROOT/'build/diagnostics/boss_motion_r60'
def main():
 OUT.mkdir(parents=True,exist_ok=True);sections=[]
 for n in range(1,9):
  cap=SRC/f'captures_L{n}.json'
  if not cap.exists():continue
  rows=json.loads(cap.read_text());frames=[image((SRC/r['file']).read_bytes())for r in rows]
  if not frames:continue
  dur=[max(20,round((rows[min(i+1,len(rows)-1)]['frame']-r['frame'])*1000/60))for i,r in enumerate(rows)];dur[-1]=dur[-2]if len(dur)>1 else 100
  frames[0].save(OUT/f'L{n}.png');frames[0].save(OUT/f'L{n}.gif',save_all=True,append_images=frames[1:],duration=dur,loop=0,disposal=2)
  sections.append(f'<section><h2>Level {n}</h2><img src="L{n}.gif"></section>')
 (OUT/'index.html').write_text('<meta charset="utf-8"><title>r60 native boss motion</title><style>body{background:#111;color:white;font:18px system-ui}main{display:flex;flex-wrap:wrap;gap:20px}img{image-rendering:pixelated;max-width:100%}</style><h1>r60 native game captures</h1><p>Completed game bitmap and ECM captures, 16 consecutive world updates. Timing follows emulated refresh intervals; these are not physical hardware captures. Each short excerpt jumps when it loops. Invulnerability and the double-B checkpoint are diagnostic aids.</p><main>'+''.join(sections)+'</main>')
if __name__=='__main__':main()

