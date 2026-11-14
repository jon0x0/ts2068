from pathlib import Path
import json,collections,numpy as np
exec(Path('scripts/analyze_l2_scroll_r66.py').read_text().split('report=[]')[0])
c=collections.Counter();counts=collections.Counter()
for old,new in zip(rows,rows[1:]):
 a=decode((O/old['file']).read_bytes());b=decode((O/new['file']).read_bytes())
 for y in range(8,160,8):
  for x in range(40,224,16):
   pix=b[y:y+8,x:x+24]
   if pix.sum()<16:continue
   costs=[np.count_nonzero(pix!=a[y:y+8,x+d:x+24+d])for d in[0,1,2]];counts[x,y]+=1
   if costs[0]+8<costs[1]:c[x,y]+=1
print('persistent stationary regions',[(k,n,counts[k])for k,n in c.most_common()if n>=5])
(O/'L2_scroll_static_windows.json').write_text(json.dumps([{'x':x,'y':y,'static_samples':n,'samples':counts[x,y]}for(x,y),n in c.most_common()],indent=2))
