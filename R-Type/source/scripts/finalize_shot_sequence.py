from pathlib import Path
import json,hashlib,functools,zipfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/shot_sequence_r57';PREV=ROOT/'build/fullgame/clean_player_r56'
def read(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 frozen=read(OUT/'final_run.json');assert frozen['passed']
 assert frozen['region_sha256']=={p.name:sha(p.read_bytes())for p in OUT.glob('*_region.bin')}
 manifest=read(OUT/'manifest.json');assert manifest['overlay_bytes']<=2432 and manifest['projectile_bytes']<=640
 # AF' temporarily holds the caller's bank map across the private engine.
 assert "EX AF"not in (ROOT/'src/projectile_continuous.asm').read_text().upper()
 pages=0
 for rec in manifest['regions']:
  name='boot'if rec['file']=='RTBOOT.TAP'else f'level{rec["level"]:02d}'
  raw=(OUT/f'{name}_region.bin').read_bytes();old=(PREV/f'{name}_region.bin').read_bytes();assert len(raw)==65536 and sha(raw)==rec['sha256']
  allowed=bytearray(65536)
  spans=[(0xe400,0xed80),(0xf100,0xf380),(0x8e2,0x8f0),(0x911,0x920),(0x971,0x990),(0x1928,0x1937),(0xfd4,0xfe0),(0xf70,0xf80),(0x19fc,0x1a00),(0x1a91,0x1aa0),(0xfd20,0xfd48)]
  if name=='boot':spans +=[(0x54f9,0x5559),(0x5de7,0x5dfa),(0xdd20,0xdd48)]
  for a,z in spans:allowed[a:z]=bytes([1])*(z-a)
  assert all(a==b or allowed[i]for i,(a,b)in enumerate(zip(raw,old))),name+' changed outside owned ranges'
  for a,z in [(0x2000,0x4000),(0x8000,0xa000),(0xa4ce,0xd87c),(0xed80,0xf100),(0xf380,0xfb00)]:assert raw[a:z]==old[a:z],name+' changed graphics/caches'
  tape=(OUT/'RTYPE'/rec['file']).read_bytes();p=0;blocks=[]
  while p<len(tape):
   n=int.from_bytes(tape[p:p+2],'little');v=tape[p+2:p+2+n];assert len(v)==n and functools.reduce(int.__xor__,v)==0;blocks.append(v);p+=n+2
  assert p==len(tape)and len(blocks)==16 and b''.join(v[1:-1]for v in blocks[1::2])==raw
  assert all(len(v[1:-1])==8192 for v in blocks[1::2]);pages+=8
 assert pages==72
 reports={}
 for name in ['nested_irq_validation.json','l5_single_order_validation.json','fire_queue_validation.json','continuous_clock_validation.json','single_flight_validation.json','rapid_fire_validation.json','clean_cache_validation.json','clean_copy_validation.json','projectile_clock_validation.json','projectile_capacity_validation.json','irq_injection_validation.json','overlay_component_validation.json','player_spill_validation.json','movement_validation.json','custom_controls_validation.json','charged_fire_validation.json','death_validation.json','title_validation.json','snake_route_validation.json','cache_restart_validation.json','failure_validation.json','cache_progression_validation.json','boss_preview_validation.json']:
  r=read(OUT/name);assert all(v['passed']for v in r)if isinstance(r,list)else r['passed'];reports[name]=r
 assert reports['nested_irq_validation.json']['accepted']==0 and reports['nested_irq_validation.json']['returned']
 assert reports['rapid_fire_validation.json']['late_shots']==[] and reports['rapid_fire_validation.json']['queue_count']==0
 assert reports['single_flight_validation.json']['shots']==1 and reports['single_flight_validation.json']['active_span_refreshes']<90
 assert reports['clean_copy_validation.json']['unexpected_bytes']==0
 assert reports['cache_progression_validation.json']['all8_revisited_without_disk']
 assert all(v['after']==700 for v in reports['boss_preview_validation.json']['results'])
 profiles=[read(ROOT/f'build/diagnostics/shot_sequence_r57/masked_L{i}.json')for i in range(1,9)]
 # Profiles measure workload-sensitive input timing; bounded latest input can
 # coalesce taps, and their actual counts are retained in the report.
 assert all(1<=p['shots']<=8 and p['beams']==1 for p in profiles)
 readme='''R-Type TS2068 r57 - projectile ordering and release backlog

Replace the complete RTYPE folder, RESET, then load RTFULL.TAP. Keep RTBOOT.TAP and LEVEL01.TAP..LEVEL08.TAP together with the launcher. Nested directories under TAP are supported. Do not mix previous or larger-art level files.

The interrupt source is now protected against handler re-entry, including input routines that execute EI. A controlled nested-interrupt test corrupts the older handler's return context; r57 blocks the second pulse and restores the original context. Cached projectile redraws must match the live slot's type and position, preventing stale positions or cleared shots from being replayed.

Bolts keep advancing during background work. Screen-copy completion redraws only their current position. Short fire releases are dispatched during busy preparation too. Only the latest pending release is retained; blocked short taps expire rather than accumulating several seconds of future shots. Rapid inputs can coalesce under heavy load. Charged shots retain their native handoff.

Single-shot native/raster order tests pass, including level 5; the forced open-flight test reaches the far edge within 90 display refreshes. The exact reported out-of-sequence event on PicoVideo has not been captured in emulation. Hardware confirmation is still needed. Rendering/input cadence remains workload dependent. The r56 ship-background fix, player movement settings, art, boss sizes, audio and native controls are retained.

The game asks for keys. Both native joystick sockets work with the keyboard. Title 1-8 selects a level; B-release-B previews its boss; M toggles music. The stock 64KB cartridge is unchanged.
'''
 assert 'tspico'not in readme.lower()
 (OUT/'README.txt').write_text(readme);(OUT/'RTYPE/README.txt').write_text(readme)
 manifest['status']='Validated r57 emulation; PicoVideo confirmation pending';(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
 (OUT/'validation_summary.json').write_text(json.dumps(dict(passed=True,asset_pages=pages,reports=reports,profiles=profiles,physical_validation=False,exact_reported_reversal_reproduced=False,stock64KB_unchanged=True),indent=2))
 archive=OUT/'RType_TS2068_r57.zip'
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
