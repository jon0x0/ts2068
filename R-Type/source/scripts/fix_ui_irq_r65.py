from pathlib import Path
p=Path('scripts/build_ui_r65.py');s=p.read_text().replace('b[shim_at:shim_at+8]==bytes([255])*8','b[shim_at:shim_at+9]==bytes([255])*9').replace('bytes([0xf5,0x3e,mapping','bytes([0xf5,0xf3,0x3e,mapping').replace('b[shim_at:shim_at+8]=shim','b[shim_at:shim_at+9]=shim');p.write_text(s)
