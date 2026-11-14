"""Build and verify the current stable release; do not invoke historical trial builders."""
from pathlib import Path
import subprocess,sys,shutil
root=Path(__file__).resolve().parents[1]
node=shutil.which('node')or str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')
for cmd in [[sys.executable,'scripts/build_release_r100.py'],[node,'--max-old-space-size=128','--max-semi-space-size=4','scripts/verify_selected_startup_r100.mjs'],[node,'--max-old-space-size=128','--max-semi-space-size=4','scripts/verify_cold_fire_r100.mjs'],[sys.executable,'scripts/finalize_release_r100.py']]:
 subprocess.run(cmd,cwd=root,check=True)
