"""Shared stock-ROM/ECM renderer optimizations, separate from native compatibility."""
from pathlib import Path
import subprocess,re

def kernels(root):
 out=root/'build/optimized';out.mkdir(parents=True,exist_ok=True)
 asm=root.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
 p=subprocess.run([str(asm),f'--raw={out/"kernels.bin"}',f'--sym={out/"kernels.sym"}',str(root/'src/render_kernels.asm')],cwd=root,capture_output=True,text=True)
 (out/'kernels.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
 code=(out/'kernels.bin').read_bytes();sym={n:int(v,16) for n,v in re.findall(r'(\w+): EQU 0x([0-9A-Fa-f]+)',(out/'kernels.sym').read_text())}
 return code,sym

def patch_kernels(ram,sym):
 ram=bytearray(ram)
 for address,label in ((0x8e02,'copy_vertical'),(0x8e5c,'copy_vertical_reverse_bits')):
  offset=address-0x4000;assert ram[offset:offset+3]==bytes.fromhex('dd 2e 07')
  target=sym[label];ram[offset:offset+3]=bytes([0xc3,target&255,target>>8])
 return ram

def colour_cache(ram,rom):
 # Reproduce boot's source metadata, including shared descriptor writes.
 b=bytes(0x4000)+bytes(ram);meta=bytearray([255]*8192);cells=[]
 for ident in range(1,112):
  a=0xbc67+(ident-1)*4;w,h=b[a:a+2];p=int.from_bytes(b[a+2:a+4],'little')
  for y in range(h):
   for x in range(w):
    at=b[p];meta[p-0xa000]=y*8|((x&1)*128)
    if at!=0x36 and not at&0x38:
     for k in range(8):
      if b[p+1+k]==255:meta[p+1+k-0xa000]=1
    cells.append((ident,p,at));p+=1 if at==0x36 else 9
 rows=[];indices=[];by_pointer={}
 for ident,p,at in cells:
  if at==0x36:indices.append(255);continue
  phase=meta[p-0xa000];page=rom[ident]+(phase>>7);offset=page*256+(phase&31);colors=bytearray(rom[offset:offset+8])
  for y in range(8):
   if meta[p+1+y-0xa000]==1:colors[y]=rom[(0x108 if page&254==4 else 0x180)+colors[y]]
  colors=bytes(colors)
  if p in by_pointer:assert by_pointer[p]==colors
  by_pointer[p]=colors
  if colors not in rows:rows.append(colors)
  indices.append(rows.index(colors))
 assert len(rows)<=156 and len(indices)==786,(len(rows),len(indices))
 return b''.join(rows),bytes(indices)
