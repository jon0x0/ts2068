from pathlib import Path
p=Path('scripts/preview_l2_organic_sierra.py');s=p.read_text().replace("if visible.all() and np.mean(cell@np.array([.21,.72,.07]))>90:candidates=[v for v in candidates if v[0]!=0]", "if visible.all() and np.mean(cell@np.array([.21,.72,.07]))>90 and (not vector or is_flesh):candidates=[v for v in candidates if v[0]!=0]")
s=s.replace('if 0<=xx<W and yy<H and mask[yy,xx]:','if 0<=xx<W and yy<H and mask[yy,xx] and (not vector or flesh[yy,xx]==flesh[y,x]):')
p.write_text(s)
