"""Package one retained TSPico profile; never install or copy to a device."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile',choices=['tspico-ram','tspico-sd','tspico-dir'],required=True)
    a=p.parse_args();b=ROOT/'build/profiles'/a.profile
    manifest=json.loads((b/'manifest.json').read_text())
    if manifest['profile']!=a.profile:raise ValueError('profile mismatch')
    ram=a.profile=='tspico-ram'
    native=a.profile=='tspico-dir'
    files={'README.md':(ROOT/('docs/tspico-ram.md' if ram else 'docs/tspico-directory.md' if native else 'docs/tspico-sd320.md')).read_bytes(),
           'manifest.json':(b/'manifest.json').read_bytes(),
           'TAP/CPM/'+('CPMRAM.DCK' if ram else 'CPMDIR.DCK' if native else 'CPMSD.DCK'):(b/'ts2068-cpm.dck').read_bytes(),
           'host/drive-a.img':(b/'drive-a.img').read_bytes(),
           'tools/tspico_ram_image.py':(ROOT/'tools/tspico_ram_image.py').read_bytes(),
           'tools/oliger_image.py':(ROOT/'tools/oliger_image.py').read_bytes()}
    for name in ['LICENSE','third_party/cpm22/LICENSE.txt','third_party/CPM_UTILITIES_NOTICE.md','third_party/tspico-filelib/NOTICE.md']:
        files[name]=(ROOT/name).read_bytes()
    files['picovideo.md']=(ROOT/'docs/picovideo.md').read_bytes()
    files['disk-tools.md']=(ROOT/'docs/disk-tools.md').read_bytes()
    files['startup.md']=(ROOT/'docs/startup.md').read_bytes()
    for name in ('cpm_disk.py','make_disk.py','prepare_infocom.py'):
        files['tools/'+name]=(ROOT/'tools'/name).read_bytes()
    for name in ('using-cpm.md','tspico-firmware.md','picovideo.md'):
        files[name]=(ROOT/'docs'/name).read_bytes()
    if ram:
        for i in range(8):
            name=f'CPM3200{i}.TAP';files['TAP/CPM/'+name]=(b/name).read_bytes()
        files['TAP/CPM/SAVE/README.TXT']=b'TPSAVE: legacy CPMSTATE.TAP + CPMnn.TAP; modern CPMRAM.TAP.\r\nReload directly without PC conversion. Preserve previous saves.\r\n'
    else:
        if native:
            from tspico_ram_image import encode_image
            from make_disk import make_disk
            from oliger_image import encode_dsk
            files['TAP/CPM/COMPAT.TAP']=encode_image((b/'drive-a.img').read_bytes())
            for entry in manifest['files']:files['TAP/CPM/FILES/'+entry['name']]=(b/'files'/entry['name']).read_bytes()
            utilities=[(entry['name'],(b/'files'/entry['name']).read_bytes()) for entry in manifest['files'] if not entry['name'].startswith(('PLANET','ZORK1'))]
            utilities=[(name,b'Single-sided 160KB CP/M utility disk.\r\nCPMDISK mounts DSK/TAP or returns to DIR.\r\n' if name=='README.TXT' else blob) for name,blob in utilities]
            single,_,_=make_disk(utilities,163840,128,1024)
            files['TAP/CPM/CPM160.DSK']=encode_dsk(single,1)
            files['TAP/CPM/CPM160.TAP']=encode_image(single)
        else:files['TAP/CPM/DRIVE320.IMG']=(b/'drive-a.img').read_bytes()
        for name in ['cpm_service.py','cpm_directory.py','cpm_tap.py','cpm_dsk.py']:files['optional-modern-firmware/'+name]=(ROOT/'firmware'/name).read_bytes()
        files['optional-modern-firmware/cpm_config.example320.py']=(
            "CPM_STORAGE = '"+('directory' if native else 'image')+"'\nCPM_DIRECTORY = '/CPM/FILES'\nCPM_DIRECTORY_KB = 320\nCPM_IMAGE_PATH = '/CPM/DRIVE320.IMG'\nCPM_IMAGE_SIZE = 327680\n").encode()
    for document in (ROOT/'docs').glob('*.md'):
        files.setdefault(''+document.name,document.read_bytes())
    files['checksums.txt']=''.join(hashlib.sha256(data).hexdigest()+'  '+name+'\n' for name,data in sorted(files.items())).encode()
    output=ROOT/'build'/f'ts2068-cpm-{a.profile}.zip'
    with zipfile.ZipFile(output,'w') as archive:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,data)
    print(output)

if __name__=='__main__':main()
