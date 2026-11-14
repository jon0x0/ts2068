from pathlib import Path
import json,hashlib,zipfile,functools
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/player_weapons_r54';PREV=ROOT/'build/fullgame/boss_speed_r53'
def read(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 frozen=read(OUT/'final_run.json');assert frozen['passed'];assert frozen['region_sha256']=={p.name:sha(p.read_bytes())for p in OUT.glob('*_region.bin')}
 manifest=read(OUT/'manifest.json');assert manifest['overlay_bytes']<=2432 and manifest['damage_bytes']<=128;pages=0
 # OLD/NEXT, coverage, paired planes, row pointers, clean world and collision map.
 spans=[(0xf6c0,0xf700),(0xf700,0xf740),(0xf740,0xf781),(0xf781,0xf803),(0xf820,0xf83a),(0xf83a,0xf87a),(0xf880,0xfb00)]
 assert all(a[1]<=b[0]for a,b in zip(spans,spans[1:]));assert 0xf080+manifest['damage_bytes']<=0xf100
 for rec in manifest['regions']:
  name='boot'if rec['file']=='RTBOOT.TAP'else f'level{rec["level"]:02d}';raw=(OUT/f'{name}_region.bin').read_bytes();old=(PREV/f'{name}_region.bin').read_bytes();assert len(raw)==65536 and sha(raw)==rec['sha256'];allowed=bytearray(65536)
  for a,z in [(0x190,0x1a0),(0x9b6,0x9d0),(0x19e3,0x1a00),(0x1e20,0x1e30),(0xe400,0xed80),(0xf080,0xf100)]+([(0x5dba,0x5dc1)]if name=='boot'else[]):allowed[a:z]=bytes([1])*(z-a)
  assert all(a==b or allowed[i]for i,(a,b)in enumerate(zip(raw,old))),name+' changed outside owned ranges'
  assert raw[0xed80:0xf080]==old[0xed80:0xf080];assert raw[0x8000:0xa000]==old[0x8000:0xa000];assert raw[0xa4ce:0xd87c]==old[0xa4ce:0xd87c];assert raw[0x2000:0x4000]==old[0x2000:0x4000];assert raw[0xfb00:0x10000]==old[0xfb00:0x10000]
  b=(OUT/'RTYPE'/rec['file']).read_bytes();p=0;blocks=[]
  while p<len(b):
   n=int.from_bytes(b[p:p+2],'little');v=b[p+2:p+2+n];assert len(v)==n and functools.reduce(int.__xor__,v)==0;blocks.append(v);p+=2+n
  assert p==len(b)and len(blocks)==16;assert b''.join(v[1:-1]for v in blocks[1::2])==raw;assert all(len(v[1:-1])==8192 for v in blocks[1::2]);pages+=8
 assert pages==72
 reports={}
 for name in ['overlay_component_validation.json','player_spill_validation.json','projectile_sweep_validation.json','native_shot_validation.json','projectile_capacity_validation.json','irq_injection_validation.json','movement_validation.json','custom_controls_validation.json','charged_fire_validation.json','death_validation.json','title_validation.json','snake_route_validation.json','cache_restart_validation.json','failure_validation.json','cache_progression_validation.json','boss_preview_validation.json']:
  r=read(OUT/name);assert all(v['passed']for v in r)if isinstance(r,list)else r['passed'];reports[name]=r
 assert reports['player_spill_validation.json']['cases']==128;assert reports['projectile_sweep_validation.json']['cases']==4088;assert reports['projectile_sweep_validation.json']['friendly_cells_ignored'];assert reports['native_shot_validation.json']['new_travel']==3*reports['native_shot_validation.json']['old_travel'];assert reports['irq_injection_validation.json']['injected']==7565;assert len(reports['boss_preview_validation.json']['results'])==8 and all(v['after']==700 for v in reports['boss_preview_validation.json']['results']);assert reports['cache_progression_validation.json']['all8_revisited_without_disk'];assert reports['title_validation.json']['states']==116
 profile=read(OUT/'l5_input_profile.json');assert profile['boot_sha256']==sha((OUT/'boot_region.bin').read_bytes())and profile['level05_sha256']==sha((OUT/'level05_region.bin').read_bytes());assert profile['shots']==8 and profile['beams']==1 and len(profile['positions'])==480;assert profile['ticks']>=125
 readme="""R-Type TS2068 r54 - projectile travel and ship/exhaust background spill

Replace the complete RTYPE folder, RESET, then load RTFULL.TAP. Keep RTBOOT.TAP and LEVEL01.TAP..LEVEL08.TAP together with the launcher. Nested directories under TAP are supported. Reset clears older resident level banks. Do not mix previous or larger-art level files.

The game still asks for keys. Both native joystick sockets work with the keyboard. Title1-8 selects a level; during play B-release-B previews its boss. M toggles music.

Normal/spread projectiles take up to three original travel steps per world update, stopping at the first enemy/terrain cell reached by those steps. Friendly shot/player/dirty-cell IDs do not stop this sweep. The original final drawing and damage path runs once. Normal travel in clear space is 6 cells rather than 2. This increases travel speed; it does not give weapons a separate faster update clock. Charged beams and other weapon pools retain their previous timing.

Fixed a reproducible stale-background spill around the player, including the exhaust footprint. During slow scene copies, player publication used to replay the whole damage rectangle from an older snapshot. Now only actual old/new ship coverage changes; surrounding live bitmap pixels and untouched ECM cells survive. Retained cleanup is likewise limited to the current ship coverage. It is a background-restoration fix, not newly authored flame animation.

Player keys, movement distances, compact boss sizes, artwork and sound are retained. Exact damage tracking costs some CPU; scene/input cadence remains workload dependent. The tests distinguish travel speed from update frequency. Real-hardware confirmation remains pending.

Validation includes 128 changed-world ship/exhaust cases across all phases/directions/fine+held steps, 4088 native projectile-direction/boundary/blocker checks, actual native shot drawing comparison, 16-slot capacity, 7565 IRQ boundary injections, 894 player ticks, selected controls/both joysticks/fire/death, 116 title states, all 8 boss routes of 700 updates and full level-cache/revisit/error checks. 72 asset pages/hash/XOR/ZIP checks pass. The stock 64KB read-only cartridge is unchanged.
"""
 assert 'tspico'not in readme.lower();(OUT/'README.txt').write_text(readme,encoding='utf-8');(OUT/'RTYPE/README.txt').write_text(readme,encoding='utf-8');summary=dict(passed=True,asset_pages=pages,reports=reports,l5_input_profile=profile,physical_validation=False,stock64KB_unchanged=True);(OUT/'validation_summary.json').write_text(json.dumps(summary,indent=2));manifest['status']='Validated r54, physical validation pending';(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
 archive=OUT/'RType_TS2068_r54.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  z.write(OUT/'README.txt','README.txt')
  for f in sorted((OUT/'RTYPE').iterdir()):
   if f.is_file():z.write(f,'RTYPE/'+f.name)
  for f in ['validation_summary.json','manifest.json']:z.write(OUT/f,'VALIDATION/'+f)
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for f in (OUT/'RTYPE').iterdir():
   if f.is_file():assert z.read('RTYPE/'+f.name)==f.read_bytes()
 print(archive);print(sha(archive.read_bytes()))
if __name__=='__main__':main()
