"""Dobkeratops material bands on original geometry; immutable ROM lookup."""
import json

def material(x,y):
 # Authored organic head, blue armour, warm vent cores and lower jaw.
 if y<40:
  ramp=(6,14,15,14,6,10,2,3)
 elif x>=64 and 48<=y<128:
  vent=((x-84)/22)**2+((y-72)/17)**2<1 or ((x-84)/22)**2+((y-104)/17)**2<1
  ramp=(2,10,6,14,15,14,10,2) if vent else (1,9,5,13,15,13,5,9)
 elif y>=128 and x>=40:
  ramp=(2,10,6,14,15,14,6,10)
 else:
  ramp=(2,10,3,11,15,11,3,10)
 colour=ramp[y%8]
 return (colour&7)|(64 if colour>=8 else 0)

def set_tag(lookup,p,index):
 slot=(p-0xc400)>>3
 assert lookup[slot] in (255,index),(hex(p),slot,index,lookup[slot])
 lookup[slot]=index

def small_material(attr,cx,cy,w,h):
 ink=attr&7
 # Stable material regions in pose coordinates; no repeating rainbow ramps.
 if w>=2 and h>=2 and cx==w//2 and cy==(h-1)//2:return 11
 if ink in (2,3):return 13
 if ink==4:return 14 if cx==0 and cy==0 else 12
 if ink==6:return 11
 if ink==7:return 14
 return 9 if cy==0 else 10 if cy==h-1 else 15

def build(root):
 from fullgame_context import FULL
 if FULL:
  from full_level_art import boss_palettes
  return boss_palettes(root)
 b=bytes(0x4000)+(root/'build/native/snapshot.bin').read_bytes()
 p=0xc571;lookup=bytearray([255]*640);rows=[];cells=[]
 for cy in range(18):
  for cx in range(14):
   a=b[p]
   if a==0x36:p+=1;continue
   row=bytes(material(cx*8+4,cy*8+dy) for dy in range(8))
   if row not in rows:rows.append(row)
   index=rows.index(row);set_tag(lookup,p,index)
   cells.append(dict(pointer=p,x=cx,y=cy,index=index,colours=list(row)))
   p+=9
 assert p==0xcb4d and len(rows)<256
 assert len(rows)==9
 generic=((13,)*8,(9,)*8,(14,)*8,(12,)*8,(10,)*8,(15,)*8,(7,)*8)
 for ramp in generic:rows.append(bytes((c&7)|(64 if c>=8 else 0) for c in ramp))
 known={v['pointer']:v for v in cells}
 for ident in range(1,71):
  d=0xd7f9+(ident-1)*4;w,h=b[d:d+2];q=int.from_bytes(b[d+2:d+4],'little')
  for cy in range(h):
   for cx in range(w):
    a=b[q]
    if a==0x36:q+=1;continue
    assert 0xc4ce<=q<0xd7f9
    if q not in known:
     index=small_material(a,cx,cy,w,h);set_tag(lookup,q,index);record=dict(pointer=q,x=cx,y=cy,index=index,colours=list(rows[index]),descriptor=ident);cells.append(record);known[q]=record
    q+=9
 assert len(rows)==16
 extra=(root/'build/art_assets/fireball_colours.bin').read_bytes()
 for i in range(12):rows.append(extra[i*8:i*8+8])
 for record in cells:
  if 0xd550<=record['pointer']<0xd574:
   index=16+(record['pointer']-0xd550)//9;record['index']=index;record['colours']=list(rows[index])
 palette=b''.join(rows);assert len(rows)==28 and len(palette)<=0x600
 out=root/'build/ecm_native';(out/'boss_lookup.bin').write_bytes(lookup);(out/'boss_colours.bin').write_bytes(palette)
 (out/'boss_manifest.json').write_text(json.dumps(dict(cells=cells,unique_rows=len(rows),source='All70 level1 enemy descriptors; boss materials and pose-local small-enemy shells, highlights and cores, original bitmaps unchanged'),indent=2))
 return bytes(lookup),palette
