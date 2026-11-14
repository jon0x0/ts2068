from pathlib import Path
import json,sys,collections,shutil,hashlib,re,subprocess
import numpy as np
from PIL import Image
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import pack,unpack
B=R/'build/fullgame/l2_rpc_r67';O=R/'build/fullgame/reviewed_r72';O.mkdir(exist_ok=True);(O/'rtype').mkdir(exist_ok=True)
LAY=json.loads((R/'build/fullgame/foundation/manifest.json').read_text())['levels'];REV=json.loads((R/'build/graphics/current_size_choices_r71/manifest.json').read_text());HOLD=set(json.loads((R/'src/art_review_holds.json').read_text(encoding='utf-8'))['entries']);EDITS={n:{e['descriptor']:e for e in REV['records']if e['level']==n and not e['heldForEvaluation'] and e['key']not in HOLD}for n in range(1,9)}
PAL=np.array([[0,0,0],[1,0,206],[207,1,0],[207,1,206],[0,207,21],[1,207,207],[207,207,21],[207,207,207],[0,0,0],[2,0,253],[255,2,1],[255,2,253],[0,255,28],[2,255,255],[255,255,29],[255,255,255]],float)
def asset(e):
 w,h=e['outputDimensions'];a=np.frombuffer((R/f'build/graphics/current_size_choices_r71/{e["key"]}.indices').read_bytes(),np.uint8).reshape(h,w);attr=np.frombuffer((R/f'build/graphics/current_size_choices_r71/{e["key"]}.attrs').read_bytes(),np.uint8).reshape(h,w//8);return a,attr

def frames(b,n):
 mem=bytes(0xc000)+b[0xa000:0xe000];ds=[]
 for i in range(1,LAY[n-1]['enemy_descriptors']+1):
  at=LAY[n-1]['enemy_descriptors_start']+(i-1)*4;w,h=mem[at:at+2];p=int.from_bytes(mem[at+2:at+4],'little');start=p;cells=[]
  for _ in range(w*h):
   t=mem[p];size=1 if t==54 else 9;cells.append((p,t,mem[p:p+size]));p+=size
  ds.append(dict(id=i,w=w,h=h,at=at,ptr=start,end=p,raw=mem[start:p],cells=cells))
 return ds

def fit(block,key):
 aa=np.frombuffer(key,np.uint8);p=((aa>>3)&7)+((aa>>6)&1)*8;q=(aa&7)+((aa>>6)&1)*8;black=block==0;colour=PAL[block];dp=((colour-PAL[p][:,None])**2).sum(2);dq=((colour-PAL[q][:,None])**2).sum(2);bits=dq<dp
 if any(black[y].any()and p[y]!=0 and q[y]!=0 for y in range(8)):return None
 if any((~black[y]).any()and p[y]==0 and q[y]==0 for y in range(8)):return None
 bits[black]=np.broadcast_to((q==0)&(p!=0),block.shape)[black];bits[(~black)&(p[:,None]==0)]=True;bits[(~black)&(q[:,None]==0)]=False;out=np.where(bits,q[:,None],p[:,None]);return float(((PAL[out]-colour)**2).sum()),bits,out

def native(b,n):
 original=bytes(b);ds=frames(b,n);selected=EDITS[n];used=set(range(16));rows={i:original[0x2000+i*8:0x2008+i*8]for i in range(128)}
 for d in ds:
  if d['id']not in selected:used.update(t&127 for p,t,raw in d['cells']if t!=54)
 free=sorted(set(range(128))-used-{54});priority=collections.Counter();native_images={};masked_pixels={}
 for d in ds:
  if d['id']not in selected:continue
  im,attrs=asset(selected[d['id']]);im=im.copy();lost=0
  if n==3:
   for index,(ptr,tag,raw)in enumerate(d['cells']):
    if tag==54:
     cy,cx=divmod(index,d['w']);block=im[cy*8:cy*8+8,cx*8:cx*8+8];lost+=int((block!=0).sum());block[:]=0
  native_images[d['id']]=(im,attrs);masked_pixels[d['id']]=lost
 for i,e in selected.items():
  im,attrs=native_images[i]
  for y in range(0,im.shape[0],8):
   for x in range(im.shape[1]//8):
    if (im[y:y+8,x*8:x*8+8]!=0).any():priority[attrs[y:y+8,x].tobytes()]+=1
 existing=set(rows.values());new=[k for k,c in priority.most_common()if k not in existing]
 for i,k in zip(free,new):rows[i]=k;b[0x2000+i*8:0x2008+i*8]=k
 pool={}
 for i,k in rows.items():
  if i!=54:pool.setdefault(k,i)
 report=[];replacements={}
 for i,e in selected.items():
  im,attrs=native_images[i];out=np.zeros_like(im);raw=bytearray();approx=0
  for y in range(0,im.shape[0],8):
   for x in range(im.shape[1]//8):
    block=im[y:y+8,x*8:x*8+8];key=attrs[y:y+8,x].tobytes()
    if not(block!=0).any():raw.append(54);continue
    best=None
    for k,t in ([(key,pool[key])]if key in pool else pool.items()):
     f=fit(block,k)
     if f is not None and(best is None or f[0]<best[0]):best=(*f,t)
    assert best is not None,(n,i,y,x)
    score,bits,a,t=best;raw.append(t);raw.extend(np.packbits(bits,axis=1).tobytes());out[y:y+8,x*8:x*8+8]=a;approx+=score>0
  replacements[i]=bytes(raw);Image.fromarray(PAL[out].astype('uint8')).save(O/f'L{n}_{i:03d}_installed.png');report.append({'id':i,'bytes':len(raw),'existing_transparent_cell_mask_pixels':masked_pixels[i],'approximate_cells':int(approx),'mean_RGB_error':float(np.abs(PAL[out]-PAL[im]).mean())})
 assert n in[1,3]
 for d in ds:
  if d['id']in replacements:
   raw=replacements[d['id']];assert len(raw)<=len(d['raw']),(n,d['id'],len(raw),len(d['raw']));b[d['ptr']-0x2000:d['ptr']-0x2000+len(raw)]=raw
 for d in ds:
  if d['id']in selected or(n==3 and d['id']>=101):continue
  new=frames(b,n)[d['id']-1];assert new['raw']==d['raw'],('unselected native art changed',n,d['id'])
 return {'level':n,'palette_added':min(len(free),len([k for k in priority if k not in existing])),'native_frames':report}

def phase_rows(im,shift=0,spill=True,normal=False):
 if normal:im=im&7
 h,w=im.shape;dst=np.zeros((h,w+(8 if spill else 0)),np.uint8);dst[:,shift:shift+w]=im;raw=bytearray();pairs=[(0,q)for q in range(1,8)]+[(p,q)for bank in[0,8]for p in range(1+bank,8+bank)for q in range(p+1,8+bank)]
 for x in range(dst.shape[1]//8):
  for y in range(h):
   row=dst[y,x*8:x*8+8];cs=sorted(set(map(int,row)));colour=PAL[row]
   if len(cs)<=2 and (cs[0]>=8)==(cs[-1]>=8):
    p,q=cs[0],cs[-1];bits=row==q if p!=q else np.zeros(8,bool)
   else:
    options=[pair for pair in pairs if 0 not in cs or pair[0]==0];p,q=min(options,key=lambda pair:np.minimum(((colour-PAL[pair[0]])**2).sum(1),((colour-PAL[pair[1]])**2).sum(1)).sum());bits=((colour-PAL[q])**2).sum(1)<((colour-PAL[p])**2).sum(1)
    if p==0:bits[row!=0]=True
   assert (p>=8)==(q>=8) or p==0 and q<8
   a=(p&7)*8+(q&7)+(64 if p>=8 else 0);raw.extend([sum(128>>k for k in range(8)if bits[k]),a])
 return bytes(raw)

def cached(b,n):
 original=bytes(b);code=original[0xdc50:0xdf50];off=code.find(bytes.fromhex('dd21'),0x200);assert off>=0;table=int.from_bytes(code[off+2:off+4],'little');expanded=bytearray(6144);used=0
 for k in range(original[table]):
  p=int.from_bytes(original[table+1+k*4:table+3+k*4],'little');d=int.from_bytes(original[table+3+k*4:table+5+k*4],'little')-0xc000;raw=unpack(original[p:]);expanded[d:d+len(raw)]=raw;used=max(used,d+len(raw))
 targets={};report=[];selected=EDITS[n]
 for at in range(0xe350,0xe3f0,11):
  ident=original[at]
  if ident==0:break
  if ident not in selected:continue
  im,_=asset(selected[ident]);h,w=im.shape;assert [w//8,h//8]==[original[at+1]&0x6f,original[at+2]];locked=bool(original[at+1]&128)
  for phase in range(4):
   raw=phase_rows(im,0 if locked or n==4 else phase*2,spill=not locked,normal=n==4);dest=int.from_bytes(original[at+3+phase*2:at+5+phase*2],'little')
   if dest in targets:assert targets[dest]==raw,('alias mismatch',n,ident,phase)
   targets[dest]=raw;expanded[dest-0xc000:dest-0xc000+len(raw)]=raw
  report.append({'id':ident,'size':[w,h],'normal_bank_for_native_L4_synthesis':n==4})
 assert used<=6144
 # Keep every untouched cached row byte-identical at its original destination.
 before=bytearray(6144)
 for k in range(original[table]):
  p=int.from_bytes(original[table+1+k*4:table+3+k*4],'little');d=int.from_bytes(original[table+3+k*4:table+5+k*4],'little')-0xc000;raw=unpack(original[p:]);before[d:d+len(raw)]=raw
 allowed=set()
 for p,raw in targets.items():allowed.update(range(p-0xc000,p-0xc000+len(raw)))
 assert all(a==c or i in allowed for i,(a,c)in enumerate(zip(before,expanded)))
 start=0x2800 if n==4 else 0x2400
 blocks=[]
 if n==4:
  # Native25/26/27 are always handled by the compiled cache. Their old immutable
  # source bytes can hold a preload packet; A9C7 remains visible in map6F and
  # lies beyond the A000 motion-code overlay. No untouched actor shares it.
  split=0x700;external=pack(expanded[:split]);assert len(external)<=0xd30c-0xc9c7
  b[0xa9c7:0xa9c7+len(external)]=external;blocks.append((0xa9c7,0xc000));compressed=pack(expanded[split:used]);blocks.append((start,0xc000+split))
 else:compressed=pack(expanded[:used]);blocks.append((start,0xc000))
 metas=json.loads((R/'build/fullgame/force_loading_r62/generic_manifest.json').read_text())+json.loads((R/'build/fullgame/startup_r66/generic_manifest.json').read_text());meta=[r for r in metas if r['level']==n][-1];motion=original[meta['motion_ptr']:meta['motion_ptr']+meta['motion_image_bytes']]
 backup=b'';backup_ptr=meta['backup_ptr'];new_backup=0
 if backup_ptr:
  p=backup_ptr
  while original[p]:
   c=original[p];p+=1;p+=c if c<128 else 2
  backup=original[backup_ptr:p+1];assert unpack(backup)==bytes.fromhex(meta['backup'])
  # Repacked backup must restore the SAME native HOME bytes after a restart.
  start_native=meta['plan_start']-0x2000;assert unpack(backup)==original[start_native:start_native+len(unpack(backup))]
  new_backup=start+len(compressed);pattern=bytes([0x21])+backup_ptr.to_bytes(2,'little');assert motion.count(pattern)==1;motion=motion.replace(pattern,bytes([0x21])+new_backup.to_bytes(2,'little'))
 newtable=start+len(compressed)+len(backup);newmotion=(newtable+1+4*len(blocks)+15)&~15;assert newmotion+len(motion)<=0x3a00,(n,len(compressed),len(backup),hex(newmotion+len(motion)))
 b[start:0x3a00]=bytes(0x3a00-start);b[start:start+len(compressed)]=compressed;b[start+len(compressed):start+len(compressed)+len(backup)]=backup;tablebytes=bytes([len(blocks)])+b''.join(p.to_bytes(2,'little')+d.to_bytes(2,'little')for p,d in blocks);b[newtable:newtable+len(tablebytes)]=tablebytes;b[newmotion:newmotion+len(motion)]=motion
 b[0xdc50+off+2:0xdc50+off+4]=newtable.to_bytes(2,'little');p=b.find(bytes.fromhex('21')+meta['motion_ptr'].to_bytes(2,'little'),0xdedb,0xdef0);assert p>=0;b[p+1:p+3]=newmotion.to_bytes(2,'little')
 for suffix,values in [('cache',{'PRELOAD_TABLE':newtable,'MOTION_PTR':newmotion}),('motion',{'BACKUP_PTR':new_backup})]:
  stem=f'L{n}_{suffix}';p=O/(stem+'.asm')
  if p.exists():
   text=p.read_text(encoding='utf-8-sig')
   for key,value in values.items():text=re.sub(rf'({key} EQU \$)[0-9a-fA-F]+',lambda m:m[1]+f'{value:04X}',text)
   p.write_text(text,encoding='utf-8')
  p=O/(stem+'.sym')
  if p.exists():
   text=p.read_text(encoding='utf-8-sig')
   for key,value in values.items():text=re.sub(rf'({key}: EQU 0x)[0-9a-fA-F]+',lambda m:m[1]+f'{value:08X}',text)
   p.write_text(text,encoding='utf-8')
  p=O/(stem+'.bin')
  if p.exists():p.write_bytes(bytes(b[0xdc50:0xdc50+p.stat().st_size])if suffix=='cache'else motion[:p.stat().st_size])
 return {'level':n,'cached_frames':report,'raw_bytes':used,'compressed_bytes':len(compressed)+(len(external)if n==4 else 0),'preload_blocks':blocks,'preload_table':newtable,'backup_ptr':new_backup,'backup_bytes':len(backup),'motion_ptr':newmotion,'source_end':newmotion+len(motion)}

def body2(b):
 original=bytes(b);a=R/'build/graphics/l2_reviewed_r72';j=json.loads((a/'manifest.json').read_text(encoding='utf-8'));data=(a/'body_tiles.lz').read_bytes();assert len(data)<=2160;b[0xb442:0xbcb2]=data.ljust(2160,b'\0');b[0xc762+56*5:0xc762+64*5]=(a/'map_patch.bin').read_bytes();palette=(a/'palette.bin').read_bytes();assert len(palette)==111*8;b[0x2000:0x2378]=palette
 # Preserve every old weak-point row exactly, remapping only its palette ID.
 keys={original[0x2000+i*8:0x2008+i*8]:i for i in range(16)};extras=[];sources=[]
 for p in range(0xaeae,0xaeae+432,9):
  tag=original[p];key=original[0x2000+(tag&127)*8:0x2008+(tag&127)*8]
  if key not in keys:
   keys[key]=111+len(extras);extras.append(key)
  sources.append((p,key,tag))
 assert len(extras)==17
 for i,key in enumerate(extras):b[0x2378+i*8:0x2380+i*8]=key
 for p,key,tag in sources:b[p]=(tag&128)|keys[key];assert b[p+1:p+9]==original[p+1:p+9]
 def asm(name,text):
  p=O/(name+'.asm');p.write_text(text,encoding='utf-8');q=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr;return p.with_suffix('.bin').read_bytes(),{k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)}
 sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(B/'palette_lookup.sym').read_text(),re.I)};text=(R/'src/l2_tile_expand_r67.asm').read_text(encoding='utf-8');text=re.sub(r'tile_table:\n        DW [^\n]+','tile_table:\n        DW '+','.join('$%04X'%t['pointer']for t in j['tiles']),text);helper,hs=asm('L2_tile_expand',f'KEEP_TOKEN EQU ${sy["keep_dictionary_token"]:04X}\n'+text);oldsy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(B/'tile_expand.sym').read_text(),re.I)}
 for k in['install','get_tile','restore_trailer']:assert hs[k]==oldsy[k]
 b[0x3848:0x3848+len(helper)]=helper;assert original[0x2400:0x3285]==b[0x2400:0x3285],'Held L2 head cache changed'
 return {'level':2,'body':j,'mouth_colour_patterns_preserved':True,'held_head_cache_unchanged':True}

