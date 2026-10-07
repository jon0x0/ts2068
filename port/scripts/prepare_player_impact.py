"""Short source-derived GUNSHOT attack; twelve native refreshes, channel A."""
from pathlib import Path
import sys, wave, json, hashlib
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT.parents[1] / 'speech2ay'))
from tsaudio.codecs import encode

source = (ROOT / 'port/scripts/prepare_explosion_sfx.py').read_text()
fn = source[source.index('def cannon():'):source.index("if __name__")]
fn = fn.replace('freq=255<<8', 'freq=192<<8').replace('remaining=1000', 'remaining=128').replace('((freq>>8)&hi)', '(freq>>8)')
ns = {'np': np}
exec(fn, ns)
rate, pcm = ns['cannon']()
pcm = pcm[:round(rate * 12 / 60.1145)]
target = ROOT / 'assets/sfx-player-impact.wav'
with wave.open(str(target), 'wb') as w:
    w.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
    w.writeframes((pcm * 28000).astype('<i2').tobytes())
raw, count, info = encode(target, 'harmonic1')
rows = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 14)[:12].copy()
assert len(rows) == 12 and np.all(rows[:, [9, 10]] == 0)
assert np.all(rows[:, 1] < 16) and np.all(rows[:, 8] < 16)
assert np.all(rows[:, 6] < 32) and np.all(rows[:, 7] & 0x36 == 0x36)
packed = np.column_stack([rows[:, 0], rows[:, 1]*16+rows[:, 8], rows[:, 6]*4+(rows[:, 7]&1)+((rows[:, 7]&8)>>2)]).astype(np.uint8).tobytes()
target.with_suffix('.ay').write_bytes(rows.tobytes())
target.with_suffix('.packed').write_bytes(packed)
target.with_suffix('.json').write_text(json.dumps(dict(frames=12, bytes=len(packed), source='VSNDRM9 GUNSHOT: SAMPC=128, DSFLG=0, FMAX=C0; approximate reconstruction', codec='speech2ay harmonic1', delay_seconds=12/60.1145, sha256=hashlib.sha256(packed).hexdigest()), indent=2))
print(f'Player impact: {len(packed)} bytes, 12 refreshes')
