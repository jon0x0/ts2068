"""Allocate stock player state without borrowing live level scripts or UI pages."""
from pathlib import Path
import json,os,sys
from stock_tap_motion_config import enabled as tap_motion_enabled, composition_enabled, composition_slots, compact_snapshot_enabled, procedural_enabled
R=Path.cwd();O=R/'build/cartridges/integration_work';native=json.loads((R/'build/fullgame/foundation/manifest.json').read_text())['levels'];common=json.loads((O/'L1_common_frames.json').read_text())
def size(f):
 count=len(set(f['rows'])-{-1});return 3+2*(count+int(count>54))+len(f['bits'])
for n in ([int(v)for v in sys.argv[1:]]or range(1,9)):
 j=json.loads((O/f'L{n}_written_stock_frames.json').read_text());common=json.loads((O/f'L{n}_common_direct_frames.json').read_text());meta=native[n-1];phase_bytes=32 if n==7 else 64;context=0xc4ce+phase_bytes;cache=context+(208 if procedural_enabled(n)else 112);cache_bytes=max(map(size,j['frames']+common['frames']));tail=(0xc4ae+meta['payload_bytes']+15)&~15
 motion_enabled=tap_motion_enabled(n)
 if motion_enabled:
  motion=json.loads((O/f'L{n}_tap_motion_frames.json').read_text());cache_bytes=max(cache_bytes,max(map(size,motion['frames'])))
 if procedural_enabled(n):cache_bytes=max(cache_bytes,max(3+2*(sum(p>=0 for p in f['rows'])+(sum(p>=0 for p in f['rows'])>54))+len(f['bits'])for f in motion['frames']))
 free=[[cache+cache_bytes,meta['enemy_descriptors_start']]];tails=[]
 if tail<0xf800:free.append([tail,0xf800]);tails=[tail,0xf800]
 allocations={'phase_counters':[0xc4ce,context],'context_and_stack':[context,cache],'sprite_cache':[cache,cache+cache_bytes],'player_state':[0x5b00,0x5d00]}
 for name,length in [('player_phases',768),('published_owner_map',640),('backing_pixels',640),('backing_attributes',160 if motion_enabled and compact_snapshot_enabled(n)else 640),('projectile_state',128),('working_player_palettes',64)]+([('l2_body_workspace',320)]if n==2 else [])+([('boss_motion_state',128 if n==4 else 64)]if motion_enabled else [])+([('l4_procedural_state',146),('l4_pair_cache_keys',448)]if procedural_enabled(n)else [])+([('motion_dense_parent',max(f['w']*f['h']*8 for i,f in enumerate(motion['frames'])if any(v['frame']==i and not v['py']for v in motion['variants'])))]if motion_enabled and n in (2,4,5,7)else [])+([('l4_expanded_row_tail',24)]if procedural_enabled(n)else [])+([('dynamic_palette_rows',8*composition_slots(n)),('dynamic_palette_hashes',256),('dynamic_palette_refs',(composition_slots(n)+7)//8),('dynamic_palette_state',72),('dynamic_palette_links',composition_slots(n)),('dynamic_palette_head_valid',32)]if composition_enabled(n)else []):
  alignment=128 if name=='projectile_state' else 1
  eligible=[s for s in free if ((s[0]+alignment-1)&-alignment)+length<=s[1]]
  segment=(min(eligible,key=lambda s:s[1]-s[0])if n in (2,4,7) and motion_enabled and eligible else next(iter(eligible),None));assert segment is not None,(n,name,length,free)
  start=(segment[0]+alignment-1)&-alignment
  if n in (2,4,7) and motion_enabled and start>segment[0]:free.append([segment[0],start])
  allocations[name]=[start,start+length];segment[0]=start+length
 if procedural_enabled(n):
  allocations['ecm_palette_cache']=[0x5800,0x5a80];allocations['rom_glyph_cache']=[0x7b08,0x7cc8]
 ranges=sorted((a,b,k)for k,(a,b)in allocations.items());assert all(a>=0x5800 and b<=0xf800 and a<b for a,b,k in ranges)
 for (_,end,k),(start,_,other)in zip(ranges,ranges[1:]):assert end<=start,(n,k,other)
 assert len(set(((1+i*9)&255)&(phase_bytes-1)for i in range(28)))==28
 record=dict(clock_flags=[0x5c83,0x5c9b],irq_stack_top=cache-2,native_projectile_pool_reserved=[0x5e00,0x6000],level=n,status='Static allocation; tail use and player/IRQ runtime still require validation',allocations=allocations,free_segments=free,tail_range=tails,actor_slot_hash_proof=dict(stride=9,slots=28,mask=phase_bytes-1,distinct=28),native_descriptor_start=meta['enemy_descriptors_start'],native_payload_end=0xc4ae+meta['payload_bytes'])
 folder=O/f'level{n:02d}';folder.mkdir(exist_ok=True);(folder/'player_ram_layout.json').write_text(json.dumps(record,indent=2));print(n,{k:hex(v[0])for k,v in allocations.items()},'spare',sum(b-a for a,b in free))
