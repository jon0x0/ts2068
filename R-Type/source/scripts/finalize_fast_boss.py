"""Publish tested compact r51 plus larger-art level5 comparison."""
from pathlib import Path
import json,hashlib,functools,zipfile
ROOT=Path(__file__).resolve().parents[1];SMALL=ROOT/'build/fullgame/compact_boss_r51';LARGE=ROOT/'build/fullgame/fast_boss_r51';PREV=ROOT/'build/fullgame/responsive_game_r50'
def read(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 unchanged=[]
 for folder in [SMALL,LARGE]:
  meta=read(folder/'manifest.json')
  for rec in meta['regions']:
   name='boot'if rec['file']=='RTBOOT.TAP'else f'level{rec["level"]:02d}';raw=(folder/f'{name}_region.bin').read_bytes();assert len(raw)==65536 and sha(raw)==rec['sha256']
   if rec['level']!=5:assert raw==(PREV/f'{name}_region.bin').read_bytes();unchanged.append((folder.name,name))
   tape=(folder/'RTYPE'/rec['file']).read_bytes();p=0;blocks=[]
   while p<len(tape):
    n=int.from_bytes(tape[p:p+2],'little');b=tape[p+2:p+2+n];assert len(b)==n and functools.reduce(int.__xor__,b)==0;blocks.append(b);p+=n+2
   assert p==len(tape)and len(blocks)==16;assert b''.join(b[1:-1]for b in blocks[1::2])==raw
  assert (folder/'launcher.bin').read_bytes()==(PREV/'launcher.bin').read_bytes()
  boss=read(folder/'boss_preview_validation.json');assert boss['passed']and boss['results'][0]['level']==5 and boss['results'][0]['after']==700
  region=(folder/'level05_region.bin').read_bytes();runtime=(folder/'boss_level5.dock7.bin').read_bytes();assert runtime[0x1380:0x1680]==region[0xf380:0xf680]
  assert region[0x8f10:0x9000]==bytes([255])*240,'Experimental auxiliary code must not ship'
 assert read(LARGE/'compiled_equivalence.json')['passed']and read(LARGE/'compiled_equivalence.json')['cases']==384
 assert read(SMALL/'compact_composition_validation.json')['passed']and read(SMALL/'compact_composition_validation.json')['cases']==384
 progression=read(SMALL/'cache_progression_validation.json');assert progression['passed']and progression['all8_revisited_without_disk']and progression['core_and_workspace_checks']==15
 summary=dict(passed=True,scope='Actual level5 native renderer and compact assets; remaining BOOT/levels byte-identical to r50',asset_pages_checked=144,unique_pages_in_package=80,unchanged_regions=unchanged,full_size_boss=read(LARGE/'boss_preview_validation.json'),compact_boss=read(SMALL/'boss_preview_validation.json'),progression=progression,draw_comparison=read(LARGE/'composition_timing.json'),clearance=read(LARGE/'clearance_analysis.json'),physical_validation=False,stock64KB_unchanged=True)
 baseline=read(PREV/'boss_level5.json')['frame'];compact=read(SMALL/'boss_level5.json')['frame'];large=read(LARGE/'boss_level5.json')['frame'];summary['route_timing']=dict(r50=baseline,compact=compact,large=large,compact_elapsed_reduction=1-compact/baseline,large_elapsed_reduction=1-large/baseline)
 readme=f'''R-Type TS2068 r51 - faster level5 boss

Replace the complete RTYPE folder; reset before loading this build so older resident RAM assets are discarded. Load RTYPE/RTFULL.TAP. Keep all9asset files together; nested folders under TAP work. The game retains its key-definition screen and both native joystick sockets. Select5 at the title, then start and B-release-B to preview the boss.

Default:24x24spheres (original native footprint),80x80core (between original64 and previous96). Native movement anchors unchanged. Selected artwork is resized/converted before packing; red nodes, shading and machinery remain. The smaller cluster leaves more manoeuvring room.

The native renderer skips decoding completely hidden source cells and copies unowned cached rows without material-composition temporary state. These are actual gameplay changes, not the host-side delta experiments.

Measured emulator tests:
- Same captured25-part redraw:2133922cycles in r50,1634424 with the same large art and new renderer,1274247 with compact art.
-700boss updates including startup/selection: r50 {baseline}refreshes, compact {compact}, large {large}. Compact takes about{round((1-compact/baseline)*100)}% less elapsed time on this route. This is not a fixed-FPS or hardware speed guarantee.
-384full-art exact-output/flip/clip/flash/metadata cases,384compact independent source decode/foreground/coverage cases; both700-update boss routes; compact full8levelcache/ending/revisit pass. Unchanged other levels and shared player/title/input/loader code retain r50 validation by exact region identity.

Optional larger artwork: ALTERNATE_LARGE_ART/LEVEL05.TAP keeps32x32spheres and96x96core with the faster renderer. Copy that one file over RTYPE/LEVEL05.TAP, then reset/reload. Keep the default smaller file elsewhere if you want to switch back. The alternate is slower but retains the previous dimensions/detail.

The clearance comparison is a static captured boss scene and excludes projectiles/timing; it does not prove normal fight difficulty. Physical testing pending. Original stock64KBread-only cartridge output unchanged. Previous separate delta prototypes are not integrated here.
'''
 assert 'tspico'not in readme.lower();(SMALL/'README.txt').write_text(readme,encoding='utf-8');(SMALL/'RTYPE/README.txt').write_text(readme,encoding='utf-8');(SMALL/'validation_summary.json').write_text(json.dumps(summary,indent=2))
 archive=SMALL/'RType_TS2068_r51.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  z.write(SMALL/'README.txt','README.txt')
  for p in sorted((SMALL/'RTYPE').iterdir()):z.write(p,'RTYPE/'+p.name)
  z.write(LARGE/'RTYPE/LEVEL05.TAP','ALTERNATE_LARGE_ART/LEVEL05.TAP');z.writestr('ALTERNATE_LARGE_ART/README.txt','Optional32px spheres/96px core. Replace RTYPE/LEVEL05.TAP and reset/reload. See root README.\n')
 with zipfile.ZipFile(archive)as z:assert z.testzip()is None
 meta=read(SMALL/'manifest.json');meta.update(status='Emulator-validated r51 compact hardware test build',package_sha256=sha(archive.read_bytes()),package_bytes=archive.stat().st_size,physical_validation=False);(SMALL/'manifest.json').write_text(json.dumps(meta,indent=2));print(archive);print(meta['package_sha256']);print(summary['route_timing'])
if __name__=='__main__':main()
