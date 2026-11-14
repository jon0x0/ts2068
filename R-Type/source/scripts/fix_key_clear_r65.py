from pathlib import Path
p=Path('scripts/build_ui_r65.py');s=p.read_text();s=s.replace('main()\ndef asm', '''main()
for name in ['boot']+[f'level{n:02d}'for n in range(1,9)]:
 p=OUT/f'{name}_region.bin';b=bytearray(p.read_bytes());assert b[0x7fa9:0x7fac]==bytes.fromhex('cd ef fd');b[0x7fa9:0x7fac]=bytes.fromhex('cd 72 00');p.write_bytes(b)
def asm''');p.write_text(s)
