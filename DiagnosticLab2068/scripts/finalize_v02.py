"""Freeze image-bound validation and assemble the operator release."""
from pathlib import Path
import json, shutil, hashlib, zipfile
from release_info import VERSION, RELEASE_DATE, RELEASE_DATE_DISPLAY, ARCHIVE_NAME, HOME_ARCHIVE_NAME

ROOT = Path(__file__).resolve().parents[1]
b = ROOT / 'build'
manifest = json.loads((b/'manifest-v02.json').read_text(encoding='utf-8-sig'))
sha = manifest['dck_sha256']
names = ['suite-ram-verification.json','suite-verification.json','suite-reporter-verification.json',
         'fuse-v02-result.json','fuse-v02-ram-result.json','image-format-verification.json','ay-verification.json','boot-verification.json','keyboard-verification.json','test-duration-estimates.json','duration-ui-verification.json','fault-timing-verification.json','joystick-verification.json','soak-verification.json','load-verification.json']
for name in names:
    record = json.loads((b/name).read_text())
    assert record['image_sha256'] == sha, (name, 'stale image')
    assert record.get('result', record.get('status')) in ('PASS','checkpoint_completed'), name
dest = ROOT / 'docs/validation' / ('v02-'+sha[:12])
dest.mkdir(parents=True, exist_ok=True)
for capture in b.glob('duration-*-screen.bin'): shutil.copy2(capture,dest/capture.name)
for name in ['ram-pass-active-v02.bin','ram-pass-active-v02.png']:
    if (b/name).is_file(): shutil.copy2(b/name,dest/name)
from generate_design_assets import standard_render
from PIL import Image
for stem in ['menu','fault-U6','fault-U7']:
    raw = (b/(stem+'-v02-screen.bin' if stem=='menu' else stem+'-v02.bin')).read_bytes()
    standard_render(raw[:6144], raw[6144:]).resize((768,576),Image.Resampling.NEAREST).save(b/(stem+'-v02-actual.png'))
raw=(b/'ay-listen-active-v02.bin').read_bytes()
standard_render(raw[:6144],raw[6144:]).resize((768,576),Image.Resampling.NEAREST).save(b/'ay-listen-active-v02.png')
for stem in ['startup-R','startup-F','cpu-guide','fault-guide','full-overview','full-summary','keyboard']:
    raw=(b/(stem+'-active-v02.bin')).read_bytes()
    standard_render(raw[:6144],raw[6144:]).resize((768,576),Image.Resampling.NEAREST).save(b/(stem+'-active-v02.png'))
for name in names + ['manifest-v02.json','fuse-v02-checkpoint.log','fuse-v02-ram-checkpoint.log',
                      'menu-v02-actual.png','fault-U6-v02-actual.png','fault-U7-v02-actual.png','ay-listen-active-v02.bin','ay-listen-active-v02.png',
                      'startup-R-active-v02.png','startup-F-active-v02.png','cpu-guide-active-v02.png',
                      'diagnostic-v02.dck','diagnostic-v02.bin','diagnostic-v02-picorom.bin','diagnostic-v02-eprom-27C512.bin',
                      'fault-guide-active-v02.bin','fault-guide-active-v02.png','full-overview-active-v02.bin','full-overview-active-v02.png',
                      'full-summary-active-v02.bin','full-summary-active-v02.png','keyboard-active-v02.bin','keyboard-active-v02.png','keyboard-art-layout.json','symbols.txt','crc-symbols.txt','cpu-symbols.txt']:
    shutil.copy2(b/name, dest/name)
for name in ['src/diagnostic.asm','src/modules.asm','src/crc.asm','src/cpu.asm','src/boot.asm','scripts/build_suite.py',
             'scripts/build_cartridge.py','scripts/build_v01.py','scripts/suite_assets.py',
             'scripts/verify_suite.mjs','scripts/verify_suite_ram.mjs','scripts/verify_suite_reporter.mjs',
             'scripts/generate_design_assets.py','scripts/check_suite_fuse.py','scripts/check_suite_fuse_ram.py',
             'scripts/verify_image_formats.py','scripts/verify_ay.mjs','scripts/verify_boot.mjs','scripts/verify_keyboard.mjs','scripts/keyboard_art.py','scripts/build_manual.py','scripts/check_manual.mjs','scripts/measure_test_durations.mjs','scripts/verify_duration_ui.mjs','docs/TEST_DURATIONS.md',
             'docs/EPROM_LOADING.md','docs/REPLICATED_RECOVERY_ROM.md','docs/BOOT_PATH_DIAGNOSTICS.md','docs/FULL_TEST_COVERAGE.md','docs/KEYBOARD_ART.md','docs/RAM_SOUND_CODES.md','scripts/verify_fault_timing.mjs','scripts/verify_joystick.mjs','src/joystick.asm','docs/JOYSTICK_TEST.md','docs/HOME_ROM_EDITION.md',
             'assets/keyboard/TSRun-keyboard.png','assets/keyboard/provenance.json','assets/video/ecm-pixels.bin','assets/video/ecm-attributes.bin']:
    target=dest/'source'/name; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/name,target)
