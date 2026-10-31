from pathlib import Path
import json,zipfile
import numpy as np
from PIL import Image,ImageDraw
from convert_image import PALETTE
r=Path(__file__).resolve().parent
captures=json.loads((r/'captured-pixels.json').read_text())
for name in ['dynamic','ecm']:
 idx=np.array(captures[name],dtype=np.uint8).reshape(240,640)[24:216,64:576:2]
 assert np.array_equal(idx,np.load(r/(name+'-indices.npy')))
 Image.fromarray(PALETTE[idx]).resize((768,576),Image.Resampling.NEAREST).save(r/(name+'-native.png'))
comparison=Image.new('RGB',(1536,612),(18,18,24));draw=ImageDraw.Draw(comparison)
for x,name,label in [(0,'ecm','Standard ECM: 2 colors per 8x1 cell'),(768,'dynamic','Dynamic ECM: up to 4 colors in selected 8x1 cells')]:
 draw.text((x+12,12),label,fill='white');comparison.paste(Image.open(r/(name+'-native.png')),(x,36))
comparison.save(r/'prismatic-comparison.png')
