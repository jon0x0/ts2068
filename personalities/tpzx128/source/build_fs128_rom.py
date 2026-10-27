"""Temporary Spectrum 128 BASIC SD ROM; service image is supplied by USB REPL.

No Pico connection or installed-file writes. Baseline TPZX128.ROM is untouched.
"""
import hashlib
import json
from pathlib import Path
from z80_link import link

ROOT=Path(__file__).resolve().parent
REF=ROOT/'references/fs128'
BASE=0xa000
CAVE=0x39a1  # Disabled serial keypad, ends before 3B9F token-printing extension.


def driver(rom_symbols=None):
    if rom_symbols is None:_,rom_symbols=rom_shims()
    layout='\n'.join(line for line in (REF/'layout.inc').read_text().splitlines()
                     if ' equ ' in line.lower() and not line.strip().lower().startswith('work_base '))
    transport=(REF/'tpi_legacy.asm').read_text().replace('LEGACY_REPLY_BUFFER equ $e000','LEGACY_REPLY_BUFFER equ $b800').replace('LEGACY_REPLY_CAPACITY equ $1800','LEGACY_REPLY_CAPACITY equ $0800')
    files=(REF/'files_legacy.asm').read_text()
    files=files.replace('.read:  call tpi_rx\n        ld (hl),a', '.read:  call tpi_rx\n        call store_byte')
    source='''
WORK_BASE equ $b000
saved_sp equ $b700
saved_af equ $b702
saved_ix equ $b704
saved_len equ $b706
saved_bc equ $b708
saved_de equ $b70a
verify_mode equ $b70c
verify_failed equ $b70d
operation_status equ $b70e
saved_header equ $b680
selected_sd equ $b7f0
directory_mode equ $b7f1
directory_page equ $b7f2
jp filename_entry
jp load_entry
jp save_entry
jp directory_display
jp directory_next
enter:
 pop hl
 ld ($b710),hl
 di
 ld (saved_sp),sp
 push af
 pop hl
 ld (saved_af),hl
 ld (saved_ix),ix
 ld (saved_len),de
 ld (saved_de),de
 ld (saved_bc),bc
 ld sp,$b7e0
 push iy
 xor a
 ld (verify_failed),a
 ld hl,($b710)
 push hl
 ret
; Entry callers are ROM shims. Bootstrap has already acquired the service.
filename_entry:
 call enter
 xor a
 ld (directory_mode),a
 ld hl,(saved_de)
 ld de,COMMAND_BUFFER
 ld bc,(saved_bc)
 ld a,b
 or a
 jp nz,filename_error
 ld a,c
 cp 81
 jp nc,filename_error
 ldir
 xor a
 ld (de),a
 ld a,1
 ld (selected_sd),a
 ld a,($5c74)
 or a
 jr z,filename_save
 ld hl,COMMAND_BUFFER+4
 ld de,directory_name
 call command_equal
 jr nz,filename_normal_load
 ld hl,0
 ld (directory_page),hl
 ld a,1
 ld (directory_mode),a
 call directory_request
 jp c,filename_error
 jp filename_command
filename_normal_load:
 ld hl,COMMAND_BUFFER
 ld a,1
 call legacy_execute
 jp c,filename_error
 ; A filename mounts then lets the normal ROM immediately load a header.
 ; Only these two read commands terminate before normal tape parsing.
 ld hl,COMMAND_BUFFER+4
 ld de,directory_name
 call command_equal
 jr z,filename_command
 ld hl,COMMAND_BUFFER+4
 ld de,path_name
 call command_equal
 jr z,filename_command
 ld bc,0
 ld de,COMMAND_BUFFER
 ld a,1
 or a
 jr filename_finish
filename_command:
 ld hl,$b800
 xor a
 jr filename_finish
command_equal:
 ld a,(de)
 ld b,a
 ld a,(hl)
 and $df
 cp b
 ret nz
 ld a,b
 or a
 ret z
 inc hl
 inc de
 jr command_equal
directory_name: db 'DIR',0
path_name: db 'PATH',0
filename_save:
 ld hl,COMMAND_BUFFER+4
 ld a,(hl)
 and $df
 cp 'C'
 jr nz,save_command_names
 inc hl
 ld a,(hl)
 and $df
 cp 'D'
 jr nz,save_command_names
 inc hl
 ld a,(hl)
 cp ' '
 jr z,filename_save_command
save_command_names:
 ld hl,COMMAND_BUFFER+4
 ld de,close_name
 call command_equal
 jr z,filename_save_command
 ld hl,COMMAND_BUFFER+4
 ld de,rewind_name
 call command_equal
 jr z,filename_save_command
 jr filename_save_basename
filename_save_command:
 ld hl,COMMAND_BUFFER
 xor a
 call legacy_execute
 jp c,filename_error
 jp filename_command
close_name: db 'CLOSE',0
rewind_name: db 'REW',0
filename_save_basename:
 ld bc,(saved_bc)
 dec bc
 dec bc
 dec bc
 dec bc
 ld a,b
 or a
 jr nz,filename_error
 ld a,c
 or a
 jr z,filename_error
 cp 11
 jr nc,filename_error
 ld de,COMMAND_BUFFER+4
 ld a,1
 or a
 jr filename_finish
filename_error:
 scf
filename_finish:
 push af
 push bc
 push de
 push hl
 call end_session
 pop hl
 pop de
 pop bc
 pop af
 pop iy
 ld sp,(saved_sp)
 ei
 ret
load_entry:
 call enter
 ld hl,(saved_af)
 ld a,l
 and 1
 xor 1
 ld (verify_mode),a
 call valid_region
 jr c,load_error
 ld bc,(saved_len)
 ld de,(saved_ix)
 ld hl,(saved_af)
 ld a,h
 call legacy_read_block
 jr c,load_error
 ld a,(verify_failed)
 or a
 jr nz,load_error
 ld a,1
 jr load_finish
load_error:
 xor a
load_finish:
 ld (operation_status),a
 call end_session
 ld ix,(saved_ix)
 ld de,(saved_len)
 add ix,de
 ld de,0
 pop iy
 ld sp,(saved_sp)
 ld a,(operation_status)
 or a
 ei
 ret z
 scf
 ret
save_entry:
 call enter
 ld hl,(saved_af)
 ld a,h
 or a
 jr nz,save_data
 ld hl,(saved_ix)
 ld de,saved_header
 ld bc,17
 ldir
 jr save_ok
save_data:
 call valid_region
 jr c,save_error
 ; Keep original Spectrum header type, autostart and variable length fields.
 ld hl,NAME_BUFFER
 ld (hl),0
 inc hl
 ld (hl),0
 inc hl
 ld (hl),0
 inc hl
 ex de,hl
 ld hl,saved_header
 ld bc,17
 ldir
 ld hl,NAME_BUFFER
 ld b,20
 xor a
save_header_crc:
 xor (hl)
 inc hl
 djnz save_header_crc
 ld (hl),a
 ld hl,legacy_close_cmd
 xor a
 call legacy_execute
 jr c,save_error
 xor a
 ld e,a
 ld bc,17
 call legacy_make_pre
 call legacy_preheader
 jr c,save_error
 ld hl,NAME_BUFFER
 ld b,21
 ld d,0
save_header_send:
 ld a,(hl)
 inc hl
 call tpi_tx
 djnz save_header_send
 call legacy_wait_ready
 jr c,save_error
 call tpi_rx
 cp 1
 jr nz,save_error
 ld d,0
 ld a,$ff
 call tpi_tx
 xor a
 call tpi_tx
 xor a
 call tpi_tx
 ld hl,(saved_ix)
 ld bc,(saved_len)
 ld a,b
 or c
 jr z,save_crc
save_bytes:
 ld a,(hl)
 inc hl
 call tpi_tx
 dec bc
 ld a,b
 or c
 jr nz,save_bytes
save_crc:
 ld a,d
 call tpi_tx
 call legacy_wait_ready
 jr c,save_error
 xor a
 ld (LEGACY_TEXT),a
 call legacy_reply
 jr c,save_error
save_ok:
 ld a,1
 jr save_finish
save_error:
 xor a
save_finish:
 ld (operation_status),a
 call end_session
 pop iy
 ld sp,(saved_sp)
 ei
 ld a,(operation_status)
 or a
 ret nz
 rst 8
 db $12
; Reject transfers through reserved service RAM, ROM, or address wrap.
valid_region:
 ld hl,(saved_ix)
 ld a,h
 cp $40
 jr c,region_bad
 cp $a0
 jr c,region_low
 cp $c0
 jr c,region_bad
 ld de,(saved_len)
 add hl,de
 jr nc,region_ok
 ld a,h
 or l
 jr nz,region_bad
 jr region_ok
region_low:
 ld de,(saved_len)
 add hl,de
 jr c,region_bad
 ld de,$a000
 or a
 sbc hl,de
 jr c,region_ok
 ld a,h
 or l
 jr z,region_ok
region_bad:
 scf
 ret
region_ok:
 or a
 ret
store_byte:
 push bc
 ld b,a
 ld a,(verify_mode)
 or a
 jr z,store_write
 ld a,(hl)
 cp b
 jr z,store_done
 ld a,1
 ld (verify_failed),a
 jr store_done
store_write:
 ld (hl),b
store_done:
 ld a,b
 pop bc
 ret
end_session:
 ld hl,finish_command
 xor a
 call legacy_execute
 ret nc
 ; A failed completion handshake must never return into cartridge ROM.
session_stuck:
 ld a,2
 out ($fe),a
 di
 halt
 jr session_stuck
finish_command: db 'tpi:fsend',0
directory_request:
 ld hl,(directory_page)
 ld de,page_command+12
 ld b,4
directory_digit:
 ld a,h
 rrca
 rrca
 rrca
 rrca
 and 15
 add a,'0'
 cp ':'
 jr c,directory_digit_ready
 add a,7
directory_digit_ready:
 ld (de),a
 inc de
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 djnz directory_digit
 ld hl,page_command
 ld a,1
 jp legacy_execute
directory_next:
 call enter
 call directory_request
 jp c,filename_error
 jp filename_command
; This UI executes only AFTER end_session restored paging and memory.
; No SD/FIFO transaction remains open while the user reads or presses keys.
directory_display:
 call $0d6b
 ld a,2
 call $1601
 ld hl,$b801
 call directory_print
 ld a,22
 rst $10
 ld a,20
 rst $10
 xor a
 rst $10
 ld hl,scroll_prompt
 ld a,($b800)
 cp '+'
 jr z,directory_prompt
 ld hl,end_prompt
directory_prompt:
 call directory_print
directory_release:
 xor a
 in a,($fe)
 and $1f
 cp $1f
 jr nz,directory_release
 res 5,(iy+1)
directory_wait:
 halt
 ld bc,$7ffe
 in a,(c)
 bit 0,a
 jr z,directory_done
 bit 5,(iy+1)
 jr z,directory_wait
 ld a,($5c08)
 and $df
 cp 'N'
 jr z,directory_done
 ld a,($b800)
 cp '+'
 jr nz,directory_done
 ld hl,(directory_page)
 inc hl
 ld (directory_page),hl
 ld a,h
 or l
 jr z,directory_done
 call bootstrap_rom
 call directory_next
 jp c,directory_error
 jp directory_display
directory_done:
 xor a
 ld (directory_mode),a
 ld a,22
 rst $10
 ld a,20
 rst $10
 xor a
 rst $10
 ld b,31
directory_clear_prompt:
 ld a,' '
 rst $10
 djnz directory_clear_prompt
 ret
directory_print:
 ld a,(hl)
 or a
 ret z
 rst $10
 inc hl
 jr directory_print
directory_error:
 rst 8
 db $12
page_command: db 'tpi:dirpage 0000',0
scroll_prompt: db 'scroll? (N/SPACE to stop)',0
end_prompt: db 'End of directory - any key',0
'''
    source='bootstrap_rom equ %d\n'%rom_symbols['bootstrap']+source
    data,symbols=link(source.replace('jr ','jp ')+'\n'+layout+'\n'+transport+'\n'+files,BASE)
    if len(data)>0x1000:raise ValueError('Service code exceeds protected A000-AFFF')
    return data,symbols


