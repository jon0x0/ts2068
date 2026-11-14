"""Pack selected 96x96 level-five core into the r42 disk candidate."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from build_rocket_fix import code
from build_true_black import normal
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/selected_art_r43'

def main():
    source=ROOT/'build/fullgame/boss_preview_r42';OUT.mkdir(parents=True,exist_ok=True)
    shutil.copytree(source/'RTYPE',OUT/'RTYPE',dirs_exist_ok=True)
    for file in ['launcher.bin','demand_loader.sym','boss_preview.bin','boss_preview.sym']:
        shutil.copy2(source/file,OUT/file)
    meta=json.loads((ROOT/'build/fullgame/converted/level05/manifest.json').read_text());foundation=json.loads((ROOT/'build/fullgame/foundation/manifest.json').read_text())['levels'][4]
    descs={d['id']:dict(d)for d in foundation['enemies']};descs.update({d['id']:dict(d)for d in meta['descriptors']})
    region=bytearray((source/'level05_region.bin').read_bytes())
    # Native C000..FFFF lives in cold source DOCK5/6 at A000..DFFF.
    native=bytearray(65536);native[0xc000:]=region[0xa000:0xe000]
    dictionary=bytes(region[0x2000:0x2400]);rows=[dictionary[i*8:i*8+8]for i in range(16)];ids=list(range(16))
    def row_id(row):
        if row in rows:return ids[rows.index(row)]
        ident=next(i for i in range(128)if i!=54 and i not in ids)
        rows.append(row);ids.append(ident);return ident
    patches={}
    for ident,d in descs.items():
        if ident==8:continue
        p=d['pointer']
        for y in range(d['height']):
            for x in range(d['width']):
                a=native[p]
                if a==54:p+=1;continue
                row=dictionary[(a&127)*8:(a&127)*8+8]
                patches[p]=(a&128)|row_id(row);p+=9
    trial=ROOT/'build/graphics/level5_material_trials'
    bits=np.unpackbits(np.frombuffer((trial/'cel008_1.5_option2.bits').read_bytes(),dtype=np.uint8)).reshape(96,96)
    attrs=np.frombuffer((trial/'cel008_1.5_option2.attrs').read_bytes(),dtype=np.uint8).reshape(96,12)
    start=meta['pool_end'];payload=bytearray()
    for cy in range(12):
        for cx in range(12):
            tile=bits[cy*8:cy*8+8,cx*8:cx*8+8]
            row=bytes(normal(int(v))for v in attrs[cy*8:cy*8+8,cx])
            if not tile.any()and all(v&56==0 for v in row):payload.append(54);continue
            payload.append(row_id(row));payload+=np.packbits(tile,axis=1).tobytes()
    end=start+len(payload);assert end<=0xf87c,(hex(end),len(payload));assert len(rows)<=127
    for p,a in patches.items():native[p]=a
    native[start:end]=payload
    descriptor=foundation['enemy_descriptors_start']+7*4
    native[descriptor:descriptor+4]=bytes([12,12])+start.to_bytes(2,'little')
    region[0xa000:0xe000]=native[0xc000:]
    newdict=bytearray(1024)
    for ident,row in zip(ids,rows):newdict[ident*8:ident*8+8]=row
    region[0x2000:0x2400]=newdict;region[0xe000:0xe400]=newdict
    old=bytes([0x11])+meta['pool_end'].to_bytes(2,'little');new=bytes([0x11])+end.to_bytes(2,'little')
    window=bytes(region[0x18d9:0x1904]);assert window.count(old)==1,window.hex();region[0x18d9:0x1904]=window.replace(old,new)
    records=[]
    for name,n in [('boot',1)]+[(f'level{i:02d}',i)for i in range(1,9)]:
        data=region if n==5 else(source/f'{name}_region.bin').read_bytes()
        (OUT/f'{name}_region.bin').write_bytes(data)
        tap='RTBOOT.TAP'if name=='boot'else f'LEVEL{n:02d}.TAP'
        (OUT/'RTYPE'/tap).write_bytes(b''.join(code(f'RTPAGE{page:02X}',data[page*8192:(page+1)*8192],page)for page in range(8)))
        records.append(dict(file=tap,level=n,sha256=hashlib.sha256(data).hexdigest()))
    (OUT/'native_level5.bin').write_bytes(native);(OUT/'enemy_palette.bin').write_bytes(newdict)
    (OUT/'manifest.json').write_text(json.dumps(dict(status='Selected artwork candidate, validation pending',regions=records,hook_bytes=len((OUT/'boss_preview.bin').read_bytes()),graphics=dict(level=5,descriptor=8,profile='source/gamma1.35 saturation1.3 HSV, SierraLite',size=[96,96],pool_start=start,pool_end=end,asset_bytes=len(payload),palette_rows=len(rows),all_other_levels_unchanged=True,animation_compositor_unchanged=True)),indent=2))
    print('core',hex(start),hex(end),'bytes',len(payload),'dictionary rows',len(rows))
if __name__=='__main__':main()
