from pathlib import Path
import json,collections
import numpy as np
from PIL import Image,ImageDraw
root=Path(r'D:/T7_Recover/Jon/Personal/Timex/cartridgeconversion/R-Type')
layouts=json.loads((root/'build/fullgame/foundation/manifest.json').read_text())['levels']
palette=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205),(0,0,0),(0,0,255),(255,0,0),(255,0,255),(0,255,0),(0,255,255),(255,255,0),(255,255,255)],dtype=np.uint8)
report=[];gallery=Image.new('RGB',(960,1200));draw=ImageDraw.Draw(gallery)
for layout in layouts[4:]:
 n=layout['level'];p=root/f'build/fullgame/converted/level{n:02d}';meta=json.loads((p/'manifest.json').read_text());raw=bytes(0xc4ce)+(p/'enemy_graphics.bin').read_bytes();dictionary=(p/'enemy_palette.bin').read_bytes();descs={v['id']:v for v in layout['enemies']};descs.update({v['id']:v for v in meta['descriptors']});records=[]
 for ident,d in descs.items():
  if not d['width']or not d['height']:continue
  ptr=d['pointer'];inks=collections.Counter();variable=0;cells=0;im=Image.new('RGB',(d['width']*8,d['height']*8))
  for y in range(d['height']):
   for x in range(d['width']):
    a=raw[ptr]
    if a==54:ptr+=1;continue
    row=np.frombuffer(dictionary[(a&127)*8:(a&127)*8+8],dtype=np.uint8);bits=np.unpackbits(np.frombuffer(raw[ptr+1:ptr+9],dtype=np.uint8)).reshape(8,8);bright=(row&64)>0;ink=(row&7)+bright*8;paper=((row>>3)&7)+bright*8;col=np.where(bits,ink[:,None],paper[:,None]);visible=col[col%8!=0];inks.update(map(int,visible));cells+=1;variable+=len(set(row.tolist()))>1;im.paste(Image.fromarray(palette[col]),(x*8,y*8));ptr+=9
  total=sum(inks.values());dominant=max(inks.values(),default=0)/max(total,1)
  records.append(dict(id=ident,converted=ident in meta['converted_descriptors'],visible_colours=len(inks),dominant_fraction=round(dominant,3),variable_cells=variable,cells=cells,sparse=len(inks)<=2 or dominant>=.9))
  if ident<=45:
   gx=((ident-1)%9)*106;gy=(n-5)*300+((ident-1)//9)*58;draw.text((gx,gy),f'L{n} #{ident}',fill='white');im.thumbnail((96,42),Image.Resampling.NEAREST);gallery.paste(im,(gx,gy+13))
 report.append(dict(level=n,descriptors=records,sparse=sum(v['sparse']for v in records),total=len(records),native_fallback=sum(not v['converted']for v in records)))
out=root/'build/diagnostics/enemy_colour_audit';out.mkdir(parents=True,exist_ok=True);(out/'audit.json').write_text(json.dumps(report,indent=2));gallery.save(out/'higher_level_enemy_gallery.png')
for r in report:print('Level',r['level'],'sparse',r['sparse'],'/',r['total'],'not individually arcade-converted',r['native_fallback'])