def rom_shims():
    source='''
selected_sd equ $b7f0
filename_hook:
 call filename_raw
 jp c,io_error
 ret nz
 pop de
 call print_only
 jp $1b76
print_only:
 ld a,($b7f1)
 or a
 jp nz,$a009
 push hl
 call $0d6b
 ld a,2
 call $1601
 pop hl
print_reply_loop:
 ld a,(hl)
 or a
 ret z
 rst $10
 inc hl
 jr print_reply_loop
filename_raw:
 call $2bf1
 ld a,b
 or a
 jr nz,check_prefix
 ld a,c
 or a
 jr nz,check_prefix
 ld a,1
 or a
 ret
check_prefix:
 push hl
 push bc
 push de
 ld a,b
 or a
 jr nz,prefix_no
 ld a,c
 cp 4
 jr c,prefix_no
 ld hl,prefix
 ld b,4
prefix_loop:
 ld a,(de)
 and $df
 cp (hl)
 jr nz,prefix_no
 inc hl
 inc de
 djnz prefix_loop
 pop de
 pop bc
 pop hl
 push ix
 call bootstrap
 call $a000
 pop ix
 ret
prefix_no:
 pop de
 pop bc
 pop hl
 xor a
 ld (selected_sd),a
 inc a
 ret
prefix: db 'TPI',26,0
load_hook:
 push af
 ld a,(selected_sd)
 cp 1
 jr z,load_sd
 pop af
 inc d
 ex af,af'
 dec d
 jp $0559
load_sd:
 call $1f54
 jr c,load_sd_continue
 pop af
 rst $08
 db $0c
load_sd_continue:
 pop af
 call bootstrap
 jp $a003
save_hook:
 push af
 ld a,(selected_sd)
 cp 1
 jr z,save_sd
 pop af
 ld hl,$053f
 jp $04c5
save_sd:
 pop af
 call bootstrap
 jp $a006
save_control:
 ld a,(selected_sd)
 cp 1
 jr z,save_control_sd
 push hl
 ld a,$fd
 jp $0973
save_control_sd:
 push hl
 push ix
 ld de,17
 xor a
 call $04c2
 pop ix
 pop hl
 ld e,(ix+11)
 ld d,(ix+12)
 push hl
 pop ix
 ld a,$ff
 jp $04c2
bootstrap:
 push af
 push bc
 push de
 push hl
 di
 xor a
 out ($0e),a
 ld de,20
 ld bc,0
bootstrap_wait:
 in a,($0e)
 cp $a5
 jr z,bootstrap_ready
 dec bc
 ld a,b
 or c
 jr nz,bootstrap_wait
 dec de
 ld a,d
 or e
 jr nz,bootstrap_wait
 jp io_error
bootstrap_ready:
 call receive
 cp 1
 jp nz,io_error
 call receive
 cp 7
 jp nz,io_error
 call receive
 cp 1
 jp nz,io_error
 call receive
 ld c,a
 call receive
 ld b,a
 ld a,b
 cp $10
 jp nc,io_error
 or c
 jp z,io_error
 ld hl,$a000
 ld d,0
bootstrap_copy:
 call receive
 ld (hl),a
 xor d
 ld d,a
 inc hl
 dec bc
 ld a,b
 or c
 jr nz,bootstrap_copy
 call receive
 xor d
 jp nz,io_error
 pop hl
 pop de
 pop bc
 pop af
 ret
receive:
 push bc
 ld b,18
receive_delay:
 djnz receive_delay
 pop bc
 in a,($0e)
 ret
io_error:
 ei
 rst 8
 db $12
'''
    data,symbols=link(source,CAVE)
    if CAVE+len(data)>0x3b3b:raise ValueError('ROM shims overwrite shared 128 BASIC extensions')
    return data,symbols


