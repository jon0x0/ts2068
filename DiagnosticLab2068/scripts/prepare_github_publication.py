"""Stage the public diagnostic project in the isolated ts2068 hub checkout."""
from pathlib import Path
import shutil,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT/'tmp/publish-ts2068'
DEST=REPO/'DiagnosticLab2068'
DEST.mkdir(parents=True,exist_ok=True)
def copy(relative):
    source=ROOT/relative;target=DEST/relative
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
for name in ['README.md','AGENTS.md','THIRD_PARTY_CREDITS.md']:
    copy(name)
for name in ['TS2068DiagnosticLab-v0.3.zip','TS2068DiagnosticLab-v0.3-HOME-ROM.zip']:
    copy('release/'+name)
shutil.copytree(ROOT/'release/v0.3',DEST/'release/v0.3',dirs_exist_ok=True)
shutil.copytree(ROOT/'docs/manual',DEST/'docs/manual',dirs_exist_ok=True)
copy('output/pdf/TS2068-Diagnostic-Lab-Cartridge-Manual.pdf')
for folder,suffixes in [('src',{'.asm'}),('scripts',{'.py','.mjs'}),('assets',{'.bin','.png','.json','.scr'}),('docs',{'.md','.json','.txt'})]:
    for source in (ROOT/folder).rglob('*'):
        relative=source.relative_to(ROOT)
        if source.is_file() and source.suffix.lower() in suffixes and not any(x in relative.parts for x in ['archive','validation','manual','__pycache__']):copy(relative)
# Current image-bound evidence; old checkpoints and local reference files excluded.
for prefix,manifest_file in [('v02','build/manifest-v02.json'),('home','build/home/manifest.json')]:
    manifest=json.loads((ROOT/manifest_file).read_text())
    sha=manifest.get('dck_sha256',manifest.get('sha256'))
    source=ROOT/'docs/validation'/f'{prefix}-{sha[:12]}'
    for f in source.iterdir():
        if f.is_file() and f.suffix.lower() in {'.json','.log','.png','.bin','.dck','.asm','.txt'}:copy(str(f.relative_to(ROOT)))
for folder_name in ['load-'+json.loads((ROOT/'build/manifest-v02.json').read_text())['dck_sha256'][:12]]:
    shutil.copytree(ROOT/'docs/validation'/folder_name,DEST/'docs/validation'/folder_name,dirs_exist_ok=True)
for name in ['diagnostic-v02.dck','diagnostic-v02.bin','diagnostic-v02-picorom.bin','diagnostic-v02-eprom-27C512.bin','manifest-v02.json','symbols.txt']:
    copy('build/'+name)
for name in ['diagnostic-home-u16.bin','manifest.json','symbols.txt','home.asm']:
    copy('build/home/'+name)
copy('scripts/release_info.py')
for name in ['keyboard-rom.asm','keyboard-scan.asm','load-ay.asm','load-low.asm','load-symbols.txt']:
    copy('build/'+name)
# Preserve historical evidence referenced by the canonical inventory.
def copy_evidence(value):
    if isinstance(value,dict):
        for child in value.values():copy_evidence(child)
    elif isinstance(value,list):
        for child in value:copy_evidence(child)
    elif isinstance(value,str) and value.startswith('docs/validation/') and (ROOT/value).is_file():
        copy(value)
