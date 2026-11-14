from pathlib import Path
import json,sys,zipfile,functools,hashlib,io
from PIL import Image,ImageDraw
R=Path.cwd();O=R/'build/fullgame/l1_chosen_r107';B=R/'build/fullgame/full_plume_r104';sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import unpack
c=json.loads((O/'integration_contract.json').read_text());w=next(v for v in json.loads((O/'walker_runtime.json').read_text()) if v['level']==1);raw=(O/'L1_runtime_art.bin').read_bytes();z=zipfile.ZipFile(R/'convref/rtype-l1-walker-snake-assets.zip');old=(B/'L1_runtime_art.bin').read_bytes();base=w['assets'][0]['pointer']
for a in w['assets']:
 p=a['pointer']-base;v=raw[p:p+a['bytes']]
 if a['key']=='round':assert v==z.read(f"walker/frame_{a['frame']:02d}.pairs.bin")
 elif a['key']=='snake':assert v==z.read(f"snake/frame_{a['export_frame']:02d}.pairs.bin")
 else:assert v==old[p:p+a['bytes']]
 assert all(at&0xc0==0 for at in v[1::2])
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();a=(B/f'level{n:02d}_region.bin').read_bytes();assert len(b)==65536
 if n==1:
  allowed=set(range(c['rawptr'],0x3a00))|{c['install_operand'],c['install_operand']+1,c['warmup_operand'],c['warmup_operand']+1};assert all(x==y or i in allowed for i,(x,y)in enumerate(zip(a,b)));assert unpack(b[c['rawptr']:])==raw;assert unpack(b[c['imageptr']:])==(O/'L1_runtime_image.bin').read_bytes()
 else:assert a==b
 for name in [f'LEVEL{n:02d}.TAP',f'START{n:02d}.TAP']:
  t=(O/'rtype'/name).read_bytes();p=0;parts=[]
  while p<len(t):
   size=int.from_bytes(t[p:p+2],'little');v=t[p+2:p+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0
   if v[0]==255:parts.append(v[1:-1])
   p+=size+2
  assert b''.join(parts)==(b if name.startswith('LEVEL') else b''.join(b[k*8192:(k+1)*8192]for k in [0,1,4,5,6,7]))
assert c['imageend']<=c['artbase'] and c['artend']<=0xc000 and c['end']<=0x3a00
for n in ['RTCORE.TAP','RTPRELD.TAP','RTBOOT.TAP']:assert (O/'rtype'/n).read_bytes()==(B/'rtype'/n).read_bytes()
for p in (O/'rtype').glob('*.tap'):
 t=p.read_bytes();at=0
 while at<len(t):
  size=int.from_bytes(t[at:at+2],'little');v=t[at+2:at+2+size];assert functools.reduce(int.__xor__,v,0)==0;at+=size+2
assert json.loads((O/'l1_live_validation.json').read_text())['passed'];assert json.loads((O/'l1_nofire_validation.json').read_text())['passed'];assert json.loads((O/'native_revisits_validation.json').read_text())['passed']
summary=dict(passed=True,source_zip_sha256=hashlib.sha256((R/'convref/rtype-l1-walker-snake-assets.zip').read_bytes()).hexdigest(),base='r104',walker_frames=4,snake_orientations=len([a for a in w['assets']if a['key']=='snake']),exact_export_pairs=True,other7levels_identical=True,layout=c,normalBlack=True,hardware_pending=True,known_limitation='Small diagonal gaps remain between some snake joints; movement/collision scripts unchanged.');(O/'validation_summary.json').write_text(json.dumps(summary,indent=2))
# Selected artwork comparison; offline, distinct from RAM captures.
sheet=Image.new('RGB',(768,300),(15,20,25));d=ImageDraw.Draw(sheet)
for family,row,count in [('walker',0,4),('snake',1,7)]:
 ids=range(4)if family=='walker'else sorted(set(c['mapping']))
 for k,i in enumerate(ids):
  im=Image.open(io.BytesIO(z.read(f'{family}/frame_{i:02d}.png'))).convert('RGBA');x=k*105;y=row*150+25;sheet.paste(im.resize((96,96)),(x,y),im.resize((96,96)));d.text((x,y-18),family+' '+str(i),fill='white')
sheet.save(O/'selected_art.png');print('Static scope, exported art, bank boundaries, tapes, runtime tests PASS')