def build():
    shims,rs=rom_shims();blob,symbols=driver(rs)
    baseline=(ROOT/'build/rom/TPZX128.ROM').read_bytes()
    roms=[bytearray(baseline[:16384]),bytearray(baseline[16384:])]
    changes=[]
    def patch(bank,address,expected,data,reason):
        if bytes(roms[bank][address:address+len(expected)])!=expected:
            raise ValueError('Guard failed at %d:%04X'%(bank,address))
        old=bytes(roms[bank][address:address+len(data)])
        roms[bank][address:address+len(data)]=data
        changes.append(dict(bank=bank,address=address,before=old.hex(),after=data.hex(),reason=reason))
    def jp(symbol):return bytes([0xc3,rs[symbol]&255,rs[symbol]>>8])
    patch(1,0x0631,bytes.fromhex('cdf12b'),bytes([0xcd,rs['filename_hook']&255,rs['filename_hook']>>8]),'Fetch full tpi: filename before ten-character truncation')
    filename_site=bytes(roms[0]).find(bytes.fromhex('eff12b21f6ff'))
    if filename_site<0:raise ValueError('128 filename fetch not found')
    shim128,_=link('rst $28\ndw %d\njr c,failed\njp nz,%d\nrst $28\ndw %d\nret\nfailed:call $05ac\ndb $12'
                   %(rs['filename_raw'],filename_site+3,rs['print_only']),0x2380)
    patch(0,filename_site,bytes.fromhex('eff12b'),bytes.fromhex('c38023'),'128 BASIC full filename bridge')
    patch(0,0x2380,bytes(roms[0][0x2380:0x2380+len(shim128)]),shim128,'128 command bridge with normal parameter continuation')
    patch(1,0x0556,bytes.fromhex('140815'),jp('load_hook'),'Conditional SD LOAD/VERIFY block hook, tape fallback retained')
    patch(1,0x04c2,bytes.fromhex('213f05'),jp('save_hook'),'Conditional SD SAVE block hook, tape fallback retained')
    patch(1,0x0970,bytes.fromhex('e53efd'),jp('save_control'),'Skip tape keypress and pause only for SD SAVE')
    patch(1,0x3876,bytes.fromhex('cd423a'),bytes(3),'Skip serial-keypad interrupt wrapper before reusing its disabled code')
    patch(1,0x3b80,bytes.fromhex('fdcb0166'),bytes.fromhex('c3602600'),'INKEY$ uses keyboard only; avoid reclaimed serial-keypad code')
    patch(1,CAVE,bytes(roms[1][CAVE:CAVE+len(shims)]),shims,'Disabled serial keypad area; preserve 3B9F token extension')
    sequence=bytes.fromhex('22b25c')
    offset=bytes(roms[0]).find(sequence)
    if offset<0:raise ValueError('Physical RAM top initialization not found')
    shim,_=link('ld hl,$9fff\nld ($5cb2),hl\nld ($5cb4),hl\njp %d'%(offset+3),0x2370)
    patch(0,offset,sequence,bytes.fromhex('c37023'),'Reserve HOME A000-BFFF after standard UDG initialization')
    patch(0,0x2370,bytes(roms[0][0x2370:0x2370+len(shim)]),shim,'Protected BASIC RAM top shim')
    startup_site=bytes(roms[0]).find(bytes.fromhex('116105cd7d05'))
    if startup_site<0:raise ValueError('Sinclair startup message call not found')
    branding,_=link('call $057d\nld a,13\nrst $10\nld a,13\nrst $10\nld de,interface_message\ncall $057d\nret\n'
                    'interface_message: db $7f," 2023 Timex Pico Interfac",$e5',0x23a0)
    patch(0,startup_site+3,bytes.fromhex('cd7d05'),bytes.fromhex('cda023'),
          'Print Timex Pico Interface credit below original Sinclair startup message')
    patch(0,0x23a0,bytes(roms[0][0x23a0:0x23a0+len(branding)]),branding,
          'Startup credit: copyright 2023 Timex Pico Interface')
    pair=b''.join(roms)
    manifest=dict(title='TSPico Spectrum 128 SD',filename='TPZXSD.ROM',protocol='legacy 1.00',
                  hardware_tested=False,baseline_sha256=hashlib.sha256(baseline).hexdigest(),
                  sha256=hashlib.sha256(pair).hexdigest(),patches=changes,
                  service_bytes=len(blob),service_sha256=hashlib.sha256(blob).hexdigest(),
                  symbols=symbols,rom_symbols=rs,reserved_home=[0xa000,0xbfff],
                  limitations=['Temporary USB REPL service loop required; no persistent Pico changes',
                               '8 KiB HOME reservation reduces BASIC RAM; CODE transfers through it rejected',
                               '2.3 native backend not implemented; legacy only',
                               'General BASIC integration requires physical validation'])
    return pair,blob,manifest


def main():
    pair,blob,manifest=build()
    out=ROOT/'build/fs128-rom';out.mkdir(parents=True,exist_ok=True)
    (out/'TPZXSD.ROM').write_bytes(pair)
    (out/'service.bin').write_bytes(blob)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    (ROOT/'firmware/fs128_image.py').write_text('"""Generated temporary HOME service image; definitions only."""\nFS128_BASIC_IMAGE='+repr(blob)+'\n')
    print(out/'TPZXSD.ROM')


if __name__=='__main__':main()
