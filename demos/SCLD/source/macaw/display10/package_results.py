from pathlib import Path
import json,shutil,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from palette_fit import PALETTE
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'deliverables';OUT.mkdir(exist_ok=True)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
variants=[('sierra-lite',ROOT),('sierra-line',ROOT/'variants/adaptive-line-sierra'),('sierra2',ROOT/'variants/adaptive-sierra2'),('9-independent',ROOT.parent/'dynamic-ecm-macaw-9'),('10-prover',ROOT/'variants/prover')]
report={};native={}
for name,r in variants:
 source=r/('timex-dynamic-ecm-macaw-9.dck' if name=='9-independent' else 'timex-dynamic-ecm-macaw.dck')
 shutil.copy2(source,OUT/('timex-dynamic-ecm-macaw-'+name+'.dck'))
 captures=json.loads((r/'captured-pixels.json').read_text())
 for mode in ['ecm','dynamic']:
  idx=np.array(captures[mode],np.uint8).reshape(240,640)[24:216,64:576:2]
  assert np.array_equal(idx,np.load(r/(mode+'-indices.npy')))
  im=Image.fromarray(PALETTE[idx]).resize((768,576),Image.Resampling.NEAREST)
  native[name,mode]=im;im.save(OUT/(name+'-'+mode+'.png'))
 report[name]=dict(conversion=json.loads((r/'conversion.json').read_text()),validation=json.loads((r/'validation.json').read_text()))
 if name=='10-prover':
  for y in range(64,128):
   assert sum(len(set(idx[y,c*8:c*8+8]))==4 for c in [0,3,7,10,14,17,21,24,28,31])==10
def sheet(filename,panels,columns):
 rows=(len(panels)+columns-1)//columns;im=Image.new('RGB',(768*columns,616*rows),(18,18,24));draw=ImageDraw.Draw(im)
 for i,(title,picture) in enumerate(panels):
  x=(i%columns)*768;y=(i//columns)*616;draw.text((x+12,y+10),title,font=font,fill='white');im.paste(picture,(x,y+40))
 im.save(OUT/filename)
sheet('macaw-ecm-comparison.png',[('Standard ECM - adaptive Sierra Lite',native['sierra-lite','ecm']),('Dynamic ECM - adaptive Sierra Lite',native['sierra-lite','dynamic'])],2)
sheet('macaw-dither-comparison.png',[('Standard ECM - Sierra Lite',native['sierra-lite','ecm']),('Dynamic ECM - Sierra Lite',native['sierra-lite','dynamic']),('Dynamic ECM - two-row Sierra',native['sierra2','dynamic']),('Dynamic ECM - adapted Sierra Line',native['sierra-line','dynamic'])],2)
(OUT/'results.json').write_text(json.dumps(report,indent=2))
with zipfile.ZipFile(OUT/'dynamic-ecm-macaw-cartridges.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(OUT.glob('*.dck')):z.write(p,p.name)
 z.write(ROOT/'README.md','README.md');z.write(OUT/'results.json','results.json')
with zipfile.ZipFile(OUT/'dynamic-ecm-macaw-source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name,r in [('display10',ROOT),('display9',ROOT.parent/'dynamic-ecm-macaw-9')]:
  for p in sorted(r.rglob('*')):
   if not p.is_file():continue
   rel=p.relative_to(r)
   if any(k in rel.parts for k in ['__pycache__','deliverables']):continue
   if rel.parts[0]=='variants' and (len(rel.parts)<2 or rel.parts[1] not in ['adaptive-line-sierra','adaptive-sierra2','prover']):continue
   if p.name in ['convert_fixed_plan.py','captured-pixels.json']:continue
   z.write(p,Path(name)/rel)
 for p in OUT.glob('*.png'):z.write(p,Path('previews')/p.name)
 z.write(OUT/'results.json','results.json')
print(json.dumps({n:{k:r['conversion'].get(k) for k in ['actualWrites','maxWritesPerRow','cellsWithMoreThanTwoColors','maxMulticolorCellsPerRow']} for n,r in report.items()},indent=2))
