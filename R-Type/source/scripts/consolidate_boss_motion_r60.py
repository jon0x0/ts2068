from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/boss_motion_r60'
def main():
 def read(name):return json.loads((OUT/name).read_text())
 assert read('frozen_regions.json')=={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in OUT.glob('*_region.bin')}
 mapping={'game':'boss_preview_validation.json','components':'generic_components.json','irq':'generic_irq.json','clipping':'generic_clipping.json','fx':'global_fx_validation.json','controls':'custom_controls_validation.json','charged_fire':'charged_fire_validation.json','death':'death_validation.json','title':'title_validation.json','snake':'snake_route_validation.json','failures':'failure_validation.json','rapid_fire':'rapid_fire_validation.json','l5_order':'l5_single_order_validation.json','walkers':'walker_gameplay_validation.json','restart':'cache_restart_validation.json','progression':'cache_progression_validation.json'}
 rows=[]
 for name,file in mapping.items():
  d=read(file);assert all(r['passed']for r in d)if isinstance(d,list)else d['passed'],name;rows.append(dict(case=name,passed=True,evidence=file))
 profile=ROOT/'build/diagnostics/boss_motion_r60/masked_L5.json';d=json.loads(profile.read_text());assert d['shots']==8 and d['beams']==1 and d['ticks']>0 and d['projectilePhases']>0;rows.insert(5,dict(case='profile',passed=True,evidence=str(profile.relative_to(ROOT))))
 assert len(read('boss_preview_validation.json')['results'])==8
 assert read('generic_components.json')['cases']==2084
 assert read('generic_irq.json')['irqCount']==200
 assert read('generic_clipping.json')['cases']==1164
 assert len(read('global_fx_validation.json')['reports'])==8
 assert len(read('cache_restart_validation.json'))==7
 assert read('cache_progression_validation.json')['all8_revisited_without_disk']
 assert len(read('walker_gameplay_validation.json')['large_poses'])==4
 (OUT/'final_checks.json').write_text(json.dumps(rows,indent=2));print('CONSOLIDATED',len(rows),'checks from individual actual test reports')
if __name__=='__main__':main()
