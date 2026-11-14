from pathlib import Path
p=Path('scripts/prepare_l2_tiled_r67.py');s=p.read_text(encoding='utf-8');s=s.replace('bits[black]=np.broadcast_to(q[:,None]==0,block.shape)[black];','bits[black]=np.broadcast_to((q==0)&(p!=0),block.shape)[black];');p.write_text(s,encoding='utf-8')
