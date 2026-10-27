"""Build the first TSPico-native 128 ROM from exact original English ROMs.

Inputs are user-supplied ROMs; originals are never modified. The downloaded
disassemblies were assembled and checked byte-identical to these input hashes.
"""
import argparse
import hashlib
import json
from pathlib import Path

HASHES = ('3ba308f23b9471d13d9ba30c23030059a9ce5d4b317b85b86274b132651d1425',
          '8d93c3342321e9d1e51d60afcd7d15f6a7afd978c231b43435a7c0757c60b9a3')
ROM_TITLE = 'TSPico Spectrum 128'
ROM_FILENAME = 'TPZX128.ROM'
PAGING_BC = (0x004a,0x006d,0x0091,0x00a3,0x00b7,0x00cc,0x05ad,0x1c78,
             0x1ef5,0x1f3b,0x1fcc,0x1fe6,0x2458,0x3375,0x33ed,0x33f5,0x3429)
BOOT = 0x2336
AY_READ = 0x2360


def sha(data): return hashlib.sha256(data).hexdigest()


def patch_roms(inputs):
    for i,data in enumerate(inputs):
        if len(data)!=16384 or sha(data)!=HASHES[i]:
            raise ValueError(f'ROM {i} is not the supported original English 128 ROM')
    roms=[bytearray(r) for r in inputs]
    patches=[]
    used=set()
    def edit(bank,address,new,reason,expected=None):
        old=inputs[bank][address:address+len(new)]
        if expected is not None and old!=expected:
            raise ValueError(f'Expected bytes differ at {bank}:{address:04x}')
        for a in range(address,address+len(new)):
            if (bank,a) in used: raise ValueError('Overlapping ROM patches')
            used.add((bank,a))
        roms[bank][address:address+len(new)]=new
        patches.append({'rom':bank,'address':address,'address_hex':f'{address:04X}',
                        'before':old.hex(),'after':new.hex(),'reason':reason})
    # Only the paging port operand changes; lengths and all source labels remain fixed.
    # Includes templates subsequently copied into HOME RAM and bank-7 workspace.
    for address in PAGING_BC:
        edit(0,address+1,b'\x0f','Paging BC low byte FD -> private 0F',b'\xfd')
        if inputs[0][address:address+3]!=b'\x01\xfd\x7f':
            raise ValueError('Paging site is not LD BC,7FFD')
    # Initialize SCLD to ordinary video/DOCK and reserve the upper 16K for SRAM.
    # Clear HOME 4000-BFFF because startup's C000 bank test cannot alias internal RAM.
    boot=bytes.fromhex('f3 af d3 ff 3e c0 d3 f4 21 00 40 11 01 40 01 ff 7f 36 00 ed b0 c3 c7 00')
    edit(0,9,bytes([0xc3,BOOT&255,BOOT>>8]),'Reset via Timex mapping initialization',b'\xc3\xc7\x00')
    edit(0,BOOT,boot,'Unused Spanish-ROM routine area: Timex startup shim')
    # Do not drive nonexistent Spectrum keypad/RS232 lines on Timex AY port A.
    for address in (0x00f6,0x00fb):
        edit(0,address,b'\x00\x00','Skip Spectrum keypad electrical reset',b'\xed\x79')
    edit(0,0x013a,b'\xd3\xf5','Boot AY register select',b'\xed\x79')
    edit(0,0x013f,b'\xd3\xf6','Boot AY mixer data',b'\xed\x79')
    # PLAY uses D and E; preserve the original register/flag contract by retaining OUT (C),r.
    edit(0,0x0e7e,b'\xf5','PLAY register-select port',b'\xfd')
    edit(0,0x0e83,b'\xf6','PLAY register-data port',b'\xfd')
    # Keep IN A,(C), including its flags; Timex read is from F6, not the select port.
    ay_read=bytes.fromhex('c5 01 f5 ff ed 79 0c ed 78 c1 c9')
    edit(0,AY_READ,ay_read,'AY read shim with original IN flags and preserved BC')
    edit(0,0x0e89,bytes([0xc3,AY_READ&255,AY_READ>>8]),'Redirect AY read routine',b'\xc5\x01\xfd')
    edit(0,0x11a3,b'\xc9','Disable unsupported Spectrum MIDI output',b'\x6f')
    edit(1,0x39a0,b'\xc9','Disable unavailable Spectrum serial keypad scanning',b'\xcd')
    manifest={'format':'tspico128-rom-prototype-1','hardware_tested':False,
              'title':ROM_TITLE,'preferred_filename':ROM_FILENAME,
              'legacy_filename':'tspico128.rom',
              'paging_port':15,'required_firmware':'firmware/personality128_stock.py plus personality128.py definitions',
              'sram_regions_cleared_at_boot':[
                  {'start':(bank<<16)|0xc000,'length':16384} for bank in range(8)],
              'input_sha256':list(HASHES),'output_sha256':[sha(r) for r in roms],
              'patches':patches,
              'features_pending':['SD LOAD/SAVE integration','50 Hz pacing','hardware timing validation'],
              'unsupported':['native shadow screen','true bank 2/5 aliases','Spectrum serial keypad','RS232/MIDI']}
    return [bytes(r) for r in roms],manifest


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom0',type=Path,required=True);p.add_argument('--rom1',type=Path,required=True)
    p.add_argument('--output',type=Path,default=Path('build/rom'))
    a=p.parse_args()
    roms,manifest=patch_roms([a.rom0.read_bytes(),a.rom1.read_bytes()])
    a.output.mkdir(parents=True,exist_ok=True)
    for i,r in enumerate(roms): (a.output/f'tspico128-{i}.rom').write_bytes(r)
    for i,r in enumerate((a.rom0.read_bytes(),a.rom1.read_bytes())):
        (a.output/f'original-{i}.rom').write_bytes(r)
    (a.output/'tspico128-pair.bin').write_bytes(b''.join(roms))
    (a.output/'tspico128.rom').write_bytes(b''.join(roms))
    (a.output/ROM_FILENAME).write_bytes(b''.join(roms))
    (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(f'Built {len(manifest["patches"])} guarded patches; outputs in {a.output}')


if __name__=='__main__': main()
