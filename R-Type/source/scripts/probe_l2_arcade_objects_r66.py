import sys
from pathlib import Path
sys.path.insert(0,str(Path('scripts').resolve()));from decode_arcade_objects import render
_,rows=render(16800)
for d,im in rows:
 if (d['x']<110 and d['x']+d['width']>40 and d['y']<145 and d['y']+d['height']>90) or (d['x']<384 and d['x']+d['width']>330 and d['y']<100 and d['y']+d['height']>35):print(d)
