from pathlib import Path
import sys,inspect,json,hashlib
import numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();sys.path.insert(0,str(R/'scripts'))
import decode_arcade_objects as dec
from build_graphics import decode_roms
CAP=R/'build/graphics/l6_flash_capture';S=R/'build/graphics/l6_flash_sources';S.mkdir(parents=True,exist_ok=True)
ns=dict(vars(dec));exec(inspect.getsource(dec.render).replace('build/fullgame/arcade_reference/','build/graphics/l6_flash_capture/'),ns);sp,_=decode_roms();sequence=[];unique=[];keys={};trace=[]
for frame in range(48272,48433,4):
 rows=ns['render'](frame,sp)[1];expected=308-(frame-48300)*2.5
 choices=[(d,im) for d,im in rows if d['width']==32 and d['height']==64 and d['y']==16 and d['colour']==4]
 if not choices:continue
 d,im=min(choices,key=lambda v:abs(v[0]['x']-expected))
 if abs(d['x']-expected)>12:continue
 right=next(((dd,ii) for dd,ii in rows if dd['x']==d['x']+32 and dd['y']==d['y'] and dd['width']==32 and dd['height']==64 and dd['colour']==d['colour']),None)
 if right is None:continue
 dd,ii=right;full=Image.new('RGBA',(64,64));full.alpha_composite(im,(0,0));full.alpha_composite(ii,(32,0));full=full.crop((0,0,64,48));key=hashlib.sha256(full.tobytes()).hexdigest()
 if key not in keys:
  idx=len(unique);keys[key]=idx;unique.append({'codes':[d['code'],dd['code']],'frame':frame,'sha256':key});full.save(S/f'arcade_pair_{idx}_0.png')
 idx=keys[key];sequence.append(idx);trace.append({'frame':frame,'pose':idx,'codes':[d['code'],dd['code']],'x':d['x'],'y':d['y'],'offset':d['offset']})
assert len(sequence)>25 and len(unique)>3
assert all(b['frame']-a['frame']==4 and b['x']-a['x']==-10 for a,b in zip(trace,trace[1:]))
fps=55.017606
timeline_ms=[(round((i+1)*4/fps*100)-round(i*4/fps*100))*10 for i in range(len(sequence))]
manifest={'refresh_hz':fps,'capture_step_frames':4,'track':trace,'unique':unique,'sequence':sequence,'tracking':'same top-edge actor, expected scroll trajectory within12px; paired sameY/colour atX+32'};(S/'manifest.json').write_text(json.dumps(manifest,indent=2))
# Reuse the corrected converter, now applied to every captured unique state.
s=(R/'scripts/preview_l6_cylinder_flash.py').read_text(encoding='utf-8-sig');s=s.replace("S=R/'build/graphics/l6_assembly_review'","S=R/'build/graphics/l6_flash_sources'")
s=s.replace('pairs=[(320,324),(1476,336),(1488,340)]',f'pairs={[(i,0) for i in range(len(unique))]!r}')
s=s.replace('for j in [0,1,2,1]',f'for j in {sequence!r}').replace('duration=280','duration=timeline_ms')
start=s.index("sheet=Image.new('RGB'");end=s.index('sha=hashlib',start)
s=s[:start]+s[end:];exec(compile(s,'captured_converter','exec'))
O=R/'build/graphics/l6_cylinder_flash'
# Full source reference uses the same observed sequence.
fs=[Image.open(S/f'arcade_pair_{i}_0.png').convert('RGB').resize((320,240),Image.Resampling.NEAREST) for i in sequence];fs[0].save(O/'arcade_observed.gif',save_all=True,append_images=fs[1:],duration=timeline_ms,loop=0,disposal=2)
contact=Image.new('RGB',(800,200*len(unique)),(18,18,18));draw=ImageDraw.Draw(contact)
for i,u in enumerate(unique):
 for col,(title,im) in enumerate([('SOURCE '+str(u['codes']),Image.open(S/f'arcade_pair_{i}_0.png')),('A: CYAN RIMS',Image.open(O/f'cyan_rim_{i}.png')),('B: COOL METAL',Image.open(O/f'cyan_metal_{i}.png'))]):
  draw.text((col*265+4,i*200+5),title,fill='white');contact.paste(im.convert('RGB').resize((im.width*3,im.height*3),Image.Resampling.NEAREST),(col*265+4,i*200+25))
