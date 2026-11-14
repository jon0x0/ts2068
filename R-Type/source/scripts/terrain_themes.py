"""Per-level authored theme families, each retaining two within-level arrangements."""
import json,hashlib
from PIL import Image,ImageDraw

def remap_attribute(attr,mapping):
 assert not attr&0xB8,'Theme reference must use black paper, no flash'
 ink=(attr&7)+(8 if attr&64 else 0);ink=int(mapping.get(str(ink),ink))
 assert 1<=ink<=15
 return (ink&7)|(64 if ink>=8 else 0)

def emit_theme_assets(root,out,active_level=1):
 config=json.loads((root/'assets/terrain_themes.json').read_text());assert active_level==config['active_playable_level']==1
 source=(out/'terrain_arcade.palette').read_bytes()[:128];assert len(source)==128
 folder=out/'level_themes';folder.mkdir(exist_ok=True);records=[];selected=None
 sheet=Image.new('RGB',(704,8*100));draw=ImageDraw.Draw(sheet)
 from build_graphics import PALETTE
 for theme in config['themes']:
  level=theme['level'];table=bytes(remap_attribute(a,theme['primary_ink_map'] if i<64 else theme['secondary_ink_map'])for i,a in enumerate(source))
  # All four forward records have matching reversed records in each arrangement.
  for bank in (0,64):
   for row in range(4):assert table[bank+row*8:bank+row*8+8][::-1]==table[bank+32+row*8:bank+40+row*8]
  file=f'level{level:02d}.palette';(folder/file).write_bytes(table)
  y=(level-1)*100;draw.text((8,y+3),f'Level {level}: {theme["name"]}',fill='white')
  for bank,label in ((0,'Group A'),(64,'Group B')):
   x=8+(bank//64)*348;draw.text((x,y+20),label,fill='white')
   for row in range(32):
    attr=table[bank+row];ink=(attr&7)+(8 if attr&64 else 0);colour=tuple(map(int,PALETTE[ink]));draw.rectangle((x,y+35+row*2,x+331,y+36+row*2),fill=colour)
  records.append(dict(level=level,name=theme['name'],palette_file=file,bytes=len(table),sha256=hashlib.sha256(table).hexdigest(),arrangements=2,status='integrated' if level==active_level else 'prepared; gameplay conversion pending'))
  if level==active_level:selected=table
 assert selected is not None and len(records)==8
 sheet.save(folder/'theme_families.png')
 (folder/'manifest.json').write_text(json.dumps(dict(active_playable_level=active_level,runtime_level_switching=False,group_variation=True,themes=records),indent=2)+'\n')
 return selected
