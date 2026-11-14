from pathlib import Path
import json,math,sys,numpy as np
sys.path.insert(0,str(Path.cwd()/'scripts'));from boss_motion_assets_r60 import unpack
from PIL import Image
R=Path.cwd();O=R/'build/graphics/arcade_rpc_comparison_r68';O.mkdir(exist_ok=True)
layouts=json.loads((R/'build/fullgame/foundation/manifest.json').read_text())['levels'];inv=json.loads((R/'build/graphics/arcade_rpc_inventory_r67/inventory.json').read_text());records=[];profiles=[]
pal=np.array([[0,0,0],[1,0,206],[207,1,0],[207,1,206],[0,207,21],[1,207,207],[207,207,21],[207,207,207],[0,0,0],[2,0,253],[255,2,1],[255,2,253],[0,255,28],[2,255,255],[255,255,29],[255,255,255]],np.uint8)
def current(n,i):
 b=(R/f'build/fullgame/l2_rpc_r67/level{n:02d}_region.bin').read_bytes();
 if n!=5:
  records=json.loads((R/'build/fullgame/force_loading_r62/generic_manifest.json').read_text());extra=json.loads((R/'build/fullgame/startup_r66/generic_manifest.json').read_text());records=[v for v in records if v['level']not in[vv['level']for vv in extra]]+extra
  for at in range(0xe350,0xe3f0,11):
   if b[at]==0:break
   if b[at]!=i:continue
   w=b[at+1]&0x6f;h=b[at+2]*8;ptr=int.from_bytes(b[at+3:at+5],'little')
   if ptr>=0xc000:
    cache=b[0xdc50:0xdf50];off=cache.find(bytes.fromhex('dd21'),0x200);assert off>=0
    tab=int.from_bytes(cache[off+2:off+4],'little');target=ptr;raw=None;needed=(w+(0 if b[at+1]&128 else 1))*h*2
    for k in range(b[tab]):
     source=int.from_bytes(b[tab+1+k*4:tab+3+k*4],'little');dest=int.from_bytes(b[tab+3+k*4:tab+5+k*4],'little');block=unpack(b[source:])
     if dest<=target and target+needed<=dest+len(block):raw=block[target-dest:target-dest+needed];break
    assert raw is not None,target
   else:raw=unpack(b[ptr:])
   cols=len(raw)//(h*2);assert len(raw)%(h*2)==0 and cols in[w,w+1],(len(raw),w,h)
   a=np.zeros((h,cols*8),np.uint8)
   for x in range(cols):
    for y in range(h):
     bits,t=raw[(x*h+y)*2:(x*h+y)*2+2];bank=8 if t&64 else 0
     for k in range(8):a[y,x*8+k]=((t&7)if bits&(128>>k)else(t>>3)&7)+bank
   return Image.fromarray(pal[a[:,:w*8]]),'Compiled phase0 from r67 cache'
 if n==5 and i==8:return Image.open(R/'build/graphics/bellmite_complete_preview/selected_core.png').convert('RGB'),'Accepted packed96x96 machinery core'
 m=bytes(0xc000)+b[0xa000:0xe000];at=layouts[n-1]['enemy_descriptors_start']+(i-1)*4;w,h=m[at:at+2];ptr=int.from_bytes(m[at+2:at+4],'little');a=np.zeros((h*8,w*8),np.uint8);p=ptr
 for y in range(h):
  for x in range(w):
   t=m[p];p+=1
   if t==54:continue
   for yy in range(8):
    v=b[0x2000+(t&127)*8+yy];bank=8 if v&64 else 0
    for xx in range(8):a[y*8+yy,x*8+xx]=((v&7)if m[p+yy]&(128>>xx)else(v>>3)&7)+bank
   p+=8
 return Image.fromarray(pal[a]),'r67 stored native source'
