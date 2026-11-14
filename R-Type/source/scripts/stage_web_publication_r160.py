from pathlib import Path
import shutil,json,hashlib,zipfile
_read=Path.read_text;_write=Path.write_text
Path.read_text=lambda self,*a,**k:_read(self,*a,**({'encoding':'utf-8'}|k))
Path.write_text=lambda self,*a,**k:_write(self,*a,**({'encoding':'utf-8'}|k))
R=Path.cwd();H=R/'build/publication_r160/hub';P=H/'R-Type';W=P/'play';W.mkdir(parents=True,exist_ok=True)
S=R.parent/'sinistar/play-dpad';B=R.parent/'berserk/web'
shutil.copytree(S/'tsrun',W/'tsrun',dirs_exist_ok=True);shutil.copy2(S/'tsrun-version.json',W/'tsrun-version.json')
shutil.copytree(B/'emulator',W/'emulator',dirs_exist_ok=True)
a=(B/'emulator/adapter.js').read_text().replace("const upstream='https://josef-jelinek.github.io/TSRun/';","const upstream=new URL('../tsrun/',import.meta.url).href;")
a=a.replace('berzerk','rtype').replace('Berzerk','R-Type')
a=a.replace("resource('../../build/features/rtype.dck',true)","resource(`../assets/rt_l${Math.max(1,Math.min(8,Number(new URLSearchParams(location.search).get('level'))||1))}_r160.dck`,true)")
a=a.replace("    // R-Type currently decodes fire at bit4; TSRun supplies native bit7.\n    for(let i=0;i<2;i++) if(!(joystick[i]&128)) joystick[i]&=~16;\n    const player=machine.ram[0x7802]===2?1:0;\n    joystick[player]&=touch;","    joystick[0]&=touch;")
a=a.replace("  window.addEventListener('keydown',event=>{window.rtype.start();keys.handleKeyDown(kbd,event);});","  window.addEventListener('keydown',event=>{if(window.parent.rtypeCommand?.(event,true))return;window.rtype.start();keys.handleKeyDown(kbd,event);});")
a=a.replace("  window.addEventListener('keyup',event=>keys.handleKeyUp(kbd,event));","  window.addEventListener('keyup',event=>{if(!window.parent.rtypeCommand?.(event,false))keys.handleKeyUp(kbd,event);});")
a=a.replace("    reset(){touch", "    async sequence(codes){for(const code of codes){this.press(code);await new Promise(r=>setTimeout(r,260));}},\n    chord(code){this.start();const e={code,preventDefault(){},repeat:false},s={...e,code:'ShiftLeft'};keys.handleKeyDown(kbd,s);keys.handleKeyDown(kbd,e);setTimeout(()=>{keys.handleKeyUp(kbd,e);keys.handleKeyUp(kbd,s);},160);},\n    reset(){touch")
(W/'emulator/adapter.js').write_text(a);(W/'emulator/sound.worklet.js').write_text("import '../tsrun/sound.worklet.js';\n")
i=(B/'emulator/index.html').read_text().replace('BERZERK','R-TYPE').replace('?v=controls-sound-8','?v=r160');(W/'emulator/index.html').write_text(i)
c=(B/'controls.js').read_text().replace('berzerk','rtype').replace('0x6f','0x7f')
c=c.replace("window.addEventListener('keydown',e=>{if(ready)api().key(e,true);});","window.addEventListener('keydown',e=>{if(!window.rtypeCommand(e,true)&&ready)api().key(e,true);});")
c=c.replace("window.addEventListener('keyup',e=>{if(ready)api().key(e,false);});","window.addEventListener('keyup',e=>{if(!window.rtypeCommand(e,false)&&ready)api().key(e,false);});")
c=c.replace("button.addEventListener('click',()=>api()?.press(action.code));","button.addEventListener('click',()=>{if(action.sequence)api()?.sequence(action.sequence);else if(action.shift)api()?.chord(action.code);else api()?.press(action.code);});")
c += '''\nconst levels=document.querySelector('#level');
for(let n=1;n<=8;n++){const o=document.createElement('option');o.value=n;o.textContent='Level '+n;levels.append(o);}
let armed=0;
function loadLevel(n){ready=false;api()?.release();levels.value=n;document.querySelector('#status').textContent='Loading level '+n+'...';frame.src='emulator/index.html?level='+n+'&v=r160';history.replaceState(null,'','?level='+n);}
levels.addEventListener('change',()=>loadLevel(Number(levels.value)));
window.rtypeCommand=(e,down)=>{
 if(e.target?.matches?.('input,select,textarea')||e.ctrlKey||e.altKey||e.metaKey)return false;
 if(e.code==='KeyL'){e.preventDefault();if(down&&!e.repeat){armed=performance.now()+4000;document.querySelector('#status').textContent='Choose level 1-8';}return true;}
 if(armed>performance.now()&&/^Digit[1-8]$/.test(e.code)){e.preventDefault();if(down){armed=0;loadLevel(Number(e.code.slice(-1)));}return true;}
 return false;
};
document.querySelector('#restart').addEventListener('click',()=>api()?.reset());
const first=Math.max(1,Math.min(8,Number(new URLSearchParams(location.search).get('level'))||1));loadLevel(first);
'''
(W/'controls.js').write_text(c)
shutil.copy2(B/'style.css',W/'style.css')
with (W/'style.css').open('a') as f:f.write('''\nmain{height:auto;min-height:100dvh;overflow:auto!important}header{position:relative!important;height:auto;min-height:44px;flex-wrap:wrap;pointer-events:auto;inset:auto!important}header select{font:inherit;background:#293036;color:white;padding:8px}#stage{height:min(72vh,720px)!important;flex:none}#controls-help{height:auto!important;text-align:left;max-width:1000px;margin:auto;font-size:14px}#controls-help p{margin:8px 0}a{color:#8de0ed}#below-fire button{white-space:normal}main:fullscreen #stage{height:calc(100dvh - 60px)!important}main:fullscreen #controls-help{display:none}@media(max-aspect-ratio:1/1){#stage{height:68vh!important;grid-template-rows:minmax(0,1fr) 150px}#actions{gap:6px}#fire{height:80px;width:80px}#below-fire{gap:4px}#below-fire button{min-height:30px}}\n''')
actions=[{'id':'start','label':'Start','code':'Space'},{'id':'keys','label':'Set keys','code':'Enter'},{'id':'boss','label':'Boss B B','sequence':['KeyB','KeyB']},{'id':'music','label':'Music M','code':'KeyM'},{'id':'pause','label':'Pause','code':'KeyP','shift':True},{'id':'detach','label':'Force / missile','code':'Enter'}]
for x in actions:x['placement']='below-fire'
(W/'cartridge-controls.json').write_text(json.dumps({'title':'R-Type Remastered','actions':actions,'touchPad':{'deadZone':.45}},indent=2))
D=P/'downloads';D.mkdir(exist_ok=True);A=W/'assets';A.mkdir(exist_ok=True)
for n in range(1,9):
 for ext in ['dck','bin']:
  f=R/f'build/cartridges/r160/level{n}/rt_l{n}_r160.{ext}';shutil.copy2(f,A/f.name)
