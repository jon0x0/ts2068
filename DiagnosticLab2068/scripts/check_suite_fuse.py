"""Bounded Fuse checkpoint with explicit stock TS2068 ROMs and saved outcome."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build'
up = ROOT.parent / 'TSRun/roms'
symbols = dict((n, int(a, 16)) for n,a in re.findall(r'^(\w+): EQU 0x([0-9A-F]+)', (BUILD/'symbols.txt').read_text(), re.M))
commands = f"breakpoint {hex(symbols['menu_ready'])} if [0x100] == 243 && [0x102] == 64\ncommands 1\nprint z80:pc\nprint z80:sp\nprint z80:af\nprint spectrum:frames\nexit 0\nend"
(BUILD/'fuse-checkpoint.txt').write_text(commands)
command = [r'C:\Program Files (x86)\Fuse\fuse.exe', '--machine', 'ts2068', '--speed', '5000',
           '--rom-ts2068-0', str(up/'ts2068-0.rom'), '--rom-ts2068-1', str(up/'ts2068-1.rom'),
           '--no-sound', '--no-loading-sound', '--no-confirm-actions',
           '--debugger-command', commands, '--dock', str(BUILD/'diagnostic-v02.dck')]
try:
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    result = subprocess.run(command, capture_output=True, text=True, timeout=60, startupinfo=startup)
    output = result.stdout + result.stderr
    status = 'checkpoint_completed' if (result.returncode == 0 and hex(symbols['menu_ready']) in output
                                        and 'error:' not in output.lower()) else 'unconfirmed'
    (BUILD/'fuse-v02-checkpoint.log').write_text(output)
except subprocess.TimeoutExpired as exc:
    output = str(exc)
    status = 'timeout'
    (BUILD/'fuse-v02-checkpoint.log').write_text(output)
record = dict(status=status, command=command, checkpoint=hex(symbols['menu_ready']),
              image_sha256=hashlib.sha256((BUILD/'diagnostic-v02.dck').read_bytes()).hexdigest(),
              limitation='A timeout or empty output is not evidence of a successful checkpoint.')
(BUILD/'fuse-v02-result.json').write_text(json.dumps(record,indent=2)+'\n')
print(status)
print(output[:2500])
