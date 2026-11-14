"""Fly up, then retrace the same sky cells; assert no trails or path deaths."""
from pathlib import Path
import argparse,re,subprocess,json,hashlib
from build_graphics import unpack,screen_offset
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--dck',type=Path);ap.add_argument('--readonly',action='store_true');ap.add_argument('--label',default='r4');args=ap.parse_args()
 out=ROOT/'build/diagnostics/r4_trails';out.mkdir(parents=True,exist_ok=True)
 dock=args.dck or ROOT/('build/readonly_ecm/RType_ECM_ROM_candidate.dck' if args.readonly else 'build/ecm_native/RType_level1_ECM_TSPico_RAM.dck')
 port1=0x1a00+dock.read_bytes()[9+0x1a00:9+0x1b00].index(bytes.fromhex('ed 78 57 06 02 ed 78'))+2
 done=int(re.search(r'publish_done: EQU 0x([0-9a-fA-F]+)',(ROOT/'build/ecm_native/renderer.sym').read_text()).group(1),16)
 lines=['set $phase 0','set $deaths 0','set $address 16384',
  f'breakpoint {port1} if spectrum:frames >= 800 && spectrum:frames < 830',
  'breakpoint 0x94f1 if $phase == 0 && [0x7aa4] > 0 && [0x7aa1] > 0 && [0x7aa1] < 29 && [0x7aa2] == 10',
  f'breakpoint {port1} if $phase == 1',f'breakpoint {port1} if $phase == 2',
  'breakpoint 0x94f1 if $phase == 1 && [0x7aa2] <= 3',
  'breakpoint 0x94f1 if $phase == 2 && [0x7aa2] >= 9',
  'breakpoint 0x91f2 if $phase > 0 && $phase < 3',
  'breakpoint 0x8b06 if $phase == 3',
  'breakpoint 0x4000 if $phase == 4 && $address < 65536',
  'breakpoint 0x4000 if $phase == 4 && $address == 65536',
  'breakpoint time 100 if spectrum:frames == 6000',
  'commands 1','set z80:af 0xef00 + (z80:af & 255)','continue','end',
  'commands 2','set $phase 1','set $shipx [0x7aa1]','set $begin spectrum:frames','continue','end',
  'commands 3','set z80:af 0xfe00 + (z80:af & 255)','continue','end',
  'commands 4','set z80:af 0xfd00 + (z80:af & 255)','continue','end',
  'commands 5','set $phase 2','continue','end',
  'commands 6','set $phase 3','continue','end',
  'commands 7','set $deaths $deaths + 1','continue','end',
  'commands 8','set z80:iff1 0','set z80:iff2 0','out 244 11','print 0xcafe','print $deaths','print $shipx','print [0x7aa1]','print [0x7aa2]','print [0x7aa4]','print $begin','print spectrum:frames']
 # Print logical collision IDs and retained-background bytes along the flown sky.
 for row in range(2,11):
  for col in range(3):lines += [f'print [0x7e00+{row*32}+ $shipx + {col}]']
 lines += ['print [0x4000]','print [0x4001]','print [0x4002]','out 244 1','set $phase 4','set 0x4000 0xc3','set 0x4001 0','set 0x4002 0x40','set z80:pc 0x4000','continue','end',
  'commands 9','print [$address]+256*[$address+1]','set $address $address+2','continue','end',
  'commands 10','exit','end','commands 11','print 0xdead','print $phase','print z80:pc','exit 1','end']
 if args.readonly:lines=[v.replace('out 244 11','out 244 3') for v in lines]
 program='\n'.join(lines);(out/(args.label+'.commands')).write_text(program)
 startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
 p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','ts2068','--dock',str(dock),'--speed','5000','--no-sound','--debugger-command',program],capture_output=True,text=True,timeout=30,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
 (out/(args.label+'.log')).write_text(p.stdout+p.stderr)
 v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)]
 if p.returncode or len(v)!=38+24576 or v[0]!=0xcafe:raise SystemExit(f'Roundtrip failed: exit{p.returncode} values{len(v)} {v[:12]}')
 deaths,shipx,x,y,pose,begin,end=v[1:8];ids=v[8:35];ram=bytearray(b''.join(w.to_bytes(2,'little') for w in v[38:]));ram[:3]=bytes(v[35:38])
 (out/(args.label+'.bin')).write_bytes(ram);unpack(ram[:6144],ram[8192:8192+6144]).save(out/(args.label+'.png'))
 trails=[]
 for yy in range(16,80):
  for xx in range(shipx*8,(shipx+3)*8,8):
   o=screen_offset(yy)+xx//8;at=ram[8192+o]
   if (ram[o]==0 and at&0x38) or ram[o].bit_count()>=4:trails.append(dict(x=xx,y=yy,attribute=at))
 result=dict(dck_sha256=hashlib.sha256(dock.read_bytes()).hexdigest(),deaths=deaths,start_x=shipx,x=x,y=y,pose=pose,begin_frame=begin,end_frame=end,trails=trails,logical_ids=ids)
 (out/(args.label+'.json')).write_text(json.dumps(result,indent=2));print(result)
 assert deaths==0 and y==10 and pose>0 and not trails and not any(ids[:24]),result
if __name__=='__main__':main()
