"""Exact L4 horizontal-shift corrections and procedural vertical palettes."""
from copy import deepcopy
from pack_optimal_r87 import pack_optimal
from stock_frame_packets import sparse

def dense(f):
 out=bytearray();p=0
 for pi in f['rows']:
  if pi<0:out+=bytes(8);p+=1
  else:out+=bytes(f['bits'][p+1:p+9]);p+=9
 assert p==len(f['bits']);return bytes(out)

def prepare_old(j):
 oracle=deepcopy(j);vs=j['motion_variants'];lookup={(v['id'],v['anim'],v['px'],v['py'],v['flip']):v['frame']for v in vs};proc=set(lookup.values());parents=sorted({lookup[i,a,x,0,f]for i,a,x,y,f in lookup});ordinary=[f for i,f in enumerate(j['frames'])if i not in proc]
 used=sorted({p for f in ordinary for p in f['rows']if p>=0});assert len(used)<1023
 remap={old:i for i,old in enumerate(used)};hardware=[j['palette'][i]for i in used];pairs=list(dict.fromkeys(tuple(row[k:k+2])for row in hardware for k in range(0,8,2)));
 for fi in parents:
  for pi in j['frames'][fi]['rows']:
   row=j['palette'][pi]if pi>=0 else[7]*8
   for k in range(0,8,2):
    pair=tuple(row[k:k+2])
    if pair not in pairs:pairs.append(pair)
 assert len(pairs)<=256
 bases={};horizontal=[];quads=[]
 for fi in parents:
  key=next(k for k,v in lookup.items()if v==fi and k[3]==0);ident,anim,px,_,flip=key;bf=lookup[ident,anim,0,0,flip];base=j['frames'][bf];target=j['frames'][fi];dx=(8-2*px)%8 if flip&1 else 2*px;src=dense(base);dst=dense(target);shifted=bytearray(len(dst))
  for cy in range(target['h']):
   for cx in range(target['w']):
    for r in range(8):
     a=src[(cy*base['w']+cx)*8+r]if cx<base['w']else 0;b=src[(cy*base['w']+cx-1)*8+r]if 0<=cx-1<base['w']else 0
     shifted[(cy*target['w']+cx)*8+r]=a if not dx else(a>>dx)|(b<<(8-dx)&255)
  patch=sparse(shifted,dst);p=0;restored=bytearray(shifted)
  while int.from_bytes(patch[p:p+2],'little')!=65535:
   at=int.from_bytes(patch[p:p+2],'little');n=patch[p+2];p+=3;restored[at:at+n]=patch[p:p+n];p+=n
  assert bytes(restored)==dst
  bases[bf]=dict(raw=src,packed=pack_optimal(src),w=base['w'],h=base['h'])
  colour=[]
  for pi in target['rows']:
   row=j['palette'][pi]if pi>=0 else[7]*8
   colour += [pairs.index(tuple(row[k:k+2]))for k in range(0,8,2)]
  ids=[]
  for at in range(0,len(colour),4):
   quad=tuple(colour[at:at+4])
   if quad not in quads:quads.append(quad)
   ids.append(quads.index(quad))
  blocks=[];colour_ids=bytes(i&255 for i in ids)+bytes(sum(((ids[q+b]>>8)&1)<<b for b in range(min(8,len(ids)-q)))for q in range(0,len(ids),8))
  horizontal.append(dict(frame=fi,base=bf,w=target['w'],h=target['h'],dx=dx,patch=patch,blocks=blocks,colour_ids=colour_ids))
 descriptors={};parts={ident:n for n,ident in enumerate(sorted({v['id']for v in vs}))};assert len(parts)==3
 static={tuple(row):i for i,row in enumerate(hardware)};frames=sorted(set(lookup.values()));total=sum(sum(pi>=0 for pi in oracle['frames'][fi]['rows'])for fi in frames);budget=max(0,total+len(hardware)-4096)+16;aliases={};left=budget
 for fi in frames:
  f=oracle['frames'][fi];selected=[]
  for cell,pi in enumerate(f['rows']):
   if pi>=0 and tuple(oracle['palette'][pi])in static and left:
    selected.append((cell,static[tuple(oracle['palette'][pi])])) ;left-=1
  aliases[fi]=selected
 assert not left,(budget,left)
 recipes=[];token=len(hardware)
 for fi in frames:
  key=next(k for k,v in lookup.items()if v==fi);ident,anim,px,py,flip=key;f=oracle['frames'][fi];parent=lookup[ident,anim,px,0,flip];dy=(8-2*py)%8 if flip&2 else 2*py;alias=dict(aliases[fi]);mask=bytes(sum((1<<b)if q+b<len(f['rows'])and f['rows'][q+b]>=0 else 0 for b in range(8))for q in range(0,len(f['rows']),8));body=bytes(sum((1<<b)if q+b<len(f['rows'])and f['rows'][q+b]>=0 and q+b not in alias else 0 for b in range(8))for q in range(0,len(f['rows']),8));n=sum(p>=0 for p in f['rows']);count=n-len(alias);assert 0<count<256
  payload=mask+(body if alias else b'');spec=bytes([parents.index(parent),dy,f['w'],f['h'],n])+token.to_bytes(2,'little')+bytes([len(alias),len(payload)])+payload+bytes(v for cell,pi in aliases[fi]for v in(cell,pi));descriptors[fi]=spec;recipes.append(dict(frame=fi,base=token,count=count));token+=count
 assert token<=4096
 for fi,f in enumerate(j['frames']):
  if fi not in proc:f['rows']=[remap[p]if p>=0 else -1 for p in f['rows']]
 j['palette']=hardware
 maximum=max(3+2*(sum(p>=0 for p in f['rows'])+(sum(p>=0 for p in f['rows'])>54))+len(f['bits'])for i,f in enumerate(oracle['frames'])if i in proc)
 empty=tuple([pairs.index((7,7))]*4)
 if empty not in quads:quads.append(empty)
 used=sorted({i for quad in quads for i in quad});assert len(used)<=128
 order=used+[i for i in range(len(pairs))if i not in used];remap={old:new for new,old in enumerate(order)};pairs=[pairs[i]for i in order];quads=[tuple(remap[i]for i in quad)for quad in quads];empty=tuple(remap[i]for i in empty)
 return dict(recipes=recipes,static_rows=len(hardware),token_count=token,empty_quad=quads.index(empty),oracle=oracle,quads=b''.join(bytes(q)for q in quads),hardware=hardware,pairs=pairs,bases=bases,parents=horizontal,descriptors=descriptors,frames=proc,max_cache=maximum,max_dense=max(x['w']*x['h']*8 for x in horizontal),parts=parts)


