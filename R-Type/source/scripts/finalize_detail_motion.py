"""Package r52 only after movement, graphics, loader and actual boss gates."""
from pathlib import Path
import json,hashlib,functools,zipfile
from build_rocket_fix import code
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/detail_motion_r52';PREV=ROOT/'build/fullgame/compact_boss_r51'
def read(p):return json.loads(p.read_text())
def sha(b):return hashlib.sha256(b).hexdigest()
def verify_tape(tape,raw):
 p=0;blocks=[]
 while p<len(tape):
  n=int.from_bytes(tape[p:p+2],'little');b=tape[p+2:p+2+n];assert len(b)==n and functools.reduce(int.__xor__,b)==0;blocks.append(b);p+=n+2
 assert p==len(tape)and len(blocks)==16;assert b''.join(b[1:-1]for b in blocks[1::2])==raw

def main():
 m=read(OUT/'manifest.json');engine=(OUT/'overlay.bin').read_bytes();assert len(engine)<=0x980;assert m['damage_scratch']==[0xf780,0xf802]and m['row_table']==[0xf820,0xf83a];assert 0xf802<=0xf820 and 0xf83a<=0xf880;assert m['backing_pixel_range'][1]<=0xf380 and m['backing_attr_dock2_range'][0]>=0x5d00 and m['backing_attr_dock2_range'][1]<=0x6000
 for rec in m['regions']:
  name='boot'if rec['file']=='RTBOOT.TAP'else f'level{rec["level"]:02d}';raw=(OUT/f'{name}_region.bin').read_bytes();before=(PREV/f'{name}_region.bin').read_bytes();assert len(raw)==65536 and sha(raw)==rec['sha256'];assert raw[0xe400:0xe400+len(engine)]==engine;verify_tape((OUT/'RTYPE'/rec['file']).read_bytes(),raw);allowed=bytearray(65536);allowed[0xe400:0xed80]=bytes([1])*0x980
  if rec['level']==8:
   allowed[0x2000:0x2400]=bytes([1])*1024;allowed[0xe000:0xe400]=bytes([1])*1024
   meta=read(ROOT/'build/fullgame/converted/level08/manifest.json')
   for d in meta['descriptors']:
    if d['id']not in range(42,47):continue
    p=d['pointer']-0x2000
    for _ in range(d['width']*d['height']):
     n=1 if before[p]==54 else 9;allowed[p:p+n]=bytes([1])*n;p+=n
   for idx in read(OUT/'l8_detail.json')['protected_rows']:assert raw[0xe000+idx*8:0xe000+idx*8+8]==before[0xe000+idx*8:0xe000+idx*8+8]
  assert all(a==b or allowed[i]for i,(a,b)in enumerate(zip(raw,before))),'Unintended asset/code change '+name
 reports={}
 for filename in ['movement_validation.json','custom_controls_validation.json','charged_fire_validation.json','death_validation.json','failure_validation.json','cache_restart_validation.json','cache_progression_validation.json','boss_preview_validation.json','title_validation.json','snake_route_validation.json','overlay_component_validation.json','l8_native_graphics_validation.json']:
  r=read(OUT/filename);assert all(v['passed']for v in r)if isinstance(r,list)else r['passed'];reports[filename]=r
 assert reports['movement_validation.json']['pixel_steps']>=100;assert reports['movement_validation.json']['guarded_cache_writes']>0;assert reports['overlay_component_validation.json']['split_backing_vertical_travel']>=23;assert reports['overlay_component_validation.json']['empty_backing_frames']==8;assert reports['title_validation.json']['states']==116;boss=reports['boss_preview_validation.json'];assert len(boss['results'])==8 and all(v['after']==700 for v in boss['results']);assert reports['cache_progression_validation.json']['all8_revisited_without_disk'];assert reports['l8_native_graphics_validation.json']['cases']==1056
 stage5=(OUT/'level05_region.bin').read_bytes();runtime=(OUT/'boss_level5.dock7.bin').read_bytes();assert runtime[0x1380:0x1680]==stage5[0xf380:0xf680];assert stage5[0x88eb:0x8c00]==(PREV/'level05_region.bin').read_bytes()[0x88eb:0x8c00]
 detail=read(OUT/'l8_detail.json');assert all(r['run_lengths_after'].get(str(i),0)>0 for r in detail['frames']for i in range(1,7))
 # Preserve the previous optional larger L5 artwork with the current engine.
 alt=bytearray((ROOT/'build/fullgame/fast_boss_r51/level05_region.bin').read_bytes());alt[0xe400:0xed80]=bytes([255])*0x980;alt[0xe400:0xe400+len(engine)]=engine;altbytes=b''.join(code(f'RTPAGE{p:02X}',alt[p*8192:(p+1)*8192],p)for p in range(8));verify_tape(altbytes,alt);assert alt==(ROOT/'build/fullgame/detail_motion_large_r52/level05_region.bin').read_bytes();assert read(ROOT/'build/fullgame/detail_motion_large_r52/boss_preview_validation.json')['passed'];(OUT/'alternate_large_level05_region.bin').write_bytes(alt)
 readme='''R-Type TS2068 r52 - L8 fine detail and faster player travel

Replace the complete RTYPE folder, reset, then load RTFULL.TAP. Keep RTFULL.TAP, RTBOOT.TAP and LEVEL01.TAP..LEVEL08.TAP together. Nested directories under TAP are supported. Do not mix old level files with this build.

The game still asks for keys; both native joystick sockets work alongside them. Select1-8 at the title for starting level. During play B-release-B previews that boss. M toggles music.

L8: five boss frames are reconverted from arcade sources at the existing48x32size using the previously selected gamma1.8/saturation4.5 Sierra Lite direction, followed by actual packed-palette quantization with error diffusion. Normal black/transparent edges preserved. More short1-6pixel runs and fewer solid8pixel bands; same frame dimensions, animation indices and source slots. All other L8enemy palette rows are protected.

Player: fine initial1pixel steps, then5pixels/publication while held (r50 used3). Larger64-raster background patch reduces stops during slow world redraws; paired-plane damage scratch handles up to13raster rows. Empty sky rows use a fast cache-fill path. Selected bindings and firing semantics retained. Test route:113pixels in100refreshes versus78in r50, about45%farther in equal time. During a frozen copy, vertical travel23pixels versus9on the old patch. These are travel measurements, not a claim of higher world FPS. Frame rate remains scene dependent.

Default L5 retains r51 compact24pixel spheres/80pixelcore and its faster native renderer. Optional ALTERNATE_LARGE_ART/LEVEL05.TAP retains32/96art but includes the new r52 player engine; copy it over RTYPE/LEVEL05.TAP and reset/reload. This optional combination also passed its own700-update boss route.

Tests: all8boss routes700updates;1056native L8descriptor/flip/clip/flash cases;894player component ticks plus frozen-copy/empty-backing stress; actual chosen keyboard/both joysticks, normal/chargedfire and death/respawn; title116states; all8level loading/cached revisits/ending, selected restarts and loader errors. The final packaged pages pass length/hash/XOR checks. Preview images are emulator/native or packed-source renders as labelled, not hardware photographs.

Physical validation pending. Stock64KBread-only cartridge unchanged. Separate boss delta prototypes are not integrated by this update.
'''
 assert 'tspico'not in readme.lower();(OUT/'README.txt').write_text(readme,encoding='utf-8');(OUT/'RTYPE/README.txt').write_text(readme,encoding='utf-8')
 summary=dict(optional_large_boss=read(ROOT/'build/fullgame/detail_motion_large_r52/boss_preview_validation.json'),passed=True,asset_pages=72,alternate_pages=8,reports=reports,detail=detail,physical_validation=False,stock64KB_unchanged=True);(OUT/'validation_summary.json').write_text(json.dumps(summary,indent=2));archive=OUT/'RType_TS2068_r52.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
  z.write(OUT/'README.txt','README.txt')
  for p in sorted((OUT/'RTYPE').iterdir()):z.write(p,'RTYPE/'+p.name)
  z.writestr('ALTERNATE_LARGE_ART/LEVEL05.TAP',altbytes);z.writestr('ALTERNATE_LARGE_ART/README.txt','Optional larger L5 artwork with r52player engine. Replace LEVEL05.TAP and reset/reload. See root README.\n');z.write(OUT/'l8_comparison.png','PREVIEW/l8_comparison.png');z.write(OUT/'l8_detail.json','PREVIEW/l8_detail.json');z.write(OUT/'l8_before_after.png','PREVIEW/l8_before_after.png')
 with zipfile.ZipFile(archive)as z:assert z.testzip()is None
 m.update(status='Emulator-validated r52 hardware test build',package_sha256=sha(archive.read_bytes()),package_bytes=archive.stat().st_size,physical_validation=False);(OUT/'manifest.json').write_text(json.dumps(m,indent=2));print(archive);print(m['package_sha256'])
if __name__=='__main__':main()
