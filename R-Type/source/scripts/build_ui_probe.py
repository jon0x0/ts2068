from pathlib import Path
import re,subprocess
R=Path.cwd();O=R/'build/fullgame/hardware_fire_r65'
s=(R/'src/debug_ram_screen.asm').read_text(); chars=sorted(set(''.join(re.findall(r"DB '([^']*)'",s))+ '0123456789ABCDEFPaused'))
font=(R/'assets/fullgame_preloader_font.bin').read_bytes();(O/'compact_font.bin').write_bytes(b''.join(font[(ord(c)-32)*8:(ord(c)-31)*8] for c in chars))
lookup=bytes(chars.index(chr(c)) if chr(c) in chars else chars.index(' ') for c in range(32,128));(O/'font_map.bin').write_bytes(lookup)
s=s.replace('        LD L,A\n        LD H,0\n        ADD HL,HL','        LD L,A\n        LD H,0\n        LD BC,font_map\n        ADD HL,BC\n        LD L,(HL)\n        LD H,0\n        ADD HL,HL',1)
s=s.replace('font: INCBIN "assets/fullgame_preloader_font.bin"','font_map: INCBIN "build/fullgame/hardware_fire_r65/font_map.bin"\nfont: INCBIN "build/fullgame/hardware_fire_r65/compact_font.bin"\nui_start:')
(O/'compact_debug.asm').write_text(s)
p=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={O}/compact_debug.bin',f'--sym={O}/compact_debug.sym',str(O/'compact_debug.asm')],capture_output=True,text=True);print(p.stdout+p.stderr);print('size', (O/'compact_debug.bin').stat().st_size)
