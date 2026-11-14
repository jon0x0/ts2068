from pathlib import Path
import json,hashlib,zipfile,functools
import numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();O=R/'build/fullgame/world_owner_r78';B=R/'build/fullgame/startup_bulk_r77'
player=(O/'overlay_protection.bin').read_bytes();(O/'overlay.bin').write_bytes(player);(O/'overlay.sym').write_bytes((O/'overlay_protection.sym').read_bytes());(O/'overlay.asm').write_bytes((R/'src/game_pixel_overlay_r78.asm').read_bytes())
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();old=(B/f'level{n:02d}_region.bin').read_bytes();start,end=(0xa000,0xa400)if n==5 else(0x3a00,0x3e00);at=old.find(bytes.fromhex('214086e521'),start,end);helper=0xa401 if n==5 else 0x3e01
 allowed=set(range(0xcf0,0xd00))|set(range(0xd75,0xd7d))|set(range(0xd96,0xd9f))|set(range(0xdc0,0xdc3))|set(range(at+1,at+3))|set(range(helper,helper+58))|set(range(0xe400,0xed80))
 assert all(a==c or i in allowed for i,(a,c)in enumerate(zip(b,old))),n
 assert b[0x2000:0x2400]==old[0x2000:0x2400]
 assert b[0xed80:0xf080]==old[0xed80:0xf080],'Player phases changed'
for f in['launcher.bin','demand_loader.bin','rtype/rt.tap','rtype/RTCORE.TAP','rtype/RTPRELD.TAP']:assert(O/f).read_bytes()==(B/f).read_bytes()
for n in range(1,9):assert json.loads((O/f'boss_level{n}.json').read_text())['passed']
assert json.loads((O/'jump_ownership_validation.json').read_text())['passed'];assert json.loads((O/'preload_title_L5.json').read_text())['passed'];assert json.loads((O/'initial_shift_L2.json').read_text())['passed'];assert json.loads((O/'terrain_hit_natural.json').read_text())['delaySeconds']<2
for name in['pause_validation.json','death_validation.json']:
 p=O/name
 if p.exists():assert json.loads(p.read_text())['passed']
def tape(p):
 raw=p.read_bytes();out=[];at=0
 while at<len(raw):
  size=int.from_bytes(raw[at:at+2],'little');v=raw[at+2:at+2+size];assert len(v)==size and functools.reduce(int.__xor__,v,0)==0;out.append(v);at+=size+2
 assert at==len(raw);return out
for p in(O/'rtype').iterdir():
 if p.suffix.lower()=='.tap':tape(p)
for n in range(1,9):
 raw=(O/f'level{n:02d}_region.bin').read_bytes();assert b''.join(v[1:-1]for v in tape(O/f'rtype/LEVEL{n:02d}.TAP')[1::2])==raw;assert b''.join(v[1:-1]for v in tape(O/f'rtype/START{n:02d}.TAP')[1::2])==b''.join(raw[k*8192:(k+1)*8192]for k in[0,1,4,5,6,7])
# Render actual jump captures; do not conflate map-correlation residuals with perfect pixel equivalence.
pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205),(0,0,0),(0,0,255),(255,0,0),(255,0,255),(0,255,0),(0,255,255),(255,255,0),(255,255,255)],np.uint8);contact=Image.new('RGB',(1536,600),(20,24,30));d=ImageDraw.Draw(contact)
for col,(label,p)in enumerate([('Previous L2 jump',R/'build/fullgame/terrain_token_fix_r76/jump_0_L2.home.bin'),('r78 L2 jump',O/'jump_0_L2.home.bin')]):
 b=p.read_bytes();a=np.zeros((192,256),np.uint8)
 for y in range(192):
  at=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
  for x in range(32):
   attr=b[0x6000+at+x];bits=b[0x4000+at+x]
   for k in range(8):a[y,x*8+k]=((attr&7)if bits&(128>>k)else(attr>>3)&7)+(8 if attr&64 else 0)
 im=Image.fromarray(pal[a]).resize((768,576),Image.Resampling.NEAREST);contact.paste(im,(col*768,24));d.text((col*768+8,5),label,fill='white')
