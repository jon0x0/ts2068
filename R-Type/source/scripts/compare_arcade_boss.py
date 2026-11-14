"""Original arcade-ROM rendering -> legal ECM comparison; not gameplay replacement."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw
import build_graphics as gfx
ROOT=Path(__file__).resolve().parents[1]

def main():
 out=ROOT/'build/graphics/arcade_boss_compare';out.mkdir(parents=True,exist_ok=True)
 cap=ROOT/'build/arcade_boss_capture_invuln';capture=cap/'frame9600.png';original=Image.open(capture).convert('RGB')
 crop=original.crop((176,16,384,224));crop.save(out/'boss_arcade_original_crop.png')
 sprite=Image.new('RGB',(112,144));scaled=crop.resize((112,112),Image.Resampling.NEAREST);sprite.paste(scaled,(0,16));sprite.save(out/'boss_arcade_scaled.png')
 rgb=np.asarray(sprite,dtype=float);luma=(rgb*np.array([.2126,.7152,.0722])).sum(2,keepdims=True);boost=Image.fromarray(np.clip(luma+2.5*(rgb-luma),0,255).astype('uint8'))
 variants=[];frames=[];names=[]
 for name,source in [('boss_preserve',sprite),('boss_chroma',boost)]:
  rgb_source=np.asarray(source,dtype=float)
  pairs=gfx.fit_pairs(rgb_source);edge_pairs=gfx.fit_pairs(rgb_source,black=True)
  touches_black=np.any(np.all(rgb_source.reshape(144,14,8,3)==0,axis=3),axis=2)
  pairs[touches_black]=edge_pairs[touches_black]
  bits,attrs,preview=gfx.quantize(source,pairs=pairs);preview.save(out/(name+'_sprite.png'))
  pixels=np.packbits(bits,axis=1).tobytes();colours=attrs.tobytes();coverage=np.any(np.asarray(sprite)!=0,axis=2);mask=np.packbits(~coverage,axis=1).tobytes()
  (out/(name+'.pixels')).write_bytes(pixels);(out/(name+'.colours')).write_bytes(colours);(out/(name+'.preserve_mask')).write_bytes(mask)
  assert len(pixels)==len(colours)==len(mask)==2016 and not any(a&128 for a in colours)
  canvas=Image.new('RGB',(256,192));canvas.paste(preview,(72,24));ImageDraw.Draw(canvas).text((8,4),name.replace('_',' ').upper(),fill='white')
  b,a,im=gfx.quantize(canvas);assert np.array_equal(np.asarray(im)[24:168,72:184],np.asarray(preview));pix,atr=gfx.pack(b,a);frames.append((pix,atr));names.append(name);im.save(out/(name+'.png'));(out/(name+'.pix')).write_bytes(pix);(out/(name+'.atr')).write_bytes(atr)
  variants.append(dict(name=name,pixel_bytes=len(pixels),colour_bytes=len(colours),preserve_mask_bytes=len(mask),pixel_sha256=gfx.sha(pixels),colour_sha256=gfx.sha(colours),colours=len(preview.getcolors(65536))))
 spec=Image.open(ROOT/'build/diagnostics/r10_boss_cpu.png').resize((112,144),Image.Resampling.NEAREST)
 canvas=Image.new('RGB',(256,192));canvas.paste(spec,(72,24));ImageDraw.Draw(canvas).text((8,4),'SPECTRUM SHAPE / R10 COLOURS',fill='white')
 sources=[('spectrum_recolour',canvas),('arcade_scene',gfx.scene_frame(capture))]
 enemy=Image.open(ROOT/'build/graphics/enemy_arcade.png').convert('RGBA');black=Image.new('RGBA',enemy.size,(0,0,0,255));enemy=Image.alpha_composite(black,enemy).convert('RGB');enemy.save(out/'small_enemy_arcade_original.png')
 canvas=Image.new('RGB',(256,192));draw=ImageDraw.Draw(canvas);draw.text((8,4),'ARCADE ROM ENEMY / 32 AND 16 PIXELS',fill='white')
 for x,size in [(48,(32,16)),(160,(16,16))]:
  small=enemy.resize(size,Image.Resampling.NEAREST);bits,attrs,preview=gfx.quantize(small,black=True);canvas.paste(preview,(x,64));preview.save(out/('enemy_'+str(size[0])+'_ECM.png'))
 sources.append(('small_enemies',canvas))
 for name,source in sources:
  bits,attrs,im=gfx.quantize(source);pix,atr=gfx.pack(bits,attrs);frames.append((pix,atr));names.append(name);im.save(out/(name+'.png'));(out/(name+'.pix')).write_bytes(pix);(out/(name+'.atr')).write_bytes(atr)
 sheet=Image.new('RGB',(4*240,332),(15,15,15));draw=ImageDraw.Draw(sheet)
 panels=[('ARCADE ROM CAPTURE',sprite),('ECM / PRESERVE',Image.open(out/'boss_preserve_sprite.png')),('ECM / CHROMA',Image.open(out/'boss_chroma_sprite.png')),('SPECTRUM / R10',spec)]
 for i,(label,im) in enumerate(panels):draw.text((i*240+8,8),label,fill='white');sheet.paste(im.resize((224,288),Image.Resampling.NEAREST),(i*240+8,32))
 sheet.save(out/'boss_comparison.png')
 previous=gfx.OUT;gfx.OUT=out;gfx.proof_cartridge(frames);gfx.OUT=previous
 manifest=json.loads((out/'proof_manifest.json').read_text());manifest['names']=names;(out/'proof_manifest.json').write_text(json.dumps(manifest,indent=2))
 report=dict(status='Comparison assets/static ROM viewer only; arcade geometry is NOT integrated into playable r10',capture=str(capture.relative_to(ROOT)),capture_sha256=gfx.sha(capture.read_bytes()),crop=[176,16,384,224],scaled_geometry=[112,144],resampling='Nearest neighbour; preserve aspect 112x112 letterboxed to112x144',pair_policy='Force black only in8x1 cells touching transparent/black source; allow two coloured endpoints in opaque interior cells. Black-pixel transparency is a crop heuristic, not decoded arcade alpha.',source='Original functional arcade ROMs verified by capture ROM audit; MAME runtime screenshot plus palette and sprite/tile dumps. Diagnostic Invulnerability DIP only; no graphics ROM edits.',caveat='Boss scene crop includes attached objects/overlaps; not an isolated animation atlas. Authored Spectrum recolour is shown separately. Missing archival PROM/PLD stand-ins are documented in capture audit, not authentic dumps.',variants=variants,small_enemy_source='Decoded arcade ROM sprite54 with captured palette5, as retained in original graphics proof',viewer_names=names)
 (out/'comparison_manifest.json').write_text(json.dumps(report,indent=2));print('Built original arcade boss ECM comparisons and separate64KB static viewer')
if __name__=='__main__':main()
