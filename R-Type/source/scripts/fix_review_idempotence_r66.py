from pathlib import Path
p=Path('scripts/refine_l2_head_review_r66.py');s=p.read_text();a=s.index("p=O/'index.html'");line=s[a:].strip();prefix="p=O/'index.html';s=p.read_text();";tail=line[len(prefix):];s=s[:a]+"p=O/'index.html';s=p.read_text()\nif '<table>' in s:\n "+tail+'\n';p.write_text(s)