shutil.copy2(R/'build/cartridges/r160/RType_TS2068_64K_cartridges_r160.zip',D)
controls='''<p><strong>Set movement keys:</strong> press Enter on the title screen and answer each prompt. Suggested: O left, P right, Q up, A down, Space fire, Enter missile / Force action. Follow the on-screen prompt order. Keyboard and native joystick stay active together.</p><p><strong>Start / fire:</strong> Space or joystick Fire. <strong>L, then 1-8:</strong> select a level (browser switches cartridges; resets that level). <strong>B, release, B:</strong> jump to the current boss fight. Collect the offered weapon pickup. <strong>M:</strong> music on/off. <strong>Shift-P:</strong> pause/resume, with a Paused display. Press and release each command.</p><p><strong>Virtual DPad:</strong> drag for directions, hold Fire; use the action buttons beside it. USB gamepad directions and Fire are supported. The Force / missile touch button assumes Enter was selected for that action. Keyboard bindings are chosen in the game, not forced by the player.</p><p>Click or press a key to enable browser audio. Sound On/Off mutes browser output; M toggles game music separately. The level selector is always available. Each physical cartridge contains one level; L switching belongs to this browser wrapper or the disk edition.</p>'''
(W/'index.html').write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R-Type Remastered - TS2068</title><link rel="stylesheet" href="style.css"><script type="module" src="controls.js"></script></head><body><main><header><strong>R-TYPE <small>TS2068 Remastered r160</small></strong><label>Cartridge <select id="level" aria-label="Level"></select></label><button id="restart">Reset</button><button id="fullscreen">Fullscreen</button><a href="../">Project</a></header><div id="stage"><div id="pad" role="group" aria-label="Drag to move in eight directions"><span id="knob"></span></div><iframe id="emulator" title="R-Type in modified Berzerk TSRun" allow="autoplay; gamepad"></iframe><div id="actions"><button id="fire" disabled>FIRE</button><div id="below-fire"></div></div></div><section id="controls-help"><h1>R-Type controls</h1>'''+controls+'''<p><a href="../downloads/RType_TS2068_TSRun_r160.zip">Download the complete TSRun archive</a> | <a href="https://github.com/jon0x0/ts2068/tree/main/R-Type">Source and notes</a> | <a href="../">Project page</a></p></section><p id="status" role="status">Loading cartridge...</p></main></body></html>''')
readme='''# R-Type Remastered for the TS2068

