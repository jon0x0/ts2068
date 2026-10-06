from pathlib import Path
import json,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1];d=root/'build/ring-pulse-video';meta=json.loads((d/'capture.json').read_text());data=np.fromfile(d/'frames.idx',dtype=np.uint8).reshape(360,240,640)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23);title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',29)
pal=np.array([[(c>>1&1)*204+(51 if c&8 else 0),(c>>2&1)*204+(51 if c&8 else 0),(c&1)*204+(51 if c&8 else 0)] for c in range(16)],dtype=np.uint8)
output=d/'sinistar-ring-pulse-demo.mp4'
p=subprocess.Popen(['C:/apps/video/ffmpeg-7.1.1-full_build/bin/ffmpeg.exe','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','960x800','-r',str(meta['fps']),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','15','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],stdin=subprocess.PIPE)
def raster(n):return Image.fromarray(pal[data[n]])
def page(n,heading,detail):
 im=Image.new('RGB',(960,800),'#101522');im.paste(raster(n).resize((960,720),Image.Resampling.NEAREST),(0,80));draw=ImageDraw.Draw(im);draw.text((22,6),heading,font=title,fill='white');draw.text((22,44),detail,font=font,fill='#b6c6dc');return im
for n in range(30,360):p.stdin.write(page(n,'NORMAL SPEED | native cartridge effect','Red - yellow - red - off. Three triggered Sinibomb-hit pulses.').tobytes())
start=meta['stages'][4]['frame']-4
for n in range(start,start+12):
 im=page(n,'8x SLOW MOTION | same captured frames','Only playback is slowed; these are actual emulator raster frames.')
 for _ in range(8):p.stdin.write(im.tobytes())
p.stdin.close();assert p.wait()==0
page(meta['stages'][1]['frame']+1,'RED / YELLOW / RED | native outline','A radius-30-pixel circle clipped to the playfield.').save(d/'preview.png')
(d/'WATCH.html').write_text('<!doctype html><meta charset="utf-8"><title>Sinistar ring pulse</title><body style="background:#101522;color:white;font:18px sans-serif"><h1>Red / yellow / red ring</h1><video controls autoplay loop muted style="max-width:96vw;max-height:82vh" src="sinistar-ring-pulse-demo.mp4"></video><p>Native cartridge raster capture. Stationary fixture; three injected hit events. Normal speed followed by 8x slow motion. No audio in this clip.</p></body>')
print(output)
