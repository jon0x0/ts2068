from pathlib import Path
import argparse,shutil,subprocess,tempfile,sys
sys.path.insert(0,str(Path.cwd()/'tools'))
from dck import parse
parser=argparse.ArgumentParser(description='Build a two-drive Oliger cartridge without replacing retained disks.');parser.add_argument('--kb',type=int,choices=(160,320),default=320);size=parser.parse_args().kb
root=Path(__file__).resolve().parents[1];out=root/'build/tsrun-dual';out.mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix='cpm-two-drive-') as tmp:
 t=Path(tmp);shutil.copytree(root/'src',t/'src');(t/'build').mkdir()
 values={'DISK_SIDES':2,'DISK_LBA_HIGH':10,'DISK_BSH':4,'DISK_BLM':15,'DISK_EXM':1,'DISK_AL0':192,'BUILD_OLIGER':1,'BUILD_TSPICO':0,'BUILD_BANKED':0,'BUILD_SD320':0,'BUILD_DIRECTORY':0,'BUILD_TERMINAL':1,'DISK_TRACKS':160,'DISK_BLOCKS':160,'DISK_DIRECTORY_ENTRIES':128,'DISK_ALV_BYTES':20,'BUILD_DUAL':0}
 if size==160:values.update(DISK_SIDES=1,DISK_LBA_HIGH=5,DISK_BSH=3,DISK_BLM=7,DISK_EXM=0,DISK_AL0=240,DISK_TRACKS=80,DISK_ALV_BYTES=20)
 (t/'build/disk-layout.inc').write_text(''.join(f'{n} EQU {v}\n' for n,v in values.items()))
 subprocess.run([str(root/'tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),'--nologo',f'--raw={out}/bios.bin',f'--sym={out}/bios.bin.sym',str(t/'src/bios.asm')],check=True,cwd=t)
 bios=(out/'bios.bin').read_bytes();assert len(bios)<=0x1a00
 blocks=parse((root/('build/profiles/oliger320/ts2068-cpm.dck' if size==320 else 'build/profiles/oliger/ts2068-cpm.dck')).read_bytes());result=bytearray()
 for bank,kinds,pages in blocks:
  if bank==0:
   system=bytearray(pages[5]+pages[6]);system[0x1600:0x3000]=bytes(0x1a00);system[0x1600:0x1600+len(bios)]=bios;pages[5]=bytes(system[:8192]);pages[6]=bytes(system[8192:16384])
  result+=bytes([bank]+kinds)+b''.join(pages)
 (out/f'CPM{size}.DCK').write_bytes(result)
 print(out/f'CPM{size}.DCK',len(bios),'BIOS bytes')