def prepare(j):
 """Permanent IDs encode adjacent source quads and their 2-raster phase.
 Common recipes imply their lower quad; exceptions store both 9-bit IDs.
 No frame generation, mutable palette pool or mask search is needed on read.
 """
 p=prepare_old(j);oracle=p['oracle'];quads=p['quads'];recipes=[];maps=[]
 for parent in p['parents']:
  n=parent['w']*parent['h'];raw=parent['colour_ids'];parent['quad_ids']=[raw[i]|((raw[n+i//8]>>(i%8)&1)<<8)for i in range(n)]
 for lo in range(len(quads)//4):
  choices=[]
  for parent in p['parents']:
   ids=parent['quad_ids'];w=parent['w']
   choices += [ids[i-w]if i>=w else p['empty_quad']for i,v in enumerate(ids)if v==lo]
  recipes.append((choices[0]if choices else p['empty_quad'],lo))
 for parent in p['parents']:
  n=parent['w']*parent['h'];ids=parent['quad_ids'];mapped=[]
  for y in range(parent['h']+1):
   for x in range(parent['w']):
    lo=ids[y*parent['w']+x]if y<parent['h']else p['empty_quad'];hi=ids[(y-1)*parent['w']+x]if y else p['empty_quad'];key=(hi,lo)
    if key not in recipes:recipes.append(key)
    mapped.append(recipes.index(key))
  parent['colour_ids']=bytes(v&255 for v in mapped)+bytes(sum(((mapped[q+b]>>8)&3)<<(2*b)for b in range(min(4,len(mapped)-q)))for q in range(0,len(mapped),4))
 assert len(recipes)<=960
 lookup={(v['id'],v['anim'],v['px'],v['py'],v['flip']):v['frame']for v in j['motion_variants']};parents=[v['frame']for v in p['parents']];descriptors={}
 for fi in p['frames']:
  key=next(k for k,v in lookup.items()if v==fi);ident,anim,px,py,flip=key;f=oracle['frames'][fi];parent=lookup[ident,anim,px,0,flip];assert f['w']==p['parents'][parents.index(parent)]['w'] and f['h']<=p['parents'][parents.index(parent)]['h']+1;dy=(8-2*py)%8 if flip&2 else 2*py;mask=bytes(sum((1<<b)if q+b<len(f['rows'])and f['rows'][q+b]>=0 else 0 for b in range(8))for q in range(0,len(f['rows']),8));descriptors[fi]=bytes([parents.index(parent),dy,f['w'],f['h'],sum(pi>=0 for pi in f['rows'])])+mask
 packed=bytearray();defaults=len(quads)//4
 word=sum(hi<<(9*i)for i,(hi,lo)in enumerate(recipes[:defaults]));packed+=word.to_bytes((9*defaults+7)//8,'little');extra_offset=len(packed)
 for q in range(defaults,len(recipes),4):
  group=recipes[q:q+4];word=sum((hi|(lo<<9))<<(18*b)for b,(hi,lo)in enumerate(group));packed+=word.to_bytes((18*len(group)+7)//8,'little')
 packed+=bytes(3)
 def attrs(q):return [a for pair in quads[q*4:q*4+4]for a in p['pairs'][pair]]
 p.update(codec='adjacent-quads-v2',recipes=[dict(upper=attrs(hi),lower=attrs(lo))for hi,lo in recipes],recipe_data=bytes(packed),recipe_defaults=defaults,recipe_extra_offset=extra_offset,descriptors=descriptors,token_count=256+4*len(recipes))
 return p
