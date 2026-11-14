"""Native-size L8 detail and larger motion backing window, based on r51."""
from pathlib import Path
import json,hashlib,shutil,subprocess,collections
import numpy as np
from PIL import Image,ImageEnhance,ImageDraw
from build_rocket_fix import code
from build_graphics import PALETTE
from preview_enemy_sierra import convert,decode
from build_true_black import normal
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/detail_motion_r52'
def l8(b):
 layout=json.loads((ROOT/'build/fullgame/foundation/manifest.json').read_text())['levels'][7];meta=json.loads((ROOT/'build/fullgame/converted/level08/manifest.json').read_text());descs={d['id']:d for d in layout['enemies']};descs.update({d['id']:d for d in meta['descriptors']});native=bytearray(65536);native[0xc000:]=b[0xa000:0xe000];dictionary=bytearray(b[0xe000:0xe400]);protected=set(range(16));targets=[];old={};used=[]
 for ident,d in descs.items():
  p=d['pointer']
  for cy in range(d['height']):
   for cx in range(d['width']):
    tag=native[p]
    if tag==54:p+=1;continue
    if ident not in range(42,47):protected.add(tag&127)
    p+=9
 free=[i for i in range(16,128)if i!=54 and i not in protected]
 for ident in range(42,47):
  d=descs[ident];w,h=d['width']*8,d['height']*8;source=Image.open(ROOT/f'build/fullgame/converted/level08/descriptor{ident:03d}_arcade.png').convert('RGBA').resize((w,h),Image.Resampling.LANCZOS);mask=np.asarray(source)[:,:,3]>=96;rgb=ImageEnhance.Color(source.convert('RGB')).enhance(4.5);values=np.round(255*(np.asarray(rgb,dtype=float)/255)**(1/1.8));values[~mask]=0
  preview,_,attrs=convert(source,(w,h),np.ones((h,w),bool),1.8,4.5);attrs=np.array([[normal(int(v))for v in row]for row in attrs],np.uint8);p=d['pointer'];cells=[]
  for cy in range(h//8):
   for cx in range(w//8):
    tag=native[p]
    if tag==54:p+=1;continue
    cells.append((p,cy,cx));targets.append(bytes(attrs[cy*8:cy*8+8,cx]));p+=9
  old[ident]=(values,mask,cells)
 freq=collections.Counter(targets);selected=[r for r,_ in freq.most_common(len(free))]
 for idx,row in zip(free,selected):dictionary[idx*8:idx*8+8]=row
 report=[];sheet=Image.new('RGB',(900,5*190));draw=ImageDraw.Draw(sheet);all_hist={};before_hist={}
 for ident,(values,mask,cells)in old.items():
  d=descs[ident];h,w=mask.shape;chosen=np.zeros((h,w//8),np.uint8);record=[];previous,_=decode(d,bytes(native[0xc4ce:]),b[0xe000:0xe400]);before=bytes(native)
  for p,cy,cx in cells:
   rgb=values[cy*8:cy*8+8,cx*8:cx*8+8];visible=mask[cy*8:cy*8+8,cx*8:cx*8+8];choices=[]
   for idx in range(128):
    if idx==54:continue
    a=np.frombuffer(dictionary[idx*8:idx*8+8],np.uint8);br=np.where(a&64,8,0);pi=((a>>3)&7)+br;ii=(a&7)+br
    if np.any((~visible).any(1)&(pi%8!=0)):continue
    paper=PALETTE[pi];ink=PALETTE[ii];pe=((rgb-paper[:,None])**2).sum(2);ie=((rgb-ink[:,None])**2).sum(2);choices.append((np.minimum(pe,ie).sum(),idx,a))
   _,idx,a=min(choices,key=lambda q:q[0]);chosen[cy*8:cy*8+8,cx]=a;record.append((p,cy,cx,idx))
  br=np.where(chosen&64,8,0);pcol=PALETTE[((chosen>>3)&7)+br];icol=PALETTE[(chosen&7)+br];pcol=np.repeat(pcol,8,axis=1);icol=np.repeat(icol,8,axis=1);v=icol-pcol;den=(v*v).sum(2);coverage=np.divide(((values-pcol)*v).sum(2),den,out=np.zeros((h,w)),where=den!=0);coverage=np.clip(coverage,0,1);bits=np.zeros((h,w),np.uint8)
  for y in range(h):
   direction=-1 if y&1 else 1
   for x in(range(w-1,-1,-1)if direction<0 else range(w)):
    bit=int(coverage[y,x]>=.5)if mask[y,x]else 0;bits[y,x]=bit;err=coverage[y,x]-bit
    if not mask[y,x]:continue
    for dx,dy,f in[(direction,0,.5),(-direction,1,.25),(0,1,.25)]:
     xx,yy=x+dx,y+dy
     if 0<=xx<w and yy<h and mask[yy,xx]:coverage[yy,xx]+=err*f
  for p,cy,cx,idx in record:
   native[p]=(native[p]&128)|idx;native[p+1:p+9]=np.packbits(bits[cy*8:cy*8+8,cx*8:cx*8+8],axis=1).tobytes()
  image=Image.fromarray(np.where(bits[:,:,None]!=0,icol,pcol).astype('uint8'));image.save(OUT/f'L8_{ident}.png');(OUT/f'L8_{ident}.bits').write_bytes(np.packbits(bits,axis=1).tobytes());(OUT/f'L8_{ident}.attrs').write_bytes(chosen.tobytes())
  hist=collections.Counter();prevhist=collections.Counter()
  def count_runs(bs,hist):
   for byte in bs:
    line=f'{byte:08b}';last=line[0];length=1
    for c in line[1:]:
     if c==last:length+=1
     else:hist[length]+=1;last=c;length=1
    hist[length]+=1
  nowbytes=[];oldbytes=[]
  for p,cy,cx,idx in record:nowbytes+=native[p+1:p+9];oldbytes+=before[p+1:p+9]
  count_runs(nowbytes,hist);count_runs(oldbytes,prevhist)
  report.append(dict(descriptor=ident,size=[w,h],rows=len(nowbytes),mixed_rows_before=sum(v not in(0,255)for v in oldbytes),mixed_rows_after=sum(v not in(0,255)for v in nowbytes),run_lengths_before=dict(prevhist),run_lengths_after=dict(hist)));r=ident-42;draw.text((4,r*190+4),f'L8 #{ident}: arcade / before / Sierra Lite packed',fill='white');src=Image.open(ROOT/f'build/fullgame/converted/level08/descriptor{ident:03d}_arcade.png').convert('RGB');sheet.paste(src.resize((160,160)),(4,r*190+24));sheet.paste(previous.resize((w*4,h*4)),(220,r*190+24));sheet.paste(image.resize((w*4,h*4)),(480,r*190+24))
 for idx in protected:assert dictionary[idx*8:idx*8+8]==b[0xe000+idx*8:0xe000+idx*8+8]
 b[0xa000:0xe000]=native[0xc000:];b[0x2000:0x2400]=dictionary;b[0xe000:0xe400]=dictionary;sheet.save(OUT/'l8_comparison.png');(OUT/'l8_detail.json').write_text(json.dumps(dict(protected_rows=sorted(protected),available_rows=len(free),new_palette_rows=len(selected),frames=report),indent=2))
def main():
 src=ROOT/'build/fullgame/compact_boss_r51';OUT.mkdir(exist_ok=True,parents=True);shutil.copytree(src/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True);asm=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';r=subprocess.run([str(asm),f'--raw={OUT/"overlay.bin"}',f'--sym={OUT/"overlay.sym"}',str(ROOT/'src/game_pixel_overlay_responsive.asm')],capture_output=True,text=True,cwd=ROOT);assert not r.returncode,r.stdout+r.stderr;engine=(OUT/'overlay.bin').read_bytes();assert len(engine)<=0x980;records=[]
 for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
  b=bytearray((src/f'{name}_region.bin').read_bytes());b[0xe400:0xed80]=bytes([255])*0x980;b[0xe400:0xe400+len(engine)]=engine
  if n==8:l8(b)
  (OUT/f'{name}_region.bin').write_bytes(b);tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP';(OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{p:02X}',b[p*8192:(p+1)*8192],p)for p in range(8)));records.append(dict(file=tap,level=n,sha256=hashlib.sha256(b).hexdigest()))
 for f in ['launcher.bin','demand_loader.sym','boss_preview.bin','boss_preview.sym','gateway.bin','gateway.sym','irq.bin','irq.sym']:shutil.copy2(src/f,OUT/f)
 (OUT/'manifest.json').write_text(json.dumps(dict(status='r52 validation pending',regions=records,overlay_bytes=len(engine),backing_pixel_range=[0xf100,0xf380],backing_attr_dock2_range=[0x5d00,0x5f80],damage_scratch=[0xf780,0xf802],row_table=[0xf820,0xf83a],selected_game_keys_preserved=True),indent=2));print('r52 overlay bytes',len(engine))
if __name__=='__main__':main()
