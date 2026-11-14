"""Capture native handoff/live RAM deterministically; no gameplay state injection."""
from pathlib import Path
import argparse,json,re,subprocess,hashlib
import numpy as np
from PIL import Image
from build_graphics import PALETTE,screen_offset
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--frame',type=int,default=0);ap.add_argument('--start',action='store_true');ap.add_argument('--joystick-start',action='store_true');ap.add_argument('--move',type=int,default=0);ap.add_argument('--port',type=int,choices=(1,2),default=1);args=ap.parse_args()
    out=ROOT/'build/native';stem=f'probe_{args.frame}' + ('_started' if args.start else '') + ('_joy' if args.joystick_start else '') + (f'_move{args.move}_port{args.port}' if args.move else '')
    regs=['af','bc','de','hl',"af'","bc'","de'","hl'",'ix','iy','sp','pc','i','im','iff1','iff2']
    # Set armed at the HOME handoff. The bootstrap ends exactly before $8634.
    lines=['set $armed 0','set $address 16384','breakpoint 0x8634 if $armed == 0',
      f'breakpoint time 100 if $armed == 1 && spectrum:frames >= {args.frame}',
      'breakpoint 0x4000 if $armed == 2 && $address < 65536',
      'breakpoint 0x4000 if $armed == 2 && $address == 65536',
      f'breakpoint time 100 if spectrum:frames == {max(2500,args.frame+100)}',
      'commands 1','set $armed 1']
    if args.frame:lines += ['continue','end','commands 2']
    lines += ['print 0xcafe']+[f'print z80:{r}' for r in regs]
    lines += ['print spectrum:frames','print [0x4000]','print [0x4001]','print [0x4002]',
      'set $armed 2','set z80:iff1 0','set z80:iff2 0','set 0x4000 0xc3','set 0x4001 0',
      'set 0x4002 0x40','set z80:pc 0x4000','continue','end']
    if not args.frame:lines += ['commands 2','continue','end']
    lines += ['commands 3','print [$address]+256*[$address+1]','set $address $address+2',
      'continue','end','commands 4','exit','end','commands 5','print 0xdead','print z80:pc','exit 1','end']
    
    if args.start:
        lines += ['breakpoint 0x8b31 if spectrum:frames >= 400 && spectrum:frames < 430','commands 6','set z80:af 0xfe00 + (z80:af & 255)','continue','end']
    
    if args.joystick_start:
        assert not args.start
        lines += ['breakpoint 0x1a28 if spectrum:frames >= 400 && spectrum:frames < 430','commands 6','set z80:af 0xef00 + (z80:af & 255)','continue','end']
    
    if args.move:
        assert args.joystick_start and 0 <= args.move < 32
        address=0x1a28 if args.port==1 else 0x1a2d
        lines += [f'breakpoint {address} if spectrum:frames >= 1800 && spectrum:frames < 1810','commands 7',f'set z80:af {(255-args.move)*256} + (z80:af & 255)','continue','end']
    program='\n'.join(lines);(out/(stem+'.commands')).write_text(program)
    startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
    p=subprocess.run(['C:/Program Files (x86)/Fuse/fuse.exe','--machine','ts2068','--dock',
      str(out/'RType_level1_native_experimental.dck'),'--speed','5000','--no-sound',
      '--debugger-command',program],capture_output=True,text=True,timeout=55,
      startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
    (out/(stem+'.log')).write_text(p.stdout+p.stderr)
    v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)]
    count=1+len(regs)+4
    if p.returncode or len(v)!=count+24576 or v[0]!=0xcafe:raise SystemExit(f'Failed {stem}: exit{p.returncode} values{len(v)}; inspect log')
    ram=bytearray(b''.join(w.to_bytes(2,'little') for w in v[count:]));ram[:3]=bytes(v[count-3:count])
    (out/(stem+'.bin')).write_bytes(ram)
    cpu=dict(zip(regs,v[1:1+len(regs)]))
    reference=(out/'snapshot.bin').read_bytes()
    difference=[i+0x4000 for i,(a,b) in enumerate(zip(ram,reference)) if a!=b]
    if not args.frame:assert not difference,f'Handoff changed {len(difference)} RAM bytes: {difference[:20]}'
    pixels=np.zeros((192,256,3),dtype=np.uint8)
    for y in range(192):
        for x in range(256):
            a=ram[6144+(y//8)*32+x//8];bit=bool(ram[screen_offset(y)+x//8] & (128>>(x&7)))
            if a&128 and (v[1+len(regs)]//16)&1:bit=not bit
            color=(a&7) if bit else ((a>>3)&7)
            pixels[y,x]=PALETTE[color+(8 if a&64 else 0)]
    Image.fromarray(pixels).save(out/(stem+'.png'))
    result=dict(cartridge_sha256=hashlib.sha256((out/'RType_level1_native_experimental.bin').read_bytes()).hexdigest(),cpu=cpu,frame=v[1+len(regs)],sha256=hashlib.sha256(ram).hexdigest(),
      ram_bytes_changed_since_built_checkpoint=len(difference),
      limitation='Original Spectrum graphics, experimental native level-one execution; not ECM integration.')
    (out/(stem+'.json')).write_text(json.dumps(result,indent=2));print(stem,result)
if __name__=='__main__':main()






