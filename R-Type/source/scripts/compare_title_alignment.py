"""Search actual arcade logo size/offset for fewer incompatible8x1 material cells."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
import build_graphics as g
R=Path(__file__).resolve().parents[1]
def main():
 o=R/'build/graphics/title_alignment';o.mkdir(parents=True,exist_ok=True)
 source=Image.open(R/'build/graphics/arcade_title_reference.png').convert('RGB').crop((8,98,248,140));source=source.crop(source.getbbox());legacy=Image.open(R/'build/ecm_native/title_legacy_reference.png').convert('RGB')
 def analyse(w,x):
  h=round(source.height*w/source.width);y=100+(42-h)//2;im=source.resize((w,h),Image.Resampling.NEAREST);rgb=np.zeros((192,256,3),dtype=np.uint8);rgb[y:y+h,x:x+w]=np.asarray(im);v=rgb.astype(int);on=np.any(v!=0,axis=2);blue=on&(v[:,:,2]>v[:,:,0]+32)&(v[:,:,1]>v[:,:,0]+24);white=on&~blue
  bc=blue.reshape(192,32,8).sum(2);wc=white.reshape(192,32,8).sum(2);loss=int(np.minimum(bc,wc).sum());return dict(width=w,height=h,x=x,y=y,mixed_cells=int(((bc>0)&(wc>0)).sum()),conflicting_pixels=loss,score=loss/max(1,int(on.sum()))),im,bc,wc
 candidates=[]
 for w in range(232,249):
  for x in range(max(0,(256-w)//2-4),min(256-w,(256-w)//2+4)+1):candidates.append(analyse(w,x)[0])
 best=min(candidates,key=lambda q:(q['score']+.00015*(248-q['width']),-q['width']));maximum=min((q for q in candidates if q['width']==248),key=lambda q:q['score'])
 pages=[];names=[];visuals={}
 def save(name,frame,pairs=None):
  bits,attrs,preview=g.quantize(frame,black=True,pairs=pairs);pix,atr=g.pack(bits,attrs);assert not any(a&128 for a in atr);(o/(name+'.pix')).write_bytes(pix);(o/(name+'.atr')).write_bytes(atr);preview.save(o/(name+'.png'));pages.append((pix,atr));names.append(name);visuals[name]=preview
 save('original_menu',legacy)
 def candidate(name,info,protect):
  data,logo,bc,wc=analyse(info['width'],info['x']);frame=legacy.copy();ImageDraw.Draw(frame).rectangle((0,96,255,141),fill='black');frame.paste(logo,(data['x'],data['y']));pairs=g.fit_pairs(np.asarray(frame,dtype=float),black=True)
  if protect:
   # A neutral stroke takes priority if white and blue need a third colour.
   for y in range(data['y'],data['y']+data['height']):
    for cell in range(32):
     if wc[y,cell]>0:pairs[y,cell]=(8,15)
     elif bc[y,cell]>0:pairs[y,cell]=(8,13 if y<data['y']+data['height']*0.8 else 9)
  save(name,frame,pairs)
 candidate('arcade_default',analyse(232,12)[0],False);candidate('aligned_best',best,True);candidate('aligned_248',maximum,True)
 grid=visuals['aligned_best'].copy();d=ImageDraw.Draw(grid)
 for x in range(0,256,8):d.line((x,96,x,143),fill=(72,72,72))
 grid.save(o/'aligned_best_grid.png');save('alignment_grid',grid)
 sheet=Image.new('RGB',(2*528,2*130),(16,16,16));d=ImageDraw.Draw(sheet)
 for n,(label,name) in enumerate([('CURRENT SPECTRUM MENU','original_menu'),('ARCADE LOGO / UNALIGNED','arcade_default'),('LARGER / BLUE CELLS PROTECTED','aligned_best'),('8-PIXEL COLUMN GRID','alignment_grid')]):
  xx=n%2*528;yy=n//2*130;d.text((xx+8,yy+5),label,fill='white');sheet.paste(visuals[name].crop((0,94,256,150)).resize((512,112),Image.Resampling.NEAREST),(xx+8,yy+18))
 sheet.save(o/'title_alignment_comparison.png');old=g.OUT;g.OUT=o;g.proof_cartridge(pages);g.OUT=old;m=json.loads((o/'proof_manifest.json').read_text());m['names']=names;(o/'proof_manifest.json').write_text(json.dumps(m,indent=2));(o/'alignment_manifest.json').write_text(json.dumps(dict(status='Title asset/comparison ROM only, not integrated into moving gameplay menu',best=best,maximum=maximum,candidates=candidates,policy='Original arcade geometry resized; protect neutral strokes in mixed8x1 cells. Remaining incompatible blue fragments are sacrificed rather than recolouring adjacent strokes.',source='Original arcade title reference plus actual legacy Spectrum menu capture',limitation='Size/offset cannot eliminate every three-colour cell on diagonal strokes. Static proof does not establish flicker-free animated integration.'),indent=2));print('Best title alignment',best)
if __name__=='__main__':main()
