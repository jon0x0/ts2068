from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));import build_boss_motion_r60 as build
ORIGINAL=ROOT/'build/fullgame/boss_motion_r60';REBUILD=ROOT/'build/diagnostics/boss_motion_r60/rebuild'
def main():
 build.OUT=REBUILD;build.main();files=[p for p in ORIGINAL.iterdir()if p.name.endswith('_region.bin')or p.name.endswith('_motion.bin')or p.name.endswith('_cache.bin')or p.name.endswith('_compositor.bin')]
 for p in files:assert p.read_bytes()==(REBUILD/p.name).read_bytes(),p.name
 (ORIGINAL/'reproducibility.json').write_text(json.dumps(dict(passed=True,files=[p.name for p in files]),indent=2));print('REPRODUCIBLE',len(files))
if __name__=='__main__':main()
