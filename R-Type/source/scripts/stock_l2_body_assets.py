"""Stopped boss tiles captured through the actual r145 native painter."""
import json

def append_body(root,j):
 source=json.loads((root/'build/cartridges/integration_work/L2_boss_terrain.json').read_text())
 painted=json.loads((root/'build/cartridges/integration_work/L2_boss_painted.json').read_text())
 assert [t['tile']for t in painted['tiles']]==list(range(34,52))
 ids=[];moving=bytearray()
 for tile,coord in zip(painted['tiles'],source['bossCoordinates']):
  assert len(tile['bits'])==128 and len(tile['attrs'])==16
  bits=[];rows=[]
  for c,row in enumerate(tile['attrs']):
   row=[a&~64 if a&64 and(not a&7 or not a&56)else a for a in row]
   assert len(row)==8
   if row not in j['palette']:j['palette'].append(row)
   rows.append(j['palette'].index(row));bb=tile['bits'][c*8:c*8+8];bits.extend([7]+bb)
   material=[(255 if a&7 else b^255)if a&56 else(b if a&7 else 0)for a,b in zip(row,bb)]
   header=134 if any(material)else 7
   moving.extend([header]+material)
  ids.append(len(j['frames']));j['frames'].append(dict(w=4,h=4,bits=bits,rows=rows))
 (root/'build/cartridges/integration_work/L2_boss_moving.bin').write_bytes(moving)
 return ids,source['bossCoordinates']
