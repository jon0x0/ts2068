from pathlib import Path
import json,hashlib,zipfile,functools
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/boss_motion_r60';BASE=ROOT/'build/fullgame/l5_effects_fast_r59'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 checks=json.loads((OUT/'final_checks.json').read_text());assert len(checks)==17 and all(r['passed']for r in checks)
 assert json.loads((OUT/'reproducibility.json').read_text())['passed']
 assert json.loads((OUT/'frozen_regions.json').read_text())=={p.name:sha(p)for p in OUT.glob('*_region.bin')}
 pages=0
 for n in range(9):
  name='boot'if n==0 else f'level{n:02d}';b=(OUT/f'{name}_region.bin').read_bytes();old=(BASE/f'{name}_region.bin').read_bytes();assert len(b)==65536
  if n not in [0,5]:assert b[0x8000:0xa000]==old[0x8000:0xa000],'Terrain bank changed'
  assert all(b[i]==old[i]for i in range(0xe400,65536)if i not in range(0xfba7,0xfbab)),'Shared player/projectile/audio/reversal changed'
  tape=(OUT/'RTYPE'/('RTBOOT.TAP'if n==0 else f'LEVEL{n:02d}.TAP')).read_bytes();blocks=[];at=0
  while at<len(tape):
   size=int.from_bytes(tape[at:at+2],'little');v=tape[at+2:at+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;blocks.append(v);at+=size+2
  assert len(blocks)==16 and at==len(tape)
  for k in range(8):assert blocks[k*2][0]==0 and blocks[k*2+1][0]==255 and blocks[k*2+1][1:-1]==b[k*8192:(k+1)*8192];pages+=1
 assert (OUT/'RTYPE/RTFULL.TAP').read_bytes()==(BASE/'RTYPE/RTFULL.TAP').read_bytes()
 assert json.loads((OUT/'movement_validation.json').read_text())['actors']['5']==13
 readme='''R-Type 2068 r60 - experimental boss phases and arcade walkers

Copy the complete RTYPE folder. Reset, then load RTFULL.TAP. Do not mix level files from older builds. Define your own controls as usual; keyboard and both native joystick sockets remain active. Number keys select a starting level before play. In game press B, release, then B again for the boss checkpoint. M toggles music.

Moving boss components use two-pixel presentation steps. Native animation scripts and large relocations remain, and this does not add an independent boss clock. Enemy collision cells still follow the native game logic. L1's stationary main boss and L3's terrain-based giant ship are not moved as sprites. L5 has twelve spheres rather than twenty-four, with original component dimensions and more exposed machinery. Four arcade walking poses replace the large L1 walker's two poses; small walkers have arcade-derived ECM shading, retaining their collision sizes.

This is an expanded-memory disk trial, not a stock 64KB cartridge update. The existing 64KB target is unchanged. The finer boss phases add work; L4 in particular is expensive and needs further optimization. Do not interpret two-pixel motion as an overall FPS increase. Player, projectile and audio engine bytes are retained from r59. See the accompanying validation summary for emulator measurements. Physical hardware feedback is still needed.
'''
 (OUT/'README.txt').write_text(readme);(OUT/'RTYPE/README.txt').write_text(readme)
 result=dict(status='experimental emulator-validated disk trial',hardware_tested=False,pages=pages,checks=checks,bosses=json.loads((OUT/'boss_preview_validation.json').read_text()),movement=json.loads((OUT/'movement_validation.json').read_text()),stock64KB_unchanged=True)
 profile=json.loads((ROOT/'build/diagnostics/boss_motion_r60/masked_L5.json').read_text());result['performance']={'r59_L5_700_refreshes':35862,'r60_L5_700_refreshes':25606,'L5_elapsed_reduction_percent':round((1-25606/35862)*100,2),'r60_L4_700_refreshes':63800,'held_480_refreshes':{k:profile[k]for k in ['ticks','projectilePhases','shots','beams','world_updates']},'hardware_FPS_measured':False};(OUT/'validation_summary.json').write_text(json.dumps(result,indent=2))
 archive=OUT/'RType_TS2068_r60.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  z.write(OUT/'README.txt','README.txt');z.write(OUT/'validation_summary.json','validation_summary.json')
  for p in sorted((OUT/'RTYPE').rglob('*')):
   if p.is_file():z.write(p,p.relative_to(OUT))
 with zipfile.ZipFile(archive)as z:assert z.testzip()is None
 (OUT/'package_sha256.txt').write_text(sha(archive)+'  '+archive.name+'\n');print(archive,sha(archive))
if __name__=='__main__':main()
