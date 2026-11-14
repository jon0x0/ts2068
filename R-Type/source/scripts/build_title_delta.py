"""Reusable suffix phases for narrow raster replacement deltas, no full frames."""
from pathlib import Path
import json,hashlib
def build(root):
 source=(root/'build/art_assets/title_strip.bin').read_bytes();glyphs=[(0,6),(6,3),(9,6),(15,6),(21,5),(26,6)];data=bytearray();offsets=[]
 for suffix in range(7):
  offsets.append(0xe400+len(data))
  for phase in ([0,2,4,6]if suffix==0 else [0,4]):
   for y in range(48):
    row=bytearray(7)
    for start,width in glyphs[suffix:]:
     for x in range(width):row[x]|=source[y*32+start+x]
    if phase:row=bytearray([row[0]>>phase]+[((row[x-1]<<(8-phase))&255)|(row[x]>>phase)for x in range(1,7)])
    data+=row
 assert len(data)==5376 and offsets==[0xe400,0xe940,0xebe0,0xee80,0xf120,0xf3c0,0xf660]
 out=root/'build/art_assets';(out/'title_delta_atlas.bin').write_bytes(data);(out/'title_delta_atlas.json').write_text(json.dumps(dict(bytes=len(data),source_sha256=hashlib.sha256(source).hexdigest(),offsets=offsets,sweep_step=4,spread_step=4,available_sweep_phases=[0,2,4,6],policy='Quantize once. Reusable OR-suffix phases; replace old/new dirty window, preserving fixed prefix pixels and settling its final ECM colours.'),indent=2));return bytes(data)
