from pathlib import Path
import zipfile,json,sys,numpy as np
from PIL import Image
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_reviewed_r72 import phase_rows
O=R/'build/graphics/l2_integrate_r119';z=zipfile.ZipFile(R/'convref/rtype-l2-art-assets_v2.zip');j=json.loads(z.read('choices.json'));(O/'selected_choices.json').write_text(json.dumps(j,indent=2));assets=[];pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205)],np.int16)
def add(key,frame,id,original,rotate=0,mirror=False):
 im=Image.open(z.open(f'{key}/frame_{frame:02d}.png')).convert('RGBA')
 if rotate:im=im.rotate(rotate,resample=Image.Resampling.NEAREST,expand=False)
 if mirror:im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
 if rotate or mirror:
  a=np.array(im);rgb=a[:,:,:3].astype(np.float64);inds=((rgb[:,:,None,:]-pal[None,None,:,:])**2).astype(np.int64).sum(3).argmin(2).astype('uint8');inds[a[:,:,3]==0]=0;v=phase_rows(inds,spill=False,normal=True)
 else:v=z.read(f'{key}/frame_{frame:02d}.pairs.bin')
 name=f'{key}_{frame}_{rotate}_{int(mirror)}';(O/(name+'.pairs')).write_bytes(v);im.save(O/(name+'.png'));assets.append(dict(key=key,frame=frame,id=id,original=original,size=list(im.size),rotate=rotate,mirror=mirror,file=name+'.pairs'))
for i,f in enumerate([6,7]):add('scorpion',f,180+i,[32+i])
for i in range(3):add('whitelegs',i,184+i,[]) # cyclicthreeframes, native19/20
for i in range(4):add('walker',i,188+i,[]) # preserveapproved4posecycle
for i in range(2):add('snake',3-i,192+i,[22+i])
for i,(native,f,r)in enumerate([(25,5,0),(26,5,-45),(27,5,-90),(28,4,0),(29,4,-45),(30,4,-90)]):add('snake',f,194+i,[native],rotate=r)
(O/'actor_assets.json').write_text(json.dumps(assets,indent=2));print(len(assets),'frames',sum((O/a['file']).stat().st_size for a in assets))
