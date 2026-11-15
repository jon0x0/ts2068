"""Publish only corrected game assets; keep the published TSRun core intact."""
from pathlib import Path
import shutil,hashlib,json,zipfile,subprocess,sys
R=Path(__file__).resolve().parents[1];H=R/'build/publication_r161_hub';P=H/'R-Type';W=P/'play';D=P/'downloads';C=R/'build/cartridges/r161';T=R/'build/fullgame/normal_black_r161';assert C.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
core={str(p.relative_to(W)):sha(p)for p in (W/'tsrun').rglob('*')if p.is_file()}
for n in range(1,9):
 for ext in ['dck','bin']:shutil.copy2(C/f'level{n}/rt_l{n}_r161.{ext}',W/'assets')
for name in ['RType_TS2068_64K_cartridges_r161.zip']:shutil.copy2(C/name,D/name)
shutil.copy2(T/'RType_TS2068_TSPico_r161.zip',D)
for q in (T/'rtype').iterdir():
 if q.is_file():shutil.copy2(q,P/'rtype'/q.name)
for rel in ['R-Type/README.md','R-Type/index.html','R-Type/play/index.html','R-Type/play/controls.js','R-Type/play/emulator/adapter.js','R-Type/play/emulator/index.html','README.md','ts2068-cartridges/README.md','scripts/build_site.py']:
 p=H/rel;s=p.read_text(encoding='utf-8').replace('r160','r161').replace('r145','r161')
 s=s.replace('This is the preserved\nr161 disk build; r161 identifies the separate individual cartridge edition.','Both the disk and individual cartridge editions now carry the r161 normal-black fixes.')
 s=s.replace('Browser/individual cartridges are the separate r161 edition.','Browser and individual cartridges also use r161.')
 if rel=='R-Type/play/index.html':s=s.replace('src="controls.js"','src="controls.js?v=r161"')
 p.write_text(s,encoding='utf-8')
for rel in ['R-Type/README.md','R-Type/index.html']:
 p=H/rel;s=p.read_text(encoding='utf-8');note='r161 fixes unintended bright black in title, score, preparation and restored backgrounds. Bright black remains a valid colour; the emulator palette is unchanged. Software verified; hardware confirmation pending.'
 s+=('\n\n'+note+'\n')if p.suffix=='.md'else''
 if p.suffix=='.html':s=s.replace('</body>', '<p>'+note+'</p></body>')
 p.write_text(s,encoding='utf-8')
(P/'downloads/TSPico_INSTALL.txt').write_text((T/'README.txt').read_text(encoding='utf-8'),encoding='utf-8')
E=P/'release-evidence/r161';shutil.copytree(C,E,dirs_exist_ok=True)
# Avoid duplicating the downloadable ZIP in the evidence tree.
for p in E.glob('*.zip'):p.unlink()
shutil.copy2(R/'docs/NORMAL_BLACK_R161.md',P/'NORMAL_BLACK_R161.md')
A=P/'web-validation/normal-black-r161';A.mkdir(parents=True,exist_ok=True)
for name in ['stock_fixed.json','tap_fixed.json','stock_before.json','tap_before.json','before_after.png']:shutil.copy2(R/'build/normal_black_audit'/name,A/name)
files=['scripts/normal_black_policy.py','scripts/build_normal_black_r161.py','scripts/finalize_normal_black_r161.py','scripts/build_stock_level_base.py','scripts/build_stock_shared_cache.py','scripts/validate_stock_integration.py','scripts/verify_stock_normal_black.mjs','scripts/verify_stock_scores.mjs','scripts/audit_normal_black_live.mjs','scripts/normal_black_audit.mjs','scripts/verify_normal_black_revisits_r161.mjs','scripts/boss_motion_fixture_r145.mjs','scripts/verify_visible_collision_r145.mjs','scripts/release_stock_cartridges.py','scripts/stage_normal_black_r161.py','scripts/render_normal_black_comparison.py','scripts/refresh_stock_paired.py','src/stock_normal_black.asm','src/title_delta_cell.inc','src/title_motion_colour.asm','src/title_screen_init.asm','docs/NORMAL_BLACK_R161.md','docs/STOCK_CARTRIDGES.md','docs/CURRENT_RELEASE.md','PROJECT_STATE.md','TEST_HISTORY.md']
for rel in files:
 p=P/'source'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/rel,p)
# Publish the clean frontend source, excluding the held emulator experiments.
for rel in ['index.html','controls.js','emulator/adapter.js']:
 p=P/'source/web'/rel;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/rel,p)
subprocess.run([sys.executable,'scripts/build_site.py'],cwd=H,check=True)
readme=(P/'README.md').read_text(encoding='utf-8')
with zipfile.ZipFile(D/'RType_TS2068_TSRun_r161.zip','w',zipfile.ZIP_DEFLATED)as z:
 for p in sorted(W.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(P))
 z.writestr('README.md',readme)
assert core=={str(p.relative_to(W)):sha(p)for p in(W/'tsrun').rglob('*')if p.is_file()},'Published emulator core changed'
for p in D.glob('*r161.zip'):
 with zipfile.ZipFile(p)as z:assert z.testzip()is None
checks={p.relative_to(P).as_posix():sha(p)for p in P.rglob('*')if p.is_file()and p.name!='SHA256SUMS.txt'}
(P/'SHA256SUMS.txt').write_text(''.join(f'{v}  {k}\n'for k,v in sorted(checks.items())),encoding='utf-8')
print('Staged normal-black r161; published TSRun core unchanged')
