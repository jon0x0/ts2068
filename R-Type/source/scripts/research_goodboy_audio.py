"""Capture actual 2019 R-Type release menu in Fuse Pentagon/TR-DOS."""
from pathlib import Path
import argparse,subprocess,re,json
from build_graphics import unpack,screen_offset
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--frame',type=int,default=1200);args=ap.parse_args()
 out=ROOT/'build/research/goodboy2019';stem=f'pentagon_{args.frame}'
 lines=['set $armed 0','set $p 16384',f'breakpoint time 100 if spectrum:frames == {args.frame}','breakpoint 0x4000 if $armed == 1 && $p < 23296','breakpoint 0x4000 if $armed == 1 && $p == 23296','breakpoint 0x0298 if spectrum:frames >= 200 && spectrum:frames < 210 && z80:bc == 0xfefe',
 'commands 1','set $armed 1','print 0xcafe','print z80:pc','print z80:sp','print z80:i','print z80:im','print [0x4000]','print [0x4001]','print [0x4002]','set z80:iff1 0','set z80:iff2 0','set 0x4000 0xc3','set 0x4001 0','set 0x4002 0x40','set z80:pc 0x4000','continue','end',
 'commands 2','print [$p]+256*[$p+1]','set $p $p+2','continue','end','commands 3','exit','end']
 lines += ['commands 4','set z80:af 0xfe00 + (z80:af & 255)','continue','end']
 for number,(frame,row,mask) in enumerate(((200,0xef,8),(250,0xbf,1),(400,0xfb,8),(450,0xbf,1),(3200,0x7f,1)),5):
  lines += [f'breakpoint 0x0298 if spectrum:frames >= {frame} && spectrum:frames < {frame+10} && z80:bc == {row*256+254}',f'commands {number}',f'set z80:af {(255-mask)*256} + (z80:af & 255)','continue','end']
 lines += ['breakpoint 0x6022 if spectrum:frames >= 3200 && spectrum:frames < 3220','commands 10','set z80:af 0xfe00 + (z80:af & 255)','continue','end']
 program='\n'.join(lines);(out/(stem+'.commands')).write_text(program)
 startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
 p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','pentagon','--rom-pentagon-0',str(out/'reference_pentagon0.rom'),'--rom-pentagon-1',str(out/'reference_pentagon1.rom'),'--rom-pentagon-2',str(out/'reference_pentagon_trdos.rom'),'--auto-load','--speed','5000','--no-sound','--debugger-command',program,str(out/'RTYPE_GT.SCL')],capture_output=True,text=True,timeout=25,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
 (out/(stem+'.log')).write_text(p.stdout+p.stderr)
 v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)]
 assert p.returncode==0 and len(v)==3464 and v[0]==0xcafe,(p.returncode,len(v),p.stderr)
 v=v[1:]
 screen=bytearray(b''.join(x.to_bytes(2,'little') for x in v[7:]));screen[:3]=bytes(v[4:7]);(out/(stem+'.scr')).write_bytes(screen)
 attrs=bytearray(6144)
 for y in range(192):attrs[screen_offset(y):screen_offset(y)+32]=screen[6144+(y//8)*32:6144+(y//8+1)*32]
 unpack(screen[:6144],attrs).save(out/(stem+'.png'));(out/(stem+'.json')).write_text(json.dumps(dict(frame=args.frame,pc=v[0],sp=v[1],i=v[2],im=v[3],limitation='Original 2019 release on Pentagon model; not TS2068 integration'),indent=2));print(stem,v[:4])
if __name__=='__main__':main()
