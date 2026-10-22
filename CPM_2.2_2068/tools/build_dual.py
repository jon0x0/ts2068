"""Build one cartridge selecting legacy SRAM or modern SD/SRAM at boot."""
import argparse,json,subprocess,sys,shutil,re
from pathlib import Path
from build import ROOT,assemble

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom')
    p.add_argument('--assembler',default=str(ROOT/'tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'))
    p.add_argument('--with-infocom',action='store_true');a=p.parse_args()
    assembler=a.assembler
    for profile in ('tspico-dir','tspico-ram'):
        command=[sys.executable,str(ROOT/'tools/build.py'),'--profile',profile,'--assembler',assembler]
        if a.rom:command.extend(['--rom',a.rom])
        if a.with_infocom:command.append('--with-infocom')
        subprocess.run(command,cwd=ROOT,check=True)
    b=ROOT/'build';target=b/'profiles/tspico-dual';target.mkdir(parents=True,exist_ok=True)
    layout=b/'disk-layout.inc';layout.write_text(layout.read_text().replace('BUILD_DUAL EQU 0','BUILD_DUAL EQU 1'))
    assemble(ROOT/'src/boot.asm',b/'dual-boot.bin',assembler)
    assemble(ROOT/'src/sram_loader.asm',b/'dual-loader.bin',assembler)
    def page(data):
        if len(data)>8192:raise ValueError('cartridge page overflow')
        return data.ljust(8192,b'\0')
    ram=b/'profiles/tspico-ram';modern=b/'profiles/tspico-dir'
    cart=bytearray((ram/'ts2068-cpm.dck').read_bytes())
    # Shared CCP/BDOS; the alternate BIOS lives in immutable boot-page ROM.
    system=(modern/'ts2068-cpm-system.bin').read_bytes()
    assert system[:0x1600]==(ram/'ts2068-cpm-system.bin').read_bytes()[:0x1600]
    boot=(b/'dual-boot.bin').read_bytes()
    if len(boot)>0x100:raise ValueError('boot overlaps cartridge font')
    boot=boot.ljust(0x100,b'\0')+(b/'font.bin').read_bytes()
    cart[9+4*8192:9+5*8192]=page(boot+system[0x1600:])
    cart[9+7*8192:9+8*8192]=page((b/'dual-loader.bin').read_bytes())
    (target/'ts2068-cpm.dck').write_bytes(cart)
    for name in ('bios.bin.sym','drive-a.img','CPM320.TAP',*(f'CPM3200{i}.TAP' for i in range(8))):shutil.copyfile(ram/name,target/name)
    manifest=json.loads((ram/'manifest.json').read_text());manifest['profile']='tspico-dual'
    manifest['storage_backend']='detected legacy RAMDisk / modern SD or RAMDisk snapshot'
    manifest['tspico']='validated legacy FIFO or modern status-register protocol'
    manifest['tspico_directory']='/CPM/FILES';manifest['tspico_directory_bytes']=327680
    manifest['startup_modes']=['legacy RAMDisk','modern persistent SD','modern RAMDisk snapshot','modern TAP RAMDisk']
    manifest['files_describe']='TAP preload; package also supplies native FILES and compatible images'
    (target/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(target/'ts2068-cpm.dck')

if __name__=='__main__':main()
