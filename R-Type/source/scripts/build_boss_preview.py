"""Separate r42 candidate based on released r41, preserving its loader and fixes."""
from pathlib import Path
import json, shutil, subprocess, hashlib, zipfile
from build_rocket_fix import code
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/fullgame/boss_preview_r42'

def main():
    source=ROOT/'build/fullgame/rocket_fix_r41'
    OUT.mkdir(parents=True,exist_ok=True)
    folder=OUT/'RTYPE';shutil.copytree(source/'RTYPE',folder,dirs_exist_ok=True)
    assembler=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
    p=subprocess.run([str(assembler),f'--raw={OUT/"boss_preview.bin"}',f'--sym={OUT/"boss_preview.sym"}',str(ROOT/'src/boss_preview.asm')],cwd=ROOT,capture_output=True,text=True)
    (OUT/'assembly.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
    hook=(OUT/'boss_preview.bin').read_bytes();assert len(hook)<=93
    # Enter before encounter setup. L3's ship is the level itself, not just its end.
    starts=[99,63,9,74,73,8,61,32]
    layouts=json.loads((ROOT/'build/fullgame/foundation/manifest.json').read_text())['levels']
    records=[]
    for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
        b=bytearray((source/f'{name}_region.bin').read_bytes())
        assert set(b[0x1fa3:0x2000])=={255}
        b[0x1fa3:0x1fa3+len(hook)]=hook
        raw=bytes(16384)+(ROOT/f'build/fullgame/foundation/level{n:02d}.raw').read_bytes()
        p=int.from_bytes(raw[0xc4b4:0xc4b6],'little');setting=0
        while raw[p]!=255 and raw[p]<starts[n-1]:
            if raw[p+2:p+4]==bytes([99,4]):setting=raw[p+4]
            p+=5
        assert raw[p]!=255 and raw[p]>=starts[n-1]
        # Native FEEB builds eight map columns. Begin one column BEFORE the first
        # event, otherwise its phase-zero event is already behind the next tick.
        b[0xd71:0xd75]=p.to_bytes(2,'little')+bytes([max(0,starts[n-1]-9),setting])
        # Only cold common-code source needs patching; it survives cached switches.
        if name=='boot':
            assert b[0x465f:0x4662]==bytes.fromhex('cd 06 8b')
            b[0x465f:0x4662]=bytes.fromhex('cd a3 1f')
            b[0xdd4b]=0
        (OUT/f'{name}_region.bin').write_bytes(b)
        tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP'
        (folder/tap).write_bytes(b''.join(code(f'RTPAGE{page:02X}',b[page*8192:(page+1)*8192],page)for page in range(8)))
        records.append(dict(file=tap,level=n,entry_column=starts[n-1],event_pointer=p,prior_setting=setting,sha256=hashlib.sha256(b).hexdigest()))
    for file in ['launcher.bin','demand_loader.sym']:
        shutil.copy2(source/file,OUT/file)
    with (folder/'README.txt').open('a')as f:f.write('\nBoss preview: during gameplay, press B, release it, then press B again. Restarts near the current stage boss encounter using native stage setup; not a boss-victory cheat. L3 restarts at the giant-ship entrance. Candidate pending validation.\n')
    manifest=dict(status='Boss checkpoint preview candidate, not validated',hook_bytes=len(hook),regions=records,graphics='Unchanged r41; selected art not integrated')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print(manifest)

if __name__=='__main__':main()
