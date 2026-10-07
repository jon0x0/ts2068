"""Independent native Fuse boot/self-test and interrupt checkpoints."""
from pathlib import Path
import hashlib, json, re, subprocess, sys
root=Path(__file__).resolve().parents[1]
flight='--flight' in sys.argv
scene='--scene' in sys.argv
mining='--mining' in sys.argv
prefix='mining-' if mining else 'scene-' if scene else 'flight-' if flight else ''
cartridge='sinistar-mining.dck' if mining else 'sinistar-pursuit.dck' if scene else 'sinistar-flight.dck' if flight else 'sinistar-port-kernel.dck'
symbols={k:int(v,16) for k,v in re.findall(r'^(\w+): EQU 0x([0-9A-F]+)',(root/f'build/{prefix}symbols.txt').read_text(),re.M)}
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW
checkpoints=[];traces=[]
# Break after HALT: Fuse rechecks a HALT-address breakpoint on each idle cycle.
checkpoint=symbols['frame_done'] if flight or scene or mining else symbols['idle']+1
for completed in [1,1024]:
    commands=f"breakpoint 0x{checkpoint:04x}\nignore 1 {completed-1}\ncommands 1\nprint z80:pc\nprint z80:sp\nprint spectrum:frames\nprint ula:tstates\nexit\nend"
    args=[r'C:\apps\emulation\Fuse\fuse.exe','--machine','ts2068','--dock',str(root/'build'/cartridge),'--speed','5000','--no-sound','--debugger-command',commands]
    result=subprocess.run(args,capture_output=True,text=True,timeout=45,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
    output=result.stdout+result.stderr
    traces.append(f'Idle entries: {completed}\n'+output)
    assert result.returncode==0 and 'Invalid debugger command' not in output
    values=[int(v,16) for v in re.findall(r'^0x([0-9a-f]+)\s*$',output,re.M)]
    assert len(values)==4 and values[0]==checkpoint and values[1]==0x7fff
    checkpoints.append(dict(idle_entries=completed,pc=values[0],sp=values[1],video_frame=values[2],tstates=values[3]))
(root/f'build/{prefix}fuse-trace.txt').write_text('\n'.join(traces))
print(json.dumps(checkpoints,indent=2),flush=True)
elapsed=checkpoints[1]['video_frame']-checkpoints[0]['video_frame']
if mining: assert 1023<=elapsed<=1023*4
elif scene: assert 1023*2<=elapsed<=1023*4
else: assert elapsed==1023
report=dict(dck_sha256=hashlib.sha256((root/'build'/cartridge).read_bytes()).hexdigest(),checkpoints=checkpoints,elapsed_refreshes=elapsed,completed_intervals=1023)
(root/f'build/{prefix}fuse-trace.txt').write_text('\n'.join(traces))
(root/f'build/{prefix}fuse-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
