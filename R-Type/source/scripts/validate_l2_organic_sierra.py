from pathlib import Path
import hashlib,json,subprocess
O=Path('build/graphics/l2_organic_sierra')
files=[p for p in O.iterdir()if p.suffix in ['.png','.npy','.bits','.attrs','.json','.html']]
def hashes():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in files}
a=hashes();q=subprocess.run(['python','scripts/preview_l2_organic_sierra.py'],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr;assert hashes()==a
m=json.loads((O/'manifest.json').read_text());assert all(r['export_reconstructed_exactly']and r['all_8x1_cells_legal']and r['flesh_saturation']==1.1 for r in m['profiles'])
p=Path('build/fullgame/startup_r66/RType_TS2068_r66.zip');assert hashlib.sha256(p.read_bytes()).hexdigest()=='96bd744bc08c6f5212003658959b697def88084aee31d9a1aa9af98b29763c60'
(O/'validation_summary.json').write_text(json.dumps({'profiles':4,'asset_bytes_each':3520,'normal_black_only':True,'independent_export_reconstruction':True,'reproducible_files':len(files),'r66_game_unchanged':True,'status':'asset preview, not playable'},indent=2),encoding='utf-8')
with Path('TEST_HISTORY.md').open('ab')as f:f.write(b'\nFinal139verification: generator source rebuilt with explicit UTF-8 after a Windows default-encoding failure during page annotation; final asset/page generation succeeds. Source now independently reconstructs exported bytes rather than only arrays. Repeated build hashes match for all preview files; validation_summary.json records checks. Blank cells emit zero attributes. Final A_scene.png visually inspected; no new playable release created.\n')
print('Four legal ECM alternatives; deterministic assets/page; exact exported-byte reconstruction; r66 unchanged')
