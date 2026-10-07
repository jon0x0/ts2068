from pathlib import Path
import numpy as np,json,math,hashlib
root=Path(__file__).resolve().parents[1];p=root/'build/cycling-halo-video'
d=np.fromfile(p/'frames.idx',dtype=np.uint8).reshape(360,240,640);m=json.loads((p/'capture.json').read_text())
for event in range(3):
 stages=m['stages'][event*5:event*5+5];first=stages[0]['frame'];base=d[first-1]
 assert [s['frame'] for s in stages]==list(range(first,first+5)), 'one phase per refresh'
 for stage,r in enumerate([43,45,47,49]):
  n=stages[stage]['frame'];bad=0
  for dy in range(-49,50):
   y=116+dy
   if not 64<=y<176:continue
   inner=math.isqrt(1600-dy*dy) if abs(dy)<=40 else -1
   half=math.isqrt(r*r-dy*dy) if abs(dy)<=r else -1
   for xx in range(32):
    selected=half>=0 and (120-half)//8<=xx<=(120+half-1)//8 and not(inner>=0 and (120-inner)//8<=xx<=(120+inner-1)//8)
    for px in range(xx*8,xx*8+8):
     x=px*2+64;yy=y+24
     if d[n,yy,x]!=([14,15,10,15][(y+stage)&3] if selected else base[yy,x]):bad+=1
  assert bad==0,(event,stage,bad)
  assert np.array_equal(d[n,114:166,256:368],base[114:166,256:368]), 'Sinistar unchanged'
 assert np.array_equal(d[stages[4]['frame'],88:200,64:576],base[88:200,64:576]), 'restored playfield'
report={'dck_sha256':hashlib.sha256((root/'build/sinistar-mining.dck').read_bytes()).hexdigest(),'pulses':3,'completeColorFrames':12,'oneScanlineShiftPerRefresh':True,'unchangedSinistar':True,'exactRasterRestoration':True,'source':'Actual TSRun pixels; stationary native fixture and injected hit events'}
(root/'build/cycling-raster-verification.json').write_text(json.dumps(report,indent=2));print(report)
