"""Package the dual-protocol cartridge, preserving separate profile packages."""
import hashlib,json,zipfile
from pathlib import Path
from make_disk import make_disk
from oliger_image import encode_dsk
from tspico_ram_image import encode_image
ROOT=Path(__file__).resolve().parents[1]

def main():
    b=ROOT/'build';dual=b/'profiles/tspico-dual';ram=b/'profiles/tspico-ram';modern=b/'profiles/tspico-dir'
    manifest=json.loads((ram/'manifest.json').read_text())
    payload={entry['name']:(ram/'files'/entry['name']).read_bytes() for entry in manifest['files']}
    payload['CPMDISK.COM']=(modern/'files/CPMDISK.COM').read_bytes()
    payload['README.TXT']=b'TS2068 CP/M: legacy or modern protocol.\r\nRAMDisk: run TPSAVE before power off.\r\nSD mode: CPMDISK mounts/saves DSK or TAP files.\r\n'
    single,_,_=make_disk([(n,d) for n,d in payload.items() if not n.startswith(('PLANET','ZORK1'))],163840,128,1024)
    both,_,_=make_disk(list(payload.items()),327680,128,2048)
    files={'README.md':(ROOT/'docs/tspico-dual.md').read_bytes(),
           'manifest.json':(dual/'manifest.json').read_bytes(),
           'TAP/CPM/CPM.DCK':(dual/'ts2068-cpm.dck').read_bytes(),
           'TAP/CPM/CPM160.DSK':encode_dsk(single,1),'TAP/CPM/CPM160.TAP':encode_image(single),
           'TAP/CPM/COMPAT.TAP':encode_image(both),'host/drive-a.img':(ram/'drive-a.img').read_bytes(),
           'tools/tspico_ram_image.py':(ROOT/'tools/tspico_ram_image.py').read_bytes(),
           'tools/oliger_image.py':(ROOT/'tools/oliger_image.py').read_bytes(),
           'tools/cpm_disk.py':(ROOT/'tools/cpm_disk.py').read_bytes(),
           'tools/make_disk.py':(ROOT/'tools/make_disk.py').read_bytes(),
           'disk-tools.md':(ROOT/'docs/disk-tools.md').read_bytes(),
           'TAP/CPM/SAVE/README.TXT':b'TPSAVE: modern CPMRAM.TAP; legacy CPMSTATE.TAP + CPMnn.TAP.\r\nLoader restores either directly. TPSAVE SPLIT works on either protocol.\r\nPreserve previous saves before replacing them.\r\n'}
    for name,data in payload.items():files['TAP/CPM/FILES/'+name]=data
    files['startup.md']=(ROOT/'docs/startup.md').read_bytes()
    for name in ('using-cpm.md','tspico-firmware.md','picovideo.md','tspico-session.md'):
        files[name]=(ROOT/'docs'/name).read_bytes()
    files['tools/prepare_infocom.py']=(ROOT/'tools/prepare_infocom.py').read_bytes()
    for name in ('picovideo.md','tspico-directory.md','tspico.md'):files[name]=(ROOT/'docs'/name).read_bytes()
    for i in range(8):
        name=f'CPM3200{i}.TAP';files['TAP/CPM/'+name]=(dual/name).read_bytes()
    for name in ('cpm_service.py','cpm_directory.py','cpm_tap.py','cpm_dsk.py'):files['optional-modern-firmware/'+name]=(ROOT/'firmware'/name).read_bytes()
    files['optional-modern-firmware/cpm_config.example.py']=b"CPM_STORAGE = 'directory'\nCPM_DIRECTORY = '/CPM/FILES'\nCPM_DIRECTORY_KB = 320\nCPM_IMAGE_PATH = '/CPM/COMPAT.TAP'\nCPM_IMAGE_SIZE = 327680\n"
    for name in ('LICENSE','third_party/cpm22/LICENSE.txt','third_party/CPM_UTILITIES_NOTICE.md','third_party/tspico-filelib/NOTICE.md'):files[name]=(ROOT/name).read_bytes()
    for document in (ROOT/'docs').glob('*.md'):
        files.setdefault(''+document.name,document.read_bytes())
    files['checksums.txt']=''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in sorted(files.items())).encode()
    output=b/'ts2068-cpm-tspico-dual.zip'
    with zipfile.ZipFile(output,'w') as archive:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;archive.writestr(info,data)
    print(output)

if __name__=='__main__':main()
