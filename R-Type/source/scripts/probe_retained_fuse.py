"""Capture native handoff/live RAM deterministically; no gameplay state injection."""
from pathlib import Path
import argparse,json,re,subprocess,hashlib
import numpy as np
from PIL import Image
from build_graphics import PALETTE,screen_offset
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--frame',type=int,default=0);ap.add_argument('--coherent',action='store_true');ap.add_argument('--readonly',action='store_true');ap.add_argument('--scroll-phase',type=int,choices=range(8));ap.add_argument('--dck',type=Path);ap.add_argument('--label',default='');ap.add_argument('--start',action='store_true');ap.add_argument('--joystick-start',action='store_true');ap.add_argument('--move',type=int,default=0);ap.add_argument('--port',type=int,choices=(1,2),default=1);ap.add_argument('--start-frame',type=int,default=800);ap.add_argument('--move-frame',type=int,default=1800);ap.add_argument('--blast-id',type=lambda v:int(v,0),default=0x54);ap.add_argument('--explosion',action='store_true');args=ap.parse_args()
    out=ROOT/'build/ecm_native';stem=(('explosion' if args.blast_id==0x54 else f'explosion_{args.blast_id:02x}') if args.explosion else f'probe_{args.frame}') + ('_started' if args.start else '') + ('_joy' if args.joystick_start else '') + (f'_move{args.move}_port{args.port}' if args.move else '')
    if args.scroll_phase is not None:stem += f'_phase{args.scroll_phase}'
    if args.label:stem += '_'+args.label
    if args.readonly:out=ROOT/'build/readonly_ecm'
    dock=args.dck or out/('RType_ECM_ROM_candidate.dck' if args.readonly else 'RType_level1_ECM_TSPico_RAM.dck')
    input_bytes=dock.read_bytes()[9+0x1a00:9+0x1b00]
    port1=0x1a00+input_bytes.index(bytes.fromhex('ed 78 57 06 02 ed 78'))+2
    port2=port1+5
    regs=['af','bc','de','hl',"af'","bc'","de'","hl'",'ix','iy','sp','pc','i','im','iff1','iff2']
    # Set armed at the HOME handoff. The bootstrap ends exactly before $8634.
    lines=['set $blast 0','set $armed 0','set $address 16384','breakpoint 0x8634 if $armed == 0',
      ('breakpoint 0x8b06 if $armed == 1 && $blast == 2' if args.explosion else (f'breakpoint 0x8b06 if $armed == 1 && spectrum:frames >= {args.frame}'+(f' && [0x7a82] == {args.scroll_phase}' if args.scroll_phase is not None else '') if args.coherent else f'breakpoint time 100 if $armed == 1 && spectrum:frames >= {args.frame}')),
      'breakpoint 0x4000 if $armed == 2 && $address < 65536',
      'breakpoint 0x4000 if $armed == 2 && $address == 65536',
      f'breakpoint time 100 if spectrum:frames == {max(2500,args.frame+100)}',
      'commands 1','set $armed 1','set 0x91f2 0xc9']
    if args.frame:lines += ['continue','end','commands 2']
    lines += ['print 0xcafe']+[f'print z80:{r}' for r in regs]
    lines += ['print spectrum:frames','print [0x4000]','print [0x4001]','print [0x4002]',
      'set $armed 2','set z80:iff1 0','set z80:iff2 0','set 0x4000 0xc3','set 0x4001 0',
      'set 0x4002 0x40','set z80:pc 0x4000','out 244 1','continue','end']
    if not args.frame:lines += ['commands 2','continue','end']
    lines += ['commands 3','print [$address]+256*[$address+1]','set $address $address+2',
      'continue','end','commands 4','exit','end','commands 5','print 0xdead','print z80:pc','exit 1','end']
    
    if args.start:
        lines += ['breakpoint 0x8b31 if spectrum:frames >= 400 && spectrum:frames < 430','commands 6','set z80:af 0xfe00 + (z80:af & 255)','continue','end']
    
    if args.joystick_start:
        assert not args.start
        lines += [f'breakpoint {port1} if spectrum:frames >= {args.start_frame} && spectrum:frames < {args.start_frame+30}','commands 6','set z80:af 0xef00 + (z80:af & 255)','continue','end']
    
    if args.move:
        assert args.joystick_start and 0 <= args.move < 32
        address=port1 if args.port==1 else port2
        lines += [f'breakpoint {address} if spectrum:frames >= {args.move_frame} && spectrum:frames < {args.move_frame+10}','commands 7',f'set z80:af {(255-args.move)*256} + (z80:af & 255)','continue','end']
    if args.explosion:
        pos=lines.index('print 0xcafe')
        inspect=['out 244 11','print 0xd00d']
        for base in (0x7e00,):
            inspect += [f'print [{base}+($blasty+{y})*32+$blastx+{x}]' for y in range(3) for x in range(3)]
        lines[pos:pos]=inspect
        assert args.joystick_start and not args.move
        lines += [f'breakpoint 0xc440 if $blast == 0 && z80:af >= {args.blast_id*256} && z80:af < {(args.blast_id+1)*256}','commands 7','set $blast 1','set $blastframe spectrum:frames','set $blastx z80:bc & 255','set $blasty z80:bc / 256','print 0xbeef','print z80:bc','print z80:af','print spectrum:frames','continue','end']
    if args.explosion:
        done=int(re.search(r'publish_done: EQU 0x([0-9A-Fa-f]+)',(out/'renderer.sym').read_text()).group(1),16)
        lines += [f'breakpoint {done} if $blast == 1','commands 8','set $blast 2','set $blastframe spectrum:frames','continue','end']
    pos=lines.index('print 0xcafe')
    lines[pos:pos]=['out 244 11','print 0xfeed','print [0x7aa1]','print [0x7aa2]','print [0x7aa4]','print 0xface','print [0x3ff0]']
    if args.readonly:lines=[v.replace('out 244 11','out 244 3').replace('[0x3ff0]','[0xbe00]') for v in lines]
    pos=lines.index('print 0xfeed')
    lines[pos:pos]=['print 0xbacc']+[f'print [{a}]+256*[{a+1}]' for a in range(0x7800,0x7b00,2)]
    program='\n'.join(lines);(out/(stem+'.commands')).write_text(program)
    startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
    p=subprocess.run(['C:/apps/emulation/Fuse/fuse.exe','--machine','ts2068','--dock',
      str(dock),'--speed','5000','--no-sound',
      '--debugger-command',program],capture_output=True,text=True,timeout=55,
      startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW)
    (out/(stem+'.log')).write_text(p.stdout+p.stderr)
    v=[int(x,16) for x in re.findall(r'^0x([0-9a-f]+)\s*$',p.stdout,re.M)]
    marker=v.index(0xcafe) if 0xcafe in v else 0
    prefix=v[:marker];v=v[marker:]
    assert len(prefix)>=2 and prefix[-2]==0xface,prefix
    k=prefix.index(0xbacc)
    (out/(stem+'.back_attrs.bin')).write_bytes(b''.join(w.to_bytes(2,'little') for w in prefix[k+1:k+385]))
    video_mode=prefix[-1]
    assert prefix[-6]==0xfeed,prefix
    player_info=dict(x=prefix[-5],y=prefix[-4],pose=prefix[-3])
    blast_info=prefix[:-6] if args.explosion else None
    count=1+len(regs)+4
    if p.returncode or len(v)!=count+24576 or v[0]!=0xcafe:raise SystemExit(f'Failed {stem}: exit{p.returncode} values{len(v)}; inspect log')
    ram=bytearray(b''.join(w.to_bytes(2,'little') for w in v[count:]));ram[:3]=bytes(v[count-3:count])
    (out/(stem+'.bin')).write_bytes(ram)
    cpu=dict(zip(regs,v[1:1+len(regs)]))
    from build_graphics import unpack
    attrs=bytes(ram[8192:8192+6144])
    if video_mode==0:
        plane=bytearray(6144)
        for y in range(192):plane[screen_offset(y):screen_offset(y)+32]=ram[6144+(y//8)*32:6144+(y//8+1)*32]
        attrs=bytes(plane)
    image=unpack(bytes(ram[:6144]),attrs)
    image.save(out/(stem+'.png'))
    difference=[]
    result=dict(player_info=player_info,video_mode=video_mode,blast_info=blast_info,cartridge_sha256=hashlib.sha256(dock.read_bytes()[9:]).hexdigest(),cpu=cpu,frame=v[1+len(regs)],sha256=hashlib.sha256(ram).hexdigest(),
      ecm_attribute_count=len(set(ram[8192:8192+6144])),
      limitation=('Read-only ECM level-one cartridge; physical hardware validation pending.' if args.readonly else 'Live ECM shading prototype, original Spectrum geometry. Requires writable DOCK1+2+3; not a PicoROM image.'))
    (out/(stem+'.json')).write_text(json.dumps(result,indent=2));print(stem,result)
if __name__=='__main__':main()






