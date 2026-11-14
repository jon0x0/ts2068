from pathlib import Path
import json,shutil
R=Path.cwd();O=R/'build/graphics/walker_choice_r90';m=json.loads((O/'inputs.json').read_text())
for a in m['assets']:
 if a['key']not in['small','raise0','raise1']:continue
 k=a['frame']if a['key']=='small'else 4+int(a['key'][-1]);src=f'new_A_{k}'
 for ext in['bits','attrs','rgb']:shutil.copy2(O/(src+'.'+ext),O/(a['name']+'.'+ext))
 a['selection']='User option A 39/70/100/1.01'
m['new_small_variant']='A';m['applied_gunwalker_review']='user_choice.json';(O/'inputs.json').write_text(json.dumps(m,indent=2))
for stem in['build_walker_selection','finish_player_flame']:
 s=(R/f'scripts/{stem}_r89.py').read_text().replace('walker_selection_r89','walker_choice_r90').replace('_r89','_r90');(R/f'scripts/{stem}_r90.py').write_text(s)
