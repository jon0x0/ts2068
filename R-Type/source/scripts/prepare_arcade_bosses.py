"""Fit genuine arcade boss art into safe native frames and per-cell ECM rows."""
from pathlib import Path
import sys,json,collections,shutil,os
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import arcade_boss_sources as sources_module
from build_graphics import decode_roms,palette_ram,fit_pairs,quantize,PALETTE

def features(row):
 a=np.frombuffer(row,dtype='uint8');bright=np.where(a&64,8,0);p=PALETTE[((a>>3)&7)+bright].astype(float);q=PALETTE[(a&7)+bright].astype(float);return np.concatenate([p,q],axis=1).reshape(-1)
def prepare(source,w,h,style,cell_mask=None):
 rgba=np.asarray(source.resize((w*8,h*8),Image.Resampling.LANCZOS)).copy()
 if cell_mask is not None:
  for cy,cx in cell_mask:rgba[cy*8:cy*8+8,cx*8:cx*8+8]=0
 rgb=rgba[:,:,:3].astype(float)
 if style=='chroma':
  luma=(rgb*np.array([.2126,.7152,.0722])).sum(2,keepdims=True);rgb=np.clip(luma+2.8*(rgb-luma),0,255)
 rgb[rgba[:,:,3]<96]=0;rgb=rgb.astype('uint8');pairs=fit_pairs(rgb.astype(float));edge=fit_pairs(rgb.astype(float),black=True);holes=(rgb.max(2)==0).reshape(h*8,w,8).any(2);pairs[holes]=edge[holes];_,attrs,_=quantize(Image.fromarray(rgb),pairs=pairs)
 return rgba,rgb,attrs