if __name__=='__main__':
 for p in B.iterdir():
  if p.is_file()and p.suffix in['.bin','.asm','.sym','.json']:shutil.copy2(p,O/p.name)
 for p in(B/'rtype').iterdir():
  if p.is_file():shutil.copy2(p,O/'rtype'/p.name)
 reports=[]
 for n in[1,3]:
  b=bytearray((B/f'level{n:02d}_region.bin').read_bytes());reports.append(native(b,n));(O/f'level{n:02d}_region.bin').write_bytes(b)
 for n in[4,6,8]:
  b=bytearray((B/f'level{n:02d}_region.bin').read_bytes());reports.append(cached(b,n));(O/f'level{n:02d}_region.bin').write_bytes(b)
 if any(e['key']=='L2_body'for e in EDITS[2].values()):
  b=bytearray((B/'level02_region.bin').read_bytes());reports.append(body2(b));(O/'level02_region.bin').write_bytes(b)
 from build_rocket_fix import code
 for n in range(1,9):
  b=(O/f'level{n:02d}_region.bin').read_bytes();(O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)));(O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+t*1024:p*8192+(t+1)*1024],k)for k,(p,t)in enumerate((p,t)for p in[0,1,4,5,6,7]for t in range(8))))
 metas=json.loads((R/'build/fullgame/force_loading_r62/generic_manifest.json').read_text())+json.loads((R/'build/fullgame/startup_r66/generic_manifest.json').read_text());metadata={r['level']:r for r in metas}
 for report in reports:
  if 'motion_ptr'in report:
   meta=metadata[report['level']];meta['motion_ptr']=report['motion_ptr'];meta['cache_symbols']['MOTION_PTR']=report['motion_ptr'];meta['cache_symbols']['PRELOAD_TABLE']=report['preload_table'];meta['preload_blocks']=report['preload_blocks'];meta['backup_ptr']=report['backup_ptr'];meta['backup']=bytes((O/f'level{report["level"]:02d}_region.bin').read_bytes()[meta['plan_start']-0x2000:meta['plan_end']-0x2000]).hex();meta['legacy_individual_phase_ptrs_superseded']=True
 (O/'generic_manifest.json').write_text(json.dumps(list(metadata.values()),indent=2))
 (O/'native_art_report.json').write_text(json.dumps(reports,indent=2));print(reports)
