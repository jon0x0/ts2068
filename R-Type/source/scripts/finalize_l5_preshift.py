from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/l5_preshift_r58';BASE=ROOT/'build/fullgame/shot_sequence_r57'
def main():
 checks=json.loads((OUT/'final_checks.json').read_text());assert len(checks)==14 and all(r['passed']for r in checks)
 freeze=json.loads((OUT/'frozen_regions.json').read_text());assert freeze=={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in OUT.glob('*_region.bin')}
 common=[(0x9fc,0xa06),(0xe10,0xe15),(0xee1,0xeec),(0x1af6,0x1aff),(0x1b14,0x1b1d),(0x1ff7,0x1ffc)]
 extra=[(0xd00,0xd2f),(0xdc0,0xdde),(0x19fc,0x19ff),(0x2400,0x3fe0),(0x88eb,0x8bf0),(0x8c00,0x8f00),(0xf57,0xf70),(0xfc3,0xfd4),(0x1a6e,0x1a91),(0xcfa1,0xd481),(0xdc50,0xe000),(0xe000,0xe400)]
 pages=0;regions=[]
 for name,n in [('boot',0)]+[(f'level{i:02d}',i)for i in range(1,9)]:
  b=(OUT/f'{name}_region.bin').read_bytes();old=(BASE/f'{name}_region.bin').read_bytes();allowed=bytearray(65536)
  for a,z in common+([(0x5172,0x5175)]if n==0 else[])+(extra if n==5 else[]):allowed[a:z]=bytes([1])*(z-a)
  changed=[i for i,(x,y)in enumerate(zip(b,old))if x!=y];assert all(allowed[i]for i in changed),(name,[hex(i)for i in changed if not allowed[i]][:10])
  for a,z in [(0xe400,0xe000+8192)]:
   # The live player, projectile template, input/IRQ/audio code afterE400 is intact.
   assert b[a:z]==old[a:z],(name,'Shared bank7 engines changed')
  tape=OUT/'RTYPE'/('RTBOOT.TAP'if n==0 else f'LEVEL{n:02d}.TAP');data=tape.read_bytes();blocks=[];p=0
  while p<len(data):
   count=int.from_bytes(data[p:p+2],'little');block=data[p+2:p+2+count];assert len(block)==count and not __import__('functools').reduce(int.__xor__,block,0);blocks.append(block);p+=count+2
  assert p==len(data) and len(blocks)==16
  for i in range(8):assert blocks[i*2][0]==0 and blocks[i*2+1][0]==255 and blocks[i*2+1][1:-1]==b[i*8192:(i+1)*8192];pages+=1
  regions.append(dict(name=name,changed_bytes=len(changed),sha256=hashlib.sha256(b).hexdigest()))
 assert pages==72
 for file in ['RTFULL.TAP']:
  assert(OUT/'RTYPE'/file).read_bytes()==(BASE/'RTYPE'/file).read_bytes()
 motion=json.loads((OUT/'motion_trace.json').read_text());assert motion['passed']and motion['actors']==25
 irq=json.loads((OUT/'phase_irq_components.json').read_text());assert irq['passed']and irq['irqCount']==8
 other=json.loads((OUT/'other_bosses_validation.json').read_text());assert len(other['results'])==7 and all(r['passed']for r in other['results'])
 performance=json.loads((OUT/'performance_comparison.json').read_text());profile=json.loads((ROOT/'build/diagnostics/l5_preshift_r58/masked_L5.json').read_text())
 summary=dict(performance=performance,profile={k:profile[k]for k in ['ticks','projectilePhases','shots','beams','world_updates']},status='Experimental playable expanded-RAM L5 phase trial',physical_validation=False,stock64KB_unchanged=True,phase_pixels=[0,2,4,6],native_boss_parts=25,sphere_size=[24,24],core_size=[80,80],packed_phase_bytes=7152,expanded_phase_bytes=9344,cache_prepare_cycles=2374061,actual_native_phase_cases=256,interrupt_injections=8,native_boss_updates=700,pages_verified=pages,regions=regions,checks=checks,scope='2px actor-local movement per existing boss/world update, not a new independent boss timer; original scripts/animation targets retained. Pixel publication/collision is still cell-based for native enemies.')
 (OUT/'validation_summary.json').write_text(json.dumps(summary,indent=2))
 manifest=json.loads((OUT/'manifest.json').read_text());manifest['status']='Packaged emulator-validated experimental trial; hardware pending';(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
 text="""R-Type 2068 - r58 experimental L5 two-pixel boss movement

Copy the complete RTYPE directory to your game directory. Reset, then load RTFULL.TAP. Keep this trial separate from r57; do not mix level files.
Select level 5 with the number 5 key before starting. After starting, press B, release it, then press B again to jump to the boss preview. The game still asks you to define your controls; keyboard and both native joystick sockets remain active.

Bellmite retains its 24-pixel spheres and 80-pixel core. Each part uses 0/2/4/6-pixel horizontal phases and raster-row relocation for vertical movement. Ordinary one-cell travel is spread over 2-pixel steps on successive boss updates. Large scripted relocations still snap. The native attack scripts and animation frame sequence remain. This does not increase the underlying boss update clock; extra phase/edge work has a performance cost.

The 7152-byte packed phase cache expands to 9344 bytes during level initialization, before play. It reuses palette RAM and the already-copied native asset shadow, keeping the existing 512 KB allocation. Exact source restoration is tested before cached revisits. Cache preparation takes about 2.37 million Z80 cycles in the isolated measurement; it occurs during loading, not when the boss appears.

Measured scripted 700-update route: r57 took 26295 emulated display refreshes; r58 took 36061 (about 37% longer, including boot/entrance). The movement is finer, but this is not a speedup. This is why the build is offered separately as a trial. These are emulator measurements, not hardware FPS.

Player/projectile engines, chosen-key behavior, native joystick input, music and sound assets are retained from r57. Native component, actual gameplay/restart/cache and cartridge-page checks pass. PicoVideo/real-hardware confirmation is pending. This is a movement/graphics experiment, not the stock 64 KB cartridge target.
"""
 (OUT/'README.txt').write_text(text)
 archive=OUT/'RType_TS2068_r58_L5_preshift_trial.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  z.write(OUT/'README.txt','README.txt')
  for p in sorted((OUT/'RTYPE').rglob('*')):
   if p.is_file():z.write(p,p.relative_to(OUT))
 with zipfile.ZipFile(archive)as z:assert z.testzip()is None
 digest=hashlib.sha256(archive.read_bytes()).hexdigest();(OUT/'package_sha256.txt').write_text(digest+'  '+archive.name+'\n');print(archive);print(digest)
if __name__=='__main__':main()
