from pathlib import Path
import json,shutil
R=Path.cwd();O=R/'build/graphics/walker_selection_r89';m=json.loads((O/'inputs.json').read_text())
for a in m['assets']:
 if a['key']not in['small','raise0','raise1']:continue
 k=a['frame']if a['key']=='small'else 4+int(a['key'][-1]);src=f'new_B_{k}';variant=next(v for v in json.loads((O/'replacement_variants.json').read_text())if v['id']=='B');p=variant['profiles'][k];assert [p['w'],p['h']]==a['size']
 for ext in['bits','attrs','rgb']:shutil.copy2(O/f'{src}.{ext}',O/f'{a["name"]}.{ext}')
 a['selection']='New replacement B, native footprint'
(O/'inputs.json').write_text(json.dumps(m,indent=2))
(O/'integration_choices.json').write_text(json.dumps(dict(head32='B exact52/59/82/0.87',large40='C exact51/67/80/1.44',round3='keep exact earlier baseline,3unique in4step loop',new_small='B new reference-inspired redraw atnative32x24/raised24x24',unreviewed='unchangedr86',accepted_yellow_exhaust='byte-identicalr86'),indent=2))
s=(R/'scripts/build_walker_restore_r87.py').read_text().replace('walker_restore_r87','walker_selection_r89').replace('_r87','_r89').replace('pack_optimal_r89','pack_optimal_r87');(R/'scripts/build_walker_selection_r89.py').write_text(s)
s=(R/'scripts/finish_player_flame_r87.py').read_text().replace('walker_restore_r87','walker_selection_r89').replace('_r87','_r89');(R/'scripts/finish_player_flame_r89.py').write_text(s)
