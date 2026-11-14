from pathlib import Path
import subprocess
R=Path.cwd();O=R/'build/fullgame/hardware_fire_r65';s=(R/'src/debug_ram_screen.asm').read_text().replace('ORG $8000','ORG $A000').replace('$A000','$TEMP').replace('$C000','$E000').replace('$TEMP','$C000')
# Restore execution origin; only screen snapshot buffers relocate.
s=s.replace('ORG $C000','ORG $A000').replace('ASSERT $ <= $84B4','ASSERT $ <= $A4B4')
(O/'relocated_debug.asm').write_text(s)
subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={O}/relocated_debug.bin',str(O/'relocated_debug.asm')],check=True)
b=(O/'relocated_debug.bin').read_bytes();o=bytearray();p=0;literal=bytearray()
def flush():
 while literal:
  n=min(127,len(literal));o.append(n);o.extend(literal[:n]);del literal[:n]
while p<len(b):
 best=(0,0)
 for q in range(p):
  n=0
  while n<130 and p+n<len(b) and b[q+n]==b[p+n]:n+=1
  if n>best[0]:best=n,p-q
 if best[0]>=4:
  flush();n,d=best;o.append(128+n-3);o.extend(d.to_bytes(2,'little'));p+=n
 else:literal.append(b[p]);p+=1
flush();o.append(0);(O/'debug_lz.bin').write_bytes(o);print('compressed',len(b),len(o))

