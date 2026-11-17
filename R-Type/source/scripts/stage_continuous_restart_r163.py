from pathlib import Path
import shutil,json,hashlib,zipfile,subprocess,sys
R=Path.cwd();H=R/'build/publication_r161_hub';P=H/'R-Type';W=P/'play';D=P/'downloads';C=R/'build/cartridges/r163';assert C.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
core={p.relative_to(W).as_posix():sha(p)for p in(W/'tsrun').rglob('*')if p.is_file()}
for n in range(1,9):
 for ext in ['bin','dck']:shutil.copy2(C/f'level{n}/rt_l{n}_r163.{ext}',W/'assets')
shutil.copy2(C/'RType_TS2068_64K_cartridges_r163.zip',D)
for rel in ['R-Type/README.md','R-Type/index.html','R-Type/play/index.html','R-Type/play/controls.js','R-Type/play/emulator/index.html','R-Type/play/emulator/adapter.js','README.md','ts2068-cartridges/README.md']:
 p=H/rel;s=p.read_text(encoding='utf-8')
 for old,new in [('cartridges_r162','cartridges_r163'),('TSRun_r162','TSRun_r163'),('_r162.dck','_r163.dck'),('Remastered r162','Remastered r163'),('r162 is the current','r163 is the current'),('r162 cartridge edition','r163 cartridge edition'),('v=r162','v=r163'),('cartridges are r162','cartridges are r163'),('cartridges now use r162','cartridges now use r163')]:s=s.replace(old,new)
 if rel=='R-Type/README.md':s+='\n\nr163 fixes the obsolete REWIND SIDE2 prompt after game over on later-level cartridges. Resident replay is automatic through the title screen. [Details and verification](CONTINUOUS_RESTART_R163.md). Disk stays at r161.\n'
 if rel=='R-Type/index.html':s=s.replace('</body>','<p>r163 removes the obsolete tape-rewind request on later-level cartridge replay. <a href="CONTINUOUS_RESTART_R163.md">Technical notes</a>. Disk stays at r161.</p></body>')
 p.write_text(s,encoding='utf-8')
shutil.copytree(C,P/'release-evidence/r163',dirs_exist_ok=True)
for p in(P/'release-evidence/r163').glob('*.zip'):p.unlink()
shutil.copy2(R/'docs/CONTINUOUS_RESTART_R163.md',P/'CONTINUOUS_RESTART_R163.md')
A=P/'web-validation/continuous-restart-r163';A.mkdir(parents=True,exist_ok=True)
shutil.copy2(R/'build/fullgame/normal_black_r161/continuous_restart_validation.json',A/'tap_restart.json')
for rel in ['scripts/build_stock_level_base.py','scripts/validate_stock_integration.py','scripts/release_stock_cartridges.py','scripts/verify_stock_continuous_restart.mjs','scripts/verify_tap_continuous_restart_r163.mjs','scripts/verify_continuous_browser_r163.mjs','scripts/stage_continuous_restart_r163.py','docs/CONTINUOUS_RESTART_R163.md','docs/STOCK_CARTRIDGES.md','docs/CURRENT_RELEASE.md','PROJECT_STATE.md','TEST_HISTORY.md']:
 p=P/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/rel,p)
for rel in ['index.html','controls.js','emulator/adapter.js']:shutil.copy2(W/rel,P/'source/web'/rel)
(P/'source/README.md').write_text((P/'README.md').read_text(encoding='utf-8')+'\nSnapshot:2026-11-16, cartridge/browser163; disk161.\n',encoding='utf-8')
subprocess.run([sys.executable,'scripts/build_site.py'],cwd=H,check=True)
with zipfile.ZipFile(D/'RType_TS2068_TSRun_r163.zip','w',zipfile.ZIP_DEFLATED)as z:
 for p in sorted(W.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(P))
 z.writestr('README.md',(P/'README.md').read_bytes())
assert core=={p.relative_to(W).as_posix():sha(p)for p in(W/'tsrun').rglob('*')if p.is_file()}
checks={p.relative_to(P).as_posix():sha(p)for p in P.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt'};(P/'SHA256SUMS.txt').write_text(''.join(f'{v}  {k}\n'for k,v in sorted(checks.items())),encoding='utf-8')
print('Staged r163 cartridge/browser only; TAP161 and emulator core unchanged')
