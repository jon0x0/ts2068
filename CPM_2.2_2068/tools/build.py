"""Deterministic CP/M cartridge build; Python 3 + sjasmplus 1.20.3."""
from pathlib import Path
import argparse, hashlib, json, zipfile, subprocess
from convert8080 import convert
from make_disk import make_disk

ROOT=Path(__file__).resolve().parents[1]
def assemble(asm, output, assembler):
    subprocess.run([assembler, '--nologo', f'--raw={output}', f'--sym={output}.sym', str(asm)],cwd=ROOT,check=True)
def build(assembler, rom, profile='emulator', oliger_kb=160, with_infocom=False):
    b=ROOT/'build'; b.mkdir(exist_ok=True)
    geometry=json.loads((ROOT/'config/ramdisk.json').read_text())
    pages=geometry['exrom_pages'];assert pages==list(range(1,7))
    disk_size=len(pages)*8192
    directory_entries=geometry['directory_entries']
    block_size=1024
    sides=1
    if profile in ('oliger','tspico-ram','tspico-sd','tspico-dir'):
        if profile!='oliger': oliger_kb=320
        disk_size=oliger_kb*1024
        sides=oliger_kb//160
        block_size=1024 if oliger_kb==160 else 2048
        directory_entries=128
    (b/'disk-layout.inc').write_text(f'DISK_SIDES EQU {sides}\nDISK_LBA_HIGH EQU {disk_size//32768}\nDISK_BSH EQU {3 if block_size==1024 else 4}\nDISK_BLM EQU {block_size//128-1}\nDISK_EXM EQU {block_size//1024-1}\nDISK_AL0 EQU {0xf0 if directory_entries==128 and block_size==1024 else 0xc0}\nBUILD_OLIGER EQU {int(profile=="oliger")}\nBUILD_TSPICO EQU {int(profile in ("combined","tspico-sd","tspico-dir"))}\nBUILD_BANKED EQU {int(profile=="tspico-ram")}\nBUILD_SD320 EQU {int(profile in ("tspico-sd","tspico-dir"))}\nBUILD_DIRECTORY EQU {int(profile=="tspico-dir")}\nBUILD_TERMINAL EQU {int(profile in ("oliger","tspico-ram","tspico-sd","tspico-dir"))}\nDISK_TRACKS EQU {disk_size//128//16}\nDISK_BLOCKS EQU {disk_size//block_size}\nDISK_DIRECTORY_ENTRIES EQU {directory_entries}\nDISK_ALV_BYTES EQU {(disk_size//block_size+7)//8}\n')
    (b/'sram-slots.inc').write_text('SRAM_BOOT_SLOT EQU 4\nsram_slots: db 0,2,6,8,10,12\n')
    legacy=(ROOT/'third_party/tspico-filelib/tpi_legacy.asm').read_text()
    legacy=legacy.replace('LEGACY_REPLY_BUFFER equ $f400','LEGACY_REPLY_BUFFER equ $c800').replace('LEGACY_REPLY_BUFFER equ $e000','LEGACY_REPLY_BUFFER equ $c800').replace('LEGACY_REPLY_CAPACITY equ $1800','LEGACY_REPLY_CAPACITY equ $400')
    (b/'tpi-legacy-cpm.asm').write_text(legacy)
    resident=legacy.replace('LEGACY_REPLY_BUFFER equ $c800','LEGACY_REPLY_BUFFER equ $f680').replace('LEGACY_REPLY_CAPACITY equ $400','LEGACY_REPLY_CAPACITY equ $80')
    (b/'tpi-legacy-sram.asm').write_text(resident)
    from dual_transport import adapt
    (b/'disk-layout.inc').write_text((b/'disk-layout.inc').read_text()+'BUILD_DUAL EQU 0\n')
    (b/'tpi-dual-cpm.asm').write_text(adapt(legacy))
    (b/'tpi-dual-sram.asm').write_text(adapt(resident))
    # Retain a licensed/generated font separately from the OS: caller supplies ROM.
    if rom:
        data=Path(rom).read_bytes()
        font=data[0x3d00:0x4000]
    else:
        from public_font import font_bytes
        font=font_bytes()
    (b/'font.bin').write_bytes(font)
    assert (b/'font.bin').stat().st_size==768
    for name,origin in [('ccp',0xd000),('bdos',0xd800)]:
        (b/f'{name}.asm').write_text(convert((ROOT/f'third_party/cpm22/{name}.asm').read_text(),hex(origin)))
        assemble(b/f'{name}.asm',b/f'{name}.bin',assembler)
    for name in ['boot','bios','hello','memtest','color','columns','video','format','cpmdisk','tpimport','tplimport']:
        assemble(ROOT/f'src/{name}.asm',b/f'{name}.bin',assembler)
    if profile=='tspico-ram':
        import re
        syms=dict((n,int(v,16)) for n,v in re.findall(r'^(\w+): EQU 0x([0-9A-Fa-f]+)',(b/'bios.bin.sym').read_text(),re.M))
        (b/'sram-api.inc').write_text(''.join(f'{n.upper()} EQU ${syms[n]:04x}\n' for n in ['sram_select','sram_install_page','sram_fetch_page','puts']))
        assemble(ROOT/'src/sram_loader.asm',b/'sram-loader.bin',assembler)
        assemble(ROOT/'src/tpsave.asm',b/'tpsave.bin',assembler)
    system=bytearray(0x3000)
    for name,offset,limit in [('ccp',0,0x800),('bdos',0x800,0xe00),('bios',0x1600,0x1200)]:
        blob=(b/f'{name}.bin').read_bytes(); assert len(blob)<=limit,(name,len(blob))
        system[offset:offset+len(blob)]=blob
    (b/'ts2068-cpm-system.bin').write_bytes(system)
    files=[('HELLO.COM',(b/'hello.bin').read_bytes()),('README.TXT',(ROOT/'assets/README.TXT').read_bytes()),('MEMTEST.COM',(b/'memtest.bin').read_bytes())]
    files.append(('COLOR.COM',(b/'color.bin').read_bytes()))
    files.append(('COLUMNS.COM',(b/'columns.bin').read_bytes()))
    files.append(('VIDEO.COM',(b/'video.bin').read_bytes()))
    (b/'VIDEO.COM').write_bytes((b/'video.bin').read_bytes())
    (b/'COLUMNS.COM').write_bytes((b/'columns.bin').read_bytes())
    files.append(('FORMAT.COM',(b/'format.bin').read_bytes()))
    (b/'FORMAT.COM').write_bytes((b/'format.bin').read_bytes())
    if profile in ('tspico-sd','tspico-dir'):files.append(('CPMDISK.COM',(b/'cpmdisk.bin').read_bytes()))
    if profile=='tspico-ram': files.append(('TPSAVE.COM',(b/'tpsave.bin').read_bytes()))
    (b/'COLOR.COM').write_bytes((b/'color.bin').read_bytes())
    files.append(('TPLOAD.COM',(b/'tplimport.bin').read_bytes()) if profile!='combined' else ('TPIMPORT.COM',(b/'tpimport.bin').read_bytes()))
    archive=ROOT/'third_party/cpm22-utilities.zip'
    if hashlib.sha256(archive.read_bytes()).hexdigest()!='88735cca77e786505f53a63746ddbc5ca221eda79fd822fde5dc9f00a5bfba6f':
        raise ValueError('CP/M utilities archive does not match pinned provenance')
    with zipfile.ZipFile(archive) as z:
        for name in ['STAT.COM','PIP.COM','ED.COM','ASM.COM','LOAD.COM','SUBMIT.COM','DUMP.COM'] + (['DDT.COM','XSUB.COM'] if profile in ('oliger','tspico-ram','tspico-sd','tspico-dir') else []):
            files.append((name,z.read(name)))
    files.extend((name,(ROOT/'assets'/name).read_bytes()) for name in ['HI.ASM','DEMO.SUB'])
    if profile in ('tspico-ram','tspico-sd','tspico-dir'):
        readme=('TS2068 CP/M 2.2 / 64 or PicoVideo 80 columns / 320KB\r\n'
                'DIR lists files. COLOR lists color schemes.\r\n'
                'SUBMIT DEMO assembles HI.ASM and runs HI.\r\n'+
                ('TPSAVE saves /CPM/SAVE; single TAP on modern, chunks on legacy.\r\n'
                 'Power off loses RAM changes unless exported.\r\n' if profile=='tspico-ram' else
                 ('Modern directory service: /CPM/FILES is drive A.\r\n' if profile=='tspico-dir' else
                  'Modern binary-safe image service required; SD image is writable.\r\n')+
                 'CPMDISK DIR, MOUNT NAME.TAP, or SAVE NAME.TAP.\r\n')+
                ('PLANET or ZORK1 starts a game.\r\n' if with_infocom else '')).encode('ascii')
        files=[(name,readme if name=='README.TXT' else blob) for name,blob in files]
    if with_infocom:
        if profile not in ('tspico-ram','tspico-sd','tspico-dir'):raise ValueError('--with-infocom requires a TSPico 320KB profile')
        for prefix,story in [('PLANET','planetfall-r37-s851003.z3'),('ZORK1','zork1-r88-s840726.z3')]:
            files.extend([(prefix+'.COM',(b/'planetfall'/f'{prefix}.COM').read_bytes()),(prefix+'.DAT',(b/'planetfall'/story).read_bytes())])
    files=[(name,blob.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n') if name.endswith(('.TXT','.ASM','.SUB')) else blob) for name,blob in files]
    disk,file_manifest,free_bytes=make_disk(files,disk_size,directory_entries,block_size)
    (b/'drive-a.img').write_bytes(disk)
    def page(blob):
        assert len(blob)<=8192
        return bytes(blob).ljust(8192,b'\0')
    # DOCK low TPA, both screen shadows, AROS and immutable warm boot source.
    boot=(b/'boot.bin').read_bytes()
    if len(boot)>256:raise ValueError('boot overlaps cartridge font')
    boot=boot.ljust(256,b'\0')+(b/'font.bin').read_bytes()
    dock=bytes([0,3,3,3,3,2,2,2,2 if profile=='tspico-ram' else 0])+bytes(8192*4)+page(boot)+page(system[:8192])+page(system[8192:])
    if profile=='tspico-ram': dock+=page((b/'sram-loader.bin').read_bytes())
    # Page 0 remains ROM-owned for AROS startup; page 7 always holds HOME BIOS.
    exrom=bytes([254,0,3,3,3,3,3,3,0])+disk
    (b/'ts2068-cpm.dck').write_bytes(dock if profile in ('oliger','tspico-ram','tspico-sd','tspico-dir') else dock+exrom)
    if profile=='oliger':
        from oliger_image import encode_dsk
        (b/'oliger-cpm.dsk').write_bytes(encode_dsk(disk,sides))
    # Physical TSPico loader consumes DOCK only. SD files remain separate.
    (b/'ts2068-cpm-tspico.dck').write_bytes(dock)
    sd=b/'sdcard/CPM';sd.mkdir(parents=True,exist_ok=True)
    (sd/'CPMBOOT.DCK').write_bytes(dock if profile.startswith('tspico-') else dock+exrom)
    (sd/'DRIVEA.IMG').write_bytes(disk)
    for name,blob in files:
        (sd/name).write_bytes(blob)
    directory=sd/'FILES';directory.mkdir(exist_ok=True)
    for name,blob in files:
        (directory/name).write_bytes(blob)
    taps=sd/'TAP';taps.mkdir(exist_ok=True)
    tap_map={}
    for name,blob in files:
        if len(blob)>32768:continue # TPLOAD's bounded import buffer; disk images use chunked TAPs.
        alias=name.replace('.','')
        header=bytes([3])+alias.encode().ljust(10,b' ')+len(blob).to_bytes(2,'little')+bytes([0,1,0,128])
        blocks=[bytes([0])+header,bytes([255])+blob]
        encoded=bytearray()
        for block in blocks:
            checksum=0
            for value in block: checksum^=value
            encoded+=(len(block)+1).to_bytes(2,'little')+block+bytes([checksum])
        (taps/(alias+'.TAP')).write_bytes(encoded)
        tap_map[name]=alias+'.TAP'
    (taps/'mapping.json').write_text(json.dumps(tap_map,indent=2)+'\n')
    artifacts=['ts2068-cpm.dck','ts2068-cpm-tspico.dck','ts2068-cpm-system.bin','drive-a.img']
    if profile=='tspico-ram':
        from tspico_ram_image import encode_image,encode_volumes
        (b/'CPM320.TAP').write_bytes(encode_image(disk));artifacts.append('CPM320.TAP')
        for name,data in encode_volumes(disk).items():
            (b/name).write_bytes(data);artifacts.append(name)
    if profile=='oliger': artifacts.append('oliger-cpm.dsk')
    (b/'checksums.txt').write_text(''.join(hashlib.sha256((b/n).read_bytes()).hexdigest()+'  '+n+'\n' for n in artifacts))
    (b/'manifest.json').write_text(json.dumps({'version':'CP/M 2.2 baseline','profile':profile,'storage_backend':'oliger-wd1770' if profile=='oliger' else 'tspico-or-ram' if profile=='combined' else 'ram','tspico':'modern + directory-v1 + image-v1' if profile=='combined' else 'disabled; optional TPLOAD transient only','tspico_directory':'/CPM/FILES','tspico_directory_bytes':262144,'hardware_validated':False,'ccp':0xd000,'bdos':0xd800,'bios':0xe600,'tpa_end_exclusive':0xd000,'console':'64x24 TS2068 hires','disk_bytes':disk_size,'block_size':block_size,'sides':sides,'disk_free_bytes':free_bytes,'exrom_pages':[] if profile=='oliger' else pages,'files':file_manifest,'utility_archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()},indent=2)+'\n')
    if profile.startswith('tspico-'):
        manifest=json.loads((b/'manifest.json').read_text())
        manifest.update(storage_backend='tspico-sram-legacy' if profile=='tspico-ram' else 'tspico-directory-service' if profile=='tspico-dir' else 'tspico-image-service',
                        tspico='legacy 1.00-compatible or modern TAP transport; hardware unverified' if profile=='tspico-ram' else 'modern 2.3-compatible optional binary-safe service',
                        exrom_pages=[],sram_boot_slot=4 if profile=='tspico-ram' else None,sram_disk_pairs=[0,2,6,8,10,12] if profile=='tspico-ram' else [],
                        tspico_directory='/CPM/FILES' if profile=='tspico-dir' else None,tspico_directory_bytes=327680 if profile=='tspico-dir' else 0,
                        sd_image_path='/CPM/DRIVE320.IMG' if profile=='tspico-sd' else None,
                        preload_volume_count=8 if profile=='tspico-ram' else 0,
                        with_infocom=with_infocom)
        (b/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    # Retain separate profile outputs without making callers juggle filenames.
    manifest=json.loads((b/'manifest.json').read_text())
    manifest['console']='Default 80x24 on inspected PicoVideo 4.2, otherwise 64x24 TS2068 hires; COLUMNS 64/80 selects width'
    manifest['video_auto_detect']={'version_register':127,'version_value':66,'mode':5,'columns':80,'rows':24,'fallback_columns':64,'hardware_validated':False}
    (b/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    target=b/'profiles'/('oliger320' if profile=='oliger' and oliger_kb==320 else profile);target.mkdir(parents=True,exist_ok=True)
    for name in artifacts+['manifest.json','checksums.txt']:
        (target/name).write_bytes((b/name).read_bytes())
    for name,blob in files:
        destination=target/'files'/name;destination.parent.mkdir(exist_ok=True);destination.write_bytes(blob)
    for name in ['bios.bin','bios.bin.sym','COLOR.COM']+(['sram-loader.bin','sram-loader.bin.sym','tpsave.bin','tpsave.bin.sym'] if profile=='tspico-ram' else []):
        (target/name).write_bytes((b/name).read_bytes())

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--assembler',default=str(ROOT/'tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe')); p.add_argument('--rom',help='Optional private ROM-font build; omit for redistributable public-domain font')
    p.add_argument('--profile',choices=['combined','emulator','oliger','tspico-ram','tspico-sd','tspico-dir'],default='emulator')
    p.add_argument('--oliger-kb',type=int,choices=[160,320],default=160)
    p.add_argument('--with-infocom',action='store_true',help='include locally prepared Planetfall and Zork I')
    a=p.parse_args(); build(a.assembler,a.rom,a.profile,a.oliger_kb,a.with_infocom)
