"""Final frozen r50 package: verify actual pages and current diagnostics."""
from pathlib import Path
import json,hashlib,shutil,functools,zipfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/responsive_game_r50'
def read(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 m=read(OUT/'manifest.json');reports={}
 for record in m['regions']:
  name='boot'if record['file']=='RTBOOT.TAP'else f'level{record["level"]:02d}';raw=(OUT/f'{name}_region.bin').read_bytes();assert len(raw)==65536 and sha(raw)==record['sha256'];tape=(OUT/'RTYPE'/record['file']).read_bytes();p=0;blocks=[]
  while p<len(tape):
   n=int.from_bytes(tape[p:p+2],'little');b=tape[p+2:p+2+n];assert len(b)==n and functools.reduce(int.__xor__,b)==0;blocks.append(b);p+=n+2
  assert p==len(tape)and len(blocks)==16;assert b''.join(b[1:-1]for b in blocks[1::2])==raw
  # Explicit runtime ownership: title no longer fetches its atlas from bank7.
  engine=(OUT/'overlay.bin').read_bytes();assert raw[0xe400:0xe400+len(engine)]==engine;assert len(engine)<=0x980
  title=(OUT/'title.bin').read_bytes();assert raw[0x9d10:0x9d10+len(title)]==title and len(title)<=400
 for name in ['movement_validation.json','custom_controls_validation.json','charged_fire_validation.json','death_validation.json','failure_validation.json','cache_restart_validation.json','cache_progression_validation.json','boss_preview_validation.json','title_validation.json','snake_route_validation.json','overlay_component_validation.json']:
  r=read(OUT/name);assert all(v['passed']for v in r)if isinstance(r,list)else r['passed'];reports[name]=r
 assert reports['title_validation.json']['states']==116;assert reports['boss_preview_validation.json']['passed']and len(reports['boss_preview_validation.json']['results'])==8 and all(v['after']>=700 for v in reports['boss_preview_validation.json']['results']);assert reports['cache_progression_validation.json']['all8_revisited_without_disk'];assert reports['overlay_component_validation.json']['common_pixels_never_erased']
 before=(ROOT/'build/fullgame/material_game_r49/level05_region.bin').read_bytes();after=(OUT/'level05_region.bin').read_bytes()
 for a,z in [(0xd00,0xd40),(0x14f4,0x14f8),(0x88eb,0x8f10),(0xf380,0xf680),(0xa000,0xd87c)]:assert before[a:z]==after[a:z]
 # BOOT and standalone level1 use the same snake bytes despite differing initial palette locations.
 boot=(OUT/'boot_region.bin').read_bytes();one=(OUT/'level01_region.bin').read_bytes();assert boot[0xabe7:0xad2b]==one[0xabe7:0xad2b]
 trial=ROOT/'build/diagnostics/boss_relocatable';dynamic=ROOT/'build/diagnostics/boss_dynamic';assert read(trial/'validation.json')['passed'];assert read(dynamic/'validation.json')['passed'];assert read(dynamic/'ui_validation.json')['passed'];assert sha((trial/'Bellmite_relocatable_deltas_TS2068.tap').read_bytes())==read(trial/'manifest.json')['tap_sha256']
 fixed=OUT/'TRIALS/BOSS_FIXED';fixed.mkdir(parents=True,exist_ok=True)
 for name in ['Bellmite_relocatable_deltas_TS2068.tap','README.txt','validation.json','boss_delta.gif']:shutil.copy2(trial/name,fixed/name)
 dyn=OUT/'TRIALS/BOSS_DYNAMIC';dyn.mkdir(parents=True,exist_ok=True)
 for name in ['index.html','sprites.json','validation.json','ui_validation.json','preview.png']:shutil.copy2(dynamic/name,dyn/name)
 readme='''R-Type TS2068 r50 - 512KB disk hardware test build

Replace the complete RTYPE folder. Keep RTFULL.TAP, RTBOOT.TAP and LEVEL01.TAP..LEVEL08.TAP together. The folder may be nested under TAP. Open it and load RTFULL.TAP. Levels load on demand and remain in RAM for revisits.

The game asks you to select keys. Both native joystick sockets work alongside your selected keyboard controls. Title keys1-8 choose a starting level; B-release-B during play jumps to its boss; M toggles music.

Changes:
- Faster held player movement: one-pixel initial/fine steps, then three pixels per publication after three held ticks. No triple drawing pass. Variable-height damage scratch prevents trails during larger vertical moves.
- L1 snake uses one full-sized organic joint per native24x24 frame, orientation siblings and connecting bone links. It no longer squeezes the entire arcade chain into every segment. Native anchors, collision allocation and draw dimensions remain unchanged.
- Fixed title garbage: its former bank7 atlas collided with the player engine/caches. Title suffix/phase data is now generated from the intact logo source into title scratch, restored before play. All116 moving bitmap/ECM states checked in the disk build.

Boss experiments (separate from the game):
TRIALS/BOSS_DYNAMIC/index.html is an interactive PC prototype: drag independent parts, change cels, flips and depth; arbitrary arrangements are composed over damaged cells and converted to legal8x1 pairs before delta publication. Composition/encoding is currently on the host. Native Z80 publication passed100 arbitrary-arrangement tests. This is not an integrated native boss speedup.
TRIALS/BOSS_FIXED/Bellmite_relocatable_deltas_TS2068.tap is the earlier native fixed-pose comparison:1/2/3 relocate the composed boss, Space pauses. Eight captured poses reuse deltas forward/backward. It is a comparison, not the arbitrary-state solution.

The game retains r49 Bellmite rendering. These experiments are not substituted for its gameplay renderer. World speed remains scene-dependent; weapons/AI still use rounded native coordinates; centre player pose only. Emulator validation is not physical hardware validation. Original stock64KB read-only cartridge output is unchanged.
'''
 assert 'tspico'not in readme.lower();(OUT/'README.txt').write_text(readme,encoding='utf-8');(OUT/'RTYPE/README.txt').write_text(readme,encoding='utf-8')
 summary=dict(passed=True,asset_pages=72,reports=reports,boss_dynamic=read(dynamic/'validation.json'),boss_fixed=read(trial/'validation.json'),material_compositor_reused_from_r49_by_exact_range_identity=True,physical_validation=False,stock64KB_unchanged=True);(OUT/'validation_summary.json').write_text(json.dumps(summary,indent=2));archive=OUT/'RType_TS2068_r50.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  z.write(OUT/'README.txt','README.txt')
  for folder in ['RTYPE','TRIALS']:
   for p in sorted((OUT/folder).rglob('*')):
    if p.is_file():z.write(p,p.relative_to(OUT))
 with zipfile.ZipFile(archive)as z:assert z.testzip()is None
 m.update(status='Emulator-validated r50 hardware test build',package_sha256=sha(archive.read_bytes()),package_bytes=archive.stat().st_size,physical_validation=False);(OUT/'manifest.json').write_text(json.dumps(m,indent=2));print(archive);print(m['package_sha256'])
if __name__=='__main__':main()
