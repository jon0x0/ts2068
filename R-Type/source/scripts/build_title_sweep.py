from pathlib import Path
import hashlib,json
def build(root):
 source=(root/'build/art_assets/title_strip.bin').read_bytes();atlas=bytearray()
 for phase in [0,4]:
  for y in range(48):
   row=bytearray(6)
   for start,width in [(0,6),(6,3),(9,6),(15,6),(21,5),(26,6)]:
    for x in range(width):row[x]|=source[y*32+start+x]
   if phase==0:atlas.extend(row)
   else:atlas.extend([row[0]>>4]+[((row[x-1]&15)<<4)|(row[x]>>4)for x in range(1,6)]+[(row[5]&15)<<4])
 assert len(atlas)==624
 (root/'build/art_assets/title_sweep_atlas.bin').write_bytes(atlas)
 (root/'build/art_assets/title_sweep_atlas.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source).hexdigest(),bytes=len(atlas),phases=[0,4],method='Single quantization; OR six glyph silhouettes once, shift resulting bitmap by four pixels'),indent=2))
 return bytes(atlas)
if __name__=='__main__':build(Path(__file__).resolve().parents[1])
