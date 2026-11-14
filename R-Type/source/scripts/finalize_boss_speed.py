"""Verify owned ranges, final evidence and packaged standard r53 pages."""
from pathlib import Path
import json,hashlib,zipfile,functools
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/boss_speed_r53';PREV=ROOT/'build/fullgame/detail_motion_r52';PROFILE=ROOT/'build/diagnostics/boss_speed_r53'
def read(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def tape(file,raw):
 b=file.read_bytes();blocks=[];p=0
 while p<len(b):
  n=int.from_bytes(b[p:p+2],'little');v=b[p+2:p+2+n];assert len(v)==n and functools.reduce(int.__xor__,v)==0;blocks.append(v);p+=2+n
 assert p==len(b)and len(blocks)==16;assert b''.join(v[1:-1]for v in blocks[1::2])==raw
 for v in blocks[1::2]:assert len(v[1:-1])==8192
 return 8

def main():
 manifest=read(OUT/'manifest.json');pages=0
 for rec in manifest['regions']:
  name='boot'if rec['file']=='RTBOOT.TAP'else f'level{rec["level"]:02d}';b=(OUT/f'{name}_region.bin').read_bytes();old=(PREV/f'{name}_region.bin').read_bytes();assert len(b)==65536 and sha(b)==rec['sha256'];pages+=tape(OUT/'RTYPE'/rec['file'],b);allowed=bytearray(65536)
  ranges=[(0x971,0x990),(0xe25,0xe40),(0x18a7,0x1937),(0xe400,0xed80),(0xfb00,0xfba7),(0xfd20,0xfd48)]
  if rec['level']==5:ranges +=[(0x1c8,0x200),(0xf57,0xf80),(0xfc3,0xfe0),(0x1a6e,0x1aa0),(0x88eb,0x9000)]
  if name=='boot':
   ranges +=[(0xdb00,0xdbc0),(0xdd0c,0xdd0f),(0xdd20,0xdd48),(0x7e5b,0x7e5e)]
   for a in [0x94f6,0x9563,0x8979,0x8a94,0x8afe,0xc290]:
    at=a-(0x2000 if a>=0xc000 else 0x4000);ranges.append((at,at+3))
  for a,z in ranges:allowed[a:z]=bytes([1])*(z-a)
  assert all(x==y or allowed[i]for i,(x,y)in enumerate(zip(b,old))),name+' changed outside owned ranges'
  for a,z in [(0x2000,0x4000),(0x9000,0xa000),(0xa4ce,0xd87c),(0xed80,0xfb00)]:assert b[a:z]==old[a:z],name+' art/cache changed'
  assert b[0xe400:0xe400+(OUT/'overlay.bin').stat().st_size]==(OUT/'overlay.bin').read_bytes()
  if rec['level']==5:assert b[0x8f00:0x9000]==bytes([0x5b])*256 and b[0x9000]==0
 assert pages==72
 reports={}
 for f in ['irq_injection_validation.json','classifier_validation.json','compiled_equivalence.json','compact_composition_validation.json','drawing_validation.json','overlay_component_validation.json','movement_validation.json','custom_controls_validation.json','charged_fire_validation.json','death_validation.json','title_validation.json','snake_route_validation.json','cache_restart_validation.json','failure_validation.json','cache_progression_validation.json','boss_preview_validation.json']:
  v=read(OUT/f);assert all(x['passed']for x in v)if isinstance(v,list)else v['passed'];reports[f]=v
 assert len(reports['boss_preview_validation.json']['results'])==8 and all(v['after']==700 for v in reports['boss_preview_validation.json']['results']);assert reports['cache_progression_validation.json']['all8_revisited_without_disk'];assert reports['irq_injection_validation.json']['injected']==7565;assert reports['classifier_validation.json']['pointers']==524288;assert reports['compiled_equivalence.json']['cases']==384;assert sum(v['cases']for v in reports['drawing_validation.json']['reports'])==5088;assert reports['title_validation.json']['states']==116
 comparisons=[]
 for level in range(1,9):
  a=read(PROFILE/f'baseline_L{level}.json');b=read(PROFILE/f'candidate_L{level}.json');assert len(a['positions'])==len(b['positions'])==480 and b['shots']==8 and b['beams']==1 and b['ticks']>=a['ticks']*.9;assert b['minStack']>0x5b60
  def travel(v):return sum(abs(p['x']-v['positions'][i-1]['x'])for i,p in enumerate(v['positions'])if i)
  comparisons.append(dict(level=level,display_refreshes=480,old_ticks=a['ticks'],new_ticks=b['ticks'],old_travel=travel(a),new_travel=travel(b),old_shots=a['shots'],new_shots=b['shots'],old_world_updates=a['world_updates'],new_world_updates=b['world_updates']))
 timing=read(OUT/'composition_timing.json');assert timing[1]['cycles']<timing[0]['cycles'];assert timing[1]['decoded_overlap_rows']<timing[0]['decoded_overlap_rows']
 readme="""R-Type TS2068 r53 - standard compact boss / responsive controls

Replace the complete RTYPE folder, RESET, then load RTFULL.TAP. Keep RTBOOT.TAP and LEVEL01.TAP..LEVEL08.TAP with the launcher. Nested directories below TAP are supported. Reset is required to discard older resident level banks. Do not mix previous level files or the older optional large-art level with this build.

The game still asks for its keys. Both native joystick sockets remain active alongside the keyboard. At the title, 1-8 select the starting level. During play, press B, release, then press B again for the boss preview. M toggles music.

Player input edges are sampled on every available interrupt; redraws use alternate interrupts to protect the scene budget. L5's long drawing sections allow safe interrupts with a separate interrupt stack. Short fire presses are captured during background preparation too; fine 1-pixel taps and existing held 5-pixel steps remain. Firing checks cover normal releases and a charged hold. Charge counting retains its half-rate clock rather than doubling along with movement polling.

All eight levels use a cheaper native enemy/boss palette-source lookup. L5 retains the standard 24-pixel spheres and 80-pixel core: no enlargement or artwork change. Fully hidden cells are rejected before interrupt setup and source decoding. Inside partially visible cells, covered rows skip source decoding and blending. Unowned copy loops select direction/flash once per cell.

Measurements are scripted emulation, not hardware results. Shared boss draw-call samples save about 6-7% CPU time; the captured 25-part overlapping L5 composition saves about 2.5% including interrupt support and decodes 554 rather than 1064 overlap rows. Whole-scene animation remains scene dependent: more frequent input/audio consumes CPU, so these draw savings are not a whole-game frame-rate claim.

All eight boss routes, selected controls/both joysticks, firing, real death/respawn, title states, loading and resident level revisits pass. Graphics output is byte-identical in the tested direct/retained/flip/flash/clipping cases. The stock 64KB read-only cartridge is unchanged. Physical validation is pending.
"""
 assert 'tspico'not in readme.lower();(OUT/'README.txt').write_text(readme,encoding='utf-8');(OUT/'RTYPE/README.txt').write_text(readme,encoding='utf-8')
 summary=dict(passed=True,asset_pages=pages,reports=reports,movement_comparison=comparisons,composition_timing=timing,physical_validation=False,stock64KB_unchanged=True,scope='Standard compact 512KB disk build; no art replacement or larger boss variant')
 (OUT/'validation_summary.json').write_text(json.dumps(summary,indent=2));manifest['status']='Validated standard r53, physical validation pending';(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));archive=OUT/'RType_TS2068_r53.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  z.write(OUT/'README.txt','README.txt')
  for f in sorted((OUT/'RTYPE').iterdir()):
   if f.is_file():z.write(f,'RTYPE/'+f.name)
  for f in ['validation_summary.json','manifest.json']:z.write(OUT/f,'VALIDATION/'+f)
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for f in (OUT/'RTYPE').iterdir():
   if f.is_file():assert z.read('RTYPE/'+f.name)==f.read_bytes()
 print(json.dumps(dict(archive=str(archive),sha256=sha(archive.read_bytes()),movement=comparisons),indent=2))
if __name__=='__main__':main()
