"""Reproduce key redefinition using electrical keyboard reads, with held final Enter."""
from pathlib import Path
import subprocess,re,json,argparse,hashlib
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--dck',type=Path);ap.add_argument('--readonly',action='store_true');ap.add_argument('--label',default='before');ap.add_argument('--ecm',action='store_true');a=ap.parse_args();out=ROOT/('build/ecm_native' if a.ecm else 'build/native')
 events=[(460,480,0xdf,2),(500,520,0xdf,1),(540,560,0xfb,1),(580,600,0xfd,1),(620,640,0x7f,1),(660,710,0xbf,1)]
 lines=['set $entries 0','set $stores 0','set $started 0','set $played 0','breakpoint 0xbf96 if (spectrum:frames >= 400 && spectrum:frames < 430) || (spectrum:frames >= 660 && spectrum:frames < 710)','breakpoint 0xbf99','breakpoint 0xc006','breakpoint time 100 if spectrum:frames == 1200']
 for start,end,row,mask in events:lines += [f'breakpoint 0xbf5d if spectrum:frames >= {start} && spectrum:frames < {end} && z80:bc == {row*256+254}']
 lines += ['breakpoint 0x8b73 if spectrum:frames >= 760 && spectrum:frames < 790 && z80:hl == 0x7788','commands 1','set z80:af 0xfe00 + (z80:af & 255)','continue','end','commands 2','set $entries $entries + 1','continue','end','commands 3','set $stores $stores + 1','print z80:ix','print z80:de','continue','end','commands 4','print 0xcafe','print $entries','print $stores','print z80:pc','print [0x74fb]','print $started','print $played']+[f'print [{0x7780+i}]' for i in range(12)]+['exit','end']
 for i,(start,end,row,mask) in enumerate(events,5):lines += [f'commands {i}',f'set z80:af {(255-mask)*256} + (z80:af & 255)','continue','end']
 lines += ['breakpoint 0x863d','breakpoint 0x94f1','commands 12','set $started 1','continue','end','commands 13','set $played 1','continue','end','commands 11','set z80:af 0xfe00 + (z80:af & 255)','continue','end']
 if a.readonly:lines.insert(lines.index('print 0xcafe'),'out 244 3')
 if a.ecm:lines.insert(lines.index('print 0xcafe'),'out 244 9')
 if a.readonly:out=ROOT/'build/readonly_ecm'
 dock=a.dck or out/('RType_ECM_ROM_candidate.dck' if a.readonly else 'RType_level1_ECM_TSPico_RAM.dck' if a.ecm else 'RType_level1_native_experimental.dck')
 program='\n'.join(lines)
 if a.readonly:program=program.replace('0x7788','0xbd88').replace('[0x74fb]','[0xbafb]');program=re.sub(r'print \[(3059[2-9]|3060[0-3])\]',lambda m:'print ['+str(int(m[1])+0x4600)+']',program)
 if a.ecm or a.readonly:program=re.sub(r'spectrum:frames (>=|<|==) (\d+)',lambda m:'spectrum:frames '+m[1]+' '+str(int(m[2])+400),program);(out/f'keys_{a.label}.commands').write_text(program)
 startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
 p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','ts2068','--dock',str(dock),'--speed','5000','--no-sound','--debugger-command',program],capture_output=True,text=True,timeout=35,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
 (out/f'keys_{a.label}.log').write_text(p.stdout+p.stderr)
 v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)]
 assert p.returncode==0 and 0xcafe in v,(p.returncode,v[-20:])
 marker=v.index(0xcafe);summary=dict(cartridge_sha256=hashlib.sha256(dock.read_bytes()[9:]).hexdigest(),entries=v[marker+1],stores=v[marker+2],pc=v[marker+3],control_type=v[marker+4],started=v[marker+5],played=v[marker+6],keys=v[marker+7:marker+19],store_trace=v[:marker])
 if a.label!='before':
  assert summary['entries']==1 and summary['stores']==6 and summary['started']==1 and summary['played']==1,summary
  assert summary['keys']==[0xdf,2,0xdf,1,0xfb,1,0xfd,1,0x7f,1,0xbf,1],summary
 (out/f'keys_{a.label}.json').write_text(json.dumps(summary,indent=2));print(summary)
if __name__=='__main__':main()
