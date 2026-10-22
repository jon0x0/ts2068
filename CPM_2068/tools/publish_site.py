"""Stage CP/M 2.2 source, downloads and static Pages into an existing hub clone.

Does not commit, push, install firmware or overwrite users' saved disks.
pip install Markdown==3.9 (or use build/site-tools).
"""
from pathlib import Path
import argparse, hashlib, html, json, re, shutil, sys, zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'build/site-tools'))
import markdown

TAG='cpm22-v0.1.0'
CSS='''*{box-sizing:border-box}html{color-scheme:dark}body{margin:0;background:#111820;color:#e4ecf1;font:17px/1.65 system-ui,sans-serif}main{max-width:1060px;margin:auto;padding:32px 24px 70px}a{color:#8ddceb;text-underline-offset:3px}h1{font-size:clamp(30px,5vw,51px);line-height:1.15}h2{margin-top:36px}h3{margin-top:28px}p,li{max-width:86ch}nav{display:flex;gap:18px;flex-wrap:wrap;font-size:14px;border-bottom:1px solid #3c5260;padding-bottom:18px}.lead{font-size:21px;color:#bdd5de}.buttons{display:flex;flex-wrap:wrap;gap:12px;margin:25px 0}.button{background:#244455;border:1px solid #78b7c4;border-radius:6px;padding:10px 15px;font-weight:650}pre{overflow:auto;background:#0b1118;border:1px solid #344c59;padding:16px;border-radius:6px;line-height:1.5}code{font-size:.9em}table{border-collapse:collapse;display:block;overflow:auto;font-size:15px}th,td{border:1px solid #3c5260;padding:9px 12px;text-align:left;vertical-align:top}th{background:#203540}footer{margin-top:40px;border-top:1px solid #3c5260;padding-top:16px;font-size:14px;color:#b3c7cf}.note{border-left:4px solid #8ddceb;padding:6px 18px;background:#1b2d37}img{max-width:100%}'''

def read(path):
    data=path.read_bytes()
    try:return data.decode('utf-8-sig')
    except UnicodeDecodeError:return data.decode('cp1252')

def page(title,body,prefix=''):
    links=[('Project',prefix+'index.html'),('Quickstart',prefix+'docs/quickstart.html'),
           ('Run CP/M',prefix+'play/'),('Downloads',prefix+'index.html#downloads'),
           ('Source','https://github.com/jon0x0/ts2068/tree/main/CPM_2068')]
    nav=''.join(f'<a href="{url}">{label}</a>' for label,url in links)
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} · TS2068 CP/M 2.2</title><style>{CSS}</style></head><body><main><nav>{nav}</nav>{body}<footer>Jon Becker · CP/M 2.2 · {TAG} · <a href="{prefix}docs/release.html">Build, attribution and validation</a> · <a href="{prefix}docs/infocom-notice.html">Infocom notice</a></footer></main></body></html>'

def render(text):
    out=markdown.markdown(text,extensions=['fenced_code','tables','toc'])
    # Preserve external source URLs; turn only project-relative Markdown links into Pages links.
    def link(match):
        url=match[1]
        if ':' not in url:
            url=re.sub(r'\.md(?=#|$)','.html',url)
        return 'href="'+url+'"'
    return re.sub(r'href="([^"]+)"',link,out)

