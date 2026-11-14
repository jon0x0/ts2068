"""Explicit, reversible level-one compatibility patches, separate from banking."""
from pathlib import Path
import subprocess

def patch_input(root:Path,ram:bytes):
    out=root/'build/native'
    assembler=root.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
    result=subprocess.run([str(assembler),f'--raw={out/"input.bin"}',f'--sym={out/"input.sym"}',
       str(root/'src/native_input.asm')],capture_output=True,text=True,cwd=root)
    (out/'input_assembly.log').write_text(result.stdout+result.stderr)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    code=(out/'input.bin').read_bytes();b=bytearray(ram);changes=[]
    def replace(address,old,new,reason):
        at=address-0x4000
        assert bytes(b[at:at+len(old)])==old,f'Patch mismatch at {address:04X}'
        b[at:at+len(old)]=new
        changes.append(dict(address=address,length=len(new),reason=reason))
    replace(0x8b06,bytes.fromhex('2a fc 74 e9'),bytes.fromhex('c3 00 1a 00'),'Merge native sticks after selected keyboard decoder')
    replace(0xc011,bytes.fromhex('cd 14 8b'),bytes.fromhex('cd 00 1a'),'Native fire can start game with keyboard retained')
    replace(0x74fb,bytes.fromhex('04 2d 8b'),bytes.fromhex('02 14 8b'),'Default original redefinable keyboard (Q/W/O/K/P/Space); native sticks always active')
    replace(0xbfd0,bytes.fromhex('cd c5 c2'),bytes.fromhex('cd 00 1b'),'Wait for final key release before returning to menu; prevent Enter re-entry')
    return bytes(b),changes


