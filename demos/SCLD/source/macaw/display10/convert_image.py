"""Image/compiler co-design: ten 14T candidate writes; optional profitable updates."""
from pathlib import Path
import argparse,json,struct,zlib
import numpy as np
from PIL import Image,ImageOps
from palette_fit import PALETTE,PAL,PAIRS,ATTR,DUAL,linear,row,pair_errors as segment_errors
ROOT=Path(__file__).resolve().parent
COLUMNS=np.array([0,3,7,10,14,17,21,24,28,31])
SPLITS=np.array([2,6]*5)
def pair_errors(pixels):
 # Reward real intermediate palette levels as well as dithered mixtures.
 # Segment-only fitting assigns identical scores to many two/four-level ramps.
 distances=((pixels[...,None,:]-PAL)**2).sum(axis=-1)
 nearest=np.minimum(distances[...,PAIRS[:,0]],distances[...,PAIRS[:,1]]).sum(axis=-2)
 return .85*segment_errors(pixels)+.15*nearest

def pair_fit(pixels):
 errors=pair_errors(pixels);idx=errors.argmin(axis=-1)
 return idx,np.take_along_axis(errors,idx[...,None],axis=-1)[...,0]

FANS={
 'floyd':[(1,0,7/16),(-1,1,3/16),(0,1,5/16),(1,1,1/16)],
 'sierra-lite':[(1,0,1/2),(-1,1,1/4),(0,1,1/4)],
 'sierra2':[(1,0,4/16),(2,0,3/16),(-2,1,1/16),(-1,1,2/16),(0,1,3/16),(1,1,2/16),(2,1,1/16)],
 # Experimental line-only Sierra-inspired diffusion. No same-row feedback.
 'line-sierra':[(-1,1,1/4),(0,1,1/2),(1,1,1/4)],
}

def exterior(selected):
 groups=[]
 for y in range(192):
  ids=np.flatnonzero(selected[y])[2:]
  if len(ids):groups.append((y,[int(i) for i in ids]))
 return groups

def pack(selected):
 """Fit row-grouped fast restores into the two measured blanking windows."""
 groups=exterior(selected);before=[];after=[];bt=at=0
 for y,ids in sorted(groups,key=lambda g:-(17*len(g[1])+3)):
  cost=17*len(ids)+3
  if bt+cost<=8750:before.append((y,ids));bt+=cost
  elif at+cost<=6720:after.append((y,ids));at+=cost
  else:return None
 return dict(before=sorted(before),after=sorted(after),beforeT=bt,afterT=at)

def row_pool(cells,allowed):
 base,errors=pair_fit(cells);left=np.empty(10);right=np.empty((10,len(PAIRS)))
 for i,(c,cut) in enumerate(zip(COLUMNS,SPLITS)):
  _,left[i]=pair_fit(cells[c,:cut]);right[i]=pair_errors(cells[c,cut:])
 benefits=np.maximum(0,errors[COLUMNS,None]-left[:,None]-right)*allowed[:,None]
 pool=[]
 for k in range(4):
  current=benefits[:,pool].max(axis=1) if pool else np.zeros(10)
  scores=np.maximum(current[:,None],benefits).sum(axis=0)
  if pool:scores[pool]=-1
  pool.append(int(scores.argmax()))
 for repeat in range(3):
  changed=False
  for k in range(4):
   others=pool[:k]+pool[k+1:];current=benefits[:,others].max(axis=1)
   scores=np.maximum(current[:,None],benefits).sum(axis=0);scores[others]=-1
   candidate=int(scores.argmax())
   if scores[candidate]>scores[pool[k]]+1e-12:pool[k]=candidate;changed=True
  if not changed:break
 return pool

def adaptive_quantize(rgb,method,strength,allowed):
 """Choose each cell's pairs after incoming diffusion error is known."""
 work=rgb.copy();bits=np.zeros((192,256),np.uint8);indices=np.empty_like(bits)
 p0=np.empty((192,32),int);p1=np.empty_like(p0)
 selected=np.zeros((192,10),bool);gain=np.zeros((192,10))
 lookup={int(c):i for i,c in enumerate(COLUMNS)}
 for y in range(192):
  pool=row_pool(np.clip(work[y],0,1).reshape(32,8,3),allowed[y]) if allowed[y].any() else [0]
  direction=-1 if (y&1) and method in FANS else 1
  for c in (range(31,-1,-1) if direction<0 else range(32)):
   target=np.clip(work[y,c*8:c*8+8],0,1)
   base,base_error=pair_fit(target)
   a=b=int(base);split=8;i=lookup.get(c)
   if i is not None and allowed[y,i]:
    cut=int(SPLITS[i]);aa,ae=pair_fit(target[:cut]);errors=pair_errors(target[cut:]);bb=pool[int(errors[pool].argmin())];be=errors[bb]
    improvement=float(base_error-ae-be)
    if improvement>1e-9 and aa!=bb:
     a,b,split=int(aa),int(bb),cut;selected[y,i]=True;gain[y,i]=improvement
   p0[y,c]=a;p1[y,c]=b
   for bit in (range(7,-1,-1) if direction<0 else range(8)):
    x=c*8+bit;ink,paper=PAIRS[a if bit<split else b];value=np.clip(work[y,x],0,1)
    if method=='bayer':
     matrix=((0,8,2,10),(12,4,14,6),(3,11,1,9),(15,7,13,5));delta=PAL[ink]-PAL[paper]
     blend=float((value-PAL[paper])@delta)/max(float(delta@delta),1e-20)
     on=blend>.5+strength*((matrix[y%4][x%4]+.5)/16-.5)
    else:on=((value-PAL[ink])**2).sum()<((value-PAL[paper])**2).sum()
    color=ink if on else paper;bits[y,x]=on;indices[y,x]=color
    error=(value-PAL[color])*strength
    for dx,dy,weight in FANS.get(method,[]):
     xx=x+direction*dx;yy=y+dy
     if method=='line-sierra' and x in (0,255):weight=.5
     if 0<=xx<256 and yy<192:work[yy,xx]+=error*weight
 bitmap=bytearray(6144);attrs=bytearray(6144)
 for y in range(192):
  for c in range(32):
   k=row(y)+c;bitmap[k]=sum(128>>b for b in range(8) if bits[y,8*c+b]);attrs[k]=int(ATTR[p0[y,c]])
 return p0,p1,selected,gain,bitmap,attrs,indices

