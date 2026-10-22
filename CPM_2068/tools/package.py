"""Package the selected cartridge profile and its matching data files."""
import argparse,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def package(experimental=False):
    b=ROOT/'build';items={}
    items['LICENSE']=ROOT/'LICENSE'
    items['third_party/cpm22/LICENSE.txt']=ROOT/'third_party/cpm22/LICENSE.txt'
    items['docs/provenance.md']=ROOT/'docs/provenance.md'
    items['picovideo.md']=ROOT/'docs/picovideo.md'
    items['startup.md']=ROOT/'docs/startup.md'
    for name in ('using-cpm.md','tspico-firmware.md'):
        items[name]=ROOT/'docs'/name
    manifest=json.loads((b/'manifest.json').read_text());profile=manifest['profile']
    if profile.startswith('tspico-'):
        raise SystemExit('Use tools/package_tspico.py --profile '+profile+' for its matching TAP/SD layout')
    if profile=='combined' and not experimental:
        raise SystemExit('Modern firmware prototype requires explicit --experimental; not stock 1.00 compatible')
    profile_key='oliger320' if profile=='oliger' and manifest.get('sides')==2 else profile
    items['build/profiles/'+profile_key+'/ts2068-cpm.dck']=b/'ts2068-cpm.dck'
    items['build/manifest.json']=b/'manifest.json'
    items['build/checksums.txt']=b/'checksums.txt'
    items['build/drive-a.img']=b/'drive-a.img'
    items['build/ts2068-cpm-system.bin']=b/'ts2068-cpm-system.bin'
    items['build/ts2068-cpm-tspico.dck']=b/'ts2068-cpm-tspico.dck'
    items['build/ts2068-cpm.dck']=b/'ts2068-cpm.dck'
    for f in manifest['files']:
        items['build/sdcard/CPM/FILES/'+f['name']]=b/'sdcard/CPM/FILES'/f['name']
    if profile=='oliger':
        items['build/oliger-cpm.dsk']=b/'oliger-cpm.dsk'
        items['README.md']=ROOT/'docs/oliger.md'
        items['disk-tools.md']=ROOT/'docs/disk-tools.md'
        for name in ['run_oliger.ps1','create_oliger_disk.py','make_disk.py','oliger_image.py','cpm_disk.py','tspico_ram_image.py','prepare_infocom.py']:
            items['tools/'+name]=ROOT/'tools'/name
    else:
        items['README.md']=ROOT/'README.md'
    if profile=='combined':
        for name in ['cpm_service.py','cpm_directory.py','cpm_config.example.py']:
            items['firmware/'+name]=ROOT/'firmware'/name
    for document in (ROOT/'docs').glob('*.md'):
        items.setdefault(document.name,document)
    output=b/('ts2068-cpm-'+profile_key+'.zip')
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name,p in sorted(items.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,p.read_bytes())
    print(output)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--experimental',action='store_true')
    package(p.parse_args().experimental)
