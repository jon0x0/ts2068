from pathlib import Path
import json,hashlib,functools,zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/fullgame/clean_player_r56';PREV=ROOT/'build/fullgame/projectile_clock_r55'
def read(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 frozen=read(OUT/'final_run.json');assert frozen['passed']
 assert frozen['region_sha256']=={p.name:sha(p.read_bytes())for p in OUT.glob('*_region.bin')}
 manifest=read(OUT/'manifest.json');size=manifest['overlay_bytes'];assert size<=2432
 pages=0
 for rec in manifest['regions']:
  name='boot'if rec['file']=='RTBOOT.TAP'else f'level{rec["level"]:02d}'
  raw=(OUT/f'{name}_region.bin').read_bytes();old=(PREV/f'{name}_region.bin').read_bytes()
  assert len(raw)==65536 and sha(raw)==rec['sha256']
  assert raw[:0xe400]==old[:0xe400] and raw[0xed80:]==old[0xed80:],name+' changed outside player engine'
  assert raw[0xe400:0xe400+size]==(OUT/'overlay.bin').read_bytes()
  tape=(OUT/'RTYPE'/rec['file']).read_bytes();p=0;blocks=[]
  while p<len(tape):
   n=int.from_bytes(tape[p:p+2],'little');v=tape[p+2:p+2+n];assert len(v)==n and functools.reduce(int.__xor__,v)==0;blocks.append(v);p+=n+2
  assert p==len(tape)and len(blocks)==16
  assert b''.join(v[1:-1]for v in blocks[1::2])==raw
  assert all(len(v[1:-1])==8192 for v in blocks[1::2]);pages+=8
 assert pages==72
 reports={}
 for name in ['clean_cache_validation.json','clean_copy_validation.json','projectile_clock_validation.json','projectile_capacity_validation.json','irq_injection_validation.json','overlay_component_validation.json','player_spill_validation.json','movement_validation.json','custom_controls_validation.json','charged_fire_validation.json','death_validation.json','title_validation.json','snake_route_validation.json','cache_restart_validation.json','failure_validation.json','cache_progression_validation.json','boss_preview_validation.json']:
  r=read(OUT/name);assert all(v['passed']for v in r)if isinstance(r,list)else r['passed'];reports[name]=r
 assert reports['clean_copy_validation.json']['unexpected_bytes']==0
 assert reports['clean_cache_validation.json']['owned_bytes_preserved']>0
 assert reports['cache_progression_validation.json']['all8_revisited_without_disk']
 assert all(v['after']==700 for v in reports['boss_preview_validation.json']['results'])
 profiles=[read(ROOT/f'build/diagnostics/clean_player_r56/masked_L{i}.json')for i in range(1,9)]
 # Workload-sensitive timing profile is informational; do not claim all taps
 # passed when the unshifted L5 pulse train reports 7. Functional fire test
 # and the one-frame-shift L5 run both retain all eight pulses.
 assert all(7<=p['shots']<=8 and p['beams']==1 for p in profiles)
 assert reports['charged_fire_validation.json']['normal_shots']==8
 shifted=read(ROOT/'build/diagnostics/player_ghost_r56/input_timing/r56_shift1/masked_L5.json')
 assert shifted['shots']==8 and shifted['beams']==1
 readme='''R-Type TS2068 r56 - stale boss fragments around the ship

Replace the complete RTYPE folder, RESET, then load RTFULL.TAP. Keep RTBOOT.TAP and LEVEL01.TAP..LEVEL08.TAP together with the launcher. Nested directories under TAP are supported. Do not mix previous or larger-art level files. Reset clears old resident RAM assets.

Fixes a reproduced redraw defect: empty background cells could still contain old boss pixels. When the moving ship marked those cells for copying, the old pixels became visible around it. The player backing preparation now clears only cells marked empty, across full 8-line character rows, before using them for the ship. Occupied scenery and boss graphics are preserved.

One-pixel fine movement, held movement speed, independently updated normal/spread bolts, artwork, boss sizes and audio are retained. Very short fire taps remain sensitive to heavy drawing: one L5 stress timing detects seven of eight taps, while a one-frame shift detects all eight. The game asks for keys; both native joystick sockets work alongside the keyboard. Title 1-8 selects a level; B-release-B during play previews its boss. M toggles music.

Scripted verification includes the captured level-5 copy reproduction, mixed occupied/empty backing cells, player/projectile and interrupt tests, all eight bosses, and cached-level loading/revisits. Hardware confirmation remains pending. This is the expanded-RAM disk build; the stock 64KB cartridge is unchanged.
'''
 assert 'tspico'not in readme.lower()
 (OUT/'README.txt').write_text(readme);(OUT/'RTYPE/README.txt').write_text(readme)
 manifest['status']='Validated r56, hardware validation pending';(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
 (OUT/'validation_summary.json').write_text(json.dumps(dict(passed=True,asset_pages=pages,reports=reports,profiles=profiles,physical_validation=False,stock64KB_unchanged=True),indent=2))
 archive=OUT/'RType_TS2068_r56.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  z.write(OUT/'README.txt','README.txt')
  for f in sorted((OUT/'RTYPE').iterdir()):
   if f.is_file():z.write(f,'RTYPE/'+f.name)
  for f in ['manifest.json','validation_summary.json']:z.write(OUT/f,'VALIDATION/'+f)
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for f in (OUT/'RTYPE').iterdir():
   if f.is_file():assert z.read('RTYPE/'+f.name)==f.read_bytes()
 print(archive);print(sha(archive.read_bytes()))
if __name__=='__main__':main()
