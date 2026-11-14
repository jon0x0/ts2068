"""Execute retained-colour scrolling and entering-column hooks in Fuse."""
from pathlib import Path
import subprocess,re,json
from build_graphics import screen_offset
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/diagnostics/r8_scrolling';out.mkdir(parents=True,exist_ok=True)
 raw=(ROOT/'build/ecm_native/RType_level1_ECM_TSPico_RAM.bin').read_bytes();assert raw[0x1b18:0x1b20]==bytes([255])*8
 results=[]
 for kind,attr in [('scroll',0),('column',0),('column',0x47),('column',0x56)]:
  for iff in (0,1):
   initial=bytes(((i%256)//32+i%32)%8+64 for i in range(6144));expected=bytearray(initial)
   end=0x8ce0 if kind=='scroll' else 0x89fe;entry=0x8cdd if kind=='scroll' else 0x89fb
   lines=['set $p 16384','set $armed 0','breakpoint 0x8634',f'breakpoint {end}','breakpoint 0xc000 if $armed == 1 && $p < 30720','breakpoint 0xc000 if $armed == 1 && $p == 30720','commands 1','set z80:iff1 0','set z80:iff2 0','out 244 11','set 0x3ff0 2']
   for y in range(20):
    a=0x8080+y*4;v=screen_offset(y*8)
    for j,n in enumerate((31+v%256,0x40+v//256,31+v%256,0x58+y//8)):lines += [f'set {a+j} {n}']
   lines+=['set 0xb000 '+str(attr),'out 244 5']+[f'set {16384+i} {v}' for i,v in enumerate(initial[:256])]
   fill=bytes.fromhex('21 00 40 11 00 41 01 00 17 ed b0 3e 09 d3 f4 21 54 12 e5 f1 21 00 b0 11 5f 78 01 45 23 dd 21 80 80 fd 21 78 56 31 00 d0')+bytes([0xfb if iff else 0xf3,0xc3,entry&255,entry>>8])
   lines += [f'set {0xc100+i} {v}' for i,v in enumerate(fill)]
   lines+=['set z80:af 0x1254' ,'set z80:bc 0x2345','set z80:de 0x785f','set z80:hl 0xb000','set z80:ix 0x8080','set z80:iy 0x5678','set z80:sp 0xd000','set z80:iff1 0','set z80:iff2 0','set z80:pc 0xc100','continue','end','commands 2']
   lines += [f'print z80:{r}' for r in ('af','bc','de','hl','ix','iy','sp','iff1')]+['set z80:iff1 0','set z80:iff2 0','out 244 5','set 0xc000 0xc3','set 0xc001 0','set 0xc002 0xc0','set $armed 1','set z80:pc 0xc000','continue','end','commands 3','print [$p]+256*[$p+1]','set $p $p+2','continue','end','commands 4','exit','end','breakpoint time 100 if spectrum:frames == 2000','commands 5','exit 1','end']
   name=f'{kind}_{attr:02x}_{iff}';program='\n'.join(lines);(out/(name+'.commands')).write_text(program)
   si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW
   p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','ts2068','--dock',str(ROOT/'build/ecm_native/RType_level1_ECM_TSPico_RAM.dck'),'--speed','5000','--no-sound','--debugger-command',program],capture_output=True,text=True,timeout=25,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
   (out/(name+'.log')).write_text(p.stdout+p.stderr);v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)];assert p.returncode==0 and len(v)==7176,(name,len(v),p.stderr)
   if kind=='scroll':
    assert v[:8]==[0x1254,0x2345,0x7801,0xb000,0x8080,0x5678,0xd000,iff],(name,v[:8])
    for y in range(160):
     a=screen_offset(y);expected[a+1:a+31]=initial[a+2:a+32]
   else:
    assert v[1:8]==[0x2345,0x785f,0xb000,0x8080,0x5678,0xd000,iff],(name,v[:8])
    for y in range(8):expected[screen_offset(y)+31]=attr&127
   actual=b''.join(w.to_bytes(2,'little') for w in v[8:]);assert actual[:6144]==expected,(name,next((i,a,b) for i,(a,b) in enumerate(zip(actual,expected)) if a!=b))
   if kind=='column':
    for y in range(8):assert actual[8192+screen_offset(y)+31]==expected[screen_offset(y)+31],(name,'live-column',y)
   results.append(dict(test=name,passed=True))
 (out/'validation.json').write_text(json.dumps(results,indent=2));print('8 scrolling/column cases pass: entire6144-byte shadow, untouched borders/HUD, registers, stack and IFF.')
if __name__=='__main__':main()
