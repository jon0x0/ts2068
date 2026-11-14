"""Normal-black publication overlay; never normalize encoded palette IDs."""
from pathlib import Path
import json,hashlib,zipfile,struct,re
ROOT=Path(__file__).resolve().parents[1]
def normal(a):
 return a&~64 if a&64 and (a&7==0 or (a>>3)&7==0) else a
def change(data,level,runtime=False):
 b=bytearray(data);folder=ROOT/f'build/fullgame/level{level:02d}';before=bytes(b)
 def attrs(a,z):b[a:z]=bytes(normal(v)for v in b[a:z])
 for a,z in [(0xe000,0xe400),(0x1b20,0x1e20),(0xdbd0,0xdc50),(0x9600,0x9c00)]:attrs(a,z)
 if runtime:attrs(0x2000,0x2400)
 # Decode-only renderer masks, preserving all source/token arithmetic.
 symbols={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9a-fA-F]+)',(folder/'renderer.sym').read_text())}
 for start,stop in [('hud_cell','hud_unchanged'),('mirror_attributes','paint_tile'),('paint_flat','paint_finish')]:
  a,z=symbols[start],symbols[stop];code=bytes(b[a:z]);assert code.count(bytes.fromhex('e6 7f'))==1
  b[a:z]=code.replace(bytes.fromhex('e6 7f'),bytes.fromhex('e6 3f'))
 a,z=symbols['full_retained_attribute'],symbols['full_retained_variable'];code=bytes(b[a:z]);assert code.count(bytes.fromhex('f6 40'))==1;b[a:z]=code.replace(bytes.fromhex('f6 40'),bytes.fromhex('f6 00'))
 a,z=symbols['restore_empty_cell'],symbols['restore_colour_done'];b[a:z]=bytes(b[a:z]).replace(bytes.fromhex('e6 47'),bytes.fromhex('e6 07')).replace(bytes.fromhex('3e 47'),bytes.fromhex('3e 07'))
 for a,z in [(0xf20,0xf80),(0xc00,0xd00),(0xdc80,0xdd20)]:
  code=bytes(b[a:z]).replace(bytes.fromhex('3e 47'),bytes.fromhex('3e 07')).replace(bytes.fromhex('3e 45'),bytes.fromhex('3e 05')).replace(bytes.fromhex('36 47'),bytes.fromhex('36 07'));b[a:z]=code
 assert b[0xe05:0xe07]==bytes.fromhex('30 06');b[0xe06]=0x11
 b[0xe18:0xe1d]=bytes.fromhex('e6 3f c3 0d 0e')
 assert b[0xe47]==0x30
 old_target=0xe49+b[0xe48];b[0xe48]=(0xe20-0xe49)&255
 b[0xe20:0xe25]=bytes.fromhex('e6 3f c3')+old_target.to_bytes(2,'little')
 # True native common sprite attributes; no level enemy source IDs touched.
 mem=bytes(16384)+(folder/'snapshot.bin').read_bytes()
 for ident in range(111):
  d=0xbc67+ident*4;w,h=mem[d:d+2];p=int.from_bytes(mem[d+2:d+4],'little')
  for _ in range(w*h):
   a=mem[p]
   if a==54:p+=1;continue
   assert 0x8000<=p<0xc000
   b[p-0x4000]=normal(b[p-0x4000]);p+=9
 layout=json.loads((ROOT/'build/fullgame/foundation/manifest.json').read_text())['levels'][level-1]
 for p in range(layout['terrain_start'],layout['map_start'],9):
  at=p-0x2000
  if not b[at]&128:b[at]=normal(b[at])
 # Compiler emits a small documented instruction vocabulary in the ship cache.
 meta=json.loads((folder/'compiled_ship.json').read_text())
 for row in meta['rows']:
  p=0xfb00+row['entry']-0x5b00
  while True:
   op=b[p]
   if op in (14,54):b[p+1]=normal(b[p+1]);p+=2
   elif op==62:p+=2
   elif op in (18,113,20,36):p+=1
   elif op==195:assert b[p+1:p+3]==bytes.fromhex('80 fb');break
   else:raise AssertionError((hex(p),op))
 assert len(b)==len(before)
 return bytes(b)
def tap(flag,payload):
 c=flag
 for v in payload:c^=v
 return struct.pack('<H',len(payload)+2)+bytes([flag])+payload+bytes([c])
def main():
 base=ROOT/'build/fullgame';out=base/'true_black_r31';out.mkdir(parents=True,exist_ok=True);records=[]
 raw=(base/'loading_text_r28/RType_TS2068_fullgame_r28.ram512').read_bytes();image=b''.join(change(raw[n*65536:(n+1)*65536],n+1,n>0)for n in range(8));(out/'RType_TS2068_true_black_r31.ram512').write_bytes(image)
 with zipfile.ZipFile(base/'disk_layout_r30/RType_TS2068_disk_r30.zip')as source,zipfile.ZipFile(out/'RType_TS2068_disk_r31.zip','w',zipfile.ZIP_DEFLATED)as dest:
  for name in source.namelist():
   data=source.read(name)
   if '/RTFG' in name and name.endswith('.TAP'):
    volume=int(Path(name).stem[-2:],16);at=0;idx=0;result=b''
    while at<len(data):
     length=int.from_bytes(data[at:at+2],'little');block=data[at+2:at+2+length]
     result+=data[at:at+2+length]if idx%2==0 else tap(255,image[(volume*4+idx//2)*8192:(volume*4+idx//2+1)*8192]);idx+=1;at+=length+2
    data=result
   elif name.startswith('Fuse-level-previews/')and name.endswith('.dck'):
    level=int(Path(name).stem.split('_')[-1]);p=base/f'preview_end_r29/Level_{level}_preview_r29.dck';data=p.read_bytes();data=data[:9]+change(data[9:],level);(out/f'Level_{level}_true_black_r31.dck').write_bytes(data)
   dest.writestr(name,data)
   records.append(dict(file=name,sha256=hashlib.sha256(data).hexdigest()))
  dest.writestr('BLACK_POLICY.txt','Space and black-edged art use normal black. BRIGHT is cleared on pairs containing black; coloured interior pairs retain BRIGHT. Standalone previews stop at completion. Disk progression unchanged. Hardware validation pending.\n')
 (out/'manifest.json').write_text(json.dumps(dict(image_sha256=hashlib.sha256(image).hexdigest(),files=records,status='Normal-black candidate; native gameplay verification required'),indent=2));print(out)
if __name__=='__main__':main()



