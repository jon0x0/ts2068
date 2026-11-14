from pathlib import Path
import json,numpy as np,hashlib
from PIL import Image,ImageDraw
R=Path.cwd();O=R/'build/fullgame/walker_choice_r90';A=R/'build/graphics/walker_choice_r90';B=R/'build/fullgame/walker_selection_r89';reports=json.loads((O/'walker_runtime.json').read_text());old=json.loads((B/'walker_runtime.json').read_text());frozen=[];changed=[];pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)],np.uint8)
for r in reports:
 n=r['level'];raw=(O/f'L{n}_runtime_art.bin').read_bytes();prev=next(x for x in old if x['level']==n);before=(B/f'L{n}_runtime_art.bin').read_bytes()
 for a in r['assets']:
  at=a['pointer']-r['assets'][0]['pointer'];v=raw[at:at+a['bytes']];p=next(x for x in prev['assets']if x['name']==a['name']);off=p['pointer']-prev['assets'][0]['pointer']
  if a['key']not in['small','raise0','raise1']:assert v==before[off:off+p['bytes']],a['name'];frozen.append(a['name']);continue
  w,h=a['size'];pix=np.zeros((h,w),np.uint8)
  for x in range(w//8):
   for y in range(h):
    bits,attr=v[(x*h+y)*2:(x*h+y)*2+2]
    for k in range(8):pix[y,x*8+k]=(attr&7)if bits&(128>>k)else(attr>>3)&7
  attrs=np.frombuffer((A/(a['name']+'.attrs')).read_bytes(),np.uint8).reshape(h,w//8);bits=np.unpackbits(np.frombuffer((A/(a['name']+'.bits')).read_bytes(),np.uint8)).reshape(h,w);wanted=np.where(bits,np.repeat(attrs&7,8,1),np.repeat((attrs>>3)&7,8,1));assert np.array_equal(wanted,pix);Image.fromarray(pal[pix]).save(A/(a['name']+'_installed.png'));changed.append(a['name'])
for n in[2,3,5,6,8]:assert (O/f'level{n:02d}_region.bin').read_bytes()==(B/f'level{n:02d}_region.bin').read_bytes(),n
source=R/'convref/rtype-new-gunwalker-r89.json';(O/'review_application_validation.json').write_text(json.dumps(dict(passed=True,choice='A',settings=dict(brightness=39,contrast=70,saturation=100,gamma=1.01),exact_installed_palette_indices=changed,frozen_frames=frozen,unchanged_levels=[2,3,5,6,8],review_sha256=hashlib.sha256(source.read_bytes()).hexdigest()),indent=2))
can=Image.new('RGB',(960,155),(16,22,28));d=ImageDraw.Draw(can)
for k,(key,f)in enumerate([('small',0),('small',1),('small',2),('small',3),('raise0',0),('raise1',0)]):
 im=Image.open(A/f'L1_{key}_{f}_installed.png');can.paste(im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST),(k*160+5,30));d.text((k*160+5,5),'Walk '+str(k+1)if k<4 else'Raise '+str(k-3),fill='white')
can.save(A/'chosen_walker.png');print('Exact chosen frames',len(changed),'frozen',len(frozen))
