from pathlib import Path
import json,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1];d=root/'build/local-pulse-video';meta=json.loads((d/'capture.json').read_text());data=np.fromfile(d/'frames.idx',dtype=np.uint8).reshape(360,240,640)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23);title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',29)
pal=np.array([[(c>>1&1)*204+(51 if c&8 else 0),(c>>2&1)*204+(51 if c&8 else 0),(c&1)*204+(51 if c&8 else 0)] for c in range(16)],dtype=np.uint8)
output=d/'sinistar-local-bright-demo.mp4'
p=subprocess.Popen(['C:/apps/video/ffmpeg-7.1.1-full_build/bin/ffmpeg.exe','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','960x800','-r',str(meta['fps']),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','15','-pix_fmt','yuv420p','-movflags','+faststart',str(output)],stdin=subprocess.PIPE)
def raster(n):return Image.fromarray(pal[data[n]])
def page(n,heading,detail):
 im=Image.new('RGB',(960,800),'#101522');im.paste(raster(n).resize((960,720),Image.Resampling.NEAREST),(0,80));draw=ImageDraw.Draw(im);draw.text((22,6),heading,font=title,fill='white');draw.text((22,44),detail,font=font,fill='#b6c6dc');return im
for n in range(30,360):p.stdin.write(page(n,'NORMAL SPEED | native cartridge effect','Three triggered pulses. Watch Sinistar in the center.').tobytes())
for n in range(174,199):
 im=page(n,'8x SLOW MOTION | same captured frames','The native pulse lasts one refresh; only playback is slowed.')
 for _ in range(8):p.stdin.write(im.tobytes())
im=Image.new('RGB',(960,800),'#101522');draw=ImageDraw.Draw(im);draw.text((22,24),'STILL COMPARISON | native raster capture',font=title,fill='white')
for n,x,label in [(185,20,'Before'),(186,490,'During pulse')]:
 face=raster(n).crop((256,114,368,166)).resize((448,416),Image.Resampling.NEAREST);im.paste(face,(x,175));draw.text((x,125),label,font=title,fill='white')
draw.text((22,640),'v9 cartridge. Stationary test fixture; pulse requests injected.',font=font,fill='#b6c6dc');draw.text((22,677),'Colors are the emulator standard palette; no enhanced effect.',font=font,fill='#b6c6dc');im.save(d/'comparison.png')
for _ in range(150):p.stdin.write(im.tobytes())
p.stdin.close();assert p.wait()==0
print(output)
