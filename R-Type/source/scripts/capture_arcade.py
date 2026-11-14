"""Capture genuine R-Type screen/palette/sprite state using local MAME.

Original archives are read-only. Missing archival PROM/PLD regions, unused by
the M72 renderer/device configuration, get explicitly labelled diagnostic FF
stand-ins in build only. Never use these as authentic ROM dumps or hardware data.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mame', type=Path, default=Path('C:/apps/games/MAME/mame.exe'))
    ap.add_argument('--output', type=Path, default=ROOT/'build/arcade_capture')
    ap.add_argument('--archival-fill',type=lambda x:int(x,0),choices=(0,255),default=255)
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    xml = subprocess.run([str(args.mame), '-listxml', 'rtype'], capture_output=True, text=True, check=True).stdout
    machine = next(x for x in ET.fromstring(xml).findall('machine') if x.get('name') == 'rtype')
    with zipfile.ZipFile(ROOT / 'arcade/rtype.zip') as archive:
        crcs = {f'{n.CRC:08x}': n for n in archive.infolist()}
        verified = []
        missing = []
        for rom in machine.findall('rom'):
            crc = rom.get('crc')
            if crc in crcs:
                member = crcs[crc]
                verified.append(dict(expected=rom.get('name'), member=member.filename,
                                     region=rom.get('region'), crc32=crc,
                                     sha256=hashlib.sha256(archive.read(member)).hexdigest()))
            elif rom.get('region') in ('proms', 'plds'):
                missing.append(dict(name=rom.get('name'), bytes=int(rom.get('size')), region=rom.get('region')))
            else:
                raise SystemExit(f'Missing functional ROM: {rom.attrib}')
    support = ROOT / f'build/mame_archival_standins_{args.archival_fill:02x}/rtype'
    support.mkdir(parents=True, exist_ok=True)
    for item in missing:
        (support / item['name']).write_bytes(bytes([args.archival_fill]) * item['bytes'])
    (out / 'rom_audit.json').write_text(json.dumps(dict(
        verified_functional_roms=verified, archival_standins=missing,fill=args.archival_fill,
        caveat='FF stand-ins are NOT authentic ROM data. M72 proms/plds are archival regions, not palette sources; the emulated game CPU populates palette RAM.',
        source='MAME 0.289 m72.cpp, m72_v.cpp and m72.h'), indent=2))
    lua = r'''
local out = OUTDIR
local machine = manager.machine
local space = machine.devices[":maincpu"].spaces["program"]
local frame = 0
local function key(name,value)
  for _,port in pairs(machine.ioport.ports) do
    for _,field in pairs(port.fields) do
      if field.name == name then field:set_value(value); print("INPUT "..name.."="..value) end
    end
  end
end
local function capture(n)
  local base=out..string.format("/frame%04d",n)
  machine.screens[":screen"]:snapshot(base..".png")
  for _,item in ipairs({{"palette_sprite",0xc8000,0xc00},{"palette_tile",0xcc000,0xc00},{"sprites",0xc0000,0x400},{"tiles0",0xd0000,0x4000},{"tiles1",0xd8000,0x4000}}) do
    local f=assert(io.open(base.."_"..item[1]..".bin","wb"))
    for address=item[2],item[2]+item[3]-1 do f:write(string.char(space:read_u8(address))) end
    f:close()
  end
  print("CAPTURE "..n)
end
local function tick()
  frame=frame+1
  if frame==720 then key("Coin 1",1) end
  if frame==730 then key("Coin 1",0) end
  if frame==780 then key("1 Player Start",1) end
  if frame==790 then key("1 Player Start",0) end
  if frame==420 or frame==540 or frame==660 or frame==900 or frame==1080 or frame==1320 or frame==1560 or frame==1800 then capture(frame) end
end
subscription=emu.add_machine_frame_notifier(tick)
'''.replace('OUTDIR', json.dumps(out.as_posix()))
    script = out / 'capture.lua'
    script.write_text(lua)
    for name in ('cfg', 'nvram', 'snap'):
        (out/name).mkdir(exist_ok=True)
    command = [str(args.mame), 'rtype', '-noreadconfig', '-rompath', str(ROOT/'arcade')+';'+str(support.parent),
               '-video', 'none', '-sound', 'none', '-nothrottle', '-skip_gameinfo', '-seconds_to_run', '35',
               '-autoboot_delay', '0', '-autoboot_script', str(script),
               '-cfg_directory', str(out/'cfg'), '-nvram_directory', str(out/'nvram'), '-snapshot_directory', str(out/'snap')]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=90)
    (out/'mame.log').write_text(result.stdout + result.stderr)
    print(result.stdout[-2000:] + result.stderr[-2000:])
    if result.returncode or not (out/'frame0540.png').exists():
        raise SystemExit('Arcade capture failed; inspect build/arcade_capture/mame.log')
    print('Captured original arcade scenes, palette RAM and sprite descriptors')


if __name__ == '__main__':
    main()
