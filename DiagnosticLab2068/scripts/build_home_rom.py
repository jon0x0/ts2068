"""Separate16KiB U16 reset ROM; never modifies the cartridge build artifacts.

Reuses the cartridge's stackless RAM/boot/audio/IRQ implementations. Unsupported
external-ROM transfers are removed, and every HSR write forces HOME selected.
The generated variant source and a source-bound manifest make differences auditable.
"""
from pathlib import Path
import re, json, hashlib, subprocess
from build_suite import DEFAULT_ASSEMBLER
from suite_assets import pack
from generate_design_assets import offset

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/home'; OUT.mkdir(parents=True,exist_ok=True)

def build():
    stock=(ROOT.parent/'David Anderson/TS2068-Ref-Library/2068 ROMS/TS2068_U16.BIN').read_bytes()
    font=stock[0x3d00:0x4000]
    pool=bytearray(font)
    # Same24 guided AY records, relocated into HOME ROM.
    cart=(ROOT/'build/diagnostic-v02.bin').read_bytes()
    ay_addr=0x2000+len(pool); pool.extend(cart[0x4400:0x4580])
    definitions=[f'font_data EQU $2000']
    assets=[]
    def page(name,title,lines,status='ROM control / HOME edition'):
        pixels=bytearray(6144);attrs=bytearray([0x47]*768)
        def text(row,col,s,attr=0x47):
            assert col+len(s)<=32,(name,s)
            for x,ch in enumerate(s,col):
                for y in range(8): pixels[offset(x,row*8+y)]=font[(ord(ch)-32)*8+y]
                attrs[row*32+x]=attr
        attrs[:96]=bytes([0x4d])*96
        text(0,1,'TS2068 Diagnostic Lab / HOME',0x4d)
        text(2,1,title,0x4f);text(4,1,status,0x45)
        for row,s in lines: text(row,1,s)
        text(22,1,'Press a new key to stop/return',0x4f)
        return bytes(pixels+attrs)
    screens={
      'menu':page('menu','HOME ROM / choose a test',[(6,'1 Full: RAM/sound/keyboard'),(7,'2 RAM / failing-chip codes'),(8,'4 Keyboard'),(9,'5 Beeper / AY sound'),(10,'7 Overnight RAM'),(11,'9 SCLD interrupt test'),(12,'J Joysticks / EAR inputs'),(14,'0 Help / sound-code training'),(17,'No DOCK/video/ROM CRC tests')]),
      'fullinfo':page('fullinfo','HOME Full / coverage',[(6,'All 48K complete RAM'),(8,'Beeper + 24 AY sound steps'),(10,'Keyboard: user observation'),(13,'No cartridge banks/video/CRC'),(18,'1 Start / M Return')]),
      'fullsummary':page('fullsummary','HOME Full completed',[(6,'RAM + AY comparisons matched'),(8,'All 6 RAM chip paths matched'),(11,'Judge sound and keys yourself'),(15,'Unpressed keys are untested')]),
      'startupquick':page('startupquick','Reset / quick RAM',[(6,'00/FF checks all 48K'),(8,'Hold R complete / F HOME Full'),(11,'R ~84sec / F ~2min to keys'),(14,'Screen RAM is being tested'),(17,'Faults: sync / 2 / chip / bit')]),
      'startupfull':page('startupfull','Reset / selected tests',[(6,'R Complete RAM ~84 seconds'),(8,'F HOME Full RAM/sound/keys'),(11,'Release; new key cancels'),(14,'Screen RAM is being tested')]),
      'rammenu':page('rammenu','RAM / choose coverage',[(6,'1 Complete ~84 sec'),(8,'2 Patterns/bits ~41 sec'),(10,'3 March ~8 sec / 4 Addr ~8 sec'),(12,'5 Random ~3 sec / 6 Hold ~24s'),(16,'Can identify failing RAM chips')]),
      'rampass':page('rampass','All 6 RAM chips PASS',[(6,'All 48K comparisons matched'),(8,'U6 U7 U12 U13 U17 U18'),(12,'Only covered tests passed'),(15,'No intermittent-fault guarantee')]),
      'soak':page('soak','Overnight RAM',[(7,'Complete48K repeated passes'),(11,'~1.5 min/pass'),(14,'PASS COUNT:'),(17,'First mismatch stops'),(20,'Press any key to stop')]),
      'soakstop':page('soakstop','RAM soak / stopped',[(7,'No failures during the test'),(10,'Completed passes (hex):'),(14,'Count:'),(19,'Covered comparisons only')]),
      'soundmenu':page('soundmenu','Sound / choose',[(7,'1 Beeper / 15 seconds'),(10,'2 AY / 24 steps / 22 seconds')]),
      'beeper':page('beeper','Beeper / three tones',[(8,'Low red / mid magenta'),(12,'High green / about15 seconds'),(16,'Listen for all three')]),
      'help':page('help','Help / RAM sound codes',[(6,'Long sync / 2 / chip / bit'),(8,'1 U6 / 2 U7 / 3 U12'),(10,'4 U13 / 5 U17 / 6 U18'),(12,'Bit1-4;5 means multiple bits'),(16,'C Code training / P Inputs')]),
      'soundguide':page('soundguide','TRAINING / synthetic codes',[(6,'1 RAM example:2/6/2 U18/D5'),(10,'2 Bank example / 3 CPU example'),(15,'Examples are not failures'),(18,'M Return to Help')]),
      'pass':page('pass','Selected checks PASS',[(8,'Selected comparisons matched'),(14,'Covers this test on this run')]),
      'fail':page('fail','Mismatch / suspect path',[(7,'Digital comparison failed'),(14,'DETAIL:'),(15,'ADDRESS:'),(17,'REGISTER/PHASE:')]),
      'inputs':page('inputs','Joysticks / EAR observation',[(7,'EAR HIGH/LOW:'),(10,'JOY 1 RAW:'),(12,'JOY 2 RAW:'),(17,'Move/press each joystick'),(19,'Not automatic certification')]),
      'irqmenu':page('irqmenu','SCLD interrupt checks',[(8,'I Inhibit + arrival'),(13,'Early CPU checks run at reset'),(18,'U extended CPU unavailable')]),
      'unavailable':page('unavailable','Cartridge-edition test',[(8,'Not in the16K HOME edition'),(12,'Use the Diagnostic Lab cart')]),
    }
    # Preserve AY label/highlight coordinates and keyboard contact rectangles.
    from suite_assets import pages
    original,coords=pages(font)
    screens['aylisten']=original['aylisten']
    screens['inputs']=original['inputs']
    screens['keyboard']=page('keyboard','Keyboard / live contacts',[(19,'Green held / cyan released'),(20,'Test both CAPS separately'),(21,'CAPS+SPACE or ENTER+SPACE exits')],status='Press keys / timeout ~4 min')
    pix=bytearray(screens['keyboard'][:6144]); attrs=bytearray(screens['keyboard'][6144:])
    for name,rectangles in coords.items():
        if name=='BREAK': continue
        for cy,cx,width in rectangles:
            for y in [cy,cy+1]: attrs[y*32+cx:y*32+cx+width]=bytes([0x78])*width
            for x,ch in enumerate(name):
                for y in range(8): pix[offset(cx+x,cy*8+y)]=font[(ord(ch)-32)*8+y]
    screens['keyboard']=bytes(pix+attrs)
    glyphs={font[n*8:n*8+8]:n+32 for n in range(96)};glyphs[bytes(8)]=32
    for name,screen in screens.items():
        tiles=bytearray(768)
        for row in range(24):
            for col in range(32):
                glyph=bytes(screen[offset(col,row*8+y)] for y in range(8))
                assert glyph in glyphs,(name,row,col)
                ch=glyphs[glyph]; tiles[row*32+col]=0 if ch==32 else ch
        encoded=pack(tiles+screen[6144:]);addr=0x2000+len(pool);pool.extend(encoded)
        definitions += [f'load_{name}:',f' ld hl,${addr:04x}',' ld de,$6400',' ld bc,1536',' ld a,$40',' ld i,a',f' ld iy,render_{name}',' jp unpack',f'render_{name}:',f' ld iy,{name}_ready',' jp render_tiles']
        assets.append(dict(name=name,address=addr,packed=len(encoded)))
        (OUT/(name+'.screen')).write_bytes(screen)
    assert len(pool)<=8190,('HOME asset pool exceeds16K',len(pool))
    aliases={'videomenu':'unavailable','bars':'keyboard','standard':'unavailable','secondary':'unavailable','ecm':'unavailable','hires':'unavailable','mix128':'unavailable','rommenu':'unavailable','romresult':'unavailable','cpuinfo':'unavailable'}
    for name,dest in aliases.items(): definitions += [f'load_{name}:',f' jp load_{dest}']
    definitions+=['load_bank:'," ex af,af'",' ld b,a'," ex af,af'",' ld a,b',' cp 7',' jp z,load_beeper',' jp load_unavailable']
    definitions+=['unavailable_ready:',' jp result_wait']
    modules=(ROOT/'src/modules.asm').read_text()
    def omit(start,end,replacement):
        nonlocal modules
        a=modules.index(start);b=modules.index(end,a);modules=modules[:a]+replacement+'\n'+modules[b:]
    omit('fault_draw:\n','keyboard_ready:\n','fault_draw:\n jp fault_draw_done ; HOME minimal fault output is border/beeper only.')
    omit('bank_ready:\n','rommenu_ready:\n','bank_ready:\n jp load_beeper')
    omit('home_crc_select:\n','irqmenu_ready:\n','home_crc_select:\nexrom_crc_select:\nromresult_ready:\n jp load_unavailable')
    omit('cartridge_check:\n','cartridge_alarm:\n','cartridge_check:\n jp home_integrity')
    modules=modules[:modules.index('cpu_select:\n')]+'cpu_select:\ncpuinfo_ready:\n jp load_unavailable\n'
    modules=modules.replace('ld de,$4400',f'ld de,${ay_addr:04x}')
    modules=re.sub(r'^(\s*)out \(\$f4\),a',r'\1xor a\n\1out ($f4),a',modules,flags=re.M)
    main=(ROOT/'src/diagnostic.asm').read_text()
    main=main.replace(' DB 0,1\n DW entry\n DB $ee',' jp entry\n DS 5-$,255')
    main=main[:main.index(' INCLUDE "modules.asm"')]
    main=main.replace(' INCLUDE "../build/ram-tests.asm"',(ROOT/'build/ram-tests.asm').read_text())
    boot=(ROOT/'src/boot.asm').read_text()
    main=main.replace(' INCLUDE "boot.asm"',boot)
    main=re.sub(r'^(\s*)out \(\$f4\),a',r'\1xor a\n\1out ($f4),a',main,flags=re.M)
    keyboard=(ROOT/'build/keyboard-scan.asm').read_text()
    modules=modules.replace(' INCLUDE "../build/keyboard-scan.asm"',keyboard)
    integrity='''home_integrity:
 ld hl,0
 ld de,0
 ld bc,$3ffe
home_sum:
 ld a,(hl)
 add a,e
 ld e,a
 jp nc,home_sum_no_carry
 inc d
home_sum_no_carry:
 inc hl
 dec bc
 ld a,b
 or c
 jp nz,home_sum
 ld a,($3ffe)
 cp e
 jp nz,cartridge_alarm
 ld a,($3fff)
 cp d
 jp nz,cartridge_alarm
 jp cartridge_checked
'''
    code=main+modules+integrity+'\n'+'\n'.join(definitions)+'\nhome_code_end:\n ASSERT $ <= $2000\n DS $2000-$,255\n INCBIN "pool.bin"\n DS $3ffe-$,255\n DW 0\n'
    assert not re.search(r'^\s*(call|ret|reti|retn|push|pop|rst|halt)\b','\n'.join(l.split(';')[0] for l in code.splitlines()),re.M|re.I)
    (OUT/'pool.bin').write_bytes(pool);(OUT/'home.asm').write_text(code)
    subprocess.run([str(DEFAULT_ASSEMBLER),'--nologo','--raw=diagnostic-home-u16.bin','--sym=symbols.txt','home.asm'],cwd=OUT,check=True)
    image=bytearray((OUT/'diagnostic-home-u16.bin').read_bytes());assert len(image)==16384
    assert 0x2000+len(pool)<=0x3f00,'HOME data must not overlap joystick helper'
    wrapper=' INCLUDE "symbols.txt"\n INCLUDE "'+(ROOT/'src/joystick.asm').as_posix()+'"\n'
    (OUT/'joystick-wrapper.asm').write_text(wrapper)
    subprocess.run([str(DEFAULT_ASSEMBLER),'--nologo','--raw=joystick.bin','joystick-wrapper.asm'],cwd=OUT,check=True)
    helper=(OUT/'joystick.bin').read_bytes();assert len(helper)==96
    image[0x3f00:0x3f00+len(helper)+1]=helper+bytes([sum(helper)&255])
    image[-2:]=(sum(image[:-2])&65535).to_bytes(2,'little');(OUT/'diagnostic-home-u16.bin').write_bytes(image)
    manifest=dict(edition='HOME U16 reset ROM',bytes=len(image),sha256=hashlib.sha256(image).hexdigest(),entry='0000 JP0100',assets=assets,asset_bytes=len(pool),asset_sha256=hashlib.sha256(pool).hexdigest(),helper_sha256=hashlib.sha256(helper).hexdigest(),font_rom_sha256=hashlib.sha256(stock).hexdigest(),generated_source_sha256=hashlib.sha256(code.encode()).hexdigest(),parent_cartridge_sha256=hashlib.sha256(cart).hexdigest(),source_sha256={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['src/diagnostic.asm','src/modules.asm','src/boot.asm','src/joystick.asm','scripts/build_home_rom.py','scripts/suite_assets.py']},limitations=['Physical U16/adapter validation pending','Fault display uses border/beeper; no large degraded chip renderer','No DOCK banking, HOME/EXROM CRC, optional high-ROM CPU or video cards','SCLD HOME/reset/opcode/bus paths must work'])
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Built16K U16 HOME ROM; asset bytes',len(pool))

if __name__=='__main__': build()
