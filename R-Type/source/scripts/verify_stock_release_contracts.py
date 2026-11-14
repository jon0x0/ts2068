"""Static/data acceptance for the separate stock64KB cartridge release."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[1];O=R/'build/cartridges/integration_work'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
reports=[]
for n in range(1,9):
 d=O/f'level{n:02d}';rom=d/f'L{n}_shared_cache_internal.rom';b=rom.read_bytes();s=json.loads((d/'current_validation_summary.json').read_text());assert s['passed']and s['rom_sha256']==sha(rom)
 for a,h in s['evidence'].items():
  p=d/a;assert sha(p)==h and json.loads(p.read_text())['passed'],(n,a)
 assert len(b)==65536 and (d/f'L{n}_shared_cache_internal.dck').read_bytes()==bytes([0]+[2]*8)+b
 j=json.loads((d/'combined_frames.json').read_text());rl=json.loads((d/'player_ram_layout.json').read_text());layout=json.loads((d/'shared_cache_layout.json').read_text());terra=json.loads((d/'terrain/contract.json').read_text())
 assert all(not(a&64 and(not a&7 or not a&56))for row in j['palette']for a in row),(n,'bright black')
 assert b[0x16c5:0x16c9]==bytes.fromhex('3e07e607')and b[0x145a:0x145d]==bytes.fromhex('7ee63f')
 ranges=sorted((v[0],v[1],k)for k,v in rl['allocations'].items());assert all(a[1]<=c[0]for a,c in zip(ranges,ranges[1:])),ranges
 assert layout['max_frame_cache_bytes']<=rl['allocations']['sprite_cache'][1]-rl['allocations']['sprite_cache'][0]
 assert terra['tile_dimensions']==[32,32]and len((d/'terrain/native_tiles.bin').read_bytes())==terra['tiles']*144
 g=json.loads((R/f'build/fullgame/audio/music_grammar_{n-1}.json').read_text());music=json.loads((d/'compressed_kernel_layout.json').read_text())['music']
 expected=b''.join(int(a).to_bytes(2,'little')for pair in g['pairs']for a in pair);assert b[music['pairs']:music['pairs']+len(expected)]==expected
 expected=b''.join(int(a).to_bytes(2,'little')for a in g['sequence']);assert b[music['sequence']:music['sequence']+len(expected)]==expected
 for i,frame in enumerate(g['frames']):
  a=int.from_bytes(b[music['directory']+i*2:music['directory']+i*2+2],'little');assert b[a:a+len(frame)]==bytes(frame)
 current=(R/f'build/fullgame/visible_hits_r145/level{n:02d}_region.bin').read_bytes();assert b[0x480:0x8c0]==current[0x480:0x8c0],(n,'current SFX')
 if n==4:
  required={'tap_motion_validation.json','compact_snapshot_validation.json','l4_procedural_validation.json','l4_constructor_irq_validation.json','rom_font_validation.json','l4_bank_windows_validation.json','launcher_layers_validation.json','launcher_actor_guard_validation.json'}
  assert required<=s['evidence'].keys(), 'L4 fractional codec evidence is mandatory'
  codec=json.loads((d/'l4_stable_tokens.json').read_text());assert codec['codec']=='adjacent-quads-v2'
  assert rl['allocations']['ecm_palette_cache']==[0x5800,0x5a80], 'Native HUD attributes must remain reserved'
  cache_ranges=sorted(codec['expanded_rows']+[codec['keys']]);assert all(a[1]<=b[0]for a,b in zip(cache_ranges,cache_ranges[1:]))
  assert sum(b-a for a,b in codec['expanded_rows'])==8*codec['cache_entries']
  assert codec['keys'][1]-codec['keys'][0]==2*codec['cache_entries']

 if n==2:
  c=json.loads((d/'l2_body_ram_contract.json').read_text());assert c['tickets'][1]<=c['source_free_segment'][1]and c['state'][0]>=c['source_free_segment'][0]
 r=dict(passed=True,level=n,rom_sha256=sha(rom),rom_bytes=len(b),read_only_banks=8,frames=len(j['frames']),palette_rows=len(j['palette']),native_actor_variants=len(j['variants']),shared_variants=len(j['common_variants']),frame_cache_bytes=layout['max_frame_cache_bytes'],ordinary_tiles=terra['tiles'],unique_frame_native_bytes=sum(len(f['bits'])for f in j['frames']),palette_bytes=len(j['palette'])*8,music_source_sha256=g['source_sha256'],sfx_match_current=True,normal_black=True,ram_nonoverlap=True,source_native_boss_scripts='Preserved; L4 health16, current selected visual frames and stock HOME cache renderer',validation={a:sha(d/a)for a in s['evidence']},limitations=['Software/emulator acceptance; physical cartridge hardware not yet tested.','Boss draw stress uses invulnerability; L4 victory and recovery have separate evidence.','Stock renderer uses native boss timing/placement; expanded-RAM bank caches and level switching are not part of an individual cartridge.','IRQ vector return probes use explicit target injection in a fixed-FF emulator; not a measured hardware vector.'])
 (d/'release_acceptance.json').write_text(json.dumps(r,indent=2));reports.append(r)
(O/'release_acceptance.json').write_text(json.dumps(dict(passed=True,baseline='r145',target='Stock TS2068, individual64KB read-only cartridge',levels=reports),indent=2));print('PASS all8 stock release data/memory/audio contracts')
