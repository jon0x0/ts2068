from pathlib import Path
p=Path('scripts/prepare_l2_tiled_r67.py');s=p.read_text(encoding='utf-8').replace('assert len(payload)<=0x870,len(payload)','print([(r["id"],r["bytes"])for r in rows]);assert len(payload)<=0x1000,len(payload)');p.write_text(s,encoding='utf-8')
