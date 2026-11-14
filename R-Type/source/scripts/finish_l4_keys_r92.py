from pathlib import Path
import json,re,subprocess,sys
sys.path.insert(0,'scripts');from build_rocket_fix import code
O=Path('build/fullgame/l4_speed_r92');r=next(x for x in json.loads((O/'walker_runtime.json').read_text())if x['level']==4)
def asm(name,s):
 p=O/(name+'.asm');p.write_text(s);v=subprocess.run([str(Path('../sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe')),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert v.returncode==0,v.stdout+v.stderr;return p.with_suffix('.bin').read_bytes()
s=(O/'level_hotkeys.asm').read_text();needle='        PUSH HL\n';new='''        LD A,(HOT_STATE)
        ADD A,A
        JR NC,latched_none
        SRL A
        LD D,A
        JP hot_jump
latched_none:
''';s=s.replace(needle,needle+new,1);hot=asm('level_hotkeys_latched',s);assert len(hot)==1024,len(hot)
for n in range(1,9):
 if n==5:continue # L5 DOCK1 is boss phase payload; its HOME hotkey variant stays unchanged.
 p=O/f'level{n:02d}_region.bin';b=bytearray(p.read_bytes());b[0x3a00:0x3e00]=hot;p.write_bytes(b)
 (O/f'rtype/LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
 data=b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7]);(O/f'rtype/START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',data[k*1024:(k+1)*1024],k)for k in range(48)))
print('Pending key consumer installed; hotkeys end exactly3E00')

