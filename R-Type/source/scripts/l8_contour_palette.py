"""Plan reusable L8 contour palettes; asset proof, not a playable ROM patch."""
import json, hashlib
import numpy as np
from PIL import Image

def build(root, out, original, mem=None):
    d=json.loads((root/'build/fullgame/foundation/manifest.json').read_text())['levels'][7]
    mem=mem if mem is not None else bytes(16384)+(root/'build/native/snapshot.bin').read_bytes()
    w=mem[d['map_start']:d['map_end']]; n=len(original)//144
    tiles=np.zeros((n,32,32),dtype=np.uint8)
    for t in range(n):
        for cy in range(4):
            for cx in range(4):
                p=t*144+(cy*4+cx)*9
                tiles[t,cy*8:cy*8+8,cx*8:cx*8+8]=np.unpackbits(np.frombuffer(original[p+1:p+9],dtype=np.uint8)).reshape(8,8)
    world=np.zeros((160,len(w)//5*32),dtype=np.uint8)
    keys=np.zeros(world.shape,dtype=np.int32)
    local=np.arange(n*128).reshape(n,32,4).repeat(8,axis=2)
    for c in range(len(w)//5):
        for r in range(5):
            code=w[c*5+r]; t=code&63; im=tiles[t]; k=local[t]
            if code&64: im=im[:,::-1]; k=k[:,::-1]
            if code&128: im=im[::-1]; k=k[::-1]
            world[r*32:r*32+32,c*32:c*32+32]=im
            keys[r*32:r*32+32,c*32:c*32+32]=k
    parent=list(range(n*128))
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]]; x=parent[x]
        return x
    gaps=[]
    for y in range(160):
        xs=np.flatnonzero(world[y]); a,b=xs[:-1],xs[1:]
        for left,right in zip(a,b):
            if right-left<=8:
                ka,kb=int(keys[y,left]),int(keys[y,right]);parent[find(ka)]=find(kb)
            elif right-left-1>=8:
                gaps.append(dict(y=y,left=int(left),right=int(right),blank_pixels=int(right-left-1)))
    # Consistent ramps along each curve; several independently shaded material
    # arrangements within the existing gold/amethyst level family.
    ramps=((7,7,6,6,2,2,6,7),(7,7,3,3,1,1,3,7))
    groups={}
    for y,x in zip(*np.nonzero(world)):
        k=int(keys[y,x]);g=find(k); v=groups.setdefault(g,[0,0,0]);v[0]+=int(x);v[1]+=int(y);v[2]+=1
    colours={}
    for g,(sx,sy,count) in groups.items():
        # Local source scanline preserves flipped geometry; component X picks
        # a stable material, never screen coordinates or a frame counter.
        source_y=(g//4)%32; material=((sx//count)//32)%2
        colours[g]=64|ramps[material][(source_y//2)%8]
    rows=[]; cellrows={}
    for t in range(n):
        for cy in range(4):
            for cx in range(4):
                p=t*144+(cy*4+cx)*9
                if not original[p]&128: continue
                row=bytes(colours.get(find(int(local[t,cy*8+i,cx*8])),71) for i in range(8))
                cellrows[p]=row
                for v in (row,row[::-1]):
                    if v not in rows: rows.append(v)
    folder=root/'build/fullgame/converted/level08'
    used=json.loads((folder/'manifest.json').read_text())['palette_rows']
    assert used+len(rows)<=128,(used,len(rows),'candidate dictionary capacity')
    palette=bytearray((folder/'enemy_palette.bin').read_bytes())
    for i,row in enumerate(rows):
        ident=used+i;palette[ident*8:ident*8+8]=row
    # Verify every gap decision against all eight possible byte alignments.
    planned=np.zeros(world.shape,dtype=np.uint8)
    for y,x in zip(*np.nonzero(world)):planned[y,x]=colours[find(int(keys[y,x]))]
    conflicts=0
    for phase in range(8):
        for y in range(160):
            for x in range(-phase,world.shape[1],8):
                vals=planned[y,max(0,x):x+8];vals=vals[vals!=0]
                conflicts+=len(set(vals))>1
    assert conflicts==0,conflicts
    (out/'terrain_contour_dictionary.bin').write_bytes(palette)
    from build_graphics import PALETTE
    rgb=PALETTE[((planned&7)+((planned&64)>0)*8)].astype(np.uint8);rgb[world==0]=0
    Image.fromarray(rgb[:,:256]).resize((1024,640),Image.Resampling.NEAREST).save(out/'level8_contour_plan.png')
    np.save(out/'level8_contour_world.npy',planned)
    report=dict(level=8,status='Offline asset proof only; no playable cartridge generated',rule='Union source scanline colours whenever foreground pixels can share an8x1 cell at any scroll phase; a full8-pixel blank permits independent colours. Repeated/flipped source instances are constrained together.',gaps=gaps,palette_rows_added=len(rows),enemy_rows_preserved=used,all_phase_conflicts=conflicts,geometry_unchanged=True,dictionary_sha256=hashlib.sha256(palette).hexdigest(),cell_palette_rows={str(p):used+rows.index(row)for p,row in cellrows.items()},remaining='Integrate terrain-specific dictionary source IDs, reverse lookup and retained token publication; source solid bit must remain set. Verify real scrolling and actor restoration before publishing a DCK.')
    (out/'level8_contour_plan.json').write_text(json.dumps(report,indent=2))
    return report

if __name__=='__main__':
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    source=root/'build/fullgame/level08';out=root/'build/diagnostics/l8_contours';out.mkdir(parents=True,exist_ok=True)
    report=build(root,out,(source/'terrain_patches.bin').read_bytes(),bytes(16384)+(source/'snapshot.bin').read_bytes())
    print(json.dumps({k:report[k]for k in ('status','palette_rows_added','enemy_rows_preserved','all_phase_conflicts')}))
