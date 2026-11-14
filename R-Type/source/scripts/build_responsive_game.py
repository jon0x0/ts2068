"""r50: faster sustained pixel controls and one arcade joint per snake frame."""
from pathlib import Path
import json,hashlib,shutil,subprocess
import numpy as np
from PIL import Image,ImageDraw
from build_rocket_fix import code
from preview_enemy_sierra import convert
from build_graphics import PALETTE
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/responsive_game_r50'
def patch_snake(b,report):
 layout=json.loads((ROOT/'build/fullgame/foundation/manifest.json').read_text())['levels'][0];descs={d['id']:d for d in layout['enemies']};dictionary=b[0xe000:0xe400];native=bytearray(65536);native[0xc000:]=b[0xa000:0xe000];source=Image.open(ROOT/'build/fullgame/converted/level01/descriptor016_arcade.png').convert('RGBA');joint=source.crop((30,0,61,30));sheet=Image.new('RGB',(800,200));draw=ImageDraw.Draw(sheet);changes=[]
 for index,ident in enumerate([16,17,18,19]):
  # Native geometry remains3x3cells; use one joint and orientation siblings.
  rotated=joint.rotate(index*30,resample=Image.Resampling.BICUBIC,expand=False).resize((24,24),Image.Resampling.LANCZOS)
  connected=Image.new('RGBA',(24,24));pen=ImageDraw.Draw(connected)
  paths={16:[((0,12),(4,12)),((19,12),(23,12))],17:[((12,0),(12,4)),((12,19),(12,23))],18:[((23,0),(18,5)),((5,18),(0,23))],19:[((0,12),(4,12)),((19,12),(23,12))]}
  for ends in paths[ident]:pen.line(ends,fill=(170,150,95,255),width=5);pen.line(ends,fill=(235,225,170,255),width=2)
  connected.alpha_composite(rotated);preview,bits,attrs=convert(connected,(24,24),np.ones((24,24),bool),1.8,2,False,True);target=np.asarray(preview,dtype=float);p=descs[ident]['pointer'];start=p;fitted=np.zeros((24,24,3),np.uint8)
  for cy in range(3):
   for cx in range(3):
    tag=native[p]
    if tag==54:p+=1;continue
    rgb=target[cy*8:cy*8+8,cx*8:cx*8+8];visible=rgb.max(2)>0;choices=[]
    for rowid in range(128):
     if rowid==54:continue
     a=np.frombuffer(dictionary[rowid*8:rowid*8+8],dtype=np.uint8);br=np.where(a&64,8,0);pi=((a>>3)&7)+br;qi=(a&7)+br
     if np.any((~visible).any(1)&(pi%8!=0)):continue
     paper=PALETTE[pi];ink=PALETTE[qi];pe=((rgb-paper[:,None])**2).sum(2);ie=((rgb-ink[:,None])**2).sum(2);tile=ie<pe;tile[~visible]=False;error=np.minimum(pe,ie)[visible].sum();choices.append((error,rowid,tile,paper,ink))
    _,rowid,tile,paper,ink=min(choices,key=lambda c:c[0]);native[p]=(tag&128)|rowid;native[p+1:p+9]=np.packbits(tile,axis=1).tobytes();fitted[cy*8:cy*8+8,cx*8:cx*8+8]=np.where(tile[:,:,None],ink[:,None],paper[:,None]);p+=9
  image=Image.fromarray(fitted);image.save(OUT/f'snake{ident}.png');draw.text((index*200+4,4),f'One joint: frame{ident}',fill='white');sheet.paste(image.resize((144,144),Image.Resampling.NEAREST),(index*200+4,30));changes.append(dict(descriptor=ident,pointer=start,bytes=p-start,size=[24,24],angle=index*30))
 b[0xa000:0xe000]=native[0xc000:];sheet.save(OUT/'snake_frames.png');report.update(source_box=[30,0,61,30],source_size=list(source.size),frames=changes,dictionary_unchanged=True,native_dimensions_and_pointers_unchanged=True)
def main():
 source=ROOT/'build/fullgame/material_game_r49';OUT.mkdir(exist_ok=True,parents=True);shutil.copytree(source/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True)
 asm=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';r=subprocess.run([str(asm),f'--raw={OUT/"overlay.bin"}',f'--sym={OUT/"overlay.sym"}',str(ROOT/'src/game_pixel_overlay_fast.asm')],cwd=ROOT,capture_output=True,text=True);(OUT/'overlay.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stdout+r.stderr;engine=(OUT/'overlay.bin').read_bytes();assert len(engine)<=0x980
 symbols={k:int(v,16)for k,v in __import__('re').findall(r'(\w+): EQU 0x([0-9a-f]+)',(ROOT/'build/audio/title_delta_sram.sym').read_text(),__import__('re').I)}
 text=''.join(f'{name} EQU ${symbols[name]:04X}\n'for name,label in [('DELTA_BASE_OPERAND','delta_base'),('DELTA_COLOUR_OFFSET_OPERAND','delta_colour_offset'),('DELTA_PREFIX_OPERAND','delta_prefix'),('DELTA_COLOUR_BASE_OPERAND','delta_colour_base')])+(ROOT/'src/title_delta_scratch.asm').read_text();(OUT/'title.asm').write_text(text)
 r=subprocess.run([str(asm),f'--raw={OUT/"title.bin"}',f'--sym={OUT/"title.sym"}',str(OUT/'title.asm')],cwd=ROOT,capture_output=True,text=True);assert not r.returncode,r.stdout+r.stderr;title=(OUT/'title.bin').read_bytes();assert len(title)<=400
 records=[];snake={}
 for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
  b=bytearray((source/f'{name}_region.bin').read_bytes());b[0xe400:0xed80]=bytes([255])*0x980;b[0xe400:0xe400+len(engine)]=engine
  b[0x9d10:0x9d10+len(title)]=title
  if n==1:patch_snake(b,snake)
  assert len(b)==65536;(OUT/f'{name}_region.bin').write_bytes(b);tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP';(OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{p:02X}',b[p*8192:(p+1)*8192],p)for p in range(8)));records.append(dict(file=tap,level=n,sha256=hashlib.sha256(b).hexdigest()))
 for f in ['launcher.bin','demand_loader.sym','boss_preview.bin','boss_preview.sym','gateway.bin','gateway.sym','irq.bin','irq.sym','native_level5.bin','enemy_palette.bin']:shutil.copy2(source/f,OUT/f)
 (OUT/'manifest.json').write_text(json.dumps(dict(status='r50 candidate; validation pending',regions=records,overlay_bytes=len(engine),snake=snake,movement='one-pixel fine taps; three pixels per publication after three held ticks; no extra render passes',selected_game_keys_preserved=True),indent=2));print('r50 overlay bytes',len(engine))
if __name__=='__main__':main()
