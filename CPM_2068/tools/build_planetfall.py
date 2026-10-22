"""Prepare Planetfall for the TS2068 Oliger CP/M cartridge from supplied files."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from make_disk import make_disk
from oliger_image import DISK_BYTES, encode_dsk
from convert8080 import convert

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--story',type=Path,default=ROOT/'build/planetfall/planetfall-r37-s851003.z3')
    p.add_argument('--source',type=Path,default=ROOT/'build/planetfall/interpreter/cpm80/zorkcpm.asm')
    p.add_argument('--assembler',default=str(ROOT/'tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'))
    p.add_argument('--output',type=Path,default=ROOT/'build/planetfall-cpm.dsk')
    p.add_argument('--collection',action='store_true',help='Add Zork I and the selected programming examples/utilities')
    a=p.parse_args()
    current=json.loads((ROOT/'build/manifest.json').read_text())
    if current.get('profile')!='oliger' or current.get('disk_bytes')!=327680:
        raise ValueError('First build the cartridge with --profile oliger --oliger-kb 320')
    story=a.story.read_bytes()
    if story[0]!=3: raise ValueError('This interpreter requires a version 3 story file')
    b=ROOT/'build/planetfall';b.mkdir(exist_ok=True)
    original=a.source.read_text();source=original
    for pattern,replacement in [
        (r'CPMCPL: DB 79', 'CPMCPL: DB 63'),
        (r"CPMFN:\s*DB 'SUSPECT '", "CPMFN: DB 'PLANET  '"),
        (r'CPMINV: DB 80H','CPMINV: DB 0'),
        (r'RTRMST: DB 0','RTRMST: DB 1,12'),
        (r'CPMSTR:(?=[ \t]*(?:;|\r?\n))','CPMSTR:\n LD A,(0EFF5H)\n CP 1\n LD A,63\n JR NZ,CPWSET\n LD A,79\nCPWSET:\n LD (CPMCPL),A'),
    ]:
        source,count=re.subn(pattern,replacement,source)
        if count!=1: raise ValueError(f'unexpected interpreter source: {pattern}')
    configured=b/'planetfall.asm';configured.write_text(source)
    program=b/'PLANET.COM'
    subprocess.run([a.assembler,'--nologo',f'--raw={program}',f'--sym={program}.sym',str(configured)],check=True,cwd=ROOT)
    readme=(
        'Planetfall for TS2068 CP/M 2.2 / Oliger\r\n'
        'Type PLANET to play. LOOK repeats the room description.\r\n'
        'SAVE and RESTORE use a CP/M .SAV file on this disk.\r\n'
        'Use Fuse JLO Save/Save As to preserve disk changes on the host.\r\n'
        'Use the updated Oliger cartridge with ADM-3A console support.\r\n'
    ).encode('ascii')
    files=[('PLANET.COM',program.read_bytes()),('PLANET.DAT',story),('README.TXT',readme)]
    selected=[f['name'] for f in current['files'] if f['name']!='README.TXT']
    if a.collection:
        zork=(b/'zork1-r88-s840726.z3').read_bytes()
        if zork[0]!=3: raise ValueError('Zork I must use version 3')
        zsource=b/'zork1.asm';zsource.write_text(source.replace("DB 'PLANET  '","DB 'ZORK1   '"))
        zprogram=b/'ZORK1.COM'
        subprocess.run([a.assembler,'--nologo',f'--raw={zprogram}',f'--sym={zprogram}.sym',str(zsource)],check=True,cwd=ROOT)
        readme=(
            'Planetfall + Zork I / TS2068 CP/M / 64 or PicoVideo 80 columns\r\n'
            'Type PLANET or ZORK1 to play. SAVE / RESTORE use separate .SAV files.\r\n'
            'Backspace (Caps Shift+0) deletes; plain 0 types zero.\r\n'
            'Type SUBMIT DEMO to assemble HI.ASM, LOAD HI, and run HI.COM.\r\n'
            'ASM HI assembles; LOAD HI creates HI.COM; HI runs the example.\r\n'
            'MEMTEST checks screen shadow RAM; ED edits text. STAT shows free space.\r\n'
            'COLOR lists the eight schemes; COLOR 0 to COLOR 7 selects one.\r\n'
            'Use Fuse JLO Save/Save As to preserve disk changes on the host.\r\n'
        ).encode('ascii')
        files=[('PLANET.COM',program.read_bytes()),('PLANET.DAT',story),
               ('ZORK1.COM',zprogram.read_bytes()),('ZORK1.DAT',zork),('README.TXT',readme)]
        selected=['HELLO.COM','PIP.COM','ASM.COM','LOAD.COM','SUBMIT.COM','DEMO.SUB','HI.ASM','MEMTEST.COM','ED.COM','STAT.COM','COLOR.COM','COLUMNS.COM','VIDEO.COM','FORMAT.COM']
        hi_source=b/'hi-example.asm';hi_source.write_text(convert((ROOT/'assets/HI.ASM').read_text(),'0x100').replace('MSG:', 'msg:'))
        hi_program=b/'HI.COM'
        subprocess.run([a.assembler,'--nologo',f'--raw={hi_program}',str(hi_source)],check=True,cwd=ROOT)
        files.append(('HI.COM',hi_program.read_bytes()))
    for name in selected:
        files.append((name,(ROOT/'build/sdcard/CPM/FILES'/name).read_bytes()))
    raw,entries,free=make_disk(files,DISK_BYTES*2,128,2048)
    a.output.write_bytes(encode_dsk(raw,2))
    a.output.with_suffix('.dck').write_bytes((ROOT/'build/profiles/oliger320/ts2068-cpm.dck').read_bytes())
    manifest={'story_source':'https://eblong.com/infocom/gamefiles/planetfall-r37-s851003.z3',
              'interpreter_source':'https://eblong.com/infocom/interpreters/cpm80.zip',
              'story_sha256':hashlib.sha256(story).hexdigest(),
              'interpreter_source_sha256':hashlib.sha256(a.source.read_bytes()).hexdigest(),
              'program_sha256':hashlib.sha256(program.read_bytes()).hexdigest(),
              'release':int.from_bytes(story[2:4],'big'),'serial':story[18:24].decode(),
              'free_bytes':free,'files':entries,'terminal':'ADM-3A automatic 64/80 columns; no inverse video','geometry':'40 cylinders x 2 sides x 16 sectors x 256 bytes','block_size':2048}
    if a.collection:
        manifest['zork1']={'source':'https://eblong.com/infocom/gamefiles/zork1-r88-s840726.z3',
                           'sha256':hashlib.sha256(zork).hexdigest(),'release':88,'serial':'840726',
                           'program_sha256':hashlib.sha256(zprogram.read_bytes()).hexdigest()}
    a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'{a.output}: {free//1024}KB free; run PLANET')

if __name__=='__main__':main()