def archive(path,files):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,data)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--hub',type=Path,default=ROOT/'build/publish-hub');a=p.parse_args()
    hub=a.hub.resolve();target=hub/'CPM_2068';target.mkdir(exist_ok=True)
    for folder in ['src','assets','config','firmware','tools','tests','web','third_party']:
        shutil.copytree(ROOT/folder,target/folder,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.git','__pycache__','sjasmplus','z88dk','*.pyc'))
    for name in ['README.md','LICENSE','Makefile','.gitignore','.gitattributes']:
        shutil.copyfile(ROOT/name,target/name)
    docs=target/'docs';docs.mkdir(exist_ok=True)
    for doc in (ROOT/'docs').glob('*.md'):
        text=read(doc)
        (docs/doc.name).write_text(text,encoding='utf-8')
        (docs/(doc.stem+'.html')).write_text(page(doc.stem,render(text),'../'),encoding='utf-8')
    downloads=target/'downloads';downloads.mkdir(exist_ok=True)
    notices={'LICENSE':(ROOT/'LICENSE').read_bytes(),
             'third_party/cpm22/LICENSE.txt':(ROOT/'third_party/cpm22/LICENSE.txt').read_bytes(),
             'third_party/font8x8/NOTICE.md':(ROOT/'third_party/font8x8/NOTICE.md').read_bytes(),
             'third_party/CPM_UTILITIES_NOTICE.md':(ROOT/'third_party/CPM_UTILITIES_NOTICE.md').read_bytes(),
             'INFOCOM-NOTICE.md':(ROOT/'docs/infocom-notice.md').read_bytes()}
    guide={f'docs/{d.name}':d.read_bytes() for d in docs.glob('*.md')}
    tools={f'tools/{n}':(ROOT/'tools'/n).read_bytes() for n in ['cpm_disk.py','make_disk.py','oliger_image.py','tspico_ram_image.py','prepare_infocom.py','fetch_infocom.py','run_oliger.ps1']}
    # Package the current, public-font dual build; game inputs remain outside source import.
    from package_dual import main as package_dual
    package_dual()
    with zipfile.ZipFile(ROOT/'build/ts2068-cpm-tspico-dual.zip') as z:
        dual={n:z.read(n) for n in z.namelist()}
    dual.update(notices);dual.update(guide)
    dual['QUICKSTART.md']=(ROOT/'docs/quickstart.md').read_bytes()
    dual.pop('checksums.txt',None)
    dual['checksums.txt']=''.join(hashlib.sha256(v).hexdigest()+'  '+k+'\n' for k,v in sorted(dual.items())).encode()
    archive(downloads/'cpm22-tspico-dual.zip',dual)
    oliger={**notices,**guide,**tools,'QUICKSTART.md':(ROOT/'docs/quickstart.md').read_bytes()}
    for kb,key in [(160,'oliger'),(320,'oliger320')]:
        prof=ROOT/'build/profiles'/key
        for ext,src in [('dck','ts2068-cpm.dck'),('dsk','oliger-cpm.dsk')]:
            data=(prof/src).read_bytes();oliger[f'{kb}/cpm22.{ext}']=data
            (downloads/f'cpm22-utilities-{kb}.{ext}').write_bytes(data)
    archive(downloads/'cpm22-oliger.zip',oliger)
    gamefiles={**notices,**guide,**tools,'build/infocom-cpm.dsk':(ROOT/'build/infocom-cpm.dsk').read_bytes(),
               'build/infocom-cpm.dck':(ROOT/'build/profiles/oliger320/ts2068-cpm.dck').read_bytes(),
               'build/infocom-cpm.manifest.json':(ROOT/'build/infocom-cpm.manifest.json').read_bytes(),
               'tools/run_infocom.ps1':(ROOT/'tools/run_infocom.ps1').read_bytes()}
    archive(downloads/'cpm22-infocom-oliger.zip',gamefiles)
    (downloads/'cpm22-infocom-320.dsk').write_bytes(gamefiles['build/infocom-cpm.dsk'])
    (downloads/'cpm22-infocom-320.dck').write_bytes(gamefiles['build/infocom-cpm.dck'])
    archive(downloads/'cpm22-python-tools.zip',{**tools,**notices,**guide})
    play=target/'play';play.mkdir(exist_ok=True)
    for file in (ROOT/'web/tsrun').glob('*'):
        if file.is_file():shutil.copyfile(file,play/file.name)
    runtime=play/'tsrun';runtime.mkdir(exist_ok=True)
    for module in ['machine','keyboard']:
        (runtime/(module+'.js')).write_text(f'export * from "../../../arcade-ports/sinistar/play/tsrun/{module}.js";\n')
    media=play/'media';media.mkdir(exist_ok=True)
    for kb in [160,320]:
        shutil.copyfile(downloads/f'cpm22-utilities-{kb}.dck',media/f'cpm{kb}.dck')
    shutil.copyfile(downloads/'cpm22-utilities-160.dsk',media/'cpm160.dsk')
    shutil.copyfile(downloads/'cpm22-infocom-320.dsk',media/'cpm320.dsk')
    config={'rom0':'../../arcade-ports/sinistar/play/tsrun/roms/ts2068-0.rom','rom1':'../../arcade-ports/sinistar/play/tsrun/roms/ts2068-1.rom',
            'media':{str(kb):{'disk':f'CP/M 2.2 {kb}KB'+(' Planetfall + Zork I' if kb==320 else ' utilities'),
                             'diskUrl':f'./media/cpm{kb}.dsk','cartridgeUrl':f'./media/cpm{kb}.dck','games':kb==320} for kb in [160,320]}}
    (play/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    content=read(play/'index.html').replace('<h1>CP/M on TSRun</h1>','<h1>CP/M 2.2 on TSRun</h1><p><a href="../">Project &amp; downloads</a> · <a href="../docs/quickstart.html">Quickstart</a> · <a href="?size=320">320KB games</a> · <a href="?size=160">160KB utilities</a></p>').replace('DIR, SUBMIT DEMO, PLANET, ZORK1…','DIR, SUBMIT DEMO, PLANET, ZORK1…')
    content=content.replace('</main>','<p>Emulator: <a href="https://github.com/josef-jelinek/TSRun">Josef Jelinek’s TSRun</a>, hub snapshot 41dbe3e. <a href="../docs/infocom-notice.html">Game attribution</a>. Download working disks before switching startup size.</p></main>')
    (play/'index.html').write_text(content,encoding='utf-8')
    # A source ZIP is convenient without putting machine-local builds or attachments on GitHub.
    excluded={'play','downloads','.git','build'}
    source={str(f.relative_to(target)).replace('\\','/'):f.read_bytes() for f in target.rglob('*') if f.is_file() and not any(part in excluded for part in f.relative_to(target).parts) and f.suffix!='.html'}
    archive(downloads/'cpm22-source.zip',source)
    sums=''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n' for f in sorted(downloads.iterdir()) if f.is_file() and f.name!='SHA256SUMS')
    (downloads/'SHA256SUMS').write_text(sums)
    entries=[('quickstart','Quickstart: TSPico, Fuse and browser'),('tspico-session','Example session and saving RAMDisk'),('using-cpm','Utilities, colors, columns and HI'),('picovideo','PicoVideo 4.2 upgrade and 64/80 columns'),('ramdisk-implementation','Technical background: banked RAM and Oliger images'),('tspico-firmware','Firmware feature matrix'),('software-install','Download software and create a disk'),('disk-tools','Python disk utilities'),('release','Build, provenance and validation'),('infocom-notice','Infocom source and rights notice')]
    body='''<h1>CP/M 2.2 on the TS2068</h1><p class="lead">A cartridge-booted CP/M environment for TSPico, Oliger-enabled Fuse and your browser.</p><p>Release cpm22-v0.1.0 · 64 columns on a normal TS2068 · 80 columns with supported PicoVideo 4.2 · 160KB and 320KB disks</p><div class="buttons"><a class="button" href="play/">Run CP/M in your browser</a><a class="button" href="docs/quickstart.html">Get started on hardware or Fuse</a></div><p>The TSPico version loads a disk into banked SRAM using the original 1.00 protocol or compatible modern interfaces. Work in CP/M, assemble the HI example, edit files, or run Planetfall and Zork I. Save your RAMDisk explicitly before power-off. Modern direct-SD/native-file support needs the optional CP/M service.</p><h2 id="downloads">Downloads</h2>'''
    for label,name in [('TSPico cartridge, preload, games and tools','cpm22-tspico-dual.zip'),('Fuse/Oliger utilities: matched 160KB and 320KB pairs','cpm22-oliger.zip'),('Planetfall + Zork I: 320KB Oliger disk and cartridge','cpm22-infocom-oliger.zip'),('Source code','cpm22-source.zip'),('Python disk tools and guides','cpm22-python-tools.zip')]:
        body+=f'<p><a href="downloads/{name}">{label}</a></p>'
    body+='<p>Direct game files: <a href="downloads/cpm22-infocom-320.dsk">320KB DSK</a> + <a href="downloads/cpm22-infocom-320.dck">matching cartridge</a>. <a href="downloads/SHA256SUMS">SHA-256 checksums</a>. <a href="docs/infocom-notice.html">Infocom attribution and rights</a>.</p><h2>Guides</h2><ul>'
    body+=''.join(f'<li><a href="docs/{name}.html">{label}</a></li>' for name,label in entries)+'</ul>'
    body+='<h2>Why the extra RAM?</h2><p>CP/M needs writable low memory. The cartridge supplies 32KiB of DOCK RAM while the upper OS resides in HOME RAM, leaving a 52,992-byte TPA. TSPico supplies this mapping plus separate banked SRAM for RAMDisk. A suitably modified PicoCartridge/PicoROM could provide the required RAM too.</p><h2>64 or 80 columns</h2><p>Use COLUMNS 64 or COLUMNS 80. The older published PicoVideo V4 reports version register 10 hex, lacks the supported text renderer and captures writes to banked video-address ranges. That can look like screen corruption while CP/M is still running. PicoVideo 4.2 filters banked writes and supplies 80-column text. TSPico firmware is a separate device and upgrade.</p><h2>Disk compatibility</h2><p>Single-sided 160KB and double-sided 320KB standard DSK images share disk bytes through our TAP adapters. This is CP/M filesystem/image compatibility, not a general Oliger controller emulation on TSPico. A is the only implemented drive. The browser and Fuse require a cartridge matching the image geometry.</p><div class="note"><p>Original TSPico 1.00 has booted and run the games on hardware. Many failure cases, modern services and PicoVideo 4.2 are tested with native Z80/protocol models; see the validation notes for limits. This release is CP/M 2.2, leaving a separate path for future 3.x work.</p></div>'
    (target/'index.html').write_text(page('Cartridge, RAMDisk and browser',body),encoding='utf-8')
    print('Staged',target)

if __name__=='__main__':main()
