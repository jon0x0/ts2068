from pathlib import Path
import json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/diagnostics/l5_preshift_r58'
def image(raw):
 im=Image.new('RGB',(256,192));p=im.load()
 for y in range(192):
  at=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
  for x in range(256):
   bits=raw[0x4000+at+(x>>3)];a=raw[0x6000+at+(x>>3)];c=(a&7)if bits&(128>>(x&7))else(a>>3)&7;v=255 if a&64 else 205;p[x,y]=(v if c&2 else 0,v if c&4 else 0,v if c&1 else 0)
 return im.resize((512,384),Image.Resampling.NEAREST)
def main():
 first=[];metrics=[]
 for name in ['baseline','candidate']:
  folder=OUT/name;captures=json.loads((folder/'captures.json').read_text());frames=[image((folder/f'scene_{r["update"]}.bin').read_bytes())for r in captures];dur=[max(10,round((captures[min(i+1,len(captures)-1)]['frame']-r['frame'])/60*1000))for i,r in enumerate(captures)];dur[-1]=dur[-2];frames[0].save(OUT/(name+'.gif'),save_all=True,append_images=frames[1:],duration=dur,loop=0,disposal=2);frames[0].save(OUT/(name+'.png'));first.append(frames[0]);metrics.append(dict(build=name,native_frames=len(frames),capture_span_refreshes=captures[-1]['frame']-captures[0]['frame'],gif_frame_ms=dur))
 canvas=Image.new('RGB',(1056,420),'#111111');d=ImageDraw.Draw(canvas);d.text((12,8),'r57 - original cell steps',fill='white');d.text((540,8),'r58 - two-pixel phase trial',fill='white');canvas.paste(first[0],(8,30));canvas.paste(first[1],(536,30));canvas.save(OUT/'comparison.png')
 (OUT/'preview_metrics.json').write_text(json.dumps(metrics,indent=2));(OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>L5 native movement comparison</title><style>body{background:#111;color:#eee;font:17px system-ui;margin:28px}main{display:flex;gap:24px;flex-wrap:wrap}img{image-rendering:pixelated;max-width:100%}section{max-width:512px}p{max-width:1000px;line-height:1.5}</style><h1>L5 native movement trial</h1><p>Actual game framebuffer captures from r57 and the r58 trial, following the same double-B route. Each animation keeps its measured emulated update spacing. These are short 16-update loops; the jump when a loop restarts is from the excerpt. They are not hardware captures.</p><main><section><h2>r57</h2><img src="baseline.gif"></section><section><h2>r58: 2-pixel phases</h2><img src="candidate.gif"></section></main><p>The boss simulation clock remains unchanged. Fine movement adds drawing work; this trial is for comparison. Player and projectiles retain their independent update paths. Original sprite dimensions are retained.</p>')
 print(OUT/'index.html')
if __name__=='__main__':main()