registry = ROOT/'docs/test-registry.json'
data=json.loads(registry.read_text(encoding='utf-8-sig'))
def refresh(value):
    if isinstance(value,dict):
        current_v02 = 'validation/v02-' in json.dumps(value)
        for k,v in value.items():
            if k=='image_sha256' and isinstance(v,str) and current_v02: value[k]=sha
            else: value[k]=refresh(v)
    elif isinstance(value,list): value=[refresh(v) for v in value]
    elif isinstance(value,str):
        import re
        value=re.sub(r'validation/v02-[0-9a-f]+/', 'validation/v02-'+sha[:12]+'/', value)
    return value
registry.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
release=ROOT/'release'/VERSION; release.mkdir(parents=True,exist_ok=True)
for name in ['diagnostic-v02.dck','diagnostic-v02.bin','diagnostic-v02-picorom.bin','diagnostic-v02-eprom-27C512.bin']:
    shutil.copy2(b/name,release/name)
shutil.copy2(b/'manifest-v02.json',release/'manifest.json')
shutil.copy2(b/'menu-v02-actual.png',release/'menu.png')
if (b/'ram-pass-active-v02.png').is_file(): shutil.copy2(b/'ram-pass-active-v02.png',release/'ram-pass.png')
shutil.copy2(ROOT/'docs/tests/V02_DIAGNOSTIC_SUITE.md',release/'OPERATOR_NOTES.md')
shutil.copy2(ROOT/'THIRD_PARTY_CREDITS.md',release/'CREDITS.md')
shutil.copy2(ROOT/'docs/PICOROM_LOADING.md',release/'PICOROM_LOADING.md')
shutil.copy2(ROOT/'docs/EPROM_LOADING.md',release/'EPROM_LOADING.md')
shutil.copy2(ROOT/'docs/BOOT_PATH_DIAGNOSTICS.md',release/'BOOT_DIAGNOSTICS.md')
shutil.copy2(ROOT/'docs/FULL_TEST_COVERAGE.md',release/'FULL_TEST_COVERAGE.md')
shutil.copy2(ROOT/'docs/TEST_DURATIONS.md',release/'TEST_DURATIONS.md')
shutil.copy2(ROOT/'docs/RAM_SOUND_CODES.md',release/'RAM_SOUND_CODES.md')
shutil.copy2(ROOT/'docs/JOYSTICK_TEST.md',release/'JOYSTICK_TEST.md')
shutil.copy2(ROOT/'docs/HOME_ROM_EDITION.md',release/'HOME_ROM_EDITION.md')
shutil.copy2(ROOT/'docs/SINISTAR_LOAD_TEST.md',release/'SINISTAR_LOAD_TEST.md')
shutil.copy2(ROOT/'docs/POWER_LOAD_TROUBLESHOOTING.md',release/'POWER_LOAD_TROUBLESHOOTING.md')
for source_name in ['src/load.asm','src/load_low.asm','scripts/verify_load.mjs','docs/SINISTAR_LOAD_TEST.md','docs/POWER_LOAD_TROUBLESHOOTING.md']:
    target=dest/'source'/source_name; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/source_name,target)
shutil.copy2(b/'joystick-active.screen',dest/'joystick-active.screen')
home=b/'home'
home_manifest=json.loads((home/'manifest.json').read_text())
home_sha=home_manifest['sha256']
assert hashlib.sha256((home/'diagnostic-home-u16.bin').read_bytes()).hexdigest()==home_sha
for evidence_name in ['verification.json','fuse-verification.json','joystick-verification.json','soak-verification.json']:
    record=json.loads((home/evidence_name).read_text())
    assert record['image_sha256']==home_sha,(evidence_name,'stale HOME image')
    assert record.get('result',record.get('status')) in ('PASS','checkpoint_completed'),evidence_name
