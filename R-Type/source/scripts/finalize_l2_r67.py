from pathlib import Path
import json,hashlib,zipfile,functools
R=Path.cwd();O=R/'build/fullgame/l2_rpc_r67';B=R/'build/fullgame/startup_r66';A=R/'build/graphics/l2_integrated_r67'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(B/'RType_TS2068_r66.zip')=='96bd744bc08c6f5212003658959b697def88084aee31d9a1aa9af98b29763c60'
checks=json.loads((O/'r67_checks.json').read_text());assert len(checks)==7 and all(x['passed']for x in checks)
assert json.loads((O/'boss_preview_validation.json').read_text())['results'][0]['after']==700
for n in[1,3,4,5,6,7,8]:assert (O/f'level{n:02d}_region.bin').read_bytes()==(B/f'level{n:02d}_region.bin').read_bytes()
assert (O/'boot_region.bin').read_bytes()==(B/'boot_region.bin').read_bytes();assert (O/'launcher.bin').read_bytes()==(B/'launcher.bin').read_bytes();assert (O/'rtype/RTCORE.TAP').read_bytes()==(B/'rtype/RTCORE.TAP').read_bytes()
readme="""R-Type TS2068 r67 - L2 arcade boss upgrade, expanded RAM disk game

Reset and replace the COMPLETE rtype folder. Start lowercase rt.tap.
Do not mix LEVEL02.TAP / START02.TAP with an older package.
Select level2, start, and press B twice with a release between presses for
boss preview; ordinary level2 progression also uses the new artwork.

Selected192x104 RPC body: brightness44, contrast54, saturation71, gamma0.98,
Sierra Lite, normal black and bright nonblack pairs.18 compressed scenery
pieces reuse the old boss area. Four arcade-source weak-point poses replace
the old yellow mouth; native spawn and hitbox move together. Correct isolated
32px arcade worm heads replace neck-contaminated crops, centered within the
original40x40 gameplay box. Four two-pixel phases retained for each pose.

The scenery uses native scrolling and terrain ownership. All11 measured lower
boss bands move1pixel on each of31 consecutive updates during entry. Native
stop retained. This is completed-frame emulation evidence; physical video
presentation still needs a hardware check. Native collision logic is retained,
with the weak-point descriptor/spawn aligned; no claim of a full boss defeat
or full-level hardware playthrough.

Seven regression groups plus700boss updates pass: ordinary approach, cached
jumps, pause, keyboard setup, actual death/respawn, Load All. Other seven levels,
loader, boot, shared core and controls are unchanged fromr66. Existing stock
64KB target is unchanged. Remaining L3 hardware issue is still open.

Controlled160-update boss comparison:108338030 CPU T-states versus104523296
forr66, about3.65percent additional world-loop CPU time with the richer art.
This is not hardware FPS or a player-response benchmark.

Keys are defined by the game. Both native joystick sockets remain active.
P pauses (Shift-P if P is a defined game key); P resumes. L at title or Shift-L
in game loads all and returns to title. During play L then1-8 changes level.
Initial Shift-L queues Load All. Existing loading/verification feedback retained.

Review: build/graphics/l2_integrated_r67/index.html.
This integrates the selected L2 boss upgrade; some other enemy/scenery artwork
retains earlier conversions. An all-level RPC source inventory is prepared,
including identity-review flags. No unverified source matches auto-installed.
"""
(O/'rtype/README.txt').write_text(readme,encoding='utf-8');(R/'docs/r67_readme.txt').write_text(readme,encoding='utf-8')
def tape(p):
 raw=p.read_bytes();out=[];at=0
 while at<len(raw):
  l=int.from_bytes(raw[at:at+2],'little');v=raw[at+2:at+2+l];assert len(v)==l and functools.reduce(int.__xor__,v,0)==0;out.append(v);at+=l+2
 assert at==len(raw);return out
