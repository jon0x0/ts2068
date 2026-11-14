from pathlib import Path
import json,hashlib,zipfile,functools
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/fullgame/projectile_clock_r55'
PREV=ROOT/'build/fullgame/player_weapons_r54'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 frozen=read(OUT/'final_run.json');assert frozen['passed']
 assert frozen['region_sha256']=={p.name:sha(p.read_bytes())for p in OUT.glob('*_region.bin')}
 manifest=read(OUT/'manifest.json');size=manifest['projectile_engine_bytes'];assert size<=640
 # Cold backing source is copied only after the native HOME code is installed.
 assert 0x5880+size<=0x5b5b and 0xf100+size<=0xf380
 pages=0
 for rec in manifest['regions']:
  name='boot'if rec['file']=='RTBOOT.TAP'else f'level{rec["level"]:02d}'
  raw=(OUT/f'{name}_region.bin').read_bytes();old=(PREV/f'{name}_region.bin').read_bytes()
  assert len(raw)==65536 and sha(raw)==rec['sha256']
  allowed=bytearray(65536)
  spans=[(0x190,0x1a0),(0x9b6,0x9d0),(0x19e3,0x1a00),(0x1e20,0x1e30),(0x1928,0x1937),(0xfd4,0xfe0),(0xf70,0xf80),(0x986,0x990),(0x1a91,0x1aa0),(0xe39,0xe3d),(0x1488,0x148b),(0xa09,0xa0c),(0xfb81,0xfb84),(0xf100,0xf100+size)]
  if name=='boot':spans += [(0x54f9,0x5559),(0x5da5,0x5dfa),(0xdb81,0xdb84)]
  for a,z in spans:allowed[a:z]=bytes([1])*(z-a)
  assert all(a==b or allowed[i]for i,(a,b)in enumerate(zip(raw,old))),name+' modified outside owned ranges'
  for a,z in [(0xe400,0xf100),(0xf380,0xfb00),(0x2000,0x4000),(0x8000,0xa000),(0xa4ce,0xd87c)]:assert raw[a:z]==old[a:z],name+' art/player code changed'
  assert raw[0xf100:0xf100+size]==(OUT/'projectile_clock.bin').read_bytes()
  tape=(OUT/'RTYPE'/rec['file']).read_bytes();p=0;blocks=[]
  while p<len(tape):
   n=int.from_bytes(tape[p:p+2],'little');v=tape[p+2:p+2+n];assert len(v)==n and functools.reduce(int.__xor__,v)==0;blocks.append(v);p+=n+2
  assert p==len(tape)and len(blocks)==16
  assert b''.join(v[1:-1]for v in blocks[1::2])==raw
  assert all(len(v[1:-1])==8192 for v in blocks[1::2]);pages+=8
 assert pages==72
 reports={}
 for name in ['projectile_clock_validation.json','projectile_capacity_validation.json','irq_injection_validation.json','player_spill_validation.json','custom_controls_validation.json','charged_fire_validation.json','death_validation.json','title_validation.json','snake_route_validation.json','cache_restart_validation.json','failure_validation.json','cache_progression_validation.json','boss_preview_validation.json']:
  r=read(OUT/name);assert all(v['passed']for v in r)if isinstance(r,list)else r['passed'];reports[name]=r
 assert reports['projectile_clock_validation.json']['visible_positions']==21
 assert reports['cache_progression_validation.json']['all8_revisited_without_disk']
 assert len(reports['boss_preview_validation.json']['results'])==8
 assert all(v['after']==700 for v in reports['boss_preview_validation.json']['results'])
 profiles=[read(ROOT/f'build/diagnostics/projectile_clock_r55/masked_L{i}.json')for i in range(1,9)]
 assert all(p['shots']==8 and p['beams']==1 and p['projectilePhases']>p['world_updates']for p in profiles)
 readme='''R-Type TS2068 r55 - independently updated bolts

Replace the complete RTYPE folder, RESET, and load RTFULL.TAP. Keep RTBOOT.TAP and LEVEL01.TAP..LEVEL08.TAP together with the launcher. Nested directories under TAP are supported. Reset clears older resident level banks. Do not mix older or larger-art level files.

Normal and spread bolts now have their own interrupt update and visible drawing phase, separate from boss/world updates. Each step is 8 pixels rather than the previous 48-pixel normal-shot jump. Original bolt graphics are retained. An open-space test shows 21 successive positions rather than about three. Work is bounded to eight active slots per phase with round-robin service. Continuous world copies still pause the overlay. Charged beams and other weapon pools retain their existing timing.

Enemy/terrain contacts are queued for safe main-loop damage handling. Actor signatures reject stale targets. Exact byte ownership removes old bolt pixels before scenery copies. Normal black is used for cleared space. The player retains its one-pixel fine movement, held movement speed and independent update path. Artwork, boss sizes and sound are retained.

The game asks for keys. Both native joystick sockets work alongside the keyboard. Title 1-8 selects a level; B-release-B during play previews its boss. M toggles music.

Scripted emulation validation includes native bolt drawing/cleanup/collision tests, full 16-slot capacity, 7565 interrupt boundary injections, ship redraw checks, controls/fire/death/restarts, all eight bosses and full resident level revisits. Real-hardware testing remains pending. This change applies to the expanded-RAM disk build; the stock 64KB cartridge is unchanged.
'''
 assert 'tspico'not in readme.lower()
 (OUT/'README.txt').write_text(readme);(OUT/'RTYPE/README.txt').write_text(readme)
 summary=dict(passed=True,asset_pages=pages,reports=reports,profiles=profiles,physical_validation=False,stock64KB_unchanged=True)
 (OUT/'validation_summary.json').write_text(json.dumps(summary,indent=2))
 manifest['status']='Validated r55, hardware validation pending';(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
 archive=OUT/'RType_TS2068_r55.zip'
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
