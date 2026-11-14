from pathlib import Path
import sys,json,base64,numpy as np
from PIL import Image,ImageFilter
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from walker_review_r85 import current,PAL
O=R/'build/graphics/walker_candidates_r88';V=R/'build/graphics/walker_review_r85';O.mkdir(exist_ok=True);groups=[]
def b64(v):return base64.b64encode(v).decode()
def source_profile(im,size,id):
 im=im.convert('RGBA');r=min(size[0]/im.width,size[1]/im.height);im=im.resize((max(1,round(im.width*r)),max(1,round(im.height*r))),Image.Resampling.LANCZOS);can=Image.new('RGBA',size);can.alpha_composite(im,((size[0]-im.width)//2,size[1]-im.height));a=np.array(can);mask=(a[:,:,3]>=112)&(a[:,:,:3].max(2)>0);rgb=a[:,:,:3].copy();rgb[~mask]=0;return dict(id=id,w=size[0],h=size[1],bright=False,strategy='segment-coverage',raw=b64(rgb.tobytes()),mask=b64(mask.astype('uint8').tobytes()))
def imgdata(im):
 im=im.convert('RGB');return dict(w=im.width,h=im.height,rgb=b64(im.tobytes()))
def native_rgba(im):
 a=np.array(im.convert('RGB'));return Image.fromarray(np.concatenate([a,np.where(a.max(2,keepdims=True)>0,255,0).astype('uint8')],2))
def lighting(im,style):
 a=np.array(im.convert('RGBA'));rgb=a[:,:,:3].astype(float);mask=(a[:,:,3]>=112)&(rgb.max(2)>0);h,w=mask.shape;y,x=np.indices(mask.shape);r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2];gold=(r>120)&(g>95)&(b<r*.55);red=(r>g*1.5)&(r>b*1.3)&mask;neutral=(rgb.max(2)-rgb.min(2)<55)&mask;lum=rgb.mean(2)
 if style=='gray':
  shade=np.clip(lum*.83+5,0,255);rgb[neutral]=np.repeat(shade[:,:,None],3,2)[neutral]
 elif style=='rim':
  upper=np.zeros_like(mask);upper[1:]=mask[1:]&~mask[:-1];left=np.zeros_like(mask);left[:,1:]=mask[:,1:]&~mask[:,:-1];rim=(upper|left)&neutral;rgb[neutral]=np.stack([lum*.65,lum*.9,lum],2)[neutral];rgb[rim]=np.array([120,220,240])
 elif style in['steel','warm']:
  light=np.clip(.45+.35*(1-y/max(h-1,1))+.2*(1-x/max(w-1,1)),.35,1);rgb[neutral]=np.stack([light*150,light*205,light*220],2)[neutral]
  rgb[gold]=np.stack([light*245,light*(185 if style=='warm' else 220),light*(50 if style=='warm' else 90)],2)[gold];legs=mask&(y>=h*.68)&~red;rgb[legs]=np.stack([light*80,light*175,light*220],2)[legs]
 rgb[~mask]=0;return Image.fromarray(np.concatenate([rgb.clip(0,255).astype('uint8'),np.where(mask[:,:,None],255,0).astype('uint8')],2))
def add(id,title,size,frames,baseline,old,provenance,kind='head',larger=False):
 variants=[]
 specs=([('A','Faithful source',None,dict(brightness=50,contrast=54,saturation=62,gamma=1.15)),('B','Deeper gray casing','gray',dict(brightness=50,contrast=54,saturation=60,gamma=1.12)),('C','Cyan rim / metal shading','rim',dict(brightness=52,contrast=52,saturation=68,gamma=1.2))]if kind=='head'else[('A','Faithful source',None,dict(brightness=50,contrast=54,saturation=66,gamma=1.2)),('B','Cool steel / shaped highlights','steel',dict(brightness=53,contrast=54,saturation=70,gamma=1.3)),('C','Warm metal / blue struts','warm',dict(brightness=51,contrast=58,saturation=70,gamma=1.2))])
 for v,label,style,settings in specs:variants.append(dict(id=v,label=label,preset=settings,profiles=[source_profile(lighting(im,style)if style else im,size,f'{id}_{v}_{k}')for k,im in enumerate(frames)]))
 groups.append(dict(id=id,title=title,size=size,provenance=provenance,larger=larger,frames=len(frames),source=[imgdata(im.convert('RGB'))for im in frames],baseline=[imgdata(im)for im in baseline],rejected=[imgdata(im)for im in old],variants=variants))
head=Image.open(R/'build/graphics/l6_assembly_review/head_arcade.gif');heads=[]
for k in range(4):head.seek(k);heads.append(head.convert('RGBA'))
def prior(n,key):return[Image.open(R/f'build/graphics/walker_runtime_r86/L{n}_{key}_{k}.png').convert('RGB')for k in range(4)]
add('head32','L6 walking head — existing 32x32 footprint',(32,32),heads,[Image.open(R/f'build/graphics/l6_surface_refinement/head_deeper_{k}.png')for k in range(4)],prior(6,'head'),'Verified arcade224/226/228/230. Baseline is the earlier saved deeper-gray conversion. All four cels share settings.')
base7=[current(7,i)[0]for i in[18,19,20,22]]
add('head24','L7 walking head — existing 24x24 footprint',(24,24),heads,base7,prior(7,'head'),'Verified shared walking-head source. Baseline is actual earlier L7 native artwork, not the L6 preview.')
add('head32_l7','L7 walking head — modest 1.33x size proposal',(32,32),heads,[Image.open(R/f'build/graphics/l6_surface_refinement/head_deeper_{k}.png')for k in range(4)],prior(7,'head'),'Same arcade cels at full32x32 source detail. Choosing this would require gameplay/geometry review; not installed.',larger=True)
for n,key,ids,title in[(3,'round',[31,32,33],'Before31 round walker'),(7,'round',[11,12,13],'L7 round walker')]:
 fs=[Image.open(V/f'L{n}_round_{i}_source.png').convert('RGBA')for i in ids];a=np.array(fs[1]);cut=a.shape[0]*2//3;leg=a[cut:].copy();a[cut:]=0;a[cut:,1:]=leg[:,:-1];fs.append(Image.fromarray(a));add(f'round{n}',title,(24,24),fs,[current(n,i)[0]for i in ids]+[current(n,ids[1])[0]],prior(n,'round'),'Native geometry retained; no verified arcade match yet. Three native poses plus an explicitly authored leg-only intermediate; no new AI replacement.',kind='round')
large=[Image.open(R/f'build/graphics/enemy_upgrades_r60/{i}_arcade.png').convert('RGBA')for i in range(201,205)];add('large40','L1 large walker — source and pose review',(40,40),large,[current(1,i)[0]for i in range(201,205)],prior(1,'large'),'Four existing arcade-derived extractions. Pose4 includes a crouch/action change: review whether it belongs in a walking cycle. No new source identity is asserted.',kind='large')
for h in[16,24]:
 aa=[a for a in json.loads((R/'build/graphics/walker_runtime_r86/inputs.json').read_text())['assets']if a['level']==3 and a['key']=='ground'+str(h)];fs=[Image.open(R/f'build/graphics/walker_runtime_r86/{a["name"]}_source.png').convert('RGBA')for a in aa];add(f'ground{h}',f'L3 ground walker — 32x{h}',(32,h),fs,[Image.open(R/f'build/graphics/walker_restore_r87/{a["name"]}.png')for a in aa],prior(3,'ground'+str(h)),'Original foundation HOME geometry recovered before its data area became scratch RAM. Native source identity only; arcade match unverified. Fourth pose is authored.',kind='ground')
for g in groups:
 g['source']=[dict(w=p['w'],h=p['h'],rgb=p['raw'])for p in g['variants'][0]['profiles']]
 for v in g['variants'][1:]:
  for i,p in enumerate(v['profiles']):
   src=g['variants'][0]['profiles'][i];rgb=np.frombuffer(base64.b64decode(src['raw']),np.uint8).reshape(p['h'],p['w'],3).astype(float);red=(rgb[:,:,0]>rgb[:,:,1]*1.4)&(rgb[:,:,0]>rgb[:,:,2]*1.3);p['red_mask']=b64(red.astype('uint8').tobytes())
worker=(R/'build/graphics/arcade_review_r69/worker.js').read_text(encoding='utf-8-sig');worker=worker.replace('const n=p.w*p.h;alphaMask=mask;','const n=p.w*p.h;alphaMask=mask;const redMask=p.red_mask?from64(p.red_mask):null;').replace('const candidates=[];for(let k=0;k<all.length;k+=3){if(!partial||(all[k]===0&&(all[k+1]===0||all[k+2]===0)))','const allowRed=!redMask||redMask.subarray(y*p.w+bx*8,y*p.w+bx*8+8).some(v=>v);const candidates=[];for(let k=0;k<all.length;k+=3){if((!partial||(all[k]===0&&(all[k+1]===0||all[k+2]===0)))&&(allowRed||(![2,3].includes(all[k+1])&&![2,3].includes(all[k+2]))))');(O/'worker.js').write_text(worker,encoding='utf-8');data=dict(groups=groups,blue=dict(image='blue_21_25_keep.png',frames=[imgdata(Image.open(R/f'build/graphics/small_walker_highlights/blue_{i}.png'))for i in range(21,26)]),rpc_sha=json.loads((R/'build/graphics/walker_runtime_r86/manifest.json').read_text())['rpc_sha256']);(O/'data.json').write_text(json.dumps(data,separators=(',',':')));print('comparison groups',len(groups),'candidate frames',sum(g['frames']*3 for g in groups))

