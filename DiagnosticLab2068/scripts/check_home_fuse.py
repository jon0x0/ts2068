"""Independent native-reset Fuse checkpoint for the16K U16 edition, no DOCK."""
from pathlib import Path
import re, subprocess, json, hashlib
ROOT=Path(__file__).resolve().parents[1]; out=ROOT/'build/home'
symbols=dict((n,int(a,16)) for n,a in re.findall(r'^(\w+): EQU 0x([0-9A-F]+)',(out/'symbols.txt').read_text(),re.M))
(out/'absent-exrom.bin').write_bytes(bytes([255])*8192)
checkpoint=hex(symbols['menu_ready'])
commands=f'breakpoint {checkpoint} if [0] == 195 && [0x100] == 243\ncommands 1\nprint z80:pc\nprint z80:sp\nprint spectrum:frames\nexit 0\nend'
command=[r'C:\Program Files (x86)\Fuse\fuse.exe','--machine','ts2068','--speed','5000','--rom-ts2068-0',str(out/'diagnostic-home-u16.bin'),'--rom-ts2068-1',str(out/'absent-exrom.bin'),'--no-sound','--no-loading-sound','--no-confirm-actions','--debugger-command',commands]
startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
try:
    p=subprocess.run(command,capture_output=True,text=True,timeout=60,startupinfo=startup)
    output=p.stdout+p.stderr;status='checkpoint_completed' if p.returncode==0 and checkpoint in output and 'error:' not in output.lower() else 'unconfirmed'
except subprocess.TimeoutExpired as e: output=str(e);status='timeout'
(out/'fuse.log').write_text(output)
(out/'fuse-verification.json').write_text(json.dumps(dict(status=status,image_sha256=hashlib.sha256((out/'diagnostic-home-u16.bin').read_bytes()).hexdigest(),command=command,checkpoint=checkpoint,limitations=['Native emulator reset with absent EXROM and no DOCK; physical socket/EPROM timing not validated']),indent=2)+'\n')
print(status);print(output[:1500])
