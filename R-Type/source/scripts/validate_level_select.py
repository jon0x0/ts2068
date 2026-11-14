from pathlib import Path
import subprocess,sys,os
ROOT=Path(__file__).resolve().parents[1];node=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
def main():
 env=os.environ.copy();env.update(RTYPE_TITLE_DELTA='1',RTYPE_LEVEL_SELECT='1')
 for script in ['build_fullgame_image.py','build_fullgame_package.py','verify_level_select.mjs','verify_level_select_keyboard.mjs','verify_selector_bosses.mjs','verify_selector_pages.mjs','verify_fullgame_gateway.mjs','verify_fullgame_progression.mjs','verify_fullgame_ending.mjs','verify_fullgame_preloader.mjs','verify_title_delta.mjs','publish_fullgame.py']:
  current=env.copy()
  if script=='verify_title_delta.mjs':current['RTYPE_TITLE_FULL']='1'
  print(script,flush=True)
  with (ROOT/'build/fullgame'/('r25_'+script+'.log')).open('w')as log:subprocess.run([str(node)if script.endswith('.mjs')else sys.executable,str(ROOT/'scripts'/script)],cwd=ROOT,env=current,stdout=log,stderr=subprocess.STDOUT,check=True)
if __name__=='__main__':main()