contact.save(O/'observed_states.png')
(O/'source_sequence.json').write_text(json.dumps(manifest,indent=2))
(O/'index.html').write_text('''<meta charset=utf-8><title>L6 cylinder and original flashing sequence</title><style>body{background:#151515;color:white;font:18px system-ui;max-width:1150px;margin:24px auto}img{max-width:100%;image-rendering:pixelated}.row{display:flex;gap:25px;flex-wrap:wrap}a{color:cyan}</style><h1>Corrected cylinder bounds and observed arcade flashing</h1><p>Lower cylinder shading now uses its actual source rows32-46, matching the upper cylinder diameter treatment. Both versions retain source dark strokes. A keeps yellow faces/cyan rims; B uses cyan/white metal. The darker32x32 #9-13 version is accepted and retained.</p><p>These animations follow one arcade actor captured every4 source frames, including the original small side-light and dome changes, rather than the previous guessed three-pose cycle. Playback follows the measured source-frame sequence at the MAME-reported 55.017606 Hz, rounded to GIF timing. Side lamps use the original dim/bright red palette phase; domes retain the source highlight changes.</p><div class=row><figure><figcaption>Original arcade actor</figcaption><img src=arcade_observed.gif></figure><figure><figcaption>A: cyan rims</figcaption><img src=cyan_rim.gif></figure><figure><figcaption>B: cool metal</figcaption><img src=cyan_metal.gif></figure></div><details><summary>All observed states beside conversions</summary><img src=observed_states.png></details><p>Asset preview only; not installed in game. <a href=source_sequence.json>Capture trace</a>.</p>''',encoding='utf-8')
validation=json.loads((O/'validation.json').read_text());validation['legal_frames']=2*len(unique);validation['source_codes']=[u['codes'] for u in unique];validation['side_lamps']='Source palette red intensity threshold170: dim off, bright red on';validation['refresh_hz']=fps;(O/'validation.json').write_text(json.dumps(validation,indent=2))
lamp_checks=[]
for i in range(len(unique)):
 im=Image.open(S/f'arcade_pair_{i}_0.png').resize((43,32),Image.Resampling.NEAREST);can=Image.new('RGBA',(48,32));can.alpha_composite(im,(2,0));v=np.array(can).astype(float);r,g,b=v[:,:,:3].transpose(2,0,1);y,x=np.indices(r.shape);sx=(x-2)*64/43;sy=y*48/32
 lamp=(r>g*1.4)&(r>b*1.05)&(sx>=18)&(sx<26)&(((sy>=13)&(sy<15))|((sy>=44)&(sy<46)))&(v[:,:,3]>127);lit=bool((r[lamp]>=170).any());counts=[]
 for style in ['cyan_rim','cyan_metal']:
  a=np.load(O/f'{style}_{i}.npy');n=int(((a==2)&lamp).sum());assert (n>0 if lit else n==0);counts.append(n)
 lamp_checks.append({'state':i,'source_lit':lit,'red_pixels':counts})
validation['side_lamp_checks']=lamp_checks;validation['accepted_head']={'directory':'../l6_ordered_machinery','pattern':'head_darker_*.npy','size':[32,32],'status':'User accepted'};(O/'validation.json').write_text(json.dumps(validation,indent=2))
print('observed',len(sequence),'samples;',len(unique),'unique states;',[(u['codes'],u['frame']) for u in unique])
