from pathlib import Path
import re,subprocess,json
root=Path(__file__).resolve().parents[1]
symbols=dict((k,int(v,16)) for k,v in re.findall(r'^(\w+): EQU 0x([0-9A-F]+)',(root/'build/symbols.txt').read_text(),re.M))
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW
traces=[];checkpoints=[]
for completed in [1,1024]:
    commands=f"breakpoint 0x{symbols['frame_done']:04x}\nignore 1 {completed-1}\ncommands 1\nprint z80:pc\nprint z80:sp\nprint spectrum:frames\nprint ula:tstates\nexit\nend"
    (root/'build/fuse-commands.txt').write_text(commands)
    args=[r'C:\apps\emulation\Fuse\fuse.exe','--machine','ts2068','--dock',str(root/'build/sinistar.dck'),'--speed','5000','--no-sound','--debugger-command',commands]
    r=subprocess.run(args,capture_output=True,text=True,timeout=45,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
    output=r.stdout+r.stderr;traces.append(f'Completed updates: {completed}\n'+output)
    assert r.returncode==0 and 'Invalid debugger command' not in output
    values=[int(v,16) for v in re.findall(r'^0x([0-9a-f]+)\s*$',output,re.M)]
    assert len(values)==4 and values[0]==symbols['frame_done'] and values[1]==0x7fff
    checkpoints.append(dict(updates=completed,pc=values[0],sp=values[1],video_frame=values[2],tstates=values[3]))
assert checkpoints[1]['video_frame']-checkpoints[0]['video_frame']==1023,'Native Fuse missed a refresh'
(root/'build/fuse-trace.txt').write_text('\n'.join(traces))
(root/'build/fuse-report.json').write_text(json.dumps(dict(checkpoints=checkpoints,updates_per_refresh=1),indent=2))
print(json.dumps(checkpoints,indent=2));print('Fuse: 1023 consecutive refresh intervals, no missed update')
