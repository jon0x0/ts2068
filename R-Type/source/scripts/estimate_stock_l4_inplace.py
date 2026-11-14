"""Measure exact L4 metadata with procedural pixel reconstruction."""
from pathlib import Path
import json
from pack_optimal_r87 import pack_optimal
from stock_frame_packets import frame_packets
prefix=Path('scripts/estimate_stock_l4_grammar.py').read_text().split('seq=[]',1)[0];exec(prefix)
# Prefix keeps frame set but not a remap; identify normalized source frames again.
def find(f):return next(i for i,g in enumerate(j['frames'])if all(f[k]==g[k]for k in ('w','h','bits','rows')))
mi={}
for v in m['variants']:
 f=m['frames'][v['frame']];f=dict(f,rows=[pmap[p]if p>=0 else -1 for p in f['rows']]);mi[v['id'],v['anim'],v['px'],v['py'],v['flip']]=find(f)
used=sorted({pi for f in j['frames']for pi in f['rows']if pi>=0});pm={old:i for i,old in enumerate(used)};j['palette']=[j['palette'][i]for i in used]
for f in j['frames']:f['rows']=[pm[p]if p>=0 else -1 for p in f['rows']]

parents=sorted({mi[i,a,x,0,f]for i,a,x,y,f in mi});used={pi for k in parents for pi in j['frames'][k]['rows']if pi>=0}
from stock_frame_packets import frame_packets
ordinary=[f for i,f in enumerate(j['frames'])if i not in set(mi.values())]
used|={pi for f in ordinary for pi in f['rows']if pi>=0}
bitmap=maskbytes=0;details=[]
for i in parents:
 f=j['frames'][i];dense=bytearray();off=0
 for pi in f['rows']:
  if pi<0:dense+=bytes(8);off+=1
  else:dense+=bytes(f['bits'][off+1:off+9]);off+=9
 packed=pack_optimal(dense);bitmap+=len(packed);details.append((f['w'],f['h'],len(dense),len(packed)))
for key,fi in mi.items():
 if key[3]==0:continue
 f=j['frames'][fi];mask=bytes(sum((1<<(k&7))if p>=0 else 0 for k,p in enumerate(f['rows'][q:q+8]))for q in range(0,len(f['rows']),8));maskbytes+=len(pack_optimal(mask))+3
print(dict(bitmap_packets=bitmap,parent_palette_maps=sum(len(j['frames'][i]['rows'])*2 for i in parents),static_palette_patterns=len(used),procedural_descriptor_bytes=maskbytes,parents=details))

