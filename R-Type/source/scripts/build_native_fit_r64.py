from pathlib import Path
import sys,json,shutil,re,subprocess,collections
import numpy as np
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from boss_motion_assets_r60 import LAYOUTS,PALETTE
from build_rocket_fix import code
OUT=R/'build/fullgame/native_fit_r64';BASE=R/'build/fullgame/l6_selected_r63'
def asm(name,text):
 p=OUT/(name+'.asm');p.write_text(text);q=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],cwd=R,capture_output=True,text=True);p.with_suffix('.log').write_text(q.stdout+q.stderr);assert q.returncode==0 and 'warning:'not in(q.stdout+q.stderr).lower(),q.stdout+q.stderr;sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)};return p.with_suffix('.bin').read_bytes(),sy
def art7():
 b=bytearray((BASE/'level07_region.bin').read_bytes());mem=bytes(0xc000)+b[0xa000:0xe000];layout=LAYOUTS[6];used=set(range(64))
 for d in layout['enemies']:
  if d['pointer']>=0xd800:continue
  p=d['pointer']
  for _ in range(d['width']*d['height']):t=mem[p];used.add(t&127);p+=1 if t==54 else 9
 for t in range(layout['terrain_tiles']):
  p=layout['terrain_start']+t*144
  used.update(mem[p+j*9]&127 for j in range(16))
 oldpool={bytes(b[0x2000+t*8:0x2008+t*8]):t for t in used if all(v<64 for v in b[0x2000+t*8:0x2008+t*8])};cells=[];priority=collections.Counter()
 for row in json.loads((R/'build/graphics/r64_native_fit/manifest.json').read_text()):
  i=row['id'];a=np.load(R/f'build/graphics/r64_native_fit/L7_{i}.npy');d=layout['enemies'][i-1];p=d['pointer']
  for cy in range(d['height']):
   for cx in range(d['width']):
    tag=mem[p]
    if tag==54:p+=1;continue
    pix=a[cy*8:cy*8+8,cx*8:cx*8+8];key=[]
    for line in pix:
     cs=sorted(set(map(int,line)));key.append(cs[0]*8+cs[-1])
    key=bytes(key);cells.append((i,p,pix,key));priority[key]+=10 if 14<=i<=22 else 1;p+=9
 free=sorted(set(range(128))-used);newkeys=[k for k,n in priority.most_common() if k not in oldpool];added={k:t for k,t in zip(newkeys,free)}
 for k,t in added.items():b[0x2000+t*8:0x2008+t*8]=k
 pool={**oldpool,**added};approximated=0;rendered={}
 for i,p,pix,key in cells:
  best=None
  for k,t in ([ (key,pool[key])] if key in pool else pool.items()):
   attrs=np.frombuffer(k,np.uint8);pp=attrs>>3;qq=attrs&7
   if any(np.any(pix[y]==0)and pp[y]!=0 and qq[y]!=0 for y in range(8)):continue
   dp=((PALETTE[pix]-PALETTE[pp][:,None,:])**2).sum(2);dq=((PALETTE[pix]-PALETTE[qq][:,None,:])**2).sum(2);bits=dq<dp;arr=np.where(bits,qq[:,None],pp[:,None]);bad=(pix!=0)&(arr==0);bits[bad]=np.broadcast_to(qq[:,None]!=0,pix.shape)[bad];arr=np.where(bits,qq[:,None],pp[:,None]);score=((PALETTE[arr]-PALETTE[pix])**2).sum()
   if best is None or score<best[0]:best=(score,k,t,bits,arr)
  assert best is not None
  _,k,t,bits,arr=best;at=p-0x2000;b[at]=t;b[at+1:at+9]=np.packbits(bits,axis=1).tobytes();approximated+=int(k!=key)
  if i not in rendered:rendered[i]=np.zeros((layout['enemies'][i-1]['height']*8,layout['enemies'][i-1]['width']*8),np.uint8)
  # Locate native cell index through its unchanged stream position.
  d=layout['enemies'][i-1];pos=d['pointer'];idx=0
  while pos<p:pos+=1 if mem[pos]==54 else 9;idx+=1
  cy,cx=divmod(idx,d['width']);rendered[i][cy*8:cy*8+8,cx*8:cx*8+8]=arr
 from PIL import Image,ImageDraw
 image=Image.new('RGB',(800,150*((len(rendered)+3)//4)),(18,18,18));draw=ImageDraw.Draw(image)
 from boss_motion_assets_r60 import decode
 for j,(i,a)in enumerate(rendered.items()):
  np.save(OUT/f'L7_sprite{i}.npy',a);old=decode(7,i)[0];x=j%4*200;y=j//4*150;draw.text((x+3,y+3),f'#{i} old / installed',fill='white')
  for dx,im in [(3,old),(100,a)]:image.paste(Image.fromarray(PALETTE[im].astype('uint8')).resize((im.shape[1]*3,im.shape[0]*3),Image.Resampling.NEAREST),(x+dx,y+24))
 image.save(OUT/'L7_installed_comparison.png')
 (OUT/'l7_art_manifest.json').write_text(json.dumps({'native_geometry_preserved':True,'native_animation_preserved':True,'ids':list(rendered),'new_palette_rows':len(added),'available_rows':len(free),'approximate_cells':approximated,'cells':len(cells),'art_scope':'Native art with ECM material shading;18..22 accepted arcade-derived heads at native24x24; no unverified arcade walker replacement'},indent=2));return b

def main():
 import build_l6_selected_r63 as l6
 l6.OUT=OUT
 for i in range(140,146):l6.ART[i]=R/f'build/graphics/r64_native_fit/L6_{i}.npy'
 l6.main()
 shutil.copy2(BASE/'selected_art.json',OUT/'r63_selected_art_reference.json')
 (OUT/'level07_region.bin').write_bytes(art7())
 # Reassemble title-aware helpers without changing their bank/stack budgets.
 import build_preload_helpers_r62 as helper
 ns=dict(vars(helper));src=(R/'scripts/build_preload_helpers_r62.py').read_text().replace('level_hotkeys_r62.asm','level_hotkeys_r64.asm').replace('preload_snapshot_r62.asm','preload_snapshot_r64.asm');exec(compile(src,'r64_helpers','exec'),ns)
 sy={k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',(OUT/'demand_loader.sym').read_text(),re.I)}
 hot,hs,driver,restore=ns['build'](OUT,asm,(OUT/'demand_loader.bin').stat().st_size,sy['preload_entry']);home,hsy,_,_=ns['build'](OUT,asm,(OUT/'demand_loader.bin').stat().st_size,sy['preload_entry'],home=True);assert len(home)<=1024 and len(hot)<=1024
 defs={**sy,'PRELOAD_DRIVER_BYTES':driver,'PRELOAD_DRIVER_STATE':hs['preload_driver.state'],'RESTORE_BYTES':restore}
 worker,_=asm('preload_worker',''.join(f'{k} EQU ${v:04X}\n'for k,v in defs.items()if '.'not in k)+(R/'src/preload_worker_r61.asm').read_text());(OUT/'RTYPE/RTPRELD.TAP').write_bytes(code('RTPRELOAD',worker.ljust(8192,b'\0'),0x8000))
 engine,_=asm('projectile_clock',(R/'src/projectile_continuous_r64.asm').read_text());assert len(engine)<=640;engine=engine.ljust(640,b'\xff');(OUT/'projectile_clock.bin').write_bytes(engine)
 for name in ['boot']+[f'level{n:02d}'for n in range(1,9)]:
  p=OUT/f'{name}_region.bin';b=bytearray(p.read_bytes());b[0xf100:0xf380]=engine;assert b[0xcc2:0xcd4]==bytes.fromhex('f3 cd 00 0c fb f5 3a a2 fd b7 28 02 f1 c9 f1 c3 14 c0');b[0xcc2:0xcd7]=bytes.fromhex('cd db 00 f3 cd 00 0c fb f5 3a a2 fd b7 28 02 f1 c9 f1 c3 14 c0');b[0xcd7:0xcde]=bytes.fromhex('32 fb 74 32 a3 fd c9')
  if name=='boot':
   assert b[0xa042:0xa045]==bytes.fromhex('cd d4 0c');b[0xa042:0xa045]=bytes.fromhex('cd d7 0c')
  if name=='level05':b[0xa000:0xa000+len(home)]=home
  elif name!='boot':b[0x3a00:0x3a00+len(hot)]=hot
  p.write_bytes(b)
 boot=(OUT/'boot_region.bin').read_bytes();common=bytearray(boot[0x4000:0x8000]);assert common[0x656:0x659]==bytes(3);common[0x656:0x659]=bytes.fromhex('cd db 00');core=bytes(common)+boot[0x3400:0x3fe0].ljust(3072,b'\0')+boot[0x3000:0x33b0].ljust(1024,b'\0')+boot[0xa000:0xa4ae].ljust(2048,b'\0');assert len(core)==22528;(OUT/'RTYPE/RTCORE.TAP').write_bytes(b''.join(code(f'RTCORE{k:02X}',core[k*1024:(k+1)*1024],k)for k in range(22)))
 # Boot core shares the patched native C011->title polling code in common RAM;
 # low-bank title hook lives in START payloads. RTCORE common bytes unchanged.
 for n in range(1,9):
  b=(OUT/f'level{n:02d}_region.bin').read_bytes();(OUT/'RTYPE'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)));(OUT/'RTYPE'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+s*1024:p*8192+(s+1)*1024],k)for k,(p,s)in enumerate((p,s)for p in[0,1,4,5,6,7]for s in range(8))))
 (OUT/'r64_contracts.json').write_text(json.dumps({'title_plain_L':True,'gameplay_shift_L':True,'gameplay_L_number':True,'hot_bytes':len(hot),'home_hot_bytes':len(home),'machinery_size':[16,32],'machinery_native_origin':True,'source_moving_component_only':True},indent=2));print('r64 helpers',len(hot),len(home))
if __name__=='__main__':main()
