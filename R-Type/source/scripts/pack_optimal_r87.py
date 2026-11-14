"""Optimal packet selection for the existing unchanged Z80 LZ decoder."""
def pack_optimal(raw):
 raw=bytes(raw);n=len(raw);positions={};matches=[(0,0)]*n
 for i in range(n):
  key=raw[i:i+3];best=0;dist=0
  if len(key)==3:
   for p in reversed(positions.get(key,[])[-128:]):
    length=3;limit=min(130,n-i)
    while length<limit and raw[p+length]==raw[i+length]:length+=1
    if length>best:best=length;dist=i-p
    if best==limit:break
   positions.setdefault(key,[]).append(i)
  matches[i]=(best,dist)
 cost=[0]*(n+1);choice=[None]*n
 for i in range(n-1,-1,-1):
  best=10**9;ch=None
  for length in range(1,min(127,n-i)+1):
   c=1+length+cost[i+length]
   if c<best:best=c;ch=(False,length,0)
  maxlen,dist=matches[i]
  for length in range(3,maxlen+1):
   c=3+cost[i+length]
   if c<best:best=c;ch=(True,length,dist)
  cost[i]=best;choice[i]=ch
 out=bytearray();i=0
 while i<n:
  ref,length,dist=choice[i]
  if ref:out.extend([128|(length-3),dist&255,dist>>8])
  else:out.append(length);out.extend(raw[i:i+length])
  i+=length
 out.append(0);return bytes(out)
