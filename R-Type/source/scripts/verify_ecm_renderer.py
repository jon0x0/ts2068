"""Execute real ECM tile hook and verify legacy registers and 8x1 output."""
from pathlib import Path
import json,re,subprocess,argparse
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--all-cells',action='store_true');ap.add_argument('--cell-start',type=int,default=0);ap.add_argument('--bitmap-base',type=lambda s:int(s,0),choices=(0x40,0x60),default=0x40);args=ap.parse_args();bitmap_base=args.bitmap_base
 out=ROOT/'build/ecm_native';raw=(out/'RType_level1_ECM_TSPico_RAM.bin').read_bytes()
 logical=bytes(0x4000)+(ROOT/'build/native/snapshot.bin').read_bytes()
 samples=[]
 for ident in (range(1,112) if args.all_cells else (3,6,0x4c,0x54)):
  at=0xbc67+(ident-1)*4;w,h=logical[at:at+2];ptr=int.from_bytes(logical[at+2:at+4],'little')
  for y in range(h):
   for x in range(w):
    attr=logical[ptr]
    if attr!=0x36 and (args.all_cells or x in (0,1)):samples.append((ident,ptr,y*8+(x%2)*128,attr))
    ptr+=1 if attr==0x36 else 9
 if args.all_cells:samples=samples[args.cell_start:args.cell_start+16]
 tag=f'{bitmap_base:02x}'+(f'_all_{args.cell_start:03d}' if args.all_cells else '')
 cases=[(sample,flip,iff) for sample in samples for flip in (0,1,2,3) for iff in (0,1)]
 table=bytearray()
 for (ident,ptr,phase,attr),flip,iff in cases:
  ret=(0x8d2a,0x8dfd,0x8d91,0x8e57)[flip]
  table+=ptr.to_bytes(2,'little')+bytes([ident])+ret.to_bytes(2,'little')+bytes([iff])
 setup=['set $row 0xcc00 + $case * 6','out 244 9','set z80:hl [$row] + 256 * [$row+1]',
  'set 0x7a9c [$row+2]','set 0x8eb1 ($case & 1) * 69',f'set 0x8ebf {bitmap_base}','set z80:bc 0x5dc3','set z80:de 0x7e10',
  'set z80:ix 0x1234','set z80:iy 0x5678','set z80:sp 0xe000',
  'set 0xe000 [$row+3]','set 0xe001 [$row+4]','set z80:iff1 [$row+5]','set z80:iff2 [$row+5]',
  'set $stamp ula:tstates','set $stampframe spectrum:frames','set z80:pc 0x8ea2']
 lines=['set $armed 0','set $case 0','breakpoint 0x8634 if $armed == 0',
  'breakpoint 0x8d2a if $armed == 1','breakpoint 0x8dfd if $armed == 1',
  'breakpoint 0x8d91 if $armed == 1','breakpoint 0x8e57 if $armed == 1','breakpoint 0x4001 if $armed == 1','commands 1','set $armed 1','set z80:iff1 0','set z80:iff2 0','out 244 11','set 0x3ff0 2','out 255 66','set 0x4000 0']
 lines += [f'set {0xcc00+i} {v}' for i,v in enumerate(table)]
 lines += setup+['continue','end']
 for index in (2,3,4,5):
  lines += [f'commands {index}']+[f'print z80:{r}' for r in ('af','bc','de','hl','ix','iy','sp','iff1')]
  lines += ['print [0x7e10]','print [0x7810]',f'out 244 {1 if bitmap_base==0x40 else 5}']+[f'print [{(0x6010 if bitmap_base==0x40 else 0x4010)+256*y}]' for y in range(8)]+['print $stamp','print $stampframe','print ula:tstates','print spectrum:frames']
  lines += ['set $case $case + 1']+setup+[f'set z80:pc 0x8ea2 - ($case == {len(cases)}) * 0x4ea2','continue','end']
 lines += ['commands 6','exit','end','breakpoint time 100 if spectrum:frames == 2000','commands 7','print 0xdead','exit 1','end']
 program='\n'.join(lines);(out/f'tile_cpu_{tag}.commands').write_text(program)
 startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
 p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','ts2068','--dock',str(out/'RType_level1_ECM_TSPico_RAM.dck'),'--speed','5000','--no-sound','--debugger-command',program],capture_output=True,text=True,timeout=35,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
 (out/f'tile_cpu_{tag}.log').write_text(p.stdout+p.stderr)
 v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)]
 assert not p.returncode and len(v)==22*len(cases),(p.returncode,len(v),len(cases))
 for i,((ident,ptr,phase,attr),flip,iff) in enumerate(cases):
  r=v[i*22:(i+1)*22]
  assert r[:8]==[(0x4010 if bitmap_base==0x40 else 0x6034),0x5dc3,0x7810,ptr+1,0x1234,0x5678,0xe002,iff],(i,r[:8],hex(ptr))
  chosen=69 if iff else attr
  assert r[8:10]==[ident,chosen],(i,'legacy tile metadata',r[8:10])
  page=raw[ident]+(phase>>7);base=page*256+(phase&31)
  expected=list(raw[base:base+8])
  if not attr&0x38:
   for line in range(8):
    if logical[ptr+1+line]==255:
     lookup=0x108 if (page&0xfe)==4 else 0x180
     expected[line]=raw[lookup+expected[line]]
  expected=expected[::-1] if flip&1 else expected
  if chosen&0x38 or not chosen&7:expected=[chosen&127]*8
  assert r[10:18]==expected,(i,hex(ident),r[10:18],expected)
 times=[v[i*22+20]-v[i*22+18] for i,(_,_,iff) in enumerate(cases) if iff==0 and v[i*22+19]==v[i*22+21]]
 timing=dict(samples_without_irq=len(times),min_tstates=min(times),max_tstates=max(times),mean_tstates=sum(times)/len(times))
 (out/f'tile_cpu_{tag}.json').write_text(json.dumps(dict(bitmap_base=bitmap_base,cases=len(cases),passed=True,timing=timing,coverage='Original result AF/BC/DE/HL/IX/IY/SP, both IRQ states, all four mirror variants and legacy forced-attribute mode, source-relative palettes for ship/enemy/explosions'),indent=2))
 print(len(cases),'tile-hook CPU cases passed, registers/flags/stack/IRQ and all 8 attributes exact.',timing)
if __name__=='__main__':main()