home_dest=ROOT/'docs/validation'/('home-'+home_sha[:12]);home_dest.mkdir(parents=True,exist_ok=True)
for name in ['manifest.json','verification.json','fuse-verification.json','fuse.log','joystick-verification.json','soak-verification.json','diagnostic-home-u16.bin','home.asm','pool.bin','symbols.txt','joystick.bin','joystick-active.screen']:
    shutil.copy2(home/name,home_dest/name)
for name in ['scripts/build_home_rom.py','scripts/verify_home_rom.mjs','scripts/check_home_fuse.py','scripts/verify_joystick.mjs','scripts/verify_soak.mjs','src/joystick.asm','docs/HOME_ROM_EDITION.md','docs/JOYSTICK_TEST.md']:
    target=home_dest/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
shutil.copy2(home/'diagnostic-home-u16.bin',release/'diagnostic-home-u16.bin')
shutil.copy2(home/'manifest.json',release/'home-manifest.json')
shutil.copy2(ROOT/'docs/KEYBOARD_ART.md',release/'KEYBOARD_ART.md')
shutil.copy2(ROOT/'docs/RELEASE_POST.txt',release/'RELEASE_POST.txt')
shutil.copy2(ROOT/'scripts/verify_soak.mjs',dest/'source/scripts/verify_soak.mjs')
for name in ['soak-stopped.screen','soak-stopped.png']:
    shutil.copy2(b/name,dest/name)
shutil.copy2(b/'soak-stopped.png',release/'soak-stopped.png')
if (ROOT/'output/pdf/TS2068-Diagnostic-Lab-Cartridge-Manual.pdf').is_file():
    shutil.copy2(ROOT/'output/pdf/TS2068-Diagnostic-Lab-Cartridge-Manual.pdf',release/'TS2068-Diagnostic-Lab-Cartridge-Manual.pdf')
    shutil.copytree(ROOT/'docs/manual',release/'manual',dirs_exist_ok=True)
shutil.copy2(ROOT/'docs/TSPICO_DIAGNOSTIC_PROFILE.md',release/'TSPICO_PROFILE.md')
shutil.copy2(ROOT/'docs/HARDWARE_ASSISTED_ROADMAP.md',release/'HARDWARE_ROADMAP.md')
shutil.copy2(b/'ay-listen-active-v02.png',release/'ay-listen.png')
(release/'RELEASE.json').write_text(json.dumps(dict(product='TS2068 Diagnostic Lab cartridge',version=VERSION,release_date=RELEASE_DATE,cartridge_sha256=sha,home_rom_sha256=home_sha),indent=2)+'\n')
for document in release.glob('*'):
    if document.suffix.lower() not in ('.md','.txt') or document.name=='SHA256SUMS.txt':continue
    content=document.read_text(encoding='utf-8')
    stamp=f'Release {VERSION} | {RELEASE_DATE_DISPLAY}'
    if stamp not in content:
        if content.startswith('#'):
            first,separator,rest=content.partition('\n')
            content=first+'\n\n'+stamp+'\n'+rest
        else:content=stamp+'\n\n'+content
        document.write_text(content,encoding='utf-8')
(release/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(release).as_posix()+'\n' for p in sorted(release.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.txt'))
with zipfile.ZipFile(ROOT/'release'/ARCHIVE_NAME,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(release.rglob('*')):
        if p.is_file(): z.write(p,p.relative_to(release).as_posix())
with zipfile.ZipFile(ROOT/'release'/HOME_ARCHIVE_NAME,'w',zipfile.ZIP_DEFLATED) as z:
    for name in ['diagnostic-home-u16.bin','home-manifest.json','HOME_ROM_EDITION.md','JOYSTICK_TEST.md','RAM_SOUND_CODES.md','CREDITS.md','TS2068-Diagnostic-Lab-Cartridge-Manual.pdf']:
        z.write(release/name,name)
shutil.copy2(ROOT/'release'/ARCHIVE_NAME,ROOT/'release/diagnostic-current.zip')
shutil.copy2(ROOT/'release'/HOME_ARCHIVE_NAME,ROOT/'release/diagnostic-home-current.zip')
print('Frozen validated image',sha,'at',dest)
