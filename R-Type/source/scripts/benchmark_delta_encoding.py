"""Read-only TSVideoCodec comparison on consecutive completed R-Type frames."""
import sys,json,struct,subprocess
from pathlib import Path
import statistics as st
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/diagnostics/delta_benchmark'
sys.path.insert(0,str(ROOT.parents[1]/'TSVideoCodec/src/encoder'))
from svd_stream import encode_xor,decode_xor,encode_hybrid,decode_hybrid
from svd_ecm import ECMFrame

def main():
    rows=[];pairs=[]
    for index in range(150,211):
        b=(OUT/f'sample_{index}.home.bin').read_bytes();pairs.append(ECMFrame(b[0x4000:0x5800],b[0x6000:0x7800]))
    for n,(old,new) in enumerate(zip(pairs,pairs[1:])):
        payload,_=encode_xor(old,new);assert decode_xor(old,payload)==new
        (OUT/f'xor_{n:02d}.bin').write_bytes(payload)
        sparse=bytearray();changed=0
        for base,a,b in [(0x4000,old.bitmap,new.bitmap),(0x6000,old.attributes,new.attributes)]:
            records=[struct.pack('<HB',base+i,y)for i,(x,y)in enumerate(zip(a,b))if x!=y];changed+=len(records);sparse+=struct.pack('<H',len(records))+b''.join(records)
        (OUT/f'sparse_{n:02d}.bin').write_bytes(sparse)
        oldcmd=json.loads((OUT/f'sample_{150+n}.commands.json').read_text());newcmd=json.loads((OUT/f'sample_{151+n}.commands.json').read_text())
        stable=sum(a==b for a,b in zip(oldcmd,newcmd))
        dirty=set()
        for i in range(max(len(oldcmd),len(newcmd))):
            a=oldcmd[i]if i<len(oldcmd)else None;b=newcmd[i]if i<len(newcmd)else None
            if a==b:continue
            for c in [a,b]:
                if not c:continue
                # Native draw entry is top-left bounding box even for flips.
                y=c['y']if c['y']<128 else c['y']-256
                for yy in range(max(0,y),min(20,y+c['height'])):
                    for xx in range(max(1,c['x']),min(31,c['x']+c['width'])):dirty.add((xx,yy))
        row=dict(pair=n,changed_bytes=changed,xor_bytes=len(payload),sparse_bytes=len(sparse),stable_parts=stable,total_parts=len(newcmd),dirty_cells=len(dirty))
        if n in [0,20,40]:
            hybrid,_=encode_hybrid(old,new);assert decode_hybrid(old,hybrid)==new;(OUT/f'hybrid_{n:02d}.bin').write_bytes(hybrid);row['hybrid_bytes']=len(hybrid)
        rows.append(row)
    stats={k:dict(mean=st.mean(r[k]for r in rows),min=min(r[k]for r in rows),max=max(r[k]for r in rows))for k in ['changed_bytes','xor_bytes','sparse_bytes','stable_parts','total_parts','dirty_cells']}
    (OUT/'delta_metrics.json').write_text(json.dumps(dict(consecutive_pairs=60,source='r44 actual completed native game frames, boss updates150..210; no artificial frame skipping',rows=rows,summary=stats),indent=2))
    print(json.dumps(stats,indent=2))
if __name__=='__main__':main()
