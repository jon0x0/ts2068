"""Measure bounded shared RePair grammar for exact L4 frame bytes."""
from pathlib import Path
import collections,json,time
from pack_optimal_r87 import pack_optimal
O=Path('build/cartridges/integration_work/level04');j=json.loads((O/'combined_frames.json').read_text());m=json.loads((O.parent/'L4_tap_motion_frames.json').read_text());pmap=[];fmap=[]
for row in m['palette']:
 row=[a&~64 if a&64 and(not a&7 or not a&56)else a for a in row]
 if row not in j['palette']:j['palette'].append(row)
 pmap.append(j['palette'].index(row))
for f in m['frames']:
 f=dict(f,rows=[pmap[p]if p>=0 else -1 for p in f['rows']]);found=next((i for i,g in enumerate(j['frames'])if all(f[k]==g[k]for k in ('w','h','bits','rows'))),None)
 if found is None:found=len(j['frames']);j['frames'].append(f)
 fmap.append(found)
zero={(v['id'],v['flip']):fmap[v['frame']]for v in m['variants']if not v['px']and not v['py']}
for v in j['variants']:
 if(v['id'],v['flip'])in zero:v['frame']=zero[v['id'],v['flip']]
used={v['frame']for v in j['variants']+j['common_variants']if v['frame']>=0}|set(fmap);j['frames']=[j['frames'][i]for i in sorted(used)]
seq=[]
for f in j['frames']:
 local=sorted(set(f['rows'])-{-1});mapping={pi:i+(i>=54)for i,pi in enumerate(local)};local=local[:54]+([0]+local[54:]if len(local)>54 else []);native=bytearray(f['bits']);offset=0
 for pi in f['rows']:
  if pi<0:offset+=1
  else:native[offset]=mapping[pi];offset+=9
 seq.append(list(bytes([f['w'],f['h'],len(local)])+b''.join(pi.to_bytes(2,'little')for pi in local)+native))
pairs=[];depth=[0]*256;length=[1]*256;started=time.monotonic()
for rule in range(4096):
 counts=collections.Counter()
 for row in seq:counts.update(zip(row,row[1:]))
 candidates=counts.most_common(64);candidate=next(((pair,count)for pair,count in candidates if count>=4 and 1+max(depth[pair[0]],depth[pair[1]])<=22),None)
 if candidate is None:break
 pair,count=candidate;new=[];subs=0
 for row in seq:
  out=[];i=0
  while i<len(row):
   if i+1<len(row)and(row[i],row[i+1])==pair:out.append(256+len(pairs));i+=2;subs+=1
   else:out.append(row[i]);i+=1
  new.append(out)
 if subs<3:break
 seq=new;pairs.append(pair);depth.append(1+max(depth[pair[0]],depth[pair[1]]));length.append(length[pair[0]]+length[pair[1]])
 if rule%128==0:print(rule,'bytes',len(pairs)*4+sum(map(len,seq))*2,'depth',max(depth),'seconds',round(time.monotonic()-started,1),flush=True)
root_packets=[pack_optimal(b''.join(i.to_bytes(2,'little')for i in row))for row in seq];print('Hybrid root LZ',sum(map(len,root_packets)),'dictionary12bit',len(pairs)*3,'max roots',max(2*len(row)for row in seq),flush=True)
record=dict(pairs=pairs,streams=seq,root_lz_bytes=sum(map(len,root_packets)),dictionary_packed_bytes=len(pairs)*3,max_root_bytes=max(2*len(row)for row in seq),depth=max(depth),bytes=len(pairs)*4+sum(map(len,seq))*2+len(seq)*4,scope='Global exact frame grammar storage estimate; not a Z80 runtime or performance result')
(O/'motion_grammar_estimate.json').write_text(json.dumps(record));print({k:v for k,v in record.items()if k not in ('pairs','streams')},flush=True)
