# Compatibility entry: the earlier static-bank6 experiment was rejected.
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name('build_l2_final_r125.py')),run_name='__main__')
