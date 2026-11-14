"""Export L1 pause/font/respawn correction; no release/latest promotion."""
from pathlib import Path
import json,hashlib,zipfile,shutil
R=Path(__file__).resolve().parents[1];W=R/'build/cartridges/integration_work/level01';O=R/'build/cartridges/r156_l1_respawn_test';O.mkdir(exist_ok=True)
b=(W/'L1_shared_cache_internal.rom').read_bytes();assert len(b)==65536
s=json.loads((W/'current_validation_summary.json').read_text());assert s['passed'] and s['rom_sha256']==hashlib.sha256(b).hexdigest()
d=json.loads((W/'death_respawn_validation.json').read_text());assert d['passed'] and d['pauseBeforeDeath'] and d['nativeFontPreserved'] and d['messageChecks']>=2
assert json.loads((W/'controls_validation.json').read_text())['nativeFontPreserved']
for ext in ['rom','bin']:(O/f'rt_l1_r156_test.{ext}').write_bytes(b)
(O/'rt_l1_r156_test.dck').write_bytes(bytes([0]+[2]*8)+b)
for name in ['current_validation_summary.json','death_respawn_validation.json','controls_validation.json','pause_ram_contract.json','respawn_message.screen.png']:shutil.copy2(W/name,O/name)
(O/'manifest.json').write_text(json.dumps(dict(status='Scoped L1 pause/font/respawn correction; overall parity blockers remain',rom_sha256=hashlib.sha256(b).hexdigest(),hardware_tested=False),indent=2))
(O/'README.txt').write_text('L1 r156: pause no longer stores screen/audio backup over the native message font. It borrows the decoded frame cache with interrupts disabled, restores the screen/audio and invalidates that cache before resuming. Real menu/pause/two-death tests check every PILOT STAND BY bitmap byte. Includes r154 double-B fix. Exact64KB ROM/BIN; ROM-only DCK. Emulator verified, hardware pending. Scoped test only, not full release/TAP parity.\n')
with zipfile.ZipFile(O/'RType_L1_respawn_fix_r156.zip','w',zipfile.ZIP_DEFLATED)as z:
 for p in O.iterdir():
  if p.suffix!='.zip':z.write(p,p.name)
with zipfile.ZipFile(O/'RType_L1_respawn_fix_r156.zip')as z:assert z.testzip()is None
print(O/'rt_l1_r156_test.rom')
