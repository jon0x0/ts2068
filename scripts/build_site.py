"""Generate the static hub and cartridge catalog without external dependencies."""
from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parents[1]
GITHUB = 'https://github.com/jon0x0/'
groups = {
    'TS2068 Arcade ports': [
        ('Sinistar', 'Mine crystals, build your Sinibomb supply and survive the hunt.', [('Play · virtual D-pad', 'arcade-ports/sinistar/play-dpad/'), ('Newer TSRun comparison', 'arcade-ports/sinistar/play/'), ('Original 60 Hz demo', 'arcade-ports/sinistar/web/'), ('Source', GITHUB+'ts2068/tree/main/arcade-ports/sinistar'), ('Graphics & optimization article', 'articles/drawing-less/')]),
        ('Berzerk', 'The arcade port with virtual D-pad and touch controls.', [('Play', 'https://jon0x0.github.io/berzerk_ts2068/'), ('Project', GITHUB+'berzerk_ts2068')]),
    ],
    'Development tools': [
        ('AI skill', 'Reusable skills, tools, examples and technical references for TS2068 development.', [('Project', GITHUB+'AISkill_TS2068')]),
        ('TSRun', 'Josef Jelinek’s TS2068 browser emulator.', [('Emulator', 'https://josef-jelinek.github.io/TSRun/'), ('Project', 'https://github.com/josef-jelinek/TSRun')]),
    ],
    'Demos': [
        ('Boing Ball', 'Amiga-inspired bouncing ball in TS2068 Extended Colour Mode with AY sound.', [('Play', 'https://jon0x0.github.io/TSVideoCodec/?demo=boing'), ('Project', GITHUB+'TSVideoCodec')]),
        ('Juggler', 'Banked video cartridge demonstrating temporal reconstruction.', [('Play', 'https://jon0x0.github.io/TSVideoCodec/?demo=juggler'), ('Project', GITHUB+'TSVideoCodec')]),
        ('Newton', 'Tape-loadable TSVideoCodec RAM-player demo.', [('Play', 'https://jon0x0.github.io/TSVideoCodec/?demo=newton'), ('Project', GITHUB+'TSVideoCodec')]),
        ('Beast demo', 'Shadow of the Beast inspired parallax cartridge.', [('Play', 'https://jon0x0.github.io/beastdemo_ts2068/'), ('Project', GITHUB+'beastdemo_ts2068')]),
        ('Aqueduct', 'Aqueduct and speedboat parallax demo.', [('Play', 'https://jon0x0.github.io/aqueduct_ts2068/'), ('Project', GITHUB+'aqueduct_ts2068')]),
    ],
    'Applications': [
        ('TSWriter', 'Native word processor with proportional fonts, extended color, pictures and RTF interchange.', [('Run in browser', 'https://jon0x0.github.io/TSWriter/play/'), ('Project page', 'https://jon0x0.github.io/TSWriter/'), ('Project', GITHUB+'TSWriter')]),
    ],
    'Audio and video': [
        ('speech2ay', 'Harmonic AY synthesis for speech and effects, with the TS2068 Audio Lab.', [('Audio Lab', 'https://jon0x0.github.io/speech2ay/'), ('Project', GITHUB+'speech2ay')]),
        ('TSVideoCodec', 'SCLD-aware video codec, including Boing and Juggler cartridge demos.', [('Project', GITHUB+'TSVideoCodec')]),
    ],
}
style = '''*{box-sizing:border-box}html{color-scheme:dark}body{margin:0;background:#10151c;color:#edf2f8;font:16px/1.65 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:45px 24px}a{color:#8de0ed;text-underline-offset:4px}a:hover{color:white}h1{font-size:clamp(38px,7vw,66px);line-height:1.1;letter-spacing:-.04em;margin:12px 0}h2{font-size:23px;margin:34px 0 14px}h3{font-size:20px;margin:0 0 8px}p{color:#b8c6d7;margin:8px 0 16px}.eyebrow{font-size:12px;letter-spacing:.18em;text-transform:uppercase}.feature{border:1px solid #53707f;background:#192d36;padding:22px;border-radius:12px;margin:28px 0}.feature a{font-size:24px;font-weight:700}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}.card{background:#1a222d;border:1px solid #334354;border-radius:10px;padding:22px}.card p{font-size:14px}.links{display:flex;gap:16px;flex-wrap:wrap;font-size:14px}footer{border-top:1px solid #334354;margin-top:38px;padding-top:18px;font-size:13px}nav{display:flex;gap:24px;flex-wrap:wrap;font-size:14px}.download{font-weight:700}'''

