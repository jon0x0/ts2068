"""Filesystem gateway diagnostic. Does not modify the working Spectrum ROM."""
import hashlib
import json
from pathlib import Path
from build_nopaging_rom import ROOT
from z80_link import link

REF=ROOT/'references/fs128'


def tape(name,payload):
    header=bytes([3])+name.encode('ascii').ljust(10,b' ')+len(payload).to_bytes(2,'little')+bytes.fromhex('00800080')
    def block(flag,data):
        body=bytes([flag])+data;crc=0
        for value in body:crc^=value
        return (len(body)+1).to_bytes(2,'little')+body+bytes([crc])
    return block(0,header)+block(255,payload)


def library():
    layout='\n'.join(line for line in (REF/'layout.inc').read_text().splitlines()
                     if ' equ ' in line.lower() and not line.strip().lower().startswith('work_base '))
    transport=(REF/'tpi_legacy.asm').read_text()
    transport=transport.replace('legacy_wait_ready:\n',
        'legacy_wait_ready:\n ld a,(DUAL_PROTOCOL)\n cp 2\n jp z,dual_ready\n')
    transport=transport.replace('legacy_preheader:\n',
        'legacy_preheader:\n ld a,(DUAL_PROTOCOL)\n cp 2\n jr nz,.legacy\n push hl\n call dual_reset\n pop hl\n ret c\n.legacy:\n')
    dual=(REF/'dual_transport.asm').read_text().replace('DUAL_PROTOCOL equ $eff3','DUAL_PROTOCOL equ $c3a0')
    detector=(REF/'detect_protocol.asm').read_text().replace('$eff3','DUAL_PROTOCOL')
    # Preserve the selected SD directory. PATH uses LOAD/TADDR=1 in the
    # installed legacy dispatcher; its eight-byte body keeps framing sizes.
    detector=detector.replace('detect_header: db $42,0,$ff,0,0,0,0,8,0,$b5',
                              'detect_header: db $42,1,$ff,0,0,0,0,8,0,$b4')
    detector=detector.replace("'tpi:cd /',$44^8^'t'^'p'^'i'^':'^'c'^'d'^' '^'/'",
                              "'tpi:path',$44^8^'t'^'p'^'i'^':'^'p'^'a'^'t'^'h'")
    source='WORK_BASE equ $c000\ndiagnostic_stage equ $c3a1\n'+layout+'\n'+transport+'\n'+(REF/'files_legacy.asm').read_text()+'\n'+dual+'\n'+detector
    return link(source,0x9000,{'loader_error':0x6300})


