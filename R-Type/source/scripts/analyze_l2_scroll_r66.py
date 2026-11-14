from pathlib import Path
import json,numpy as np,collections
O=Path('build/fullgame/startup_r66');rows=json.loads((O/'L2_fine_approach.json').read_text())['fineShots']
def decode(b):
 a=np.zeros((160,256),np.uint8)
 for y in range(160):
  off=((y&192)<<5)|((y&7)<<8)|((y&56)<<2);a[y]=np.unpackbits(np.frombuffer(b[0x4000+off:0x4020+off],np.uint8))
 return a
report=[]
for old,new in zip(rows,rows[1:]):
 a=decode((O/old['file']).read_bytes());b=decode((O/new['file']).read_bytes());r=[]
 for y in range(64,160,8):
  crop=b[y:y+8,112:240];n=int(crop.sum())
  if n<10:continue
  costs=[int(np.count_nonzero(crop!=a[y:y+8,112+d:240+d]))for d in range(3)];r.append({'y':y,'dx':int(np.argmin(costs)),'costs':costs})
 report.append({'old':old['u'],'new':new['u'],'fine':new['fine'],'bands':r})
(O/'L2_scroll_band_motion.json').write_text(json.dumps(report,indent=2));print(collections.Counter((r['y'],r['dx'])for q in report for r in q['bands']));print(report[:2])
