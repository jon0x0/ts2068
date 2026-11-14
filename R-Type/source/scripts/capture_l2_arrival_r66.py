from pathlib import Path
p=Path('scripts/probe_l2_boss_r66.mjs');s=p.read_text().replace('after>=100&&after<=115','after>=10&&after<=100&&after%10===0').replace('after>=700','after>=160');p.write_text(s)
