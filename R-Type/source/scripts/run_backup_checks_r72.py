from pathlib import Path
import subprocess,os,json
O=Path('build/fullgame/reviewed_r72');node='C:/Users/Jon/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe';rows=[r for r in json.loads((O/'r72_backup_checks.json').read_text())if r['passed']]if(O/'r72_backup_checks.json').exists()else[]
for name,script,env in [('jumps4','verify_level_jumps_r72.mjs',{}),('preload6','verify_preload_title_r72.mjs',{'TEST_LEVEL':'6'}),('death6','verify_death6_r72.mjs',{})]:
 if any(r['case']==name for r in rows):continue
 p=subprocess.run([node,'--max-old-space-size=128','--max-semi-space-size=4','scripts/'+script],env={**os.environ,**env},capture_output=True,text=True);(O/f'check_{name}.log').write_text(p.stdout+p.stderr);rows.append({'case':name,'passed':p.returncode==0});(O/'r72_backup_checks.json').write_text(json.dumps(rows,indent=2));print(name,p.returncode,(p.stdout+p.stderr)[-450:],flush=True);assert p.returncode==0
