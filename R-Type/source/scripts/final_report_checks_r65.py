from pathlib import Path
p=Path('scripts/finalize_ui_r65.py');s=p.read_text().replace("'tests':json.loads((O/'r65_checks.json').read_text())", "'tests':json.loads((O/'r65_checks.json').read_text())+json.loads((O/'r65_extra_checks.json').read_text())");p.write_text(s)
