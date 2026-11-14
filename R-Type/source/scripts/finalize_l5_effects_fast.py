from pathlib import Path
import json,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/l5_effects_fast_r59';BASE=ROOT/'build/fullgame/shot_sequence_r57'
def main():
 checks=json.loads((OUT/'final_checks.json').read_text());assert len(checks)==16 and all(r['passed']for r in checks)
 assert json.loads((OUT/'reproducibility.json').read_text())['passed']
 freeze=json.loads((OUT/'frozen_regions.json').read_text());assert freeze=={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in OUT.glob('*_region.bin')}
 common=[(0x9fc,0xa06),(0xe10,0xe15),(0xee1,0xeec),(0x1af6,0x1aff),(0x1b14,0x1b1d),(0x1ff7,0x1ffc)]
 extra=[(0x40,0x100),(0x1561,0x1567),(0xd00,0xd2f),(0xdc0,0xdde),(0x19fc,0x19ff),(0x2400,0x3fe0),(0x88eb,0x8bf0),(0x8c00,0x8f00),(0xf57,0xf70),(0xfc3,0xfd4),(0x1a6e,0x1a91),(0xcfa1,0xd481),(0xdc50,0xe000),(0xe000,0xe400)]
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
 irq=json.loads((OUT/'phase_irq_components.json').read_text());assert irq['passed']and irq['irqCount']==16
 previous=ROOT/'build/fullgame/l5_preshift_r58'
 for name in ['boot']+[f'level{i:02d}'for i in range(1,9)if i!=5]:assert(OUT/f'{name}_region.bin').read_bytes()==(previous/f'{name}_region.bin').read_bytes(),name
 clipping=json.loads((OUT/'phase_clipping.json').read_text());assert clipping['passed']and clipping['cases']==768
 fx=json.loads((OUT/'global_fx_validation.json').read_text());assert fx['passed']and fx['r59_mismatching_cases']==0
 profile=json.loads((ROOT/'build/diagnostics/l5_effects_fast_r59/masked_L5.json').read_text())
 performance=dict(route_r57_refreshes=26295,route_r58_refreshes=36061,route_r59_refreshes=35862,held_r58_player_updates=141,held_r59_player_updates=profile['ticks'],held_r58_projectile_updates=138,held_r59_projectile_updates=profile['projectilePhases'],component_r58_cycles=204098.171875,component_r59_cycles=json.loads((OUT/'phase_components.json').read_text())['mean_total_cycles'])
 summary=dict(effects=fx,clipping=clipping,performance=performance,profile={k:profile[k]for k in ['ticks','projectilePhases','shots','beams','world_updates']},status='Emulator-validated r59 L5 effect repair and cell-plan optimization',physical_validation=False,stock64KB_unchanged=True,phase_pixels=[0,2,4,6],native_boss_parts=25,sphere_size=[24,24],core_size=[80,80],packed_phase_bytes=7152,expanded_phase_bytes=9344,cache_prepare_cycles=2374061,actual_native_phase_cases=256,interrupt_injections=16,native_boss_updates=700,pages_verified=pages,regions=regions,checks=checks,scope='2px actor-local movement per existing boss/world update, not a new independent boss timer; original scripts/animation targets retained. Pixel publication/collision is still cell-based for native enemies.')
 (OUT/'validation_summary.json').write_text(json.dumps(summary,indent=2))
 manifest=json.loads((OUT/'manifest.json').read_text());manifest['status']='Packaged emulator-validated experimental trial; hardware pending';(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
 text="""R-Type 2068 - r59 L5 effects repair and drawing optimization

Copy the complete RTYPE directory to your game directory. Reset, then load RTFULL.TAP. Keep separate from r57/r58; do not mix level files.
Select level 5 with number 5 before starting. After starting, press B, release, then B again for the boss preview. Define your controls as usual; keyboard and both native joystick sockets remain active.

Fixes r58's corrupted firing sparks and explosions: 617 global colour IDs now live in separate immutable storage rather than the overwritten phase-cache bank. All 2568 native effect comparisons match r57 exactly. The actual L5 death/respawn path is exercised.

Boss cell layouts are prepared once per part, avoiding repeated source coordinate work in painting. Cells outside the playfield or behind verified fully opaque foreground are skipped before source preparation. Retained source and bank transitions are restored for cached revisits. Boss part sizes and 2-pixel movement remain as in r58.

Matched held-input emulator workload: player updates 141 -> 173, projectile updates 138 -> 172 in 480 display refreshes; same 8 short shots and 1 charged beam. Native component work including planning falls from about 204098 to 167702 cycles. The 700-update boss route changes only from 36061 to 35862 display refreshes; r57 takes 26295. This remains an experimental smoother-movement build, not an overall boss-FPS improvement over r57. These are emulator measurements, not hardware FPS.

Native pixel/ECM, clipping, IM2 interruptions, gameplay, chosen keys/joysticks, death/respawn, title, snake, firing order, restart, error handling and all-level resident loading regression checks pass. Other levels' images are byte-identical to r58. Physical hardware confirmation is pending. Expanded-memory disk target; stock 64 KB cartridge remains unchanged.
"""
 (OUT/'README.txt').write_text(text)
 archive=OUT/'RType_TS2068_r59.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  z.write(OUT/'README.txt','README.txt')
  for p in sorted((OUT/'RTYPE').rglob('*')):
   if p.is_file():z.write(p,p.relative_to(OUT))
 with zipfile.ZipFile(archive)as z:assert z.testzip()is None
 digest=hashlib.sha256(archive.read_bytes()).hexdigest();(OUT/'package_sha256.txt').write_text(digest+'  '+archive.name+'\n');print(archive);print(digest)
if __name__=='__main__':main()
