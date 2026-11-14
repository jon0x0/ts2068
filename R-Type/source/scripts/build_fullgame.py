"""Reproduce the all-level candidate from existing audited source/capture assets."""
from pathlib import Path
import subprocess,sys,os
ROOT=Path(__file__).resolve().parents[1]
def main():
 os.environ.setdefault('RTYPE_TITLE_DELTA','1');os.environ.setdefault('RTYPE_LEVEL_SELECT','1')
 node=Path(os.environ.get('RTYPE_NODE',str(Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')))
 scripts=['prepare_arcade_bosses.py','build_all_music_grammars.py','build_all_ecm_levels.py','verify_all_ecm_levels.mjs','build_fullgame_image.py','build_fullgame_package.py','verify_fullgame_bosses.mjs','verify_retained_palette.mjs','verify_fullgame_music.mjs','verify_fullgame_controls.mjs','verify_fullgame_gateway.mjs','verify_fullgame_progression.mjs','verify_fullgame_ending.mjs','verify_fullgame_preloader.mjs','publish_fullgame.py']
 if os.environ.get('RTYPE_LEVEL_SELECT')=='1':scripts[-1:-1]=['verify_level_select.mjs','verify_level_select_keyboard.mjs','verify_selector_bosses.mjs','verify_selector_pages.mjs']
 if os.environ.get('RTYPE_TITLE_DELTA')=='1':scripts.insert(-1,'verify_title_delta.mjs')
 for script in scripts:
  env=os.environ.copy()
  if script=='verify_title_delta.mjs':env['RTYPE_TITLE_FULL']='1'
  print('Running',script,flush=True);subprocess.run([str(node)if script.endswith('.mjs')else sys.executable,str(ROOT/'scripts'/script)],cwd=ROOT,env=env,check=True)
 # Keep ordinary builds and accepted level-one files reproducible.
 env=os.environ.copy();env.pop('RTYPE_TITLE_DELTA',None)
 subprocess.run([sys.executable,str(ROOT/'scripts/build_ecm_native.py')],cwd=ROOT,env=env,check=True)
if __name__=='__main__':main()
