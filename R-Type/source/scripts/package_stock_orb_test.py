"""Export scoped L4 destructible-chain erasure fix; no latest promotion."""
from pathlib import Path
import json,hashlib,zipfile,shutil
R=Path(__file__).resolve().parents[1];W=R/'build/cartridges/integration_work/level04';O=R/'build/cartridges/r155_l4_orb_test';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=(W/'L4_shared_cache_internal.rom').read_bytes();assert len(b)==65536
summary=json.loads((W/'current_validation_summary.json').read_text());assert summary['passed'] and summary['rom_sha256']==hashlib.sha256(b).hexdigest()
for name in ['orb_erase_validation.json','actor_ownership_validation.json','live_boss_key_validation.json']:
 assert json.loads((W/name).read_text())['passed']
assert not json.loads((W/'orb_erase_baseline_validation.json').read_text())['passed']
for ext in ['rom','bin']:(O/f'rt_l4_r155_test.{ext}').write_bytes(b)
(O/'rt_l4_r155_test.dck').write_bytes(bytes([0]+[2]*8)+b)
for name in ['orb_erase_validation.json','orb_erase_baseline_validation.json','orb_erased.screen.png','current_validation_summary.json']:shutil.copy2(W/name,O/name)
(O/'manifest.json').write_text(json.dumps(dict(status='Scoped L4 chain-erasure test; not full release',rom_sha256=hashlib.sha256(b).hexdigest(),summary_sha256=sha(W/'current_validation_summary.json'),hardware_tested=False),indent=2))
(O/'README.txt').write_text('L4 r155. Preserves opaque blank cells in destructible chain grow/erase frames64..95. Original r153 cleared collision markers but left visible ring pixels. Native removal and ordinary bolt damage now erase both. Includes double-B cold latch fix. Existing visible art retained. Exact64KB read-only ROM/BIN; ROM-only DCK. Scoped emulator acceptance only; overall TAP/cartridge parity issues remain open. No stable/latest promotion.\n')
with zipfile.ZipFile(O/'RType_L4_orb_fix_r155.zip','w',zipfile.ZIP_DEFLATED)as z:
 for p in O.iterdir():
  if p.suffix!='.zip':z.write(p,p.name)
with zipfile.ZipFile(O/'RType_L4_orb_fix_r155.zip')as z:assert z.testzip()is None
print(O/'rt_l4_r155_test.rom')