def build():
    lib,symbols=library()
    if 0x2c00+len(lib)>0x3d00:raise ValueError('Transport code exceeds reserved ROM area')
    src=[];attr_index=0
    def emit(text):src.extend(text.splitlines())
    def colour(row,value):
        nonlocal attr_index
        label='attr_'+str(attr_index);attr_index+=1
        emit('ld hl,%d\nld b,32\nld a,%d\n%s: ld (hl),a\ninc hl\ndjnz %s'%(0x5800+row*32,value,label,label))
    def check_payload(tag):
        emit('ld hl,$8000\nld b,0\nld d,0\n%s: ld a,(hl)\ncp d\njp nz,loader_error\ninc hl\ninc d\ndjnz %s'%(tag,tag))
    def page(value):emit('ld bc,$7f0f\nld a,%d\nout (c),a'%value)
    emit('di\nxor a\nout ($ff),a\nout ($f4),a\nld sp,$bfff\nld a,1\nout ($fe),a\nld hl,$1000\nld de,$4000\nld bc,$1b00\nldir')
    emit('ld hl,$c000\nld de,$c001\nld bc,$3ff\nld (hl),0\nldir')
    page(0x13)
    emit('ld a, $c0\nout ($f4),a\nld a,$53\nld ($c000),a\nxor a\nout ($f4),a')
    colour(4,0x20);colour(8,0x30)
    emit('xor a\nout ($0e),a\nld de,20\nld bc,0\ncookie_wait: in a,($0e)\ncp $a5\njr z,cookie_ok\ndec bc\nld a,b\nor c\njr nz,cookie_wait\ndec de\nld a,d\nor e\njr nz,cookie_wait\njp loader_error')
    emit('cookie_ok: call tpi_rx\nld ($c3a2),a\ncp 1\njr z,cookie_protocol_ok\ncp 2\njp nz,loader_error\ncookie_protocol_ok: call tpi_rx\ncp 7\njp nz,loader_error\ncall tpi_rx\nor a\njp nz,loader_error')
    emit('call detect_protocol\njp c,loader_error\nld a,($c3a2)\nld hl,DUAL_PROTOCOL\ncp (hl)\njp nz,loader_error')
    colour(8,0x20);colour(12,0x30)
    emit('ld hl,input_name\nld de,$8000\nld bc,256\ncall f_load\njp c,loader_error')
    check_payload('verify_input')
    emit('ld hl,output_name\nld de,$8000\nld bc,256\ncall f_save\njp c,loader_error')
    emit('ld hl,$8000\nld b,0\nclear_payload: ld (hl),0\ninc hl\ndjnz clear_payload')
    emit('ld hl,reload_name\nld de,$8000\nld bc,256\ncall f_load\njp c,loader_error')
    check_payload('verify_reload')
    colour(12,0x20);colour(16,0x30)
    emit('ld hl,exit_command\nxor a\ncall legacy_execute\njp c,loader_error')
    # legacy_reply includes the retained original client settle guard. This
    # diagnostic has a HOME stack and identical executable ROM halves during
    # restoration. It verifies paging afterward, not a production return ABI.
    emit('ld a,$c0\nout ($f4),a\nld a,($c000)\ncp $53\njp nz,loader_error\nld a,($3ff0)\ncp $a1\njp nz,loader_error')
    page(7);emit('ld a,$77\nld ($c000),a')
    page(0x13);emit('ld a,($c000)\ncp $53\njp nz,loader_error')
    colour(16,0x20);colour(20,0x20)
    emit('pass: ld a,4\nout ($fe),a\ndi\nhalt\njp pass\ninput_name: db "FS128.TAP",0\noutput_name: db "FSOUT",0\nreload_name: db "FSOUT.TAP",0\nexit_command: db "tpi:fsend",0')
    main,main_symbols=link('\n'.join(src),0x6000,symbols)
    if len(main)>=0x300:raise ValueError('Diagnostic main overlaps error entry')
    error,_=link('ld a,2\nout ($fe),a\ndi\nhalt_here: halt\njr halt_here',0x6300)
    boot,_=link('di\nxor a\nout ($ff),a\nout ($f4),a\nld sp,$bfff\n'
                'ld hl,$0400\nld de,$6000\nld bc,%d\nldir\n'
                'ld hl,$0300\nld de,$6300\nld bc,%d\nldir\n'
                'ld hl,$2c00\nld de,$9000\nld bc,%d\nldir\njp $6000'
                %(len(main),len(error),len(lib)))
    font=(ROOT/'build/rom/original-1.rom').read_bytes()
    display=bytearray(6912);display[6144:]=bytes([0x38])*768
    rows=((0,'TSPICO 128 FILESYSTEM TEST'),(4,'ROM AND PAGING'),(8,'SERVICE AND PROTOCOL'),
          (12,'SD LOAD SAVE RELOAD'),(16,'PAGING RESTORED'),(20,'COMPLETE WHEN GREEN'))
    for row,text in rows:
        for col,char in enumerate(text):
            for line,bits in enumerate(font[0x3d00+(ord(char)-32)*8:0x3d00+(ord(char)-32)*8+8]):
                y=8*row+line
                display[((y&0xc0)<<5)|((y&7)<<8)|((y&0x38)<<2)|col]=bits
    halves=[]
    for half in (0,1):
        rom=bytearray([255])*16384
        rom[:len(boot)]=boot;rom[0x400:0x400+len(main)]=main
        rom[0x300:0x300+len(error)]=error
        rom[0x1000:0x2b00]=display;rom[0x2c00:0x2c00+len(lib)]=lib
        rom[0x3ff0]=0xa0+half;halves.append(bytes(rom))
    return halves,{'main_bytes':len(main),'transport_bytes':len(lib),
                   'execution':'HOME RAM: main 6000, error 6300, transport 9000',
                   'symbols':main_symbols,'hardware_tested':False,
                   'limitations':['diagnostic only; no Spectrum BASIC hooks yet',
                                  'legacy backend only; modern selection path retained for future adapter',
                                  'return diagnostic uses retained legacy settle guard']}


def main():
    halves,report=build();out=ROOT/'build/fs128-test';out.mkdir(parents=True,exist_ok=True)
    data=b''.join(halves);(out/'TPZXFST.ROM').write_bytes(data)
    (out/'FS128.TAP').write_bytes(tape('FS128',bytes(range(256))))
    report['sha256']=hashlib.sha256(data).hexdigest()
    (out/'manifest.json').write_text(json.dumps(report,indent=2))
    print(out/'TPZXFST.ROM')


if __name__=='__main__':main()