def add(n,i,source,size,status,key=None):
 key=key or f'L{n}_{i:03d}';source.save(O/f'{key}_source.png');rec={'level':n,'descriptor':i,'key':key,'status':status,'size':list(size),'profiles':[]}
 try:im,kind=current(n,i);rec['current_kind']=kind;im.save(O/f'{key}_stored.png');rec['stored_size']=list(im.size)
 except Exception as e:rec['stored_error']=str(e)
 for label,scale in [('N',1),('D',1.3)]:
  w=math.ceil(size[0]*scale/8)*8;h=math.ceil(size[1]*scale/8)*8;im=source.copy();im.thumbnail((round(size[0]*scale),round(size[1]*scale)),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',(w,h));canvas.alpha_composite(im,((w-im.width)//2,(h-im.height)//2));v=np.array(canvas);mask=(v[:,:,3]>=112)&(v[:,:,:3].max(2)>0);rgb=np.round(v[:,:,:3].astype(float)*v[:,:,3:4]/255).astype('uint8');rgb[~mask]=0;id=key+'_'+label;canvas.save(O/f'{id}_scaled.png');(O/f'{id}.rgb').write_bytes(rgb.tobytes());(O/f'{id}.mask').write_bytes(mask.astype('uint8').tobytes());profiles.append(dict(id=id,size=id,w=w,h=h,bright=True,strategy='segment-coverage'));rec['profiles'].append({'id':id,'label':label,'size':[w,h]})
 records.append(rec)
for level in inv['levels']:
 n=level['level'];meta=json.loads((R/f'build/fullgame/converted/level{n:02d}/manifest.json').read_text());ds={d['id']:d for d in layouts[n-1]['enemies']};ds.update({d['id']:d for d in meta['descriptors']})
 for item in level['items']:
  i=item['descriptor'];d=ds[i];size=(max(8,d['width']*8),max(8,d['height']*8));status='Historical source; identity/assembly needs review'
  if n==6:status='HISTORICAL L6 MATCH: some source identities withdrawn; do not approve by number alone'
  if n==2:status='Historical L2 neck-containing crop; corrected isolated source is shown separately'
  add(n,i,Image.open(R/item['source']).convert('RGBA'),size,status)
for i in[3,4]:add(2,i,Image.open(R/f'build/graphics/l2_actors_r67/H{i}_source.png').convert('RGBA'),(40,40),'Corrected isolated arcade head; r67 uses this source',f'L2_{i:03d}_corrected')
add(2,41,Image.open(R/'build/graphics/l2_rpc_settings/larger_source.png').convert('RGBA'),(192,104),'Accepted L2 complete body source; terrain assembly, not native actor41','L2_body')
for k,src in enumerate(['arcade_pair_320_324.png','arcade_pair_1476_336.png','arcade_pair_1488_340.png']):add(6,14,Image.open(R/'build/graphics/l6_assembly_review'/src).convert('RGBA'),(64,48),'Corrected paired arcade machinery; complete assembly, not a drop-in moving piston',f'L6_assembly{k}')
im=Image.open(R/'build/graphics/l6_assembly_review/head_arcade.gif')
for k in range(im.n_frames):
 im.seek(k);add(6,9+k,im.convert('RGBA'),(32,32),'Corrected arcade head family9-13; compare with accepted darker gray art',f'L6_head{k}')
(O/'inputs.json').write_text(json.dumps({'records':records,'profiles':profiles},indent=2),encoding='utf-8')
s=(R/'scripts/convert_l2_actors_r67.mjs').read_text().replace('build/graphics/l2_actors_r67','build/graphics/arcade_rpc_comparison_r68');a=s.index('const profiles=');z=s.index('const reports=',a);s=s[:a]+"const profiles=JSON.parse(fs.readFileSync(path.join(out,'inputs.json'),'utf8')).profiles;\n"+s[z:];s=s.replace('reports.push({...p,settings:',"console.log('Converted',p.id,p.w,p.h);reports.push({...p,settings:");(R/'scripts/convert_arcade_rpc_r68.mjs').write_text(s,encoding='utf-8');print(len(records),'comparisons',len(profiles),'profiles')
