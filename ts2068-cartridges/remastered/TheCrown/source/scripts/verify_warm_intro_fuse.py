"""Fuse check: decline replay, see ready intro, then enter a fresh game."""
import json
import re
import subprocess
from pathlib import Path
from package_leap_cartridge import load_symbols

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/crown-combined'
S=load_symbols(ROOT/'build/combined-runtime/build/test_basic.sym')
N=load_symbols(OUT/'intro.sym')
p=json.loads((OUT/'bytecode.json').read_text())
def label(name): return p['base']+next(s['offset'] for s in p['symbols'] if s['name']==name)
def at(name): return f'([{S["VM_IP"]}]+256*[{S["VM_IP"]+1}])=={label(name)}'
def scalar(name):
    translated=next(n['leap'] for n in p['sourceNames'] if n['original']==name and n['kind']=='scalar')
    index=next(s['index'] for s in p['symbols'] if s['name']==translated and s['kind']==0)
    base=f'[{S["RT_SYMTAB_PTR"]}]+256*[{S["RT_SYMTAB_PTR"]+1}]'
    return f'[{base}+{3*index+1}]+256*[{base}+{3*index+2}]'
commands=['set $stage 0',f'breakpoint {N["wait_key"]} if $stage==0','commands 1',
          'set $stage 1',f'set z80:pc {N["release_after"]}','continue','end',
          f'breakpoint {S["VM_RUN.loop"]} if {at("QL1401")} && $stage==1',
          'commands 2','set $stage 2',f'set {S["VM_IP"]} {label("QL3020")&255}',
          f'set {S["VM_IP"]+1} {label("QL3020")>>8}','continue','end',
          f'breakpoint {S["VM_RUN.loop"]} if {at("QZW2")} && $stage==2',
          'commands 3','set $stage 3',f'set {S["KBD_LASTK"]} 110',f'set {S["KBD_KEYHIT"]} 1','continue','end',
          f'breakpoint {N["wait_key"]} if $stage==3','commands 4']
commands += [f'print [{a}]' for a in (0xFAC0,0xFAC3,0xFAC6,S['VM_ERROR_CODE'],S['PORT_FF_SHADOW'])]
commands+=['set $stage 4',f'set z80:pc {N["release_after"]}','continue','end',
           f'breakpoint {S["VM_RUN.loop"]} if {at("QL1401")} && $stage==4','commands 5']
commands += ['print '+scalar(name) for name in ('LV','RM','HP')]
commands += [f'print [{S["VM_ERROR_CODE"]}]','exit 0','end']
si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW
r=subprocess.run([__import__('os').environ.get('FUSE_EXE', 'fuse'),'--machine','ts2068','--rom-ts2068-0',str(OUT/'stock-home.rom'),
                  '--rom-ts2068-1',str(OUT/'stock-exrom.rom'),'--dock',str(OUT/'program.dck'),
                  '--speed','5000','--no-sound','--debugger-command','\n'.join(commands)],
                 capture_output=True,text=True,timeout=60,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
(OUT/'fuse-warm-intro.log').write_text(r.stdout+r.stderr)
assert r.returncode==0,r.stdout+r.stderr
values=[int(v,16) for v in re.findall(r'^0x([0-9a-f]+)\s*$',r.stdout,re.M|re.I)]
assert len(values)==9 and values[:2]==[1,1] and values[3:]==[0,2,1,1,20,0],values
report={'emulator':'Fuse','decline_replay_returns_to_ready_intro':True,'full_initialization_repeated':False,
        'fresh_game':{'level':1,'room':1,'hp':20},'vm_error':0,'keyboard_gate':'Debugger key injection; physical key matrix separately tested in TSRun'}
(OUT/'fuse-warm-intro.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