def convert(source,method='sierra-lite',strength=1.,out=ROOT):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 image=ImageOps.fit(Image.open(source).convert('RGB'),(256,192),Image.Resampling.LANCZOS)
 rgb=linear(np.asarray(image).astype(float)/255)
 allowed=np.ones((192,10),bool);original_count=None;passes=0
 while True:
  p0,p1,selected,gain,bitmap,attrs,indices=adaptive_quantize(rgb,method,strength,allowed)
  passes+=1
  if original_count is None:original_count=int(selected.sum())
  packing=pack(selected)
  if packing is not None:break
  reduced=selected.copy()
  while pack(reduced) is None:
   candidates=[(gain[y,i],y,i) for y in range(192) if reduced[y].sum()>2 for i in np.flatnonzero(reduced[y])]
   _,y,i=min(candidates);reduced[y,i]=False;allowed[y,i]=False
 left=p0[:,COLUMNS];new=p1[:,COLUMNS];trimmed=int((~allowed).sum())
 dynamic_result=(bitmap,attrs,indices)
 results={}
 for name in ['ecm','dynamic']:
  if name=='dynamic':bitmap,attrs,indices=dynamic_result
  else:_,_,_,_,bitmap,attrs,indices=adaptive_quantize(rgb,method,strength,np.zeros_like(allowed))
  (out/(name+'-bitmap.bin')).write_bytes(bitmap);(out/(name+'-attributes.bin')).write_bytes(attrs)
  np.save(out/(name+'-indices.npy'),indices)
  Image.fromarray(PALETTE[indices]).resize((768,576),Image.Resampling.NEAREST).save(out/(name+'-preview.png'))
  results[name]=indices
 schedule=[]
 for y in range(192):
  ids=np.flatnonzero(selected[y]);schedule.append(dict(columns=[int(COLUMNS[i]) for i in ids],splits=[int(SPLITS[i]) for i in ids],slots=[int(i) for i in ids],old=[int(ATTR[left[y,i]]) for i in ids],new=[int(ATTR[new[y,i]]) for i in ids]))
 (out/'schedule.json').write_text(json.dumps(schedule,indent=2));(out/'restore-plan.json').write_text(json.dumps(packing,indent=2))
 meta=dict(profile='adaptive-10',version=4,width=256,height=192,candidateColumns=COLUMNS.tolist(),candidateSplits=SPLITS.tolist(),dither=method,strength=strength,schedule=schedule)
 records=json.dumps(meta,separators=(',',':')).encode()
 payload=(out/'dynamic-bitmap.bin').read_bytes()+(out/'dynamic-attributes.bin').read_bytes()+records
 (out/'image.tdec').write_bytes(struct.pack('<4sB3xIIII',b'TDEC',4,6144,6144,len(records),zlib.crc32(payload))+payload)
 def avg(v):return v.reshape(96,2,128,2,3).mean(axis=(1,3))
 mse={n:float(((avg(PAL[idx])-avg(rgb))**2).mean()) for n,idx in results.items()}
 counts=[len(s['columns']) for s in schedule]
 actual4=[sum(len(set(results['dynamic'][y,c*8:c*8+8]))>2 for c in s['columns']) for y,s in enumerate(schedule)]
 report=dict(source=Path(source).name,dither=method,strength=strength,candidateWritesPerRow=10,actualWrites=int(selected.sum()),maxWritesPerRow=max(counts),rowsWithNineOrTenWrites=sum(n>=9 for n in counts),writeCountHistogram={str(n):counts.count(n) for n in sorted(set(counts))},cellsWithMoreThanTwoColors=sum(actual4),maxMulticolorCellsPerRow=max(actual4),untrimmedWrites=original_count,budgetTrimmed=trimmed,averaged2x2LinearRgbMse=mse,relativeAveragedMseReduction=1-mse['dynamic']/mse['ecm'],restoreTiming=packing,hardwareVerified=False)
 # Keep the compact metrics separate from the detailed restore plan.
 report['restoreTiming']={k:packing[k] for k in ('beforeT','afterT')}
 (out/'conversion.json').write_text(json.dumps(report,indent=2));image.save(out/'scaled-input.png');print(json.dumps(report))
 return report

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('--dither',choices=[*FANS,'bayer','none'],default='sierra-lite');p.add_argument('--strength',type=float,default=1);p.add_argument('--out',default=str(ROOT));a=p.parse_args();convert(a.source,a.dither,a.strength,a.out)
