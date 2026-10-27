"""Build a stack-free, interrupt-free TSPico memory diagnostic, not a 128 BASIC ROM."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def build(font_rom):
    if len(font_rom)!=16384:
        raise ValueError('A 16K Spectrum font ROM is required')
    code=bytearray();labels={};fixups=[]
    def emit(*values):code.extend(values)
    def label(name):labels[name]=len(code)
    def jump(op,name):
        emit(op,0,0);fixups.append((len(code)-2,name))
    def border(value):emit(0x3e,value,0xd3,0xfe)
    def colour(row,value):
        address=0x5800+row*32
        emit(0x21,address&255,address>>8,0x06,32,0x3e,value)
        name='colour_'+str(len(code));label(name)
        emit(0x77,0x23,0x10,0xfc)  # LD (HL),A; INC HL; DJNZ -4
    def ram_test(start,end,name):
        # Two full write/read sweeps with address-dependent data and its inverse.
        # No stack, CALL, interrupts, ROM selection, or bank-select OUT.
        for inverse in (0,255):
            for read in (False,True):
                emit(0x21,start&255,start>>8)
                loop=f'{name}_{inverse}_{read}';label(loop)
                emit(0x7c,0xad)  # LD A,H; XOR L
                if inverse:emit(0xee,255)
                if read:
                    emit(0xbe);jump(0xc2,name+'_fail')
                else:emit(0x77)
                emit(0x23,0x7c,0xfe,end)
                jump(0xc2,loop)
    emit(0xf3,0xaf,0xd3,0xff,0xd3,0xf4)  # DI; normal SCLD; all HOME RAM
    border(1)
    emit(0x21,0,0x10,0x11,0,0x40,0x01,0,0x1b,0xed,0xb0)
    colour(4,0x20)  # Screen copy completed: green PAPER, black INK.
    colour(8,0x30)
    ram_test(0x8000,0xc0,'home')
    colour(8,0x20)
    colour(12,0x30)
    emit(0x3e,0xc0,0xd3,0xf4)  # Map only C000-FFFF to fixed DOCK page.
    border(6)
    ram_test(0xc000,0,'dock')
    colour(12,0x20)
    colour(16,0x20)
    label('pass');border(4);jump(0xc3,'pass')
    for name,row in (('home',8),('dock',12)):
        label(name+'_fail');colour(row,0x10);border(2)
        label(name+'_halt');jump(0xc3,name+'_halt')
    for offset,name in fixups:
        address=labels[name];code[offset:offset+2]=address.to_bytes(2,'little')
    if len(code)>0x1000:raise ValueError('Code overlaps display data')
    display=bytearray(6912);display[6144:]=bytes([0x38])*768
    for row,text in ((0,'TSPICO NO PAGING TEST'),(4,'ROM TO HOME SCREEN'),
                     (8,'HOME RAM 8000-BFFF'),(12,'FIXED DOCK C000-FFFF'),
                     (16,'COMPLETE WHEN THIS ROW IS GREEN')):
        for col,char in enumerate(text):
            glyph=font_rom[0x3d00+(ord(char)-32)*8:0x3d00+(ord(char)-32)*8+8]
            for line,bits in enumerate(glyph):
                y=row*8+line
                offset=((y&0xc0)<<5)|((y&7)<<8)|((y&0x38)<<2)|col
                display[offset]=bits
    # Pending labels are white; change only their row attributes as stages execute.
    rom=bytearray([255])*16384;rom[:len(code)]=code;rom[0x1000:0x2b00]=display
    return bytes(rom),{'labels':labels,'code_length':len(code),
                       'ports':[0xff,0xf4,0xfe],'destructive_ram':['4000-5AFF','8000-FFFF'],
                       'physical_dock_window':'initial fixed bank, C000-FFFF; no bank selection'}


def main():
    font=(ROOT/'build/rom/original-1.rom').read_bytes()
    rom,report=build(font)
    output=ROOT/'build/no-paging';output.mkdir(parents=True,exist_ok=True)
    for name,data in (('tspico-nopaging-16k.bin',rom),('tspico-nopaging.rom',rom*2)):
        (output/name).write_bytes(data)
        report[name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    report['hardware_tested']=False
    (output/'manifest.json').write_text(json.dumps(report,indent=2))
    print(output/'tspico-nopaging.rom')


if __name__=='__main__':main()