copy_evidence(json.loads((ROOT/'docs/test-registry.json').read_text(encoding='utf-8')))
(DEST/'.gitignore').write_text('__pycache__/\n/tmp/\n*.pyc\n',encoding='utf-8')
(DEST/'BUILDING.md').write_text('''# Building and validation

Release v0.3 | October 13, 2026

The supplied release images are the tested outputs. Firmware source, asset
generators, test scripts and current image-bound emulator evidence are included.
The original development workspace remains authoritative.

The build scripts currently expect the development/reference directory layout:
Python with Pillow; SjASMPlus 1.20.3 (use --assembler with build_suite.py to choose
an executable); and the verified stock TS2068 U16 ROM at the path specified in
build_suite.py and build_home_rom.py. The ROM is used to extract the embedded
character font. Original Timex manuals/schematics and third-party reference
programs are not republished here; see THIRD_PARTY_CREDITS.md for sources.

The complete entry point is python scripts/build_cartridge.py. For a different
assembler path, run python scripts/build_suite.py --assembler PATH, followed by
python -c "from scripts.build_home_rom import build; build()" with scripts on
PYTHONPATH. Verification scripts import a compatible sibling TSRun checkout;
manual generation uses ReportLab. Fuse/native/browser verification also expects
the locally configured tool paths. Adjust paths for a new development machine.

Historical validation snapshots are retained in the original workspace; only
the current image evidence is published here. Some historical registry/source
references therefore require that workspace. Read AGENTS.md and
docs/PROJECT_STATE.md before changing diagnostic behavior. Physical validation
is still pending.
''',encoding='utf-8')
readme=(DEST/'README.md').read_text(encoding='utf-8')
readme=readme.replace('## Build and run','See [build dependencies and validation notes](BUILDING.md) before rebuilding.\n\n## Build and run')
(DEST/'README.md').write_text(readme,encoding='utf-8')
(DEST/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TS2068 Diagnostic Lab</title><style>body{max-width:850px;margin:50px auto;padding:24px;font:18px/1.6 system-ui;color:#173247}a{color:#087182}h1{line-height:1.2}</style><h1>TS2068 Diagnostic Lab cartridge</h1><p>v0.3 · October 13, 2026</p><p>ROM-based hardware diagnostics with RAM chip/bit fault reporting, RAM soak, banking, audio, video, keyboard and joystick tests. A simplified replacement HOME ROM image is included.</p><p><a href="release/TS2068DiagnosticLab-v0.3.zip">Download the complete release</a> · <a href="docs/manual/index.html">Read the manual</a> · <a href="output/pdf/TS2068-Diagnostic-Lab-Cartridge-Manual.pdf">PDF manual</a> · <a href="https://github.com/jon0x0/ts2068/tree/main/DiagnosticLab2068">Source and documentation</a></p><p>Emulator-validated release candidate; physical validation pending. The cartridge requires working native startup. Follow the manual before installing the replacement U16 HOME ROM.</p></html>''',encoding='utf-8')
p=REPO/'README.md';text=p.read_text(encoding='utf-8')
text='\n'.join(line for line in text.split('\n') if not line.startswith('| TS2068 Diagnostic Lab |'))
anchor='| AI skill |'
row='| TS2068 Diagnostic Lab | ROM-based hardware diagnostics, RAM chip/bit reporting and simplified replacement HOME ROM; v0.3 | [Project](DiagnosticLab2068/) · [Release](DiagnosticLab2068/release/TS2068DiagnosticLab-v0.3.zip) · [Manual](https://jon0x0.github.io/ts2068/DiagnosticLab2068/docs/manual/) |\n'
text=text.replace(anchor,row+anchor,1);p.write_text(text,encoding='utf-8')
p=REPO/'scripts/build_site.py';text=p.read_text(encoding='utf-8')
text="\n".join(line for line in text.split("\n") if "('TS2068 Diagnostic Lab'," not in line)
anchor="    'Development tools': [\n"
row="        ('TS2068 Diagnostic Lab', 'ROM-based hardware diagnostics and RAM chip/bit reporting; cartridge and simplified HOME ROM editions.', [('Project', 'DiagnosticLab2068/'), ('Download v0.3', 'DiagnosticLab2068/release/TS2068DiagnosticLab-v0.3.zip'), ('Manual', 'DiagnosticLab2068/docs/manual/')]),\n"
text=text.replace(anchor,anchor+row,1);p.write_text(text,encoding='utf-8')
(DEST/'.gitattributes').write_text('# Preserve release checksums and image-bound source/evidence bytes on all hosts.\n* -text\n*.pdf binary\n*.bin binary\n*.dck binary\n*.zip binary\n',encoding='utf-8')
print('Prepared',DEST)
print('Files',sum(p.is_file() for p in DEST.rglob('*')))
assert (DEST/'release/TS2068DiagnosticLab-v0.3.zip').read_bytes()==(ROOT/'release/TS2068DiagnosticLab-v0.3.zip').read_bytes()
