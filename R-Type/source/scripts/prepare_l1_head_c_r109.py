from pathlib import Path
import json,base64,shutil
from PIL import Image
R=Path.cwd();O=R/'build/graphics/l1_head_c_r109';O.mkdir(exist_ok=True);d=json.loads((R/'build/graphics/walker_candidates_r88/data.json').read_text());g=next(x for x in d['groups']if x['id']=='head32');v=next(x for x in g['variants']if x['id']=='B');jobs=[]
for i,p in enumerate(v['profiles']):
 rgb=Image.frombytes('RGB',(p['w'],p['h']),base64.b64decode(p['raw'])).resize((24,24),Image.Resampling.LANCZOS);mask=Image.frombytes('L',(p['w'],p['h']),bytes(x*255 for x in base64.b64decode(p['mask']))).resize((24,24),Image.Resampling.LANCZOS);q=dict(p,w=24,h=24,raw=base64.b64encode(rgb.tobytes()).decode(),mask=base64.b64encode(bytes(int(x>=112) for x in mask.tobytes())).decode())
 if p.get('red_mask'):q['red_mask']=base64.b64encode(bytes(int(x>=112)for x in Image.frombytes('L',(p['w'],p['h']),bytes(x*255 for x in base64.b64decode(p['red_mask']))).resize((24,24),Image.Resampling.NEAREST).tobytes())).decode()
 jobs.append(dict(name=f'L1_head_{i}',profile=q,settings=dict(brightness=52,contrast=59,saturation=82,gamma=.87),review_id='head32 adapted to existing L1 size',choice='B modified = comparison C'))
(O/'conversion_jobs.json').write_text(json.dumps(jobs));shutil.copy2(R/'build/graphics/walker_selection_r89/worker.js',O/'worker.js');s=(R/'scripts/convert_walker_selection_r89.mjs').read_text().replace('build/graphics/walker_selection_r89','build/graphics/l1_head_c_r109');(R/'scripts/convert_l1_head_c_r109.mjs').write_text(s)
