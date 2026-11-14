"""Original arcade cels and accepted title -> fixed-size native cartridge assets."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from build_graphics import decode_roms,palette_ram,fit_pairs,quantize,PALETTE,screen_offset,sha
def build(root):
 out=root/'build/art_assets';out.mkdir(parents=True,exist_ok=True)
 sprites,_=decode_roms();palette=palette_ram(root/'build/arcade_boss_capture_invuln/frame9600_palette_sprite.bin')[80:96]
 frames=bytearray();rows=bytearray();report=[];images=[]
 for code in (0x175,0x176,0x177):
  indices=sprites[code];rgb=palette[indices];pairs=fit_pairs(rgb.astype(float));edge=fit_pairs(rgb.astype(float),black=True);touch=(indices==0).reshape(16,2,8).any(2);pairs[touch]=edge[touch]
  bits,attrs,_=quantize(Image.fromarray(rgb),pairs=pairs);bits[indices==0]=0
  p=np.repeat(PALETTE[pairs[:,:,0]],8,axis=1);q=np.repeat(PALETTE[pairs[:,:,1]],8,axis=1);preview=Image.fromarray(np.where(bits[:,:,None],q,p).astype('uint8'));images.append(preview.resize((128,128),Image.Resampling.NEAREST))
  start=len(frames)
  for cy in range(2):
   for cx in range(2):
    a=int(attrs[cy*8,cx]);assert a!=54 and not a&128
    frames.append(a);frames+=np.packbits(bits[cy*8:cy*8+8,cx*8:cx*8+8],axis=1).tobytes();rows+=attrs[cy*8:cy*8+8,cx].tobytes()
  report.append(dict(code=code,frame_offset=start,palette=5))
 assert len(frames)==108 and len(rows)==96
 (out/'fireball_frames.bin').write_bytes(frames);(out/'fireball_colours.bin').write_bytes(rows)
 images[0].save(out/'arcade_orb_pulse.gif',save_all=True,append_images=[images[1],images[2],images[1]],duration=100,loop=0)
 images[0].save(out/'arcade_orb_frame0.png')
 title=root/'build/graphics/title_alignment';pix=(title/'aligned_best.pix').read_bytes();atr=(title/'aligned_best.atr').read_bytes();blob=b''.join(plane[screen_offset(y):screen_offset(y)+32] for plane in (pix,atr) for y in range(96,144));assert len(blob)==3072
 (out/'title_strip.bin').write_bytes(blob);plan=b''.join((0x4000+screen_offset(y)).to_bytes(2,'little') for y in range(96,144));(out/'title_rows.bin').write_bytes(plan)
 (out/'manifest.json').write_text(json.dumps(dict(source='Original arcade graphics ROM cels175/176/177 with captured palette5; accepted239x39 arcade title alignment',fireball_frames=report,pulse=[0,1,2,1],fireball_pixels_sha256=sha(frames),fireball_colours_sha256=sha(rows),title_sha256=sha(blob),title_area=[0,96,256,48],note='Authored pulse order uses original arcade cels; not claimed to reproduce original arcade timing. Native orb descriptor57 remains2x2 cells.'),indent=2))
 build_terrain(root,out)
 from fullgame_context import FULL,LEVEL
 if FULL and LEVEL==1:
  frames=(root/'build/fullgame/converted/level01/orb_frames.bin').read_bytes();(out/'fireball_frames.bin').write_bytes(frames)
 return bytes(frames),bytes(rows),blob,plan
def build_terrain(root,out):
 from fullgame_context import FULL
 if FULL:
  from full_level_art import build_terrain as full_terrain
  return full_terrain(root,out)
 import os
 from PIL import ImageDraw
 b=bytes(0x4000)+(root/'build/native/snapshot.bin').read_bytes();end=int.from_bytes(b[0xc4bc:0xc4be],'little')
 scene=Image.open(root/'build/arcade_boss_capture_invuln/frame2400.png').convert('RGB')
 templates=[scene.crop((152,208,216,240)).resize((32,32),Image.Resampling.NEAREST),scene.crop((88,192,152,240)).resize((32,32),Image.Resampling.NEAREST)]
 for n,im in enumerate(templates):im.save(out/f'terrain_arcade_material{n}.png')
 for profile in ('preserve','chroma','arcade'):
  refs=[];pool=[];rgbs=[]
  for im in templates:
   rgb=np.asarray(im,dtype=float)
   if profile in ('chroma','arcade'):
    luma=(rgb*np.array([.2126,.7152,.0722])).sum(2,keepdims=True);rgb=np.clip(luma+(5.0 if profile=='chroma' else 3.0)*(rgb-luma),0,255)
   rgbs.append(rgb)
  # Every native tile occupies an aligned32x32 map slot. Shared row pairs,
  # fitted across both arcade materials and their vertical mirrors, are invariant
  # under every horizontal tile join and either native vertical orientation.
  samples=np.concatenate(rgbs+[rgb[::-1] for rgb in rgbs],axis=1)
  pairs=fit_pairs(samples,mode='row',black=True)[:,:4].copy()
  if profile=='arcade':
   from arcade_terrain_colour import row_pairs
   pairs=row_pairs(samples)
  for yy in range(32):
   if not np.any(samples[yy]):pairs[yy,:,:]=[8,15]
  assert np.array_equal(pairs,pairs[::-1])
  for rgb in rgbs:
   bits,attrs,_=quantize(Image.fromarray(rgb.astype('uint8')),pairs=pairs,black=True)
   ids=np.zeros((4,4),dtype='uint8')
   for cy in range(4):
    for cx in range(4):
     row=bytes(attrs[cy*8:cy*8+8,cx])
     if row not in pool:pool.append(row)
     ids[cy,cx]=pool.index(row)
   refs.append((bits,attrs,ids))
  assert len(pool)<=4
  patches=bytearray();records=[];sheet=Image.new('RGB',(6*128,4*144));draw=ImageDraw.Draw(sheet)
  for tile in range(22):
   start=end-(tile+1)*144;cells=[];old=np.zeros((32,32),dtype='uint8');solid=np.zeros((4,4),dtype=bool);weight=0;building=0
   for cy in range(4):
    for cx in range(4):
     p=start+(cy*4+cx)*9;a=b[p];bits=np.unpackbits(np.frombuffer(b[p+1:p+9],dtype='uint8')).reshape(8,8);old[cy*8:cy*8+8,cx*8:cx*8+8]=bits;solid[cy,cx]=bool(a&128);cells.append((a,b[p+1:p+9]));count=int(bits.sum());weight+=count
     if a&7 in (2,3,4,6):building+=count
   material=1 if building>weight*0.22 else 0;texture,attrs,ids=refs[material];envelope=np.zeros((32,32),dtype='uint8');outline=np.zeros_like(envelope)
   for y in range(32):
    xs=np.flatnonzero(old[y])
    if len(xs):envelope[y,xs[0]:xs[-1]+1]=1;outline[y,xs[0]]=1;outline[y,xs[-1]]=1
   allowed=np.repeat(np.repeat(solid,8,axis=0),8,axis=1);new=((texture&envelope)|outline)&allowed;tilebytes=bytearray();colours=np.zeros((32,4),dtype='uint8')
   for cy in range(4):
    for cx in range(4):
     a,original=cells[cy*4+cx]
     if a&128:
      token=128+int(ids[cy,cx]);tilebytes.append(token);tilebytes+=np.packbits(new[cy*8:cy*8+8,cx*8:cx*8+8],axis=1).tobytes();colours[cy*8:cy*8+8,cx]=attrs[cy*8:cy*8+8,cx]
     else:tilebytes.append(a);tilebytes+=original;new[cy*8:cy*8+8,cx*8:cx*8+8]=old[cy*8:cy*8+8,cx*8:cx*8+8];colours[cy*8:cy*8+8,cx]=a&127
   assert len(tilebytes)==144 and all((tilebytes[i*9]&128)==(cells[i][0]&128) for i in range(16))
   patches+=tilebytes
   ink=(colours&7)+np.where(colours&64,8,0);paper=((colours>>3)&7)+np.where(colours&64,8,0);rgb=PALETTE[np.where(new!=0,np.repeat(ink,8,1),np.repeat(paper,8,1))].astype('uint8');image=Image.fromarray(rgb);xx=tile%6*128;yy=tile//6*144;sheet.paste(image.resize((128,128),Image.Resampling.NEAREST),(xx,yy+16));draw.text((xx+3,yy+2),f'Tile {tile} material{material}',fill='white');records.append(dict(tile=tile,material=material))
  palette=bytearray(bytes([0x47])*1024)
  for i,row in enumerate(pool):palette[i*8:i*8+8]=row;palette[(4+i)*8:(5+i)*8]=row[::-1]
  if profile=='arcade':
   from terrain_groups import build as build_groups
   proof=build_groups(root,out,b,patches)
   variant_cells=set()
   # Alternate warm-metal arrangement, still black paper and mirror compatible.
   first=np.roll(pairs[:16],3,axis=0).copy()
   # Cool arcade machinery complements the copper/gold arrangement.
   cold={2:1,6:5,7:7,14:13,15:15}
   for yy in range(16):
    for xx in range(4):
     ink=cold[int(first[yy,xx,1])];first[yy,xx]=[8 if ink>=8 else 0,ink]
   alternate=np.concatenate([first,first[::-1]],axis=0)
   alternate_attrs=np.array([((int(q[0,0])&7)<<3)|(int(q[0,1])&7)|(64 if int(q[0,1])>=8 else 0) for q in alternate],dtype='uint8')
   for cy in range(4):
    original=bytes(attrs[cy*8:cy*8+8,0]);ident=pool.index(original)
    row=bytes(alternate_attrs[cy*8:cy*8+8]);palette[(8+ident)*8:(9+ident)*8]=row;palette[(12+ident)*8:(13+ident)*8]=row[::-1]
   for cell in variant_cells:
    if patches[cell*9]&128:patches[cell*9]|=8
   assert max(patches[i] &127 for i in range(0,len(patches),9) if patches[i]&128)<16
   (out/'terrain_island_proof.json').write_text(json.dumps(proof,indent=2))
   # Re-render the actual variant tokens, rather than the pre-island atlas.
   for tile in range(22):
    pixels=np.zeros((32,32),dtype='uint8');colours=np.zeros((32,32),dtype='uint8')
    for cy in range(4):
     for cx in range(4):
      p=tile*144+(cy*4+cx)*9;a=patches[p]
      pixels[cy*8:cy*8+8,cx*8:cx*8+8]=np.unpackbits(np.frombuffer(patches[p+1:p+9],dtype='uint8')).reshape(8,8)
      row=np.array([palette[(a&127)*8+y] if a&128 else a&127 for y in range(8)])
      colours[cy*8:cy*8+8,cx*8:cx*8+8]=row[:,None]
    ink=(colours&7)+np.where(colours&64,8,0);paper=((colours>>3)&7)+np.where(colours&64,8,0)
    preview=Image.fromarray(PALETTE[np.where(pixels,ink,paper)].astype('uint8'));sheet.paste(preview.resize((128,128),Image.Resampling.NEAREST),(tile%6*128,tile//6*144+16))
  (out/f'terrain_{profile}.patches').write_bytes(patches);(out/f'terrain_{profile}.palette').write_bytes(palette);sheet.save(out/f'terrain_{profile}_atlas.png')
  (out/f'terrain_{profile}.json').write_text(json.dumps(dict(palette_policy=('per-instance map groups; alternate warm/cool arrangements separated by >8-pixel gaps' if profile=='arcade' else 'shared32-pixel-row; both materials and vertical mirrors'),profile=profile,chroma_factor=5.0 if profile=='chroma' else 3.0 if profile=='arcade' else 1.0,rows=len(pool),tiles=records,source='Arcade frame2400 platform crop152,208,216,240 and pillar crop88,192,152,240; original terrain envelope/solid-cell coverage retained, interior texture replaced',palette_sha256=sha(palette),patches_sha256=sha(patches)),indent=2))
 profile=os.environ.get('RTYPE_ART_PROFILE','arcade');assert profile in ('preserve','chroma','arcade');(out/'terrain_patches.bin').write_bytes((out/f'terrain_{profile}.patches').read_bytes());(out/'terrain_palette.bin').write_bytes((out/f'terrain_{profile}.palette').read_bytes());(out/'terrain_active.json').write_text((out/f'terrain_{profile}.json').read_text())
 if profile!='arcade':(out/'terrain_group_runs.bin').write_bytes(bytes.fromhex('ff ff 00 00 00'))
 from terrain_themes import emit_theme_assets
 themed=emit_theme_assets(root,out,active_level=1)
 if profile=='arcade':
  current=bytearray((out/'terrain_palette.bin').read_bytes());current[:128]=themed;(out/'terrain_palette.bin').write_bytes(current)
  metadata=json.loads((out/'terrain_active.json').read_text());metadata['level_theme']=1;metadata['palette_sha256']=sha(current);(out/'terrain_active.json').write_text(json.dumps(metadata,indent=2))

def patch_pixels(root,ram,frames):
 from fullgame_context import FULL,LEVEL
 b=bytearray(ram)
 if FULL:b[0xc4ce-0x4000:0xf87c-0x4000]=(root/f'build/fullgame/converted/level{LEVEL:02d}/enemy_graphics.bin').read_bytes()
 if not FULL or LEVEL==1:b[0xd550-0x4000:0xd574-0x4000]=frames[:36]
 from fullgame_context import FULL,LEVEL,layout
 patches=(root/'build/art_assets/terrain_patches.bin').read_bytes();end=int.from_bytes(b[0xc4bc-0x4000:0xc4be-0x4000],'little')
 for tile in range(layout()['terrain_tiles'] if FULL else 22):p=end-(tile+1)*144-0x4000;b[p:p+144]=patches[tile*144:(tile+1)*144]
 return b

# Non-arcade comparison profiles disable the per-instance alternate arrangement.
