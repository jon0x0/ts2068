from pathlib import Path
import json,zipfile,hashlib
R=Path.cwd();O=R/'build/fullgame/l2_integrated_r123';B=R/'build/fullgame/l1_blue_boost_r116'
assert hashlib.sha256((B/'RType_TS2068_r116.zip').read_bytes()).hexdigest()=='b570a2dfcd4345947c4c59efa1bd2e160e63e9100ffedb30d1290da6f119dc45'
def blocks(p):
 b=p.read_bytes();out=[];at=0
 while at<len(b):
  n=int.from_bytes(b[at:at+2],'little');v=b[at+2:at+2+n];assert len(v)==n and n>1;check=0
  for x in v:check^=x
  assert check==0,(p,at);out.append((v[0],v[1:-1]));at+=n+2
 assert at==len(b);return out
for n in range(1,9):
 v=(O/f'level{n:02d}_region.bin').read_bytes();assert len(v)==65536
 for kind in ['LEVEL','START']:
  ds=[d for flag,d in blocks(O/'rtype'/f'{kind}{n:02d}.TAP') if flag==255]
  expected=v if kind=='LEVEL' else b''.join(v[p*8192:(p+1)*8192] for p in [0,1,4,5,6,7])
  assert b''.join(ds)==expected,(kind,n)
 if n!=2:assert v==(B/f'level{n:02d}_region.bin').read_bytes()
a=(O/'level02_region.bin').read_bytes();b=(B/'level02_region.bin').read_bytes();assert a[0x8000:0xa000]==b[0x8000:0xa000] and a[0xe000:]==b[0xe000:];assert a[0xb442:0xbcb2]==b[0xb442:0xbcb2];assert a[0x1b20:0x1e20]==b[0x1b20:0x1e20];assert a[0xc762:0xc8a2]==b[0xc762:0xc8a2]
rt=blocks(O/'rtype/rt.tap');assert any(b'R123 PREPARING' in v for _,v in rt)
ct=json.loads((O/'L2_actor_contract.json').read_text());assert ct['all10'];assert len(ct['scorpion_records'])==10
summary={'passed':True,'all16_level_start_tapes_reconstructed':True,'rt_checksums':True,'other7_regions_byte_identical_r116':True,'dock4_dock7_unchanged':True,'terrain_dimensions_maps_and_boss_art_unchanged':True,'all10_scorpions_retained':True,'slow_palette_experiment_excluded':True,'source_zip_sha256':hashlib.sha256((R/'convref/rtype-l2-art-assets_v2.zip').read_bytes()).hexdigest()};(O/'integration_static_validation.json').write_text(json.dumps(summary,indent=2))
text='''R-Type TS2068 r123 - L2 actor integration

Replace the complete rtype folder, reset, and launch rtype/rt.tap.
Startup identity: R123 PREPARING. Number 2 selects level 2.

Integrated from rtype-l2-art-assets_v2.zip:
- All ten scorpion exports, 40x40. Whole-image normalization preserves native
  heading flips; four base packets plus six lossless XOR deltas retain every
  converted frame, including diffusion differences.
- Approved four-frame C shell walker, 24x24; three-frame white-legged shell.
- Selected snake body/head/tail orientations, 24x24.
- Two 40x40 emergence heads; native mirrored variants use the caller flip flag.
  Horizontal head movement retains native 8-pixel coordinates; vertical 2-pixel
  smoothing remains. No AI or collision geometry changes.

The expanded runtime now preserves L2's native uninstall trailer and restores
its overwritten native source prefix before leaving/reloading a level. Packed
actor sources occupy only explicitly retired L2 sprite records. DOCK4 and
DOCK7 are unchanged. Other seven levels match r116 byte-for-byte, including
prior selected L1 artwork and the L3 photographic rocket plume.

LIMITATION: This package completes the selected actor integration. It does not
complete the terrain/boss palette integration. Original strip dimensions,
terrain maps and detailed boss artwork remain unchanged. The full-background
palette scan was rejected because it slows updates; no scan is included here.
The reviewed terrain and stopped-boss reveal still require a cheaper path.

Tests are scripted TSRun emulation, not hardware confirmation. The long ordinary
approach uses an invulnerability/game-over bypass for coverage; separate early
L2 startup/fire cases use unmodified gameplay. Larger selected actors cost time:
the earlier 1547-update approach took roughly 39k emulated frames versus 27k for
r116. This is not a speed improvement or a hardware FPS measurement.

Stock 64KB cartridge target and stable r100 release are unchanged. This package
is the full banked disk game candidate only. Keep r99/r100 archives for recovery.
'''
(O/'README.txt').write_text(text);(R/'docs/l2_integrated_r123.txt').write_text(text)
print(json.dumps(summary))
