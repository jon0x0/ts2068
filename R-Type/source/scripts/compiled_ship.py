"""Compile hot ship and enemy cells into audited HOME5B00-5CFF."""
import json
HOT=(0xa61f,0xa628,0xa631,0xd3ab,0xd3b4,0xd3bd,0xd3c6,0xd3cf,0xd3d9,0xd3e2)
from fullgame_context import FULL
if FULL:HOT=HOT[:3]

def build(root,ram,colours,indices,address_map=None):
 b=bytes(0x4000)+bytes(ram);source=bytes(0x4000)+(root/'build/native/snapshot.bin').read_bytes();by_pointer={};n=0
 for ident in range(1,112):
  d=0xbc67+(ident-1)*4;w,h=source[d:d+2];p=int.from_bytes(source[d+2:d+4],'little')
  for y in range(h):
   for x in range(w):
    a=source[p]
    if FULL and a!=54:assert not 16<=(a&127)<32,'Native common colour collides with retained enemy token'
    by_pointer[p]=indices[n];n+=1;p+=1 if a==54 else 9
 from boss_colours import build as boss_build
 boss_build(root)
 boss={v["pointer"]:v["colours"] for v in json.loads((root/"build/ecm_native/boss_manifest.json").read_text()).get("cells",[])}
 code=bytearray();table=bytearray();rows=[]
 for p in HOT:
  start=0x5b00+len(code);key=address_map.get(p,p) if address_map else p;table+=bytes([key&255])+start.to_bytes(2,'little');a=b[p];assert a!=54
  pixels=bytes((0x55 if y%2==0 else 0xaa)if p<0xc000 and v==255 and not a&0x38 else v for y,v in enumerate(b[p+1:p+9]));attrs=bytes(boss[p]) if p>=0xc000 else colours[by_pointer[p]*8:by_pointer[p]*8+8]
  if p<0xc000 and (a&0x38 or not a&7):attrs=bytes([a&127])*8
  constant=len(set(attrs))==1
  if constant:code+=bytes([0x0e,attrs[0]])
  last=None
  for y in range(8):
   if pixels[y]!=last:code+=bytes([0x3e,pixels[y]]);last=pixels[y]
   code+=bytes([0x12,0x71]) if constant else bytes([0x12,0x36,attrs[y]])
   if y<7:code+=bytes([0x14,0x24])
  code+=bytes.fromhex('c3 80 fb');rows.append(dict(source=p,native_source=key,entry=start,pixels=list(pixels),colours=list(attrs)))
 if FULL:table+=bytes([255,0,0])*7
 assert len(code)<=512,len(code)
 (root/('build/readonly_ecm/compiled_ship.json' if address_map else 'build/ecm_native/compiled_ship.json')).write_text(json.dumps(dict(bytes=len(code),home_range='5B00-5CFF',rows=rows),indent=2))
 return bytes(code)+bytes([255])*(512-len(code)),bytes(table)
