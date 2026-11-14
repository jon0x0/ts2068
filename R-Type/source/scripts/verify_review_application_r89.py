from pathlib import Path
import json,sys,numpy as np,hashlib,base64
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from PIL import Image
O=R/'build/fullgame/walker_selection_r89';A=R/'build/graphics/walker_selection_r89';B=R/'build/fullgame/walkers_exhaust_r86';reports=json.loads((O/'walker_runtime.json').read_text());prior=json.loads((B/'walker_runtime.json').read_text());pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)],np.uint8);changed=[];frozen=[]
for r in reports:
 n=r['level'];raw=(O/f'L{n}_runtime_art.bin').read_bytes();old=next(x for x in prior if x['level']==n);oldraw=(B/f'L{n}_runtime_art.bin').read_bytes()
 for a in r['assets']:
  off=a['pointer']-r['assets'][0]['pointer'];v=raw[off:off+a['bytes']];previous=next(x for x in old['assets']if x['name']==a['name']);oo=previous['pointer']-old['assets'][0]['pointer'];vv=oldraw[oo:oo+previous['bytes']];selected=(n==6 and a['key']=='head')or(n==1 and a['key']=='large')or(n==3 and a['key']=='round')or(a['key']in['small','raise0','raise1'])
  if not selected:assert v==vv,(n,a['name'],'unreviewed changed');frozen.append(a['name']);continue
  w,h=a['size'];pixels=np.zeros((h,w),np.uint8)
  for x in range(w//8):
   for y in range(h):
    bits,attr=v[(x*h+y)*2:(x*h+y)*2+2]
    for k in range(8):pixels[y,x*8+k]=(attr&7)if bits&(128>>k)else(attr>>3)&7
  attrs=np.frombuffer((A/(a['name']+'.attrs')).read_bytes(),np.uint8).reshape(h,w//8);bits=np.unpackbits(np.frombuffer((A/(a['name']+'.bits')).read_bytes(),np.uint8)).reshape(h,w);expected=np.where(bits,np.repeat(attrs&7,8,1),np.repeat((attrs>>3)&7,8,1));assert np.array_equal(pixels,expected),a['name'];Image.fromarray(pal[pixels]).save(A/(a['name']+'_installed.png'));changed.append(a['name'])
for n in[2,5,8]:assert(O/f'level{n:02d}_region.bin').read_bytes()==(B/f'level{n:02d}_region.bin').read_bytes()
assert(O/'player_flame_phases.bin').read_bytes()==(B/'player_flame_phases.bin').read_bytes()
source=R/'convref/rtype-walker-candidates-r88.json';record=dict(passed=True,exact_installed_palette_indices=changed,unreviewed_and_accepted_frozen=frozen,source_review_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),unchanged_complete_levels=[2,5,8]);(O/'review_application_validation.json').write_text(json.dumps(record,indent=2));print('Exact reviewed/new palette indices',len(changed),'frozen',len(frozen))
# Make replacement panel visible immediately.
p=R/'scripts/publish_walker_selection_r89.py';s=p.read_text().replace(".replace('version:88','version:89')", ".replace('version:88','version:89')")
s=s.replace("s+=\"\\nstate.blue", "s=s.replace(\"box.open=['head32','head24','round3'].includes(g.id)\",\"box.open=true\")\ns+=\"\\nstate.blue");p.write_text(s)