def link(label, url):
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'

def page(title, body, back=''):
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+escape(title)+'</title><style>'+style+'</style></head><body><main>'+back+body+'<footer>Timex Sinclair 2068 projects · '+link('GitHub', GITHUB+'ts2068')+'<p>Projects retain their own attribution and licensing. Existing project URLs remain unchanged.</p></footer></main></body></html>\n'

body='<p class="eyebrow">Timex Sinclair 2068</p><h1>TS2068</h1><p>Arcade and Spectrum ports, demos, applications and development tools — together in one place.</p>'
body+='<div class="feature">'+link('TS2068 Cartridges →', 'ts2068-cartridges/')+'<p>Get all nine available .dck cartridge downloads from one catalog.</p></div>'
for heading, projects in groups.items():
    body+='<section><h2>'+escape(heading)+'</h2><div class="cards">'
    for title, description, links in projects:
        body+='<article class="card"><h3>'+escape(title)+'</h3><p>'+escape(description)+'</p><div class="links">'+''.join(link(*pair) for pair in links)+'</div></article>'
    body+='</div></section>'
body+='<section><h2>Spectrum ports</h2><p>Elite conversion work is currently local. Public source and cartridge links will be added when ready.</p></section>'
(ROOT/'index.html').write_text(page('TS2068 · Projects and cartridges', body), encoding='utf-8')

# Cartridge rows are maintained in the catalog README, including exact download URLs.
body='<p class="eyebrow">Downloads</p><h1>TS2068 Cartridges</h1><p>All available cartridges in one place. Files stay with their owning projects; external downloads follow their current main branches.</p>'
count=0; opened=False
for line in (ROOT/'ts2068-cartridges/README.md').read_text(encoding='utf-8').splitlines():
    if line.startswith('## '):
        if opened: body+='</div></section>'
        body+='<section><h2>'+escape(line[3:])+'</h2><div class="cards">';opened=True
    if not line.startswith('| '): continue
    cells=[x.strip() for x in line.strip('|').split('|')]
    if len(cells)!=3: continue
    download=re.search(r'\[([^]]+)\]\(([^)]+)\)',cells[1])
    if not download: continue
    count+=1;name,url=download.groups()
    body+='<article class="card"><h3>'+escape(cells[0])+'</h3><p class="download">'+link('Download '+name,url)+'</p><div class="links">'
    for label,target in re.findall(r'\[([^]]+)\]\(([^)]+)\)',cells[2]):
        if target=='../arcade-ports/sinistar/':target=GITHUB+'ts2068/tree/main/arcade-ports/sinistar'
        if target=='../arcade-ports/sinistar/play/':target='../arcade-ports/sinistar/play-dpad/';label='Play with virtual D-pad'
        body+=link(label,target)
    body+='</div></article>'
if opened:body+='</div></section>'
assert count==9, f'Update the hub download count: found {count}'
body+='<p>Sinistar is a playable development port verified in emulators; physical hardware validation is pending. See each project for controls and compatibility.</p>'
(ROOT/'ts2068-cartridges/index.html').write_text(page('TS2068 Cartridges', body, '<nav>'+link('← TS2068 hub','../')+'</nav>'),encoding='utf-8')
(ROOT/'.nojekyll').touch()
print('Generated hub and cartridge catalog:',count,'downloads')
