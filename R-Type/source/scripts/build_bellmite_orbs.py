"""Native Bellmite sphere artwork trial: arcade-size cels, solid coloured shading."""
import json,hashlib,shutil
from pathlib import Path
import numpy as np
from PIL import Image
from build_rocket_fix import code
from build_true_black import normal
from preview_level5_solid import solid
from build_graphics import PALETTE
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/bellmite_orbs_r44'

def main():
    source=ROOT/'build/fullgame/selected_art_r43';OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(source/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True)
    for file in ['launcher.bin','demand_loader.sym','boss_preview.bin','boss_preview.sym']:shutil.copy2(source/file,OUT/file)
    region=bytearray((source/'level05_region.bin').read_bytes());native=bytearray((source/'native_level5.bin').read_bytes());old_dict=bytes(region[0x2000:0x2400])
    foundation=json.loads((ROOT/'build/fullgame/foundation/manifest.json').read_text())['levels'][4];table=foundation['enemy_descriptors_start'];rows=[old_dict[i*8:i*8+8]for i in range(16)];ids=list(range(16))
    def row_id(row):
        row=bytes(normal(v)for v in row)
        if row in rows:return ids[rows.index(row)]
        index=next(i for i in range(128)if i!=54 and i not in ids);rows.append(row);ids.append(index);return index
    for ident in range(1,foundation['enemy_descriptors']+1):
        if 30<=ident<=33:continue
        d=table+(ident-1)*4;w,h=native[d:d+2];p=int.from_bytes(native[d+2:d+4],'little')
        for cy in range(h):
            for cx in range(w):
                a=native[p]
                if a==54:p+=1;continue
                native[p]=(a&128)|row_id(old_dict[(a&127)*8:(a&127)*8+8]);p+=9
    # Preserve all earlier converted components; append actual live sphere cels.
    start=0xf3f1;p=start;frames=[];prepared=[];frequency=Counter()
    for ident in [9,10,11]:
        src=Image.open(ROOT/f'build/fullgame/converted/level05/descriptor{ident:03d}_arcade.png').convert('RGBA')
        image,bits,attrs=solid(src,(32,32),(12,14),.60)
        prepared.append((ident,src,image,bits,attrs))
        for cy in range(4):
            for cx in range(4):frequency[bytes(normal(int(a))for a in attrs[cy*8:cy*8+8,cx])]+=1
    # Pin other artwork exactly. Fit the new sphere rows into remaining slots.
    for value in [34,38,39,55]:
        if len(rows)<127:row_id(bytes([value])*8)
    for row,_ in frequency.most_common():
        if len(rows)<127:row_id(row)
    for ident,src,image,bits,attrs in prepared:
        target=np.asarray(image,dtype=float);mask=np.asarray(src)[:,:,3]>=128;fitted=np.zeros((32,32,3),np.uint8);data=bytearray()
        for cy in range(4):
            for cx in range(4):
                visible=mask[cy*8:cy*8+8,cx*8:cx*8+8];rgb=target[cy*8:cy*8+8,cx*8:cx*8+8]
                if not visible.any():data.append(54);continue
                candidates=[]
                for index,row in zip(ids,rows):
                    a=np.frombuffer(row,dtype=np.uint8);br=np.where(a&64,8,0);pi=((a>>3)&7)+br;qi=(a&7)+br
                    if np.any((~visible).any(1)&(pi%8!=0)):continue
                    if visible.all()and(np.any(pi%8==0)or np.any(qi%8==0)):continue
                    paper=PALETTE[pi];ink=PALETTE[qi];pe=((rgb-paper[:,None])**2).sum(2);ie=((rgb-ink[:,None])**2).sum(2);tile=ie<pe;tile[~visible]=False
                    error=np.minimum(pe,ie)[visible].sum();candidates.append((error,index,tile,paper,ink))
                assert candidates
                _,index,tile,paper,ink=min(candidates,key=lambda v:v[0]);data.append(index);data+=np.packbits(tile,axis=1).tobytes();fitted[cy*8:cy*8+8,cx*8:cx*8+8]=np.where(tile[:,:,None],ink[:,None],paper[:,None])
        Image.fromarray(fitted).save(OUT/f'orb{ident}.png')
        native[p:p+len(data)]=data;frames.append(dict(pointer=p,bytes=len(data),source_descriptor=ident));p+=len(data)
    assert p<=0xf87c,'Orb assets overlap AY code';assert len(rows)<=127
    for ident,frame in zip(range(30,34),[0,1,2,1]):
        d=table+(ident-1)*4;native[d:d+4]=bytes([4,4])+frames[frame]['pointer'].to_bytes(2,'little')
    region[0xa000:0xe000]=native[0xc000:];dictionary=bytearray(1024)
    for index,row in zip(ids,rows):dictionary[index*8:index*8+8]=row
    region[0x2000:0x2400]=dictionary;region[0xe000:0xe400]=dictionary
    window=bytes(region[0x18d9:0x1904]);old=bytes.fromhex('11 f1 f3');assert window.count(old)==1
    region[0x18d9:0x1904]=window.replace(old,bytes([0x11])+p.to_bytes(2,'little'))
    records=[]
    for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
        data=region if n==5 else(source/f'{name}_region.bin').read_bytes();(OUT/f'{name}_region.bin').write_bytes(data)
        tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP';(OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{page:02X}',data[page*8192:(page+1)*8192],page)for page in range(8)));records.append(dict(file=tap,level=n,sha256=hashlib.sha256(data).hexdigest()))
    (OUT/'native_level5.bin').write_bytes(native);(OUT/'enemy_palette.bin').write_bytes(dictionary)
    manifest=dict(status='Bellmite sphere candidate; validation pending',regions=records,graphics=dict(level=5,descriptors=list(range(30,34)),unique_frames=frames,sphere_size=[32,32],palette_rows=len(rows),pool_end=p,core_size=[96,96],shading='Solid green/yellow/white with red nodes; no interior black dithering',native_compositor_unchanged=True))
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print(manifest['graphics'])
if __name__=='__main__':main()
