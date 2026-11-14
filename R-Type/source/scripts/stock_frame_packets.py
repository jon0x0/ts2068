"""Bounded ROM frame packets: ordinary LZ bases plus sparse overwrite deltas."""
from pack_optimal_r87 import pack_optimal
from boss_motion_assets_r60 import unpack

def sparse(base,target):
 assert len(base)>=len(target)
 changed=[i for i,(a,b)in enumerate(zip(base,target))if a!=b];out=bytearray();p=0
 while p<len(changed):
  start=changed[p];end=start+1;p+=1
  while p<len(changed)and changed[p]-end<=3 and changed[p]-start<255:end=changed[p]+1;p+=1
  out+=start.to_bytes(2,'little')+bytes([end-start])+target[start:end]
 out+=b'\xff\xff';return bytes(out)

def frame_packets(raws,shapes):
 packets=[None]*len(raws);bases=[];saved=0
 for i in sorted(range(len(raws)),key=lambda i:len(raws[i]),reverse=True):
  packed=pack_optimal(raws[i]);best=(len(packed),None,packed)
  for k in bases:
   if shapes[k]!=shapes[i]or len(raws[k])<len(raws[i]):continue
   delta=bytes([k])+sparse(raws[k],raws[i])
   if len(delta)<best[0]:best=(len(delta),k,delta)
  size,base,data=best
  if base is None:bases.append(i)
  else:saved+=len(packed)-size
  packets[i]=dict(base=base,data=data)
 # Validate every final packet against its actual raw frame before ROM linking.
 # Delta bases must be full frames; offsets are bounded by the target size.
 for i,p in enumerate(packets):
  if p['base'] is None:
   restored=unpack(p['data'])
  else:
   k=p['base'];assert packets[k]['base'] is None and p['data'][0]==k
   restored=bytearray(unpack(packets[k]['data']));pos=1;end=0
   while True:
    assert pos+2<=len(p['data'])
    at=int.from_bytes(p['data'][pos:pos+2],'little');pos+=2
    if at==65535:break
    assert pos<len(p['data']);length=p['data'][pos];pos+=1
    assert length and at>=end and at+length<=len(raws[i])
    assert pos+length<=len(p['data'])
    restored[at:at+length]=p['data'][pos:pos+length];pos+=length;end=at+length
   assert pos==len(p['data'])
   restored=restored[:len(raws[i])]
  assert bytes(restored)==raws[i],('Frame packet roundtrip',i)
 return packets,saved
