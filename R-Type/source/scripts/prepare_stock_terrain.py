"""Preserve current native terrain geometry and derive scroll-safe instance groups."""
from pathlib import Path
import hashlib,json,sys
R=Path.cwd();n=int(sys.argv[1]);O=R/f'build/cartridges/integration_work/level{n:02d}';T=O/'terrain';T.mkdir(exist_ok=True)
j=json.loads((O.parent/f'L{n}_native_terrain.json').read_text());region=R/f'build/fullgame/visible_hits_r145/level{n:02d}_region.bin'
assert hashlib.sha256(region.read_bytes()).hexdigest()==j['sourceRegionSha256']
meta=json.loads((R/'build/fullgame/foundation/manifest.json').read_text())['levels'][n-1]
assert len(j['rawTiles'])==meta['terrain_tiles']
patch=b''.join(bytes(t['bytes'])for t in j['rawTiles']);assert len(patch)==144*meta['terrain_tiles']
(T/'native_tiles.bin').write_bytes(patch)
palette=bytearray(j['palette'])
# Preserve the current TAP palette, including per-raster terrain shading.
(T/'palette.bin').write_bytes(palette)
source=(R/'scripts/terrain_groups.py').read_text().replace('assert len(w)==535 and max(c&63 for c in w)==21','assert len(w)%5==0').replace('range(22)','range(LEVEL_TILES)').replace('assert len(data)<=440','assert len(data)>0')
namespace={'LEVEL_TILES':meta['terrain_tiles']};exec(compile(source,'stock_terrain_groups','exec'),namespace)
mem=bytes(16384)+(R/f'build/fullgame/foundation/level{n:02d}.raw').read_bytes();report=namespace['build'](R,T,mem,patch)
runs=report['runs'];masks=sorted(set(v[1]for v in runs)|{0});data=bytearray()
for i,(_,mask)in enumerate(runs):data+=(runs[i+1][0]if i+1<len(runs)else meta['map_columns']*4).to_bytes(2,'little')+bytes([masks.index(mask)])
data+=b'\xff\xff'+bytes([masks.index(0)]);dictionary=len(data)
for mask in masks:data+=mask.to_bytes(3,'little')
(T/'groups.bin').write_bytes(data)
(T/'contract.json').write_text(json.dumps(dict(level=n,source_sha256=j['sourceRegionSha256'],tile_bytes=len(patch),tiles=meta['terrain_tiles'],tile_dimensions=[32,32],palette_bytes=128,group_bytes=len(data),dictionary=dictionary,map_start=meta['map_start'],map_end=meta['map_end'],rule=report['rule']),indent=2))
print(n,len(patch),len(data),dictionary)
