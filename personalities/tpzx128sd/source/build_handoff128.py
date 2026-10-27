"""Build HOME-resident launch TAPs; use unchanged production ROMs in slot 4."""
import hashlib
import json
from pathlib import Path
from z80_link import link

ROOT=Path(__file__).resolve().parent

def tap_block(payload):
    check=0
    for value in payload:check^=value
    body=payload+bytes([check])
    return len(body).to_bytes(2,'little')+body

def build(mode):
    path=ROOT/('build/rom/TPZX128.ROM' if mode=='zx128' else 'build/fs128-rom/TPZXSD.ROM')
    pair=path.read_bytes()
    signature=pair[:32]
    if signature==pair[16384:16416]:raise ValueError('ROM halves do not distinguish boot gate')
    number={'zx128':1,'zx128sd':2}[mode]
    source='''
 di
 ld sp,$9ff0
 xor a
 out ($f4),a
 out ($ff),a
 ld a,1
 out ($fe),a
 ld a,$48
 out (14),a
 ld a,$31
 out (14),a
 ld a,%d
 out (14),a
 ld a,%d
 out (14),a
wait_ack:
 in a,(14)
 cp $a7
 jr nz,wait_ack
 ; The replacement 128 controller presents the ROM through HOME.
 ; Keep F4=0: low DOCK would select RAM and bypass the ROM-half gate.
 ld ix,$ffff
wait_rom:
 ld hl,0
 ld de,signature
 ld b,32
check_rom:
 ld a,(de)
 cp (hl)
 jr nz,not_ready
 inc hl
 inc de
 djnz check_rom
 ; ROM 0 can appear only after the Pico releases the gate, at the end
 ; of PIO/DMA initialization. Enter its ordinary cold-start path.
 xor a
 ld i,a
 im 1
 jp 0
not_ready:
 dec ix
 push ix
 pop bc
 ld a,b
 or c
 jr nz,wait_rom
 ld a,2
 out ($fe),a
failed:
 halt
 jr failed
signature: db %s
'''%(number,0x48^0x31^number,','.join(str(v) for v in signature))
    code,symbols=link(source,0x8000)
    name=('H128' if mode=='zx128' else 'H128SD').ljust(10).encode('ascii')
    header=b'\0\3'+name+len(code).to_bytes(2,'little')+b'\0\x80\0\x80'
    return code,tap_block(header)+tap_block(b'\xff'+code),dict(
        mode=mode,origin=0x8000,symbols=symbols,rom_sha256=hashlib.sha256(pair).hexdigest(),
        rom_slot=4,handoff_revision=2,rom_poll_f4=0,
        physical_reset_required=False,hardware_tested=False)

def main():
    target=ROOT/'build/handoff128';target.mkdir(parents=True,exist_ok=True)
    for mode,name in (('zx128','H128'),('zx128sd','H128SD')):
        code,tap,manifest=build(mode)
        (target/(name+'.TAP')).write_bytes(tap)
        (target/(name+'.bin')).write_bytes(code)
        (target/(name+'.json')).write_text(json.dumps(manifest,indent=2))
        print(target/(name+'.TAP'))

if __name__=='__main__':main()