def pixels(f):
 out=[[(0,0,7)for x in range(f['w']*8)]for y in range(f['h']*8)];p=0
 for cell,pi in enumerate(f['rows']):
  tag=f['bits'][p];p+=1
  if pi<0:continue
  bb=f['bits'][p:p+8];p+=8
  for y,b in enumerate(bb):
   a=j['palette'][pi][y]
   for x in range(8):out[(cell//f['w'])*8+y][(cell%f['w'])*8+x]=((a&7)if b&(128>>x)else(a>>3)&7,int(bool(b&(128>>x))),a)
 return out
lut={};conflicts=[];checks=0
for key,fi in mi.items():
 ident,anim,px,py,flip=key
 if py:continue
 base=mi[ident,anim,0,0,flip];b=pixels(j['frames'][base]);t=pixels(j['frames'][fi]);dx=(8-2*px)%8 if flip&1 else 2*px
 for y,row in enumerate(t):
  for x,(c,bit,a)in enumerate(row):
   source=b[y][x-dx][0]if 0<=x-dx<len(b[0])and y<len(b)else 0
   if a&7==a>>3&7:continue
   k=(a&63)*8+source
   if k in lut and lut[k]!=bit:conflicts.append((key,x,y,k,lut[k],bit))
   else:lut[k]=bit
   checks+=1
print('quantizer',dict(keys=len(lut),checks=checks,conflicts=len(conflicts),first=conflicts[:3]))

patterns=[];maps=[];errors=0
for i in parents:
 key=next(k for k,v in mi.items()if v==i and k[3]==0);ident,anim,px,py,flip=key;base=mi[ident,anim,0,0,flip];f=j['frames'][i];bp=pixels(j['frames'][base]);tp=pixels(f);bw=j['frames'][base]['w'];dx=(8-2*px)%8 if flip&1 else 2*px;mapping=[]
 for cell in range(f['w']*f['h']):
  cx=cell%f['w'];cy=cell//f['w'];codes=[]
  for y in range(8):
   ty=cy*8+y;a=tp[ty][cx*8][2];mapped=[];original=[]
   for sx in (cx-1,cx):
    bb=out=0
    for x in range(8):
     c,bit,sa=bp[ty][sx*8+x]if 0<=sx<bw and ty<len(bp)else(0,0,7);bb|=bit<<(7-x);out|=lut.get((a&63)*8+c,0)<<(7-x)
    allowed=[mode for mode,value in((2,bb),(3,bb^255),(0,0),(1,255))if value==out];assert allowed
    mapped.append(allowed[0]);original.append(bb)
   code=mapped[1]|(mapped[0]<<2);codes.append(code)
   values=[original[0],original[1]]
   for x,mode in enumerate(mapped):values[x]=(0 if mode==0 else 255 if mode==1 else values[x]if mode==2 else values[x]^255)
   result=values[1]if not dx else(values[1]>>dx)|(values[0]<<(8-dx)&255)
   actual=sum(tp[ty][cx*8+x][1]<<(7-x)for x in range(8))
   # Equal ink/paper has no visible bit distinction.
   if a&7!=a>>3&7 and result!=actual:errors+=1
  raw=bytes(codes[y]|codes[y+1]<<4 for y in range(0,8,2))
  if raw not in patterns:patterns.append(raw)
  mapping.append(patterns.index(raw))
 maps.append(mapping)
print('mapping-code factor',dict(patterns=len(patterns),pattern_bytes=len(patterns)*4,index_cells=sum(map(len,maps)),extra_index_bits=max(0,(len(patterns)-1).bit_length()-6),bitmap_exact_errors=errors))

# Prove a backward constructor can reuse the decoded base bitmap storage.
# All source reads for a row occur before its output byte is written; tags and
# local palette headers are published only after the bitmap pass finishes.
from collections import Counter
inplace=[]
for key,fi in sorted(mi.items()):
 ident,anim,px,py,flip=key;f=j['frames'][fi];bf=j['frames'][mi[ident,anim,0,0,flip]];bw=bf['w'];bh=bf['h'];dx=(8-2*px)%8 if flip&1 else 2*px;dy=(8-2*py)%8 if flip&2 else 2*py
 local=len(set(f['rows'])-{-1});header=3+2*(local+(local>54));at=header;operations=[]
 for cell,pi in enumerate(f['rows']):
  if pi<0:at+=1;continue
  cx=cell%f['w'];cy=cell//f['w']
  for y in range(8):
   sy=cy*8+y-dy;reads=[]
   for sx in ([cx-1,cx]if dx else[cx]):
    if 0<=sx<bw and 0<=sy<bh*8:reads.append(((sy//8)*bw+sx)*8+sy%8)
   operations.append((at+1+y,reads))
  at+=9
 for pad in range(2048):
  pending=Counter(a for _,reads in operations for a in reads);safe=True
  for write,reads in reversed(operations):
   for a in reads:pending[a]-=1
   if pending[write+pad]:safe=False;break
  if safe:break
 else:raise AssertionError('No bounded in-place schedule')
 inplace.append(dict(frame=fi,key=list(key),padding=pad,output=at,scratch=max(bw*bh*8,at+pad)))
unique={x['frame']:x for x in inplace};result=dict(passed=errors==0 and not conflicts,scope='Offline exact pixel reconstruction and read-before-write dependency proof; no runtime implementation or timing claim',mapping_patterns=len(patterns),mapping_bytes=len(patterns)*4,palette_map_cells=sum(map(len,maps)),mapping_extra_bits=max(0,(len(patterns)-1).bit_length()-6),pixel_errors=errors,quantizer_conflicts=len(conflicts),unique_frames=len(unique),maximum_padding=max(x['padding']for x in inplace),maximum_scratch=max(x['scratch']for x in inplace),frames=list(unique.values()))
out=Path('build/cartridges/integration_work/l4_inplace_feasibility.json');out.write_text(json.dumps(result,indent=2));print('in-place proof', {k:v for k,v in result.items()if k!='frames'})

# Alternative: native shifts followed by bounded sparse byte corrections.
# This avoids per-pixel colour quantization in the runtime constructor.
corrections=[]
from stock_frame_packets import sparse
for i in parents:
 key=next(k for k,v in mi.items()if v==i and k[3]==0);ident,anim,px,py,flip=key;base=mi[ident,anim,0,0,flip];f=j['frames'][i];bf=j['frames'][base];bp=pixels(bf);tp=pixels(f);dx=(8-2*px)%8 if flip&1 else 2*px;before=bytearray();after=bytearray()
 for cell,pi in enumerate(f['rows']):
  cx=cell%f['w'];cy=cell//f['w']
  for y in range(8):
   row=cy*8+y;v=0;t=0
   for x in range(8):
    sx=cx*8+x-dx
    if 0<=sx<len(bp[0])and row<len(bp):v|=bp[row][sx][1]<<(7-x)
    t|=tp[row][cx*8+x][1]<<(7-x)
   before.append(v);after.append(t)
 patch=sparse(before,after)
 corrections.append(dict(frame=i,base=base,dx=dx,bytes=len(patch),changed=sum(a!=b for a,b in zip(before,after)),lz=len(pack_optimal(bytes(a^b for a,b in zip(before,after))))))
print('shift corrections',corrections,'total',sum(x['bytes']for x in corrections),'xor_lz',sum(x['lz']for x in corrections))
