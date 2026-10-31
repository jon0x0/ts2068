"""RAM512 paired-patch layout, extracted unchanged from the tested builder."""
from pathlib import Path
import sys,struct
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor'))
from svd_ecm import ECMFrame,screen_offset
PAD=struct.pack('<HH',0x5800,0)*64

def physical(raw,w,h):
 n=w*h//8;out=[bytearray(6144),bytearray(6144)];x=(256-w)//16;y0=(192-h)//2
 for y in range(h):
  off=screen_offset(y+y0,x)
  for p in range(2):out[p][off:off+w//8]=raw[p*n+y*w//8:p*n+(y+1)*w//8]
 return ECMFrame(bytes(out[0]),bytes(out[1]))

def words(old,new):
 out=bytearray()
 for off in range(0,6144,2):
  for a,b,base in ((old.bitmap,new.bitmap,0x4000),(old.attributes,new.attributes,0x6000)):
   if a[off:off+2]!=b[off:off+2]:out+=struct.pack('<H',base+off)+b[off:off+2]
 if not out:out+=PAD
 while len(out)%256:out+=struct.pack('<HH',0x5800,0)
 return bytes(out)

def pack(fs,packets):
 pages=[bytearray(b'RAMV'+bytes([p,1 if p<2 else 2])+bytes(250)+PAD*31) for p in range(64)]
 pages[0][256:6400]=fs[0].bitmap;pages[1][256:6400]=fs[0].attributes
 page=2;block=0;index=bytearray();meaningful=12288
 for data in packets:
  n=len(data)//256
  if n>93:raise OverflowError('frame exceeds three cache pages')
  if n+block>93 and block:page+=1;block=0
  endpage=page+(block+n-1)//31
  if endpage>=64:raise OverflowError('512 KiB full')
  index+=bytes([page,block])+struct.pack('<H',n)
  for i in range(n):
   pages[page][256+block*256:512+block*256]=data[i*256:(i+1)*256]
   block+=1
   if block==31:page+=1;block=0
  meaningful+=len(data)
 return pages,bytes(index),endpage,meaningful

def tap_block(flag, payload):
    check = flag
    for value in payload:
        check ^= value
    return struct.pack('<H', len(payload)+2)+bytes([flag])+payload+bytes([check])

def code_pair(name, data):
    assert 0 < len(data) <= 16384
    header = bytes([3])+name.encode().ljust(10, b' ')+struct.pack('<HHH', len(data), 0x9000, 0x8000)
    assert len(header) == 17
    return tap_block(0, header)+tap_block(255, data)