A ZX Spectrum conversion remastered for the Timex Sinclair 2068, with selected
arcade-derived artwork, extended 8x1 colour shading, native joystick support,
AY music and effects, smoother player motion and enhanced boss presentation.
It belongs to Remastered games, Spectrum ports and arcade-derived conversions.
Original game: Irem; Spectrum edition: Electric Dreams / Software Studios.

[Play with keyboard or Virtual DPad](https://jon0x0.github.io/ts2068/R-Type/play/)
| [Project page](https://jon0x0.github.io/ts2068/R-Type/)
| [TSRun archive](downloads/RType_TS2068_TSRun_r160.zip)
| [Eight 64KB cartridges](downloads/RType_TS2068_64K_cartridges_r160.zip)

## Keys

Press Enter at the title to define the six controls, following the prompts.
Suggested bindings: O left, P right, Q up, A down, Space fire, Enter missile /
Force action. Start with Space or native joystick Fire. Keyboard and joystick
work together without choosing an input mode.

- L then 1-8: choose a level in the browser (loads another cartridge and resets).
- B, release, B: jump to the current level boss; collect the weapon pickup.
- M: toggle music independently from effects.
- Shift-P: pause / resume. P alone also pauses if not assigned to gameplay.
- Virtual DPad / Fire: move and shoot; action buttons provide the other commands.

Each physical cartridge is a self-contained level. It cannot change cartridges
by itself; the browser level switch is provided by the wrapper.

## Run the TSRun download

Extract the archive, run `python -m http.server 8000` in the extracted directory,
and open http://localhost:8000/play/. Audio needs a click/key and WebGL2 is needed.
All emulator modules, shaders, ROMs and level cartridges are included locally.
The modified TSRun snapshot is the same isolated Berzerk runtime used by the
hub's Sinistar Virtual DPad player; its hashes are in play/tsrun-version.json.
TSRun by Josef Jelinek; original ROM provenance is in play/tsrun/roms/README.md.
R-Type-specific adapter and controls are separate from that unchanged runtime.

## Release scope

r160 is the current eight-cartridge release. All eight software acceptance suites,
16 paired TAP actor/event/control scenarios and read-only image contracts pass.
Physical cartridge confirmation remains pending; elapsed timing differs from
the expanded-RAM disk edition. Not every graphic is an arcade replacement.
The stable hardware-confirmed r99/r100 disk archive is preserved separately.
See release-evidence for exact checks, limitations and cartridge provenance.

## Source and attribution

Development stays in the R-Type workspace. This publication is a source snapshot,
not a competing development tree. source/ includes conversion/build/verification
scripts and assembly. Original arcade and Spectrum input archives are deliberately
not copied here; provide your own inputs to rebuild conversions. Historical
scripts reference workspace build checkpoints, which are not all in this snapshot.
No blanket licence is applied to Irem, Spectrum, ROM or TSRun third-party assets.
'''
(P/'README.md').write_text(readme)
(P/'index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R-Type Remastered - TS2068</title><style>body{background:#10151c;color:#edf2f8;font:17px/1.65 system-ui;max-width:1000px;margin:auto;padding:28px}a{color:#8de0ed}h1{font-size:48px}section{background:#192d36;border-radius:12px;padding:24px;margin:24px 0}kbd{background:#354354;padding:2px 6px}</style></head><body><a href="../">TS2068 hub</a><h1>R-Type Remastered</h1><p>ZX Spectrum roots, arcade-derived artwork, and native TS2068 Extended Colour Mode. Eight individually selectable levels, AY music and effects, and keyboard, joystick or Virtual DPad play.</p><section><h2><a href="play/">Play R-Type - keyboard and Virtual DPad</a></h2><p><a href="downloads/RType_TS2068_TSRun_r160.zip">Download the self-contained TSRun archive</a> | <a href="downloads/RType_TS2068_64K_cartridges_r160.zip">Download all eight 64KB cartridges</a> | <a href="https://github.com/jon0x0/ts2068/tree/main/R-Type">Source and release notes</a></p></section><h2>Keyboard and controls</h2>'+controls+'<h2>Edition and credits</h2><p>r160 cartridge edition. A remaster of the Spectrum port, with selected graphics converted from the original Irem arcade game. TSRun by Josef Jelinek; modified Virtual DPad runtime from Berzerk, isolated from the other hub players. Browser wrapper supplies L + number cartridge switching.</p><p>Software verified; physical cartridge confirmation remains pending. This is not a claim of complete arcade artwork replacement or identical disk/cartridge timing.</p></body></html>')
E=P/'release-evidence';shutil.copytree(R/'build/cartridges/r160',E,dirs_exist_ok=True)
# Avoid a second copy of the downloadable ZIP inside evidence.
for f in E.glob('*.zip'):f.unlink()
for folder in ['src','scripts','assets','third_party','web']:
 for f in (R/folder).rglob('*'):
  if f.is_file() and '__pycache__' not in f.parts and f.suffix!='.pyc':
   t=P/'source'/f.relative_to(R);t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,t)
for name in ['AGENTS.md','PROJECT_STATE.md','TEST_HISTORY.md','requirements.txt']:
 shutil.copy2(R/name,P/'source'/name)
# The build docs record original workspace paths and historical evidence scopes.
shutil.copytree(R/'docs',P/'source/docs',dirs_exist_ok=True)
# Preserve the source snapshot itself outside generated build output.
(P/'source/README.md').write_text(readme+'\nSnapshot: 2026-11-14, stock cartridge r160. See ../release-evidence/.\n')
# Apply the maintained R-Type frontend after copying the reference adapter.
for f in (R/'web').rglob('*'):
 if f.is_file():
  q=W/f.relative_to(R/'web');q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,q)
with zipfile.ZipFile(D/'RType_TS2068_TSRun_r160.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in W.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(P))
 z.writestr('README.md',readme)
# Preserve the complete disk edition separately from the cartridge/browser edition.
disk=R/'build/fullgame/visible_hits_r145/RType_TS2068_r145.zip'
shutil.copy2(disk,D/'RType_TS2068_TSPico_r145.zip')
with zipfile.ZipFile(disk) as z:
 for name in z.namelist():
  if name.startswith('rtype/') and name.lower().endswith('.tap'):
   f=P/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read(name))
checks={str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest() for f in P.rglob('*') if f.is_file()}
(P/'SHA256SUMS.txt').write_text(''.join(f'{v}  {k}\n' for k,v in sorted(checks.items())))
print('Staged',len(checks),'R-Type files; TSRun ZIP', (D/'RType_TS2068_TSRun_r160.zip').stat().st_size)
