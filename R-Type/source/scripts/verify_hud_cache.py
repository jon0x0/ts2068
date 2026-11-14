"""Verify retained HUD exact output, changed-cell repair and no-change cost."""
from pathlib import Path
import subprocess,re,json
from build_graphics import screen_offset
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/optimized';sym=(ROOT/'build/ecm_native/renderer.sym').read_text();entry=int(re.search(r'publish_hud: EQU 0x([0-9a-fA-F]+)',sym).group(1),16)
 source=[i*7&127 for i in range(128)]
 setup=['out 244 9','set z80:af 0x1234','set z80:bc 0x2345','set z80:de 0x3456','set z80:hl 0x4567','set z80:ix 0x5678','set z80:iy 0x6789','set z80:sp 0xe000','set 0xe000 0','set 0xe001 0x40','set z80:iff1 0','set z80:iff2 0','set $stamp ula:tstates','set $frame spectrum:frames',f'set z80:pc {entry}']
 lines=['set $round 0','set $p 24576','set $armed 0','breakpoint 0x8634','breakpoint 0xe120','breakpoint 0x4001 if $armed == 1','breakpoint 0xc000 if $armed == 2 && $p < 30720','breakpoint 0xc000 if $armed == 2 && $p == 30720 && $round < 2','breakpoint 0xc000 if $armed == 2 && $p == 30720 && $round == 2','commands 1','set z80:iff1 0','set z80:iff2 0','out 244 11','set 0x3ff0 2','out 244 7']
 lines += [f'set {0x5800+i} 255' for i in range(128)]
 # Initialize HOME plane without a long command line.
 init=bytes.fromhex('21 00 60 11 01 60 01 ff 17 36 12 ed b0 c3 20 e1')
 lines += [f'set {0xe100+i} {v}' for i,v in enumerate(init)]
 lines += ['set z80:pc 0xe100','continue','end','commands 2','out 244 9']+[f'set {0x5a80+i} {v}' for i,v in enumerate(source)]+['set 0x4000 0','set $armed 1']+setup+['continue','end','commands 3']+[f'print z80:{r}' for r in ('af','bc','de','hl','ix','iy','sp','iff1')]+['print $stamp','print $frame','print ula:tstates','print spectrum:frames','set z80:iff1 0','set z80:iff2 0','out 244 1','set 0xc000 0xc3','set 0xc001 0','set 0xc002 0xc0','set z80:pc 0xc000','set $armed 2','set $p 24576','continue','end','commands 4','print [$p]+256*[$p+1]','set $p $p+2','continue','end','commands 5','set $round $round+1','out 244 9',f'set 0x5a91 {source[17]} + ($round == 2) * {0xc5-source[17]}','set $armed 1']+setup+['continue','end','commands 6','exit','end','breakpoint time 100 if spectrum:frames == 2000','commands 7','exit 1','end']
 program='\n'.join(lines);(out/'hud.commands').write_text(program);si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW
 p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','ts2068','--dock',str(ROOT/'build/ecm_native/RType_level1_ECM_TSPico_RAM_r8.dck'),'--speed','5000','--no-sound','--debugger-command',program],capture_output=True,text=True,timeout=30,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
 (out/'hud.log').write_text(p.stdout+p.stderr);v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)];assert p.returncode==0 and len(v)==3084*3,(len(v),p.stderr)
 results=[]
 for round in range(3):
  r=v[round*3084:(round+1)*3084];assert r[:8]==[0x1234,0x2345,0x3456,0x4567,0x5678,0x6789,0xe002,1],r[:8]
  expected=bytearray([0x12]*6144);colors=source.copy()
  if round==2:colors[17]=0xc5
  for i,c in enumerate(colors):
   y=160+(i//32)*8;x=i%32
   for dy in range(8):expected[screen_offset(y+dy)+x]=c&127
  actual=b''.join(w.to_bytes(2,'little') for w in r[12:]);assert actual==expected,(round,next(i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b))
  period=json.loads((ROOT/'build/diagnostics/performance/frame_period.json').read_text())['frame_tstates'];elapsed=(r[11]-r[9])*period+r[10]-r[8];results.append(dict(round=round,tstates=elapsed,passed=True))
 assert results[1]['tstates']<results[0]['tstates'],results
 (out/'hud_validation.json').write_text(json.dumps(results,indent=2));print('HUD all-changed/unchanged/one-FLASH-cell cases pass entire6144-byte plane and CPU contracts:',results)
if __name__=='__main__':main()
