"""Export only the L1 cold double-B correction; no latest/release promotion."""
from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parents[1];W=R/'build/cartridges/integration_work/level01';O=R/'build/cartridges/r154_l1_boss_key_test';O.mkdir(exist_ok=True)
evidence={}
for name in ['live_boss_key_validation.json','controls_validation.json','repeated_fire_validation.json','walker_live_pilot.json']:
 p=W/name;j=json.loads(p.read_text());assert j['passed'];evidence[name]=hashlib.sha256(p.read_bytes()).hexdigest()
b=(W/'L1_shared_cache_internal.rom').read_bytes();assert len(b)==65536
for ext in ['rom','bin']:(O/f'rt_l1_r154_test.{ext}').write_bytes(b)
(O/'rt_l1_r154_test.dck').write_bytes(bytes([0]+[2]*8)+b)
(O/'manifest.json').write_text(json.dumps(dict(status='L1 boss-key test only; overall TAP/cartridge parity remains failing',rom_sha256=hashlib.sha256(b).hexdigest(),evidence=evidence,hardware_tested=False),indent=2))
(O/'README.txt').write_text('L1 r154 test. During gameplay press B, release, then press B again. Corrects inherited FD4B latch value blocking the shortcut after cold startup. Current L1 art/gameplay retained. Actual cold keyboard-loop test and shooting/control regressions pass. Exact64KB read-only ROM/BIN; ROM-only DCK. Not a full release or proof of complete TAP parity. Previous archives unchanged.\n')
with zipfile.ZipFile(O/'RType_L1_boss_key_r154.zip','w',zipfile.ZIP_DEFLATED)as z:
 for p in O.iterdir():
  if p.suffix!='.zip':z.write(p,p.name)
print(O/'rt_l1_r154_test.rom')
