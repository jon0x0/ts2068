"""Original-vs-optimized real Z80 vertical-mirror copy contracts."""
from pathlib import Path
import subprocess,re,json
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/optimized';results={}
 cases=[(flip,carry,iff,pattern) for flip in (0,1) for carry in (0,1) for iff in (0,1) for pattern in (0,1,2,3)]
 for label,dock in [('original',ROOT/'build/native/RType_level1_native_experimental_r2.dck'),('rom',out/'RType_level1_native_ROM_optimized_r3.dck'),('ecm',ROOT/'build/ecm_native/RType_level1_ECM_TSPico_RAM_r8.dck')]:
  values=[];times=[]
  # One controlled run per kernel with parameter table at C800.
  for flip in (0,1):
   subset=[c for c in cases if c[0]==flip];table=bytearray()
   for _,carry,iff,pattern in subset:
    pix=([0]*8,[255]*8,[0x80,1,0x55,0xaa,0x12,0x34,0x56,0x78],[1<<i for i in range(8)])[pattern]
    table+=bytes([carry,iff])+bytes(pix)
   setup=['out 244 9' if label=='ecm' else 'out 244 1','set $row 0xc800+$case*10','set z80:af 0x3700 + [$row]','set z80:bc 0x5d33','set z80:de 0x4780','set z80:hl 0xb100','set z80:ix 0x1234','set z80:iy 0x5678','set z80:sp 0xe000','set z80:iff1 [$row+1]','set z80:iff2 [$row+1]']
   setup += [f'set {0xb100+i} [$row+{i+2}]' for i in range(8)]
   setup += ['set $stamp ula:tstates','set $frame spectrum:frames',f'set z80:pc {0x8e5c if flip else 0x8e02}']
   lines=['set $case 0','set $armed 0','breakpoint 0x8634 if $armed == 0',f'breakpoint {0x8e6c if flip else 0x8e10} if $armed == 1','breakpoint 0x4001 if $armed == 1','commands 1','set $armed 1','set z80:iff1 0','set z80:iff2 0','set 0x4000 0']
   lines += [f'set {0xc800+i} {v}' for i,v in enumerate(table)]
   lines += [f'set {0x5d00+i} {int(f"{i:08b}"[::-1],2)}' for i in range(256)]
   lines += setup+['continue','end','commands 2']+[f'print z80:{r}' for r in ('af','bc','de','hl','ix','iy','sp','iff1')]+[f'print [{0x4080+i*256}]' for i in range(8)]+['print $stamp','print $frame','print ula:tstates','print spectrum:frames','set $case $case+1']+setup+[f'set z80:pc {0x8e5c if flip else 0x8e02} - ($case == 16) * {0x8e5c-0x4000 if flip else 0x8e02-0x4000}','continue','end','commands 3','exit','end']
   lines += ['breakpoint time 100 if spectrum:frames == 2000','commands 4','print 0xdead','print $case','print z80:pc','exit 1','end']
   program='\n'.join(lines);(out/f'{label}_mirror{flip}.commands').write_text(program)
   si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW
   p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','ts2068','--dock',str(dock),'--speed','5000','--no-sound','--debugger-command',program],capture_output=True,text=True,timeout=30,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
   (out/f'{label}_mirror{flip}.log').write_text(p.stdout+p.stderr);v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)];assert p.returncode==0 and len(v)==320,(label,flip,len(v),p.stderr)
   for i,(_,carry,iff,pattern) in enumerate(subset):
    r=v[i*20:(i+1)*20];values.append(r[:16])
    if not iff and r[17]==r[19]:times.append(r[18]-r[16])
  results[label]=dict(cases=values,times=times)
 assert results['rom']['cases']==results['original']['cases'],results
 assert results['ecm']['cases']==results['original']['cases'],results
 (out/'kernel_validation.json').write_text(json.dumps(results,indent=2))
 print('32 mirror-copy cases per image match original registers/flags/bitmap/IFF; IRQ-off T-state means:',{k:sum(v['times'])/len(v['times']) for k,v in results.items()})
if __name__=='__main__':main()
