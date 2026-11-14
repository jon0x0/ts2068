from pathlib import Path
import sys,json,ast,shutil,numpy as np
from PIL import Image,ImageFilter
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from walker_review_r85 import current,LAY,PAL
from build_graphics import decode_roms,palette_ram
O=R/'build/graphics/walker_runtime_r86';O.mkdir(exist_ok=True);V=R/'build/graphics/walker_review_r85';sp,_=decode_roms();profiles=[];groups=[];assets=[]
tree=ast.parse((R/'scripts/prepare_walkers_rpc_r85.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
roundsheet=Image.open(V/'ai_round_sheet.png').convert('RGBA');roundposes=[]
for k in range(4):
 im=roundsheet.crop((k*roundsheet.width//4,0,(k+1)*roundsheet.width//4,roundsheet.height));roundposes.append(im.crop(im.getbbox()))
exfile=Path('C:/Users/Jon/.codex/generated_images/01a19855-5e8b-7c01-9834-206ac0fda11a/exec-59230a5b-14ef-4316-a8fa-72884518e638.png');shutil.copy2(exfile,O/'exhaust_source.png');ex=Image.open(exfile).convert('RGBA')
pal1=palette_ram(R/'build/fullgame/arcade_reference/frame004200_palette_sprite.bin')[64:80]
def small4(k):
 code=[1570,1572,1574,1572][k];a=np.block([[sp[code],sp[code+8]],[sp[code+1],sp[code+9]]]);im=Image.fromarray(np.concatenate([pal1[a],np.where(a[:,:,None],255,0)],2).astype('uint8')).crop((0,7,32,32))
 if k==3:
  v=np.array(im);legs=v[16:].copy();v[16:]=0;v[16:,:15]=legs[:,1:16];v[16:,17:]=legs[:,16:31];im=Image.fromarray(v)
 return im
def add(n,key,ims,size,original,base,variant='B'):
 groups.append(dict(level=n,key=key,original=original,base=base,count=len(ims),size=size))
 for k,im in enumerate(ims):
  im=fit(im,size);a=np.array(im);mask=(a[:,:,3]>=112)&(a[:,:,:3].max(2)>0);rgb=a[:,:,:3].copy();rgb[~mask]=0;name=f'L{n}_{key}_{k}';(O/f'{name}.rgb').write_bytes(rgb.tobytes());(O/f'{name}.mask').write_bytes(mask.astype('uint8').tobytes());im.save(O/f'{name}_source.png');st=dict(brightness=56,contrast=54,saturation=78,gamma=1.65)if variant=='C'else dict(brightness=49,contrast=65,saturation=78,gamma=1.13);profiles.append(dict(id=name,size=name,w=size[0],h=size[1],bright=True,strategy='segment-coverage',settings=st));assets.append(dict(level=n,key=key,frame=k,id=base+k,name=name,size=size))
for n,walk,raised in[(1,[21,22,23],[24,25]),(4,[14,15,16],[17,18]),(7,[25,26,27],[28,29])]:
 add(n,'small',[material(small4(k))for k in range(4)],(32,24),walk,200)
 # Raising a weapon is separate from walking; keep its two native poses.
 for k,i in enumerate(raised):add(n,f'raise{k}',[Image.open(V/f'L{n}_small_{i}_B_input.png')],(24,24),[i],i)
add(1,'large',[Image.open(R/f'build/graphics/enemy_upgrades_r60/{i}_arcade.png')for i in range(201,205)],(40,40),[43,44,201,202,203,204],204,'C')
for n,ids in[(1,list(range(53,57))),(3,[31,32,33]),(4,list(range(28,32))),(6,list(range(5,9))),(7,[11,12,13])]:add(n,'round',roundposes,(24,24),ids,208,'C')
head=Image.open(R/'build/graphics/l6_assembly_review/head_arcade.gif');hs=[]
for k in range(4):head.seek(k);hs.append(head.convert('RGBA'))
for n,ids,size in[(6,list(range(9,14)),(32,32)),(7,list(range(18,23)),(24,24))]:add(n,'head',hs,size,ids,212)
for ids,size,base in[([101,102,103],(32,16),216),([104,105,106],(32,24),220)]:
 ims=[native_early(3,i)for i in ids];extra=np.array(ims[1]);h,w=extra.shape[:2];split=h*2//3;leg=extra[split:].copy();extra[split:]=0;extra[split:,1:]=leg[:,:-1];ims.append(Image.fromarray(extra));add(3,'ground'+str(size[1]),[material(im)for im in ims],size,ids,base)
add(3,'yellow',[Image.open(V/'ai_yellow_source.png').crop(Image.open(V/'ai_yellow_source.png').getbbox())],(32,16),[94],94,'C')
engine=[]
for k in range(4):
 im=ex.crop((0,k*ex.height//4,ex.width,(k+1)*ex.height//4));im=im.resize((40,16),Image.Resampling.LANCZOS);a=np.array(im);yy,xx=np.indices((16,40));half=7-(xx/39)*4;mask=(np.abs(yy-7.5)<=half)&(a[:,:,3]>120);a[~mask]=0;can=Image.new('RGBA',(48,16));can.alpha_composite(Image.fromarray(a),(0,0));old,_=current(3,34+k%2);v=np.array(old);nozzle=v[:,40:48];rgba=np.concatenate([nozzle,np.where(nozzle.max(2,keepdims=True)>0,255,0).astype('uint8')],2);can.alpha_composite(Image.fromarray(rgba),(40,0));engine.append(can)
add(3,'exhaust',engine,(48,16),[34,35],224,'C')
(O/'inputs.json').write_text(json.dumps(dict(groups=groups,assets=assets,profiles=profiles),indent=2))
s=(R/'scripts/convert_walkers_rpc_r85.mjs').read_text().replace('build/graphics/walker_review_r85','build/graphics/walker_runtime_r86');(R/'scripts/convert_walkers_rpc_r86.mjs').write_text(s);print('runtime assets',len(assets),'groups',len(groups))
