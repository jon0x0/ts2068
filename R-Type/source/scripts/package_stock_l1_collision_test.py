"""Package the existing corrected L1 ROM after scoped collision verification."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1];W=R/'build/cartridges/integration_work';O=R/'build/cartridges/r152_l1_collision_test';O.mkdir(exist_ok=True)
checks=[]
for n in range(1,9):
 d=W/f'level{n:02d}'
 for name in ['actor_ownership_validation.json','visible_collision_validation.json']:
  q=json.loads((d/name).read_text());assert q['passed'] and q['romWrites']==0
  checks.append(dict(level=n,evidence=name,sha256=hashlib.sha256((d/name).read_bytes()).hexdigest(),cases=q.get('cases')))
for name in ['walker_live_cells_validation.json','walker_live_pilot.json','walker_charged_pilot.json','tap_walker_live_pilot.json','tap_walker_charged_pilot.json']:
 q=json.loads((W/'level01'/name).read_text());assert q['passed']
 if 'hits'in q:assert q['hits']==8 and q['dead'] and not q['enemyHealthEdited']
 checks.append(dict(level=1,evidence=name,sha256=hashlib.sha256((W/'level01'/name).read_bytes()).hexdigest()))
b=(W/'level01/L1_shared_cache_internal.rom').read_bytes();assert len(b)==65536
for ext in ['rom','bin']:(O/f'rt_l1_r152_test.{ext}').write_bytes(b)
(O/'rt_l1_r152_test.dck').write_bytes(bytes([0]+[2]*8)+b)
(O/'test_manifest.json').write_text(json.dumps(dict(status='Targeted L1 hardware test, not full release',rom_sha256=hashlib.sha256(b).hexdigest(),checks=checks,new_runtime_changes=False,includes='Prior normal-shot gateway, TAP scheduling, old-ship mask and title enemy-header fixes',scope='L1 moving last walker after boss shortcut; all8 shared actor ownership and displayed-frame normal-shot damage controls; not every boss vulnerability or hardware timing'),indent=2))
(O/'README.txt').write_text('L1 r152 collision-verified test. Same corrected current L1 runtime, no new enemy-health or armor edits. Includes prior normal-shot gateway, IRQ/input, ghost-mask and title event-pointer fixes. Actual menu-start then boss shortcut: last walker takes eight native damage hits with normal or held-fire pilots; death animation flag set. Native missiles damage captured walker in both directions. All8 actor ownership/damage controls pass. Pilot protects player only; no enemy HP edits/no native death bypass. Hardware confirmation, all boss weak points and remaining audio/performance reports not covered. This is not a full release.\n')
print(O/'rt_l1_r152_test.rom')
