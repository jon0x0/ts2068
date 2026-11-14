from pathlib import Path
import json,sys,base64,shutil,numpy as np
from PIL import Image
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));B=R/'build/graphics/walker_runtime_r86';O=R/'build/graphics/walker_selection_r89';O.mkdir(exist_ok=True);shutil.copytree(B,O,dirs_exist_ok=True);review=json.loads((R/'convref/rtype-walker-candidates-r88.json').read_text());data=json.loads((R/'build/graphics/walker_candidates_r88/data.json').read_text());runtime=json.loads((B/'inputs.json').read_text());jobs=[]
for id in['head32','large40']:
 r=next(g for g in review['groups']if g['id']==id);g=next(g for g in data['groups']if g['id']==id);v=next(v for v in g['variants']if v['id']==r['choice']);n,key=(6,'head')if id=='head32'else(1,'large');aa=[a for a in runtime['assets']if a['level']==n and a['key']==key]
 for a,p in zip(aa,v['profiles']):jobs.append(dict(name=a['name'],profile=p,settings=r['variants'][r['choice']],review_id=id,choice=r['choice']))
# Exact keep baseline: four-cycle cadence, three native drawings, no invented fourth.
g=next(g for g in data['groups']if g['id']=='round3');pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)],int)
for k,f in enumerate(g['baseline']):
 w,h=f['w'],f['h'];rgb=np.frombuffer(base64.b64decode(f['rgb']),np.uint8).reshape(h,w,3);idx=((rgb[:,:,None,:].astype(int)-pal[None,None,:,:])**2).sum(3).argmin(2).astype('uint8');assert np.array_equal(pal[idx].astype('uint8'),rgb);bits=np.zeros((h,w//8),np.uint8);attrs=np.zeros_like(bits)
 for y in range(h):
  for x in range(w//8):
   row=idx[y,x*8:x*8+8];cs=sorted(set(map(int,row)));assert len(cs)<=2;p,q=cs[0],cs[-1];attrs[y,x]=(p<<3)|q;bits[y,x]=sum(128>>j for j,c in enumerate(row)if c==q)if p!=q else 0
 name=f'L3_round_{k}';(O/(name+'.bits')).write_bytes(bits.tobytes());(O/(name+'.attrs')).write_bytes(attrs.tobytes());Image.fromarray(rgb).save(O/(name+'.png'))
for g in runtime['groups']:
 if g['level']==3 and g['key']=='round':g['expected_unique']=3;g['review_choice']='keep r88 baseline'
# Fresh native-size and modest-size replacement options.
from build_graphics import decode_roms,palette_ram
sp,_=decode_roms();pal1=palette_ram(R/'build/fullgame/arcade_reference/frame004200_palette_sprite.bin')[64:80]
import ast
tree=ast.parse((R/'scripts/prepare_walker_runtime_r86.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='small4'],type_ignores=[]),'source_helpers','exec'))
originals=[small4(k)for k in range(4)]
for code in[1600,1602]:
 a=np.block([[sp[code],sp[code+8]],[sp[code+1],sp[code+9]]]);im=Image.fromarray(np.concatenate([pal1[a],np.where(a[:,:,None],255,0)],2).astype('uint8'));originals.append(im.crop(im.getbbox()))
for k,im in enumerate(originals):im.save(O/f'gunwalker_source_{k}.png');gen=Path('C:/Users/Jon/.codex/generated_images/01a19855-5e8b-7c01-9834-206ac0fda11a/exec-e50db84b-d12c-431b-87cf-a591c2b80602.png');project_source=O/'gunwalker_redraw_source.png'
if not project_source.exists():shutil.copy2(gen,project_source)
sheet=Image.open(project_source).convert('RGBA');redraw=[];slots=[];boxes=[]
for k in range(6):
 im=sheet.crop((k*sheet.width//6,0,(k+1)*sheet.width//6,sheet.height));a=np.array(im);mask=(a[:,:,3]>=230).astype('uint8')*255;a[:,:,3]=mask;rgb=a[:,:,:3].astype(float);r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2];blue=(b>r*1.35)&(b>g*1.08)&(g>20)&(mask>0);lum=rgb.mean(2);rgb[blue&(lum<85)]=(0,30,170);rgb[blue&(lum>=85)&(lum<150)]=(0,130,210);rgb[blue&(lum>=150)]=(80,210,245);a[:,:,:3]=rgb.clip(0,255).astype('uint8');im=Image.fromarray(a);box=Image.fromarray(mask).getbbox();assert box;redraw.append(im.crop(box));slots.append(im);boxes.append(box)
union=(min(b[0]for b in boxes[:4]),min(b[1]for b in boxes[:4]),max(b[2]for b in boxes[:4]),max(b[3]for b in boxes[:4]))
for k in range(4):redraw[k]=slots[k].crop(union)
def profile(im,size,id):
 w,h=size;ratio=min(w/im.width,h/im.height);im=im.resize((max(1,round(im.width*ratio)),max(1,round(im.height*ratio))),Image.Resampling.LANCZOS);can=Image.new('RGBA',size);can.alpha_composite(im,((w-im.width)//2,h-im.height));a=np.array(can);mask=(a[:,:,3]>=180)&(a[:,:,:3].max(2)>0);rgb=a[:,:,:3].copy();rgb[~mask]=0;can.save(O/f'{id}_source.png');red=(rgb[:,:,0].astype(float)>rgb[:,:,1]*1.4)&(rgb[:,:,0].astype(float)>rgb[:,:,2]*1.3);return dict(id=id,w=w,h=h,bright=False,strategy='segment-coverage',raw=base64.b64encode(rgb.tobytes()).decode(),mask=base64.b64encode(mask.astype('uint8').tobytes()).decode(),red_mask=base64.b64encode(red.astype('uint8').tobytes()).decode())
variants=[]
for variant,ims,settings in[('A',originals,dict(brightness=52,contrast=59,saturation=78,gamma=1.15)),('B',redraw,dict(brightness=56,contrast=54,saturation=76,gamma=1.55)),('C',redraw,dict(brightness=54,contrast=56,saturation=76,gamma=1.35))]:
 vv=[]
 for k,im in enumerate(ims):
  size=((40,32)if k<4 else(32,32))if variant=='C'else((32,24)if k<4 else(24,24));p=profile(im,size,f'new_{variant}_{k}');jobs.append(dict(name=p['id'],profile=p,settings=settings,review_id='replacement',choice=variant));vv.append(p)
 variants.append(dict(id=variant,label={'A':'Fresh arcade conversion','B':'New reference-inspired redraw','C':'Larger redraw proposal40x32'}[variant],profiles=vv,settings=settings))
(O/'conversion_jobs.json').write_text(json.dumps(jobs,indent=2));(O/'replacement_variants.json').write_text(json.dumps(variants,indent=2));(O/'inputs.json').write_text(json.dumps(runtime,indent=2));shutil.copy2(R/'build/graphics/walker_candidates_r88/worker.js',O/'worker.js');shutil.copy2(R/'convref/rtype-walker-candidates-r88.json',O/'user_choices.json');print('Prepared exact saved choices and three replacement options')
