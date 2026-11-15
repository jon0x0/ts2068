from pathlib import Path
import shutil,json,hashlib,zipfile,subprocess,sys
R=Path.cwd();H=R/'build/publication_r161_hub';P=H/'R-Type';W=P/'play';D=P/'downloads';C=R/'build/cartridges/r162';O=R/'build/player_paper_r162';assert C.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
core={p.relative_to(W).as_posix():sha(p)for p in(W/'tsrun').rglob('*')if p.is_file()}
for n in range(1,9):
 for ext in ['bin','dck']:shutil.copy2(C/f'level{n}/rt_l{n}_r162.{ext}',W/'assets')
shutil.copy2(C/'RType_TS2068_64K_cartridges_r162.zip',D)
for rel in ['R-Type/README.md','R-Type/index.html','R-Type/play/index.html','R-Type/play/controls.js','R-Type/play/emulator/index.html','R-Type/play/emulator/adapter.js','README.md','ts2068-cartridges/README.md']:
 p=H/rel;s=p.read_text(encoding='utf-8')
 # Disk remains161. Only cartridge/offline-browser assets advance162.
 s=s.replace('cartridges_r161','cartridges_r162').replace('TSRun_r161','TSRun_r162').replace('_r161.dck','_r162.dck').replace('Remastered r161','Remastered r162').replace('edition. All eight','edition. All eight').replace('r161 is the current eight-cartridge release','r162 is the current eight-cartridge release').replace('r161 cartridge edition','r162 cartridge edition').replace('v=r161','v=r162')
 s=s.replace('Both the disk and individual cartridge editions now carry the r161 normal-black fixes.','The disk stays at r161. Browser/individual cartridges are r162, including the cleared-cell paper fix.').replace('Browser and individual cartridges also use r161.','Browser and individual cartridges now use r162; the disk stays at r161.')
 if rel.endswith('adapter.js'):s=s.replace('}_r161.dck','}_r162.dck')
 if rel=='R-Type/README.md':s+='\n\nr162 fixes stale coloured blocks beside the moving/firing ship. [Cause and verification](CLEARED_CELLS_R162.md). Disk archive unchanged at r161.\n'
 if rel=='R-Type/index.html':s=s.replace('</body>','<p>r162 fixes stale coloured blocks beside the moving/firing player. <a href="CLEARED_CELLS_R162.md">Technical notes</a>. Disk stays at r161.</p></body>')
 p.write_text(s,encoding='utf-8')
shutil.copytree(C,P/'release-evidence/r162',dirs_exist_ok=True)
for p in(P/'release-evidence/r162').glob('*.zip'):p.unlink()
shutil.copy2(R/'docs/CLEARED_CELLS_R162.md',P/'CLEARED_CELLS_R162.md')
A=P/'web-validation/player-clear-r162';A.mkdir(parents=True,exist_ok=True)
for name in ['before_after.png','natural_validation.json','restore_validation.json']:shutil.copy2(O/name,A/name)
files=['scripts/build_stock_shared_cache.py','scripts/validate_stock_integration.py','scripts/release_stock_cartridges.py','scripts/verify_player_clear_r162.mjs','scripts/verify_player_natural_r162.mjs','scripts/stage_player_clear_r162.py','src/stock_clear_dispatch.asm','docs/CLEARED_CELLS_R162.md','docs/STOCK_CARTRIDGES.md','docs/CURRENT_RELEASE.md','PROJECT_STATE.md','TEST_HISTORY.md']
for rel in files:
 p=P/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/rel,p)
for rel in ['index.html','controls.js','emulator/adapter.js']:shutil.copy2(W/rel,P/'source/web'/rel)
(P/'source/README.md').write_text((P/'README.md').read_text(encoding='utf-8')+'\nSnapshot:2026-11-15, cartridge/browser162; disk161.\n',encoding='utf-8')
subprocess.run([sys.executable,'scripts/build_site.py'],cwd=H,check=True)
with zipfile.ZipFile(D/'RType_TS2068_TSRun_r162.zip','w',zipfile.ZIP_DEFLATED)as z:
 for p in sorted(W.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(P))
 z.writestr('README.md',(P/'README.md').read_bytes())
assert core=={p.relative_to(W).as_posix():sha(p)for p in(W/'tsrun').rglob('*')if p.is_file()}
checks={p.relative_to(P).as_posix():sha(p)for p in P.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt'};(P/'SHA256SUMS.txt').write_text(''.join(f'{v}  {k}\n'for k,v in sorted(checks.items())),encoding='utf-8')
print('Staged r162 cartridge/browser only; TAP161 and emulator core unchanged')