def main(style):
 sprites,_=decode_roms();sources_module.SPRITES=sprites;sources=sources_module.build_sources();levels=json.loads((ROOT/'build/fullgame/foundation/manifest.json').read_text())['levels'];out=ROOT/f'build/fullgame/converted/{style}';out.mkdir(parents=True,exist_ok=True);gallery=Image.new('RGB',(768,8*180));draw=ImageDraw.Draw(gallery)
 for layout in levels:
  n=layout['level'];folder=out/f'level{n:02d}';folder.mkdir(exist_ok=True);mem=bytes(16384)+(ROOT/f'build/fullgame/foundation/level{n:02d}.raw').read_bytes();raw=bytearray(mem[0xc4ce:0xf87c]);descs={v['id']:dict(v)for v in layout['enemies']};before={};rows=[bytes([(i&7)|(64 if i&8 else 0)])*8 for i in range(16)]
  for desc in descs.values():
   p=desc['pointer']
   for cy in range(desc['height']):
    for cx in range(desc['width']):
     a=mem[p]
     if a==54:p+=1;continue
     before[p]=a;row=bytes([a&127])*8
     if row not in rows:rows.append(row)
     p+=9
  start=((0xc4ae+layout['payload_bytes']+15)//16)*16;pool_ids=set(sources[n])if n in(5,6,8)else{50}if n==7 else set();prepared={};dimensions={i:(descs[i]['width'],descs[i]['height'])for i in sources[n]};pool_end=start
  if n==7:dimensions[50]=(9,3)
  if n==8:
   for i in sources[n]:dimensions[i]=(6,6)
  def calculate_pool():
   total=0
   for ident in sorted(pool_ids):
    w,h=dimensions[ident];rgba,rgb,a=prepare(sources[n][ident],w,h,style)
    for cy in range(h):
     for cx in range(w):total+=9 if rgb[cy*8:cy*8+8,cx*8:cx*8+8].any()else 1
   return total
  if n==8 and start+calculate_pool()>0xf87c:
   for i in sources[n]:dimensions[i]=(6,4)
  assert not pool_ids or start+calculate_pool()<=0xf87c,(n,hex(start),calculate_pool())
  targets=[];flags={};recorded={};orb=[]
  for ident,source in sources[n].items():
   d=descs[ident];w,h=dimensions[ident];original_p=d['pointer'];mask=[]
   if ident not in pool_ids:
    p=original_p
    for cy in range(h):
     for cx in range(w):
      if mem[p]==54:mask.append((cy,cx));p+=1
      else:p+=9
   rgba,rgb,attrs=prepare(source,w,h,style,mask if ident not in pool_ids else None);source.save(folder/f'descriptor{ident:03d}_arcade.png')
   if ident in pool_ids:
    d.update(pointer=pool_end,width=w,height=h);p=pool_end
    table=layout['enemy_descriptors_start']+(ident-1)*4-0xc4ce;raw[table:table+4]=bytes([w,h])+p.to_bytes(2,'little')
   else:p=original_p
   recorded[ident]=[]
   for cy in range(h):
    for cx in range(w):
     if ident in pool_ids:
      if not rgb[cy*8:cy*8+8,cx*8:cx*8+8].any():raw[p-0xc4ce]=54;p+=1;continue
      flag=0
     else:
      if mem[p]==54:p+=1;continue
      flag=mem[p]&128
     row=bytes(attrs[cy*8:cy*8+8,cx]);crop=rgb[cy*8:cy*8+8,cx*8:cx*8+8];targets.append((p,row,crop));flags[p]=flag;recorded[ident].append(p);p+=9
   if ident in pool_ids:pool_end=p
  if n==1:
   pal=palette_ram(ROOT/'build/arcade_boss_capture_invuln/frame9600_palette_sprite.bin')[80:96]
   for frame,code in enumerate([0x175,0x176,0x177]):
    idx=sprites[code];rgba=np.concatenate([pal[idx],np.where(idx[:,:,None]!=0,255,0).astype('uint8')],axis=2);_,rgb,attrs=prepare(Image.fromarray(rgba,'RGBA'),2,2,style)
    for cy in range(2):
     for cx in range(2):orb.append((frame,cy,cx,bytes(attrs[cy*8:cy*8+8,cx]),rgb[cy*8:cy*8+8,cx*8:cx*8+8]))
  patterns=[v[1]for v in targets]+[v[3]for v in orb];counts=collections.Counter(patterns);unique=list(counts);feat=np.array([features(v)for v in unique]);selected=[];distance=np.full(len(unique),np.inf)
  for _ in range(min(127-len(rows),len(unique))):
   j=max(range(len(unique)),key=lambda i:counts[unique[i]])if not selected else int(np.argmax(distance*np.sqrt(np.array([counts[v]for v in unique]))));selected.append(j);distance=np.minimum(distance,((feat-feat[j])**2).sum(1));distance[selected]=-1
  for j in selected:
   if unique[j]not in rows:rows.append(unique[j])
  ids=[i for i in range(128)if i!=54][:len(rows)];dictionary=bytearray(1024)
  for ident,row in zip(ids,rows):dictionary[ident*8:ident*8+8]=row
  all_features=np.array([features(v)for v in rows]);paper_black=np.array([[(a>>3)&7==0 for a in row]for row in rows]);row_index={v:ids[i]for i,v in enumerate(rows)}
  def encode(row,crop):
   transparent=(crop.max(2)==0).any(1);safe=paper_black[:,transparent].all(1);cost=((all_features-features(row))**2).sum(1);cost[~safe]=np.inf;index=int(np.argmin(cost));ident=ids[index];a=np.frombuffer(rows[index],dtype='uint8');br=np.where(a&64,8,0);paper=PALETTE[((a>>3)&7)+br].astype(float);ink=PALETTE[(a&7)+br].astype(float);rgb=crop.astype(float);bits=(((rgb-ink[:,None])**2).sum(2)<((rgb-paper[:,None])**2).sum(2)).astype('uint8');assert not bits[crop.max(2)==0].any();return ident,np.packbits(bits,axis=1).tobytes()
  for p,a in before.items():raw[p-0xc4ce]=(a&128)|row_index[bytes([a&127])*8]
  for p,row,crop in targets:
   tag,pixels=encode(row,crop);raw[p-0xc4ce]=flags[p]|tag;raw[p+1-0xc4ce:p+9-0xc4ce]=pixels
  if orb:
   frames=[bytearray(36)for _ in range(3)]
   for frame,cy,cx,row,crop in orb:
    tag,pixels=encode(row,crop);p=(cy*2+cx)*9;frames[frame][p:p+9]=bytes([tag])+pixels
   (folder/'orb_frames.bin').write_bytes(b''.join(frames));raw[0xd550-0xc4ce:0xd574-0xc4ce]=frames[0]
  (folder/'enemy_graphics.bin').write_bytes(raw);(folder/'enemy_palette.bin').write_bytes(dictionary)
  manifest=dict(level=n,style=style,converted_descriptors=sorted(recorded),converted_source_cells=len(set(p for cells in recorded.values()for p in cells)),palette_rows=len(rows),dictionary_bytes=1024,enemy_lookup_end=max(layout['enemy_descriptors_start'],pool_end if pool_ids else 0),pool_start=start if pool_ids else None,pool_end=pool_end if pool_ids else None,enlarged_or_expanded_descriptors=sorted(pool_ids),descriptors=[descs[i]for i in sorted(recorded)],native_geometry='Unexpanded frames retain native transparent cells; selected frames use checked free payload space and updated descriptor pointers/dimensions. Original movement scripts and remaining pointers are unchanged.',source='Verified original arcade graphics ROMs, composited sprite RAM and captured tile-layer boss scenes. Independent8x1 palettes; edge rows keep black paper.',background_boss_pending=n==2)
  (folder/'manifest.json').write_text(json.dumps(manifest,indent=2));main_id={1:8,2:3,3:41,4:27,5:8,6:18,7:50,8:42}[n];desc=descs[main_id]
  if n==3:reference=Image.open(ROOT/'build/fullgame/arcade_objects/giant_ship_panorama.png').crop((0,45,570,215));native=Image.new('RGB',(368,104));drawing=[descs[i]for i in range(41,87)]
  else:reference=sources[n][main_id];native=Image.new('RGB',(desc['width']*8,desc['height']*8));drawing=[desc]
  for j,d in enumerate(drawing):
   p=d['pointer']
   for cy in range(d['height']):
    for cx in range(d['width']):
     a=raw[p-0xc4ce]
     if a==54:p+=1;continue
     attrs=np.frombuffer(dictionary[(a&127)*8:(a&127)*8+8],dtype='uint8');br=np.where(attrs&64,8,0);paper=((attrs>>3)&7)+br;ink=(attrs&7)+br;bits=np.unpackbits(np.frombuffer(raw[p+1-0xc4ce:p+9-0xc4ce],dtype='uint8')).reshape(8,8);rgb=PALETTE[np.where(bits,ink[:,None],paper[:,None])].astype('uint8');native.paste(Image.fromarray(rgb),((j if n==3 else cx)*8,cy*8));p+=9
  ref=reference.convert('RGB');ref.thumbnail((370,150),Image.Resampling.NEAREST);native.thumbnail((370,150),Image.Resampling.NEAREST);y=(n-1)*180;draw.text((4,y+2),f'LEVEL{n} ARCADE',fill='white');draw.text((388,y+2),f'ECM {style.upper()}',fill='white');gallery.paste(ref,(4,y+20));gallery.paste(native,(388,y+20));print(n,style,'cells',manifest['converted_source_cells'],'rows',len(rows),'pool',manifest['pool_start'],manifest['pool_end'],flush=True)
 gallery.save(out/'boss_conversion_gallery.png')
if __name__=='__main__':
 for style in ['preserve','chroma']:main(style)
 out=ROOT/'build/fullgame/converted'
 for n in range(1,9):shutil.copytree(out/f'chroma/level{n:02d}',out/f'level{n:02d}',dirs_exist_ok=True)
 shutil.copy2(out/'chroma/boss_conversion_gallery.png',out/'boss_conversion_gallery.png')

 if __name__=="__main__":
  from convert_gomander import build
  build()