contact.save(O/'L2_jump_before_after.png')
readme='''R-Type TS2068 r78 - level jumps and terrain collision timing
Replace complete lowercase rtype folder, reset, run rt.tap.
Expanded512KB disk; existing64KB cartridge target unchanged.

L then1-8 now completes world initialization, rebuilds initial background
ownership from its visible bitmap, resets fine-scroll phase, then performs
normal ship setup. Initial scenery no longer inherits non-scrolling object
ownership. Applies to cold and resident jumps, with a separate L5 bank gateway.
Rebuild occurs once per jump, not in the per-frame rendering loop.

Spawn/protection countdown now advances with accepted player updates. In the
real-joystick L2 terrain-contact test, the unmodified protected path waited
184.93seconds versus0.705seconds when protection was cleared. The corrected
normal path registers a hit in0.607seconds, without bypassing protection.
This retains brief protection while preventing a stalled world-clock counter
from allowing the ship to pass through terrain for a prolonged period.

r77 artwork, palettes, player phases, loading UI and queued406-file loader are
unchanged. Player code2430bytes fits beforeED80; fixed5entry jumps retained.
Four short branches and one unconditional tailcall recover code space.

Tests: all8boss routes; eleven cold/resident level jumps; 4L2/L3 ownership
audits of640cells each; actual joystick terrain hit; pause64joystick cases;
real death/respawn; queued startupLoadAll; L5LoadAll/title/cached restart.
All tape checksums and bank reconstruction pass. Hardware confirmation pending.
Known unrelated graphical issues remain open; not a claim of pixel-perfect
arcade graphics or measured hardware frame rate. No new artwork conversion.
'''
(O/'README.txt').write_text(readme,encoding='ascii');z=O/'RType_TS2068_r78.zip'
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED)as f:
 for p in sorted((O/'rtype').iterdir())+[O/'README.txt']:
  info=zipfile.ZipInfo(str(p.relative_to(O)).replace('\\','/'),date_time=(2026,11,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;f.writestr(info,p.read_bytes())
with zipfile.ZipFile(z)as f:assert f.testzip()is None
report={'version':78,'bytes':z.stat().st_size,'sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'artwork_palette_phases_and_loader_unchanged':True,'player_code_bytes':len(player),'boss_tests':8,'all_level_jumps_passed':True,'ownership_audits':4,'cells_per_audit':640,'natural_terrain_hit_seconds':json.loads((O/'terrain_hit_natural.json').read_text())['delaySeconds'],'hardware_tested':False};(O/'validation_summary.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
for name,text in [('PROJECT_STATE.md','Latest r78 addresses user-confirmed L2/L3 stationary terrain on in-game L-number jumps, not menu start. Jump-only rebuild of initial scenery ownership (640cells, bitmap ->FF/0) before ship setup; resets fine-scroll7A82/83, restoresmap9. Reserved58byte feedbackpadding helper (L5 separate bank), CF0trampoline and D75/D96padding used; originalnative86C3 warmup restored to avoid CF0recursion. Protection countdown now acceptedplayer-update clock; actual joystick terrain collision natural184.93s before vs0.607s after. Artwork/palettes/playerphases/r77loader unchanged. build/fullgame/world_owner_r78/RType_TS2068_r78.zip. TEST_HISTORY154; hardware pending.'),('TEST_HISTORY.md','154. Jump ownership and protection countdown r78 (2026-11-07). Read state/history. User distinguishes normal menu start good, L+2 jump bad; reports delayedterrainhits bothpaths. Re-examined existing r76 jump_0_L2 snapshot: broken columns reproduce there, overlooked by prior jump-load/state checks. Map top96 correlation residual1639bits vs coherent menu~93; activeowner130 vs43 differs atinit but resetting owner alone, playerflags alone, renderer-mode alone did not fix. Full8634return candidate enteredprompt/hung; abandoned. Direct-coordinate teleport collision probe violated compositor locality and tripped protectedcode guard; not valid collision evidence, not shipped.\nFinal jump path calls existing1485/8721, then rebuilds 640initialowner cells from freshly drawn bitmap toFF/0 withinterruptsdisabled, preservesIX, clearsfinephase7A82/83, restoresmap9/EI, enters8646shipsetup. This bypasses old8640resume point only forjump. Helper58bytes fits retiredfeedbackpadding3E01..3E3B orL5A401..A43B, retainsRETatfeedbackentry; noUIoverlap3E40. CF0/D75/D96padding contracts asserted. DC0originalCALL86C3 restored becauseCF0nowjump entry. Oldr76colourtokenkeeper andexitNOPfixes retained; crosslevelhookguards pass. Rebuiltowned columns no longer have the large stationary holes in matched captures; residualmapdifferences remain (notpixel-perfect claim). L2_jump_before_after.png actualcaptures.\nRealjoystickup movement test (no teleport/nativecoordinate edits) shows old natural contactdelay184.925s withprotection2 versus0.705s forcedunprotected. PlayerIRQtick previously returnedfromcollision whileprotectioncountstalled. New countdown decrements only nonzero7A98 duringacceptedactiveplayerupdates; actual naturalcontact0.6068s, forcedcontrol0.6238s. No protectionbypass in naturaltest. Source game_pixel_overlay_r78.asm fits2430<=2432 beforeED80phases. Stable5jump-tableentries kept. Four legalshortbranches andoneunconditionaltailcall +equivalentunsignedstate-rangecheck reclaimspace. Conditionaltailcall trial rejected/corrected beforeinstallation.\nAll8bossroutes pass (L7+700updates, others+160); route2/3/4/5/6/7/8/2/3/5/2 cold/cached passesloadcounts/init/reset/shipchecks. Initcounter observes1485 ratherthan8640 becausejumpentrychanged. Separate4jump L2/L3 contract verifieseach640ownershipcells exactly againstvisiblebitmap. Pause64joystick combinations/exactscreenrestore pass; realL6death/respawn pass; queuedstartupLoadAllL2 allresident beforetitle/visible406 pass; L5LoadAll/title/cachedsocket2fire restart pass. Staticperleveldiffrestrictedtocodehelper/hotoperand/playercode; allpalettes/nativeart/playerphasebytes unchanged, loader/rt.tap/RTCORE/RTPRELD identicalr77. AllTAPchecksum/LEVEL/START reconstruction/ZIPCRCpass. Hardwarepending; stock64KB unchanged. Archive '+report['sha256']+' '+str(report['bytes'])+'bytes. Sourcebuild_world_owner_r78.py +prepare_protection_r78.py; no reference projects/sourceZIPs modified.')]:
 with(R/name).open('ab')as f:f.write(('\n\n'+text+'\n').encode('ascii'))