for p in (O/'rtype').glob('*.tap'):tape(p)
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();assert b''.join(v[1:-1]for v in tape(O/f'rtype/LEVEL{n:02d}.TAP')[1::2])==b;assert b''.join(v[1:-1]for v in tape(O/f'rtype/START{n:02d}.TAP')[1::2])==b''.join(b[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7])
# Static layout contracts: common palette slots stable, helper bounds, map IDs,
# immutable compressed pointers and source/decode disjointness.
b=(O/'level02_region.bin').read_bytes();old=(B/'level02_region.bin').read_bytes();assert b[0x2000:0x2080]==old[0x2000:0x2080]
j=json.loads((A/'manifest.json').read_text());assert j['compressed_bytes']<=2160 and max(b[0xc762+280:0xc762+320])<64
head=json.loads((R/'build/graphics/l2_actors_r67/head_phases.json').read_text());assert 0x2400+head['bytes']<=0x33e6
oldtime=json.loads((R/'build/diagnostics/l2_r67_perf/r66/timing.json').read_text());newtime=json.loads((R/'build/diagnostics/l2_r67_perf/r67/timing.json').read_text());pct=(newtime['tstates']/oldtime['tstates']-1)*100
report={'version':67,'checks':checks,'boss_soak_updates':700,'reproducible_primary_products':30,'all_tapes_valid':True,'other_seven_levels_unchanged':True,'boot_launcher_core_unchanged':True,'body':j,'head_phase_bytes':head['bytes'],'mouth_frames':4,'additional_emulated_world_CPU_percent':pct,'stock64KB':'unchanged','hardware':'pending','remaining_L3_hardware_fragment':'open'}
zp=O/'RType_TS2068_r67.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED)as z:
 for p in sorted((O/'rtype').iterdir()):
  if p.is_file()and p.name!='RTBOOT.TAP':z.write(p,'rtype/'+p.name)
with zipfile.ZipFile(zp)as z:assert z.testzip()is None;assert 'rtype/rt.tap'in z.namelist()
report.update(sha256=sha(zp),bytes=zp.stat().st_size);(O/'validation_summary.json').write_text(json.dumps(report,indent=2));print(report['sha256'],report['bytes'],pct)
page='<meta charset="utf-8"><title>L2 r67 playable upgrade</title><style>body{background:#161616;color:#eee;font:18px sans-serif;max-width:1100px;margin:30px auto}img{image-rendering:pixelated;max-width:100%}a{color:cyan}</style><h1>L2 arcade boss - r67</h1><p>Selected RPC192x104 conversion integrated into expanded disk gameplay. These screen captures come from scripted emulation; not a hardware test.</p><h2>Actual gameplay</h2><img src="../../fullgame/l2_rpc_r67/scene_L2_100.png"><h2>Selected conversion</h2><img src="../l2_rpc_settings/C.png"><h2>Installed scenery asset</h2><img src="body.png"><p>Shared palette budget:251/312cells exact;61 fitted to existing row patterns. Mean RGB absolute error2.21/255. Black/nonblack source geometry preserved.</p><h2>Arcade weak-point poses</h2><img src="../l2_actors_r67/mouth_contact.png"><p>Four sampled arcade poses,32x24 native actor. No packing colour loss for these frames.</p><h2>Verification</h2><p>700boss updates; ordinary approach;31fine-scroll transitions; repeated cold/cached jumps; pause; keys; death/respawn; Load All. About3.65%more emulated world-loop CPU time on the controlled boss path. Physical hardware confirmation pending.</p><p>Other seven levels and stock64KB unchanged. This does not mean all artwork across all levels has been replaced.</p><p><a href="../arcade_rpc_inventory_r67/inventory.json">All-level source inventory for the next RPC comparison pass</a></p>'
(A/'index.html').write_text(page,encoding='utf-8');s=json.loads((R/'build/graphics/l2_rpc_settings/selected_style.json').read_text());s['playable_integration']='expanded disk r67; emulation validated, hardware pending';(R/'build/graphics/l2_rpc_settings/selected_style.json').write_text(json.dumps(s,indent=2))
