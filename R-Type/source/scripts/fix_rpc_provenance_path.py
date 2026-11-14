from pathlib import Path
p=Path('build/graphics/l2_rpc_settings/PROVENANCE.md');s=p.read_text(encoding='utf-8');s=s.replace('../../../../../../retropixel/index.html relative to the project',str((Path.cwd()/'../../retropixel/index.html').resolve()));p.write_text(s,encoding='utf-8')
