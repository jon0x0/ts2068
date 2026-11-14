"""Hash-bound internal integration report; does not package or promote a release."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]; O=R/'build/cartridges/integration_work'; P=R/'build/cartridges/tap_comparison'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def render(p):
 b=p.read_bytes();assert len(b)==12288
 im=Image.new('RGB',(256,192)); ip=im.load()
 for y in range(192):
  for x in range(256):
   at=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)|(x>>3);a=b[6144+at];bit=b[at]&(128>>(x&7));c=(a&7)if bit else((a>>3)&7);v=255 if a&64 else 205
   ip[x,y]=(v if c&2 else 0,v if c&4 else 0,v if c&1 else 0)
 return im
rows=[]; sheet=Image.new('RGB',(1040,8*416),'#141414');d=ImageDraw.Draw(sheet)
for n in range(1,9):
 folder=O/f'level{n:02d}'; summary=json.loads((folder/'current_validation_summary.json').read_text()); rom=folder/f'L{n}_shared_cache_internal.rom';assert summary['passed'] and summary['rom_sha256']==sha(rom)
 for artifact,digest in summary['evidence'].items():assert sha(folder/artifact)==digest,('Stale component evidence',n,artifact)
 scenarios=[]
 for boss in (False,True):
  name=f'level{n:02d}'+('_boss'if boss else'')+'_seeded_candidate'+('_safe'if boss else'')+('_native_shield'if n==7 else''); scene=P/name;j=json.loads((scene/'comparison.json').read_text());assert j['inputs']['cart']==sha(folder/f'L{n}_shared_cache_internal.dck'),('Stale paired binary',n,boss)
  scenarios.append(dict(trace=name,passed=j['passed'],hash=sha(scene/'comparison.json'),native_death_bypass=j['nativeKillShieldForComparison'],matched_updates=j['matchedCameraStates'],tap_refreshes=j['tap']['framesAfterActive'],cart_refreshes=j['cart']['framesAfterActive']))
  y=(n-1)*416+int(boss)*208;d.text((4,y),f'L{n} '+('boss'if boss else'early')+' completed world update100: TAP left / stock cartridge right'+(' [both coarse-death paths bypassed]'if n==7 else''),fill='white')
  for c,k in enumerate(('tap','cart')):sheet.paste(render(scene/f'{k}_completed100.screen.bin').resize((512,192),Image.Resampling.NEAREST),(520*c,y+16))
 rows.append(dict(level=n,component_checks_passed=True,rom_sha256=sha(rom),summary_sha256=sha(folder/'current_validation_summary.json'),scenarios=scenarios,fine_boss_motion=('static native boss'if n==1 else'exact TAP fractional artwork and2-pixel motion tested')))
sheet.save(O/'current_paired_completed.png')
report=dict(levels=rows,all_component_checks_passed=True,paired_scenarios_passed=all(s['passed']for r in rows for s in r['scenarios']),publish_ready=False,stock_component_package_ready=all(s['passed']for r in rows for s in r['scenarios']),tap_equivalence_confirmed=False,hardware_confirmed=False,visual_parity_confirmed=False,remaining=['L2 native painted-body reveal and L5 overlap composition are integrated. Completed-frame comparisons retain elapsed-IRQ differences in player effects/stars and some dynamic colours; actor/event matching is not pixel equivalence.','L4 fractional artwork and 2-pixel movement pass all384 direct/retained phases, permanent-row cache/IRQ probes and the unchanged240-update/12000-refresh cadence bound. It remains an emulator acceptance result.','Cartridge elapsed world-update times differ from TAP; input/music tempo and performance parity need further work.','L7 paired fixture bypasses native coarse-projectile death in both builds; does not establish unmodified survival equivalence.','No full eight-level hardware acceptance or all-boss victory claim.'],scope='Internal component and120-native-update paired runtime evidence against r145 TAP. Screens are completed world update100; images require visual review. Protected scenarios and emulated refresh counts are explicitly identified. No release promotion.')
(O/'current_integration_report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k]for k in('all_component_checks_passed','paired_scenarios_passed','publish_ready')},indent=2))
