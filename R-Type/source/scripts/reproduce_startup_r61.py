from pathlib import Path
import hashlib,json
import build_responsive_startup_r61 as b
ROOT=b.ROOT;original=b.OUT;b.OUT=ROOT/'build/fullgame/startup_r61_repro';b.main()
files=list(original.glob('*.bin'))
# Compare generated build products only, excluding emulated RAM captures.
files=[p for p in files if not any(t in p.name for t in ['.home.','.dock','failed','actual','expected','handoff','bad_']) and not p.name.startswith(('preload_before','preload_resumed'))]
files+=list((original/'RTYPE').glob('*.TAP'))
rows=[]
for p in files:
 q=b.OUT/p.relative_to(original)
 if not q.exists():continue
 assert p.read_bytes()==q.read_bytes(),str(p);rows.append(str(p.relative_to(original)))
assert len(rows)>30
(original/'reproducibility_r61.json').write_text(json.dumps({'passed':True,'matching':rows},indent=2));print('Identical',len(rows),'build products')
