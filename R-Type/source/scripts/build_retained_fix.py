"""Build real per-level disk loading from the preserved r32 gameplay image."""
from pathlib import Path
import subprocess,json,struct,hashlib,sys,zipfile,re
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_true_black import change
def block(flag,payload):
 c=flag
 for v in payload:c^=v
 return struct.pack('<H',len(payload)+2)+bytes([flag])+payload+bytes([c])
def code(name,data,address):
 return block(0,bytes([3])+name.encode().ljust(10,b' ')+struct.pack('<HHH',len(data),address,0x8000))+block(255,data)
def main():
 out=ROOT/'build/fullgame/retained_fix_r40';out.mkdir(parents=True,exist_ok=True);folder=out/'RTYPE';folder.mkdir(exist_ok=True)
 asm=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
 def assemble(name,text):
  p=out/(name+'.asm');p.write_text(text);r=subprocess.run([str(asm),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],cwd=ROOT,capture_output=True,text=True);p.with_suffix('.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
  return p.with_suffix('.bin').read_bytes()
 old=(ROOT/'src/fullgame_preloader.asm').read_text()
 checksum=old[old.index('checksum_address:'):old.index('page_registers:')]
 transport=old[old.index('select_region:'):old.index('video_settle:')]
 transport=transport.replace('LD (REQUEST),A','LD (REQUEST),A\n        PUSH AF\n        LD A,7\n        LD (LOAD_OP),A\n        POP AF',1)
 text=(ROOT/'src/cache_loader_head.asm').read_text()+'\n'+checksum+'\n'+transport+'\n'+old[old.index('video_settle:'):old.index('bad_header:')]
 # Secondary standard attributes must stay black while HOME6000 holds code.
 text=text.replace('$7800','$7B00')
 text=text.replace('cache_loaded:\n', 'cache_loaded:\n        LD A,$41\n        OUT ($FF),A\n',1)
 # Prepare the primary loading screen while secondary remains hidden.
 text=text.replace('draw_loading:\n        LD A,0\n        OUT ($FF),A\n', 'draw_loading:\n        LD HL,$7800\n        LD DE,$7801\n        LD BC,$2FF\n        LD (HL),0\n        LDIR\n',1)
 text=text.replace('        LD A,(DESIRED)\n        LD (load_text+14),A', '        XOR A\n        OUT ($FF),A\n        LD A,(DESIRED)\n        LD (load_text+14),A',1)
 tail=(ROOT/'src/cache_transition_tail.asm').read_text()
 text+='\nfinish_tail:\n        DISP $5E00\n'+tail+'\n        ENT\nfinish_tail_end:\nfont: INCBIN "assets/fullgame_preloader_font.bin"\n        INCLUDE "third_party/fullgame_tspico/ram512_transport.inc"\n        INCLUDE "third_party/fullgame_tspico/ram512b_files.inc"\nprogram_end:\n        ASSERT $ < $7800\n'
 loader=assemble('demand_loader','DRIVER_LENGTH EQU 0\n'+text)
 symbols={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9A-Fa-f]+)',(out/'demand_loader.sym').read_text())}
 original=(ROOT/'src/fullgame_gateway.asm').read_text()
 suffix=original[original.index('select_region:'):];suffix=suffix.replace('DB $42,0,$FF,1,0,0,0,11,0,0','DB $42,0,$FF,1,0,14,0,11,0,0')
 suffix=suffix.replace('        LD A,1\n        OUT ($F4),A\n        LD B,8\nprime_selectors:', 'cache_prime_setup:\n        LD A,1\n        OUT ($F4),A\n        LD B,8\nprime_selectors:').replace('        XOR A\n        OUT ($F4),A\n        RET\ncommand_failed:', 'cache_prime_end:\n        XOR A\n        OUT ($F4),A\n        RET\ncommand_failed:')
 prefix=(ROOT/'src/cache_gateway_head.asm').read_text()
 prefix=f'LOADER_LENGTH EQU {len(loader)}\n'+prefix
 gateway=assemble('demand_gateway','DRIVER_LENGTH EQU 0\n'+prefix+suffix);assert len(gateway)<=400,len(gateway)
 gateway=assemble('demand_gateway',f'DRIVER_LENGTH EQU {len(gateway)}\n'+prefix+suffix)
 loader=assemble('demand_loader',f'DRIVER_LENGTH EQU {len(gateway)}\n'+text)
 symbols={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9A-Fa-f]+)',(out/'demand_loader.sym').read_text())}
 fast_tail=assemble('cache_fast_tail',f'DRIVER_LENGTH EQU {len(gateway)}\n        ORG $5E00\n'+tail);assert len(fast_tail)<=288
 gate_symbols={k:int(v,16)for k,v in re.findall(r'(\w+): EQU 0x([0-9A-Fa-f]+)',(out/'demand_gateway.sym').read_text())}
 fast=assemble('cache_fast_dispatch',f'''        ORG $0D40
        LD A,$81
        OUT ($F4),A
        LD HL,$FBE0
        LD DE,$5E00
        LD BC,{len(fast_tail)}
        LDIR
        LD A,1
        OUT ($F4),A
        LD HL,${((gate_symbols['cache_prime_setup']-gate_symbols['command_ok']-2)<<8)|0x18:04X}
        LD (${gate_symbols['command_ok']:04X}),HL
        LD HL,$80C3
        LD (${gate_symbols['cache_prime_end']:04X}),HL
        LD A,$0D
        LD (${gate_symbols['cache_prime_end']+2:04X}),A
        LD A,($FDA4)
        SUB '1'
        ADD A,A
        RET
        ASSERT $ <= $0D70
''')
 poll=assemble('cache_ready_poll','''        ORG $0D80
        LD A,($FDA4)
        LD C,A
        LD DE,0
cache_ready_loop:
        LD A,($0D70)
        CP C
        JR Z,cache_is_ready
        DEC DE
        LD A,D
        OR E
        JR NZ,cache_ready_loop
        SCF
        RET
cache_is_ready:
        XOR A
        RET
        ASSERT $ < $0E00
''')
 blank=assemble('cache_blank_transition','''        ORG $0DA0
        LD A,1
        OUT ($F4),A
        LD HL,$6000
        LD DE,$6001
        LD BC,$1AFF
        LD (HL),0
        LDIR
        LD A,$41
        OUT ($FF),A
        RET
        ASSERT $ < $0E00
''')
 reverse_init=assemble('reverse_table_init','''        ORG $0DC0
        CALL $86C3
        CALL $FCC8
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        LD HL,$5D00
reverse_next:
        LD A,L
        LD B,8
reverse_bit:
        RRCA
        RL D
        DJNZ reverse_bit
        LD (HL),D
        INC L
        JR NZ,reverse_next
        POP HL
        POP DE
        POP BC
        POP AF
        RET
        ASSERT $ <= $0E00
''')
 title_source=(ROOT/'src/title_screen_init.asm').read_text()
 title_source=title_source.replace('        LD A,$40\n        OUT ($FF),A\n', '')
 title_source=title_source.replace('        LD HL,$4000', '        PUSH DE\n        LD HL,$7800\n        LD DE,$7801\n        LD BC,$2FF\n        LD (HL),0\n        LDIR\n        POP DE\n        LD A,$41\n        OUT ($FF),A\n        LD HL,$4000',1).replace('LD A,$47','LD A,7')
 title_init=assemble('hidden_title_init','MODE_SHADOW EQU $3FF0\nRUNTIME_MAP EQU 9\n'+title_source)
 debug_screen=assemble('debug_screen',(ROOT/'src/debug_ram_screen.asm').read_text())
 debug_poll=assemble('debug_poll','''        ORG $0DE0
        LD A,($0D7F)
        OR A
        RET Z
        LD BC,$FDFE
        IN A,(C)
        AND 4
        RET NZ
        LD B,$FE
        IN A,(C)
        AND 1
        RET NZ
        LD A,$19
        OUT ($F4),A
        JP $8000
        ASSERT $ <= $0E00
''')
 irq=assemble('debug_irq','''        ORG $FD20
        PUSH AF
        IN A,($F4)
        LD ($FBCA),A
        LD A,9
        OUT ($F4),A
        PUSH BC
        PUSH DE
        CALL $0DE0
        JP $BE26
        ASSERT $ <= $FD40
''')
 retained_clear=assemble('retained_clear','''        ORG $FCC8
        PUSH AF
        PUSH BC
        PUSH DE
        PUSH HL
        LD HL,$6000
        LD DE,$6001
        LD BC,$0FFF
        LD (HL),0
        LDIR
        LD HL,$7000
        LD B,8
clear_lower_page:
        PUSH BC
        LD D,H
        LD E,1
        LD BC,127
        LD (HL),0
        LDIR
        INC H
        LD L,0
        POP BC
        DJNZ clear_lower_page
        POP HL
        POP DE
        POP BC
        POP AF
        RET
        ASSERT $ <= $FD20
''')
 entry=assemble('demand_entry',f'DRIVER_LENGTH EQU {len(gateway)}\n'+(ROOT/'src/fullgame_transition_entry.asm').read_text())
 source=(ROOT/'build/fullgame/restart_r32/RType_TS2068_restart_r32.ram512').read_bytes()
 regions=[bytearray(source[n*65536:(n+1)*65536])for n in range(8)]
 boot=bytearray(regions[0])
 # Cold copy displays a clean primary screen while native code initializes.
 # Preserve ROM7 palette and title atlas: these are source assets, not display RAM.
 boot[0xdd48:0xdd4b]=bytes([1,0,1])
 runtime=change((ROOT/'build/fullgame/level01/runtime_region.bin').read_bytes(),1,True)
 for bank in (1,2,3):regions[0][bank*8192:(bank+1)*8192]=runtime[bank*8192:(bank+1)*8192]
 for region in [boot]+regions:
  region[0xa08:0xa08+len(entry)]=entry;region[0xa30:0xa30+len(gateway)]=gateway
  region[0xd40:0xd40+len(fast)]=fast;region[0xd80:0xd80+len(poll)]=poll;region[0xda0:0xda0+len(blank)]=blank;region[0xd70]=49+(0 if region is boot else next(i for i,v in enumerate(regions)if v is region));region[0xfbe0:0xfbe0+len(fast_tail)]=fast_tail
  region[0xf20:0xf20+len(title_init)]=title_init
  assert region[0x1485:0x1488]==bytes.fromhex('cd c3 86')
  region[0xdc0:0xdc0+len(reverse_init)]=reverse_init
  region[0x1485:0x1488]=bytes.fromhex('cd c0 0d')
  region[0xd910:0xd91c]=bytes.fromhex('3e 09 d3 f4 5e 23 56 3e 19 d3 f4 c9')
  region[0xde0:0xde0+len(debug_poll)]=debug_poll
  region[0xdd20:0xdd20+len(irq)]=irq
  region[0xd7f]=0 if region is boot else 1
  if region is not boot:
   region[0x8000:0x8000+len(debug_screen)]=debug_screen
 assert set(boot[0xdcc8:0xdd20])=={255}
 boot[0xdcc8:0xdcc8+len(retained_clear)]=retained_clear
 def stream(name,region):
  data=b''.join(code(f'RTPAGE{page:02X}',region[page*8192:(page+1)*8192],page)for page in range(8));(folder/name).write_bytes(data);return dict(file=name,sha256=hashlib.sha256(region).hexdigest(),bytes=len(region))
 records=[stream('RTBOOT.TAP',boot)]+[stream(f'LEVEL{n:02d}.TAP',region)for n,region in enumerate(regions,1)]
 (out/'boot_region.bin').write_bytes(boot)
 for n,region in enumerate(regions,1):(out/f'level{n:02d}_region.bin').write_bytes(region)
 # BASIC loads the code at8000; a short HOME trampoline relocates it to6000.
 bootstrap=assemble('disk_bootstrap',f'''        ORG $8000
        DI
        LD SP,$FFF0
        XOR A
        OUT ($F4),A
        LD HL,resident
        LD DE,$6000
        LD BC,{len(loader)}
        LDIR
        JP ${symbols['boot_entry']:04X}
resident:
''')
 player=bootstrap+loader
 kw=lambda n:bytes([n])+b' '
 val=lambda n:kw(176)+f'"{n}"'.encode()
 def line(n,b):return struct.pack('>H',n)+struct.pack('<H',len(b)+1)+b+b'\r'
 program=b''.join(line(n,b)for n,b in[(10,kw(253)+val(32767)),(20,kw(239)+b'"" '+kw(175)),(30,kw(242)+val(60)),(40,kw(249)+kw(192)+val(32768)),(50,kw(226))])
 header=bytes([0])+b'RTYPE DISK'+struct.pack('<HHH',len(program),10,len(program));launch=block(0,header)+block(255,program)+code('RTYPE LOAD',player,32768);(folder/'RTFULL.TAP').write_bytes(launch);(out/'launcher.bin').write_bytes(player)
 readme='R-Type per-level disk game\n\nPut this RTYPE folder anywhere under TAP, including nested subdirectories. Open that folder and load RTFULL.TAP. Keep RTBOOT.TAP and LEVEL01.TAP..LEVEL08.TAP beside the launcher. No command changes directory.\nStartup loads level1 only. Title keys1-8 select a starting level; release then Fire or keyboard0. Other levels load when needed, with LOADING LEVEL n and local page00..07. M toggles music. Transfers are verified before the level is used.\nUses the original shared-FIFO disk protocol and expansion RAM. No firmware changes. Physical validation pending. On error the screen shows ERROR, STEP and PAGE; keep those details.\nAll eight loaded levels remain resident. Revisited levels use RAM only, with their mutable render buffers rebuilt before play. Hardware bank-command latency still applies. Idle-title prefetch is not implemented. Mirrored sprite reversal table rebuilt on every gameplay initialization. Hidden transition helper is outside screen attributes; title and loading screen are prepared before display. Debug build: hold Caps Shift+D on levels2-8 to freeze on a diagnostic screen. Photograph it, then press Space to redraw the captured bitmap and ECM RAM; photograph that view too, then reset. Key is disabled on cold level1 to preserve its bootstrap. Retained playfield bitmap is explicitly cleared on game initialization, preserving interleaved workspace. Hardware confirmation of the level3 artifact correction is pending.\n'
 (folder/'README.txt').write_text(readme)
 with zipfile.ZipFile(out/'RType_TS2068_retained_fix_r40.zip','w',zipfile.ZIP_DEFLATED)as z:
  for p in sorted(folder.iterdir()):z.write(p,'RTYPE/'+p.name)
 manifest=dict(status='Eight resident-level cache candidate; validation pending',loader_bytes=len(loader),gateway_bytes=len(gateway),startup_pages=8,cache_levels=8,immutable_asset_chunks=[0,1,4,5,6,7],mutable_chunks=[2,3],resident_field='FD48',valid_mask_field='FD4A',relative_directory=True,idle_prefetch=False,levels=records)
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print(manifest)
if __name__=='__main__':main()



