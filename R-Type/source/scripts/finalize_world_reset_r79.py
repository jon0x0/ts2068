from pathlib import Path
import json,hashlib,zipfile,functools,subprocess
import numpy as np
from PIL import Image,ImageDraw
R=Path.cwd();O=R/'build/fullgame/world_reset_r79';B=R/'build/fullgame/startup_bulk_r77';P=R/'build/fullgame/world_owner_r78'
exe=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';q=subprocess.run([str(exe),f'--raw={O/"world_init.bin"}',str(R/'src/world_init_r79.asm')],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr;wrapper=(O/'world_init.bin').read_bytes();assert len(wrapper)==16
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();old=(B/f'level{n:02d}_region.bin').read_bytes();allowed=set(range(0xcf0,0xd00))|set(range(0xe400,0xed80));assert b[0xcf0:0xd00]==wrapper
 assert all(a==c or i in allowed for i,(a,c)in enumerate(zip(b,old))),n
 assert b[0x2000:0x2400]==old[0x2000:0x2400];assert b[0xed80:0xf080]==old[0xed80:0xf080]
 assert b[0xe400:0xed80]==(P/f'level{n:02d}_region.bin').read_bytes()[0xe400:0xed80]
for f in['launcher.bin','demand_loader.bin','rtype/rt.tap','rtype/RTCORE.TAP','rtype/RTPRELD.TAP']:assert(O/f).read_bytes()==(B/f).read_bytes()
for n in range(1,9):assert json.loads((O/f'boss_level{n}.json').read_text())['passed']
audit=json.loads((O/'initial_attribute_validation.json').read_text());assert audit['passed']and audit['attributeAudits']>=11;assert json.loads((O/'negative_control_r78.json').read_text())['expected_failure'];assert json.loads((O/'repeated_jumps_validation.json').read_text())['passed'];assert json.loads((O/'preload_title_L5.json').read_text())['passed'];assert json.loads((O/'initial_shift_L2.json').read_text())['passed'];hit=json.loads((O/'terrain_hit_natural.json').read_text());assert not hit['forced']and 0<hit['delaySeconds']<2
for f in['pause_validation.json','death_validation.json']:
 p=O/f
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
pal=np.array([(0,0,0),(0,0,205),(205,0,0),(205,0,205),(0,205,0),(0,205,205),(205,205,0),(205,205,205),(0,0,0),(0,0,255),(255,0,0),(255,0,255),(0,255,0),(0,255,255),(255,255,0),(255,255,255)],np.uint8);contact=Image.new('RGB',(1536,600),(20,24,30));d=ImageDraw.Draw(contact)
for col,(label,p)in enumerate([('r78 level jump',P/'jump_0_L2.home.bin'),('r79 level jump',O/'jump_0_L2.home.bin')]):
 b=p.read_bytes();a=np.zeros((192,256),np.uint8)
 for y in range(192):
  at=((y&192)<<5)|((y&7)<<8)|((y&56)<<2)
  for x in range(32):
   attr=b[0x6000+at+x];bits=b[0x4000+at+x]
   for k in range(8):a[y,x*8+k]=((attr&7)if bits&(128>>k)else(attr>>3)&7)+(8 if attr&64 else 0)
 im=Image.fromarray(pal[a]).resize((768,576),Image.Resampling.NEAREST);im.save(O/f'comparison_{col}.png');contact.paste(im,(col*768,24));d.text((col*768+8,5),label,fill='white')
contact.save(O/'L2_jump_before_after.png')
readme='''R-Type TS2068 r79 - stop star writes during world construction
Replace COMPLETE lowercase rtype folder, reset, run rt.tap.
Expanded512KB disk package; stock64KB cartridge unchanged.

Actual r78 fault: native stars remained enabled across an in-game level jump.
Writer BF3D repainted cleared native7800 attributes blue/cyan/magenta before
scenery initialization. This also prevented cells getting correct scrolling
classification. Menu start had already disabled that callback.

The common initializer now calls native73C2 before86C3. Native8721 calls73BC
to enable stars only after scenery construction. IRQs/audio/input otherwise
retain their native timing. r78 bitmap-derived ownership rebuild, forced fine
phase reset and jump trampolines are REMOVED. Original jump path restored.
Collision/protection countdown fix fromr78 retained. Artwork and palettes are
unchanged, as are r77 small-text406-file startup loading and controls.

Regression: before each world draw, starflagBE62 must be0 and all640 native
attributes must remain47. It fails onr78 and passes12world constructions over
11cold/cached jumps across alllevels. All8bossroutes pass. Real terrain contact
without protection bypass registers0.757seconds in the controlled joystick
route. Pause, respawn, startupLoadAll andL5LoadAll/restart pass. AllTAP checksum/
reconstruction andZIPCRC pass. Hardware confirmation pending.
'''
(O/'README.txt').write_text(readme,encoding='ascii');z=O/'RType_TS2068_r79.zip'
with zipfile.ZipFile(z,'w',compression=zipfile.ZIP_DEFLATED)as f:
 for p in sorted((O/'rtype').iterdir())+[O/'README.txt']:
  info=zipfile.ZipInfo(str(p.relative_to(O)).replace('\\','/'),date_time=(2026,11,7,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;f.writestr(info,p.read_bytes())
with zipfile.ZipFile(z)as f:assert f.testzip()is None
report={'version':79,'bytes':z.stat().st_size,'sha256':hashlib.sha256(z.read_bytes()).hexdigest(),'attributeAudits':audit['attributeAudits'],'cellsPerAudit':640,'r78_negative_control_failed_as_expected':True,'boss_tests':8,'artwork_palettes_phases_loader_unchanged':True,'r78_bitmap_ownership_workaround_removed':True,'terrain_hit_seconds':hit['delaySeconds'],'hardware_tested':False};(O/'validation_summary.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
for name,text in [('PROJECT_STATE.md','Latest r79 supersedes insufficient r78 ownership workaround. Confirmed native star writerBF3D contaminates initial7800attrs because callbackBE62 remains1 onjump. Normalmenu73C2 disablesit. CommonCF0initializer nowCALL73C2 before86C3; existing8721/73BC reenablesafterconstruction. R78ownership/finephase/trampoline patches removed; nativejump8640restored, R78collisionclock retained. Allart/palettes/phasesandR77loaderunchanged. build/fullgame/world_reset_r79/RType_TS2068_r79.zip. Newregression failsr78, passes12initializations (640nativeattrs each) across11jumps; all8bosses andloading/pause/respawnpass. TEST_HISTORY155; hardwarepending.'),('TEST_HISTORY.md','155. Native star callback race fixed r79 (2026-11-07). Userphoto12973 r78jumpL2 showsremainingcoloured/scrollingpieces; acknowledgedr78insufficient. Priorbitmap-only ownershipaudits checked an invented invariant ratherthan actualnativeattributeinitialization, so didnotprovefix. Compared menu/jump at8721: nearlyidentical commoncode exceptdiagnosticdeathbypass/IRQcountdowns, but menunative7800attrs all640=47 versusjump622=47 and18colouredliterals41/43/45. Writertrace identifiesBF3D LD(BC),A native starcolourwriter executingbetween86C3clear and8721draw, evenwithplayer5BC2=0. MenuBE62=0, jumpBE62=1. Native73C2 disablescallback,73BC enables; normal8721alreadycalls73BC afterFEEBdraw. Rootis starcallbacklifecycle, not newterrainconversion or hardware-onlypublication.\nFinalr79 buildsfromr77 plusretainedr78collisionclock. CF0wrapperCALL73C2,CALL86C3, preserveHL/resetFF81,RET fits16bytes; nativewarmupCALLCF0 retained. R78bitmapownership/finephase/extraD75/D96trampolines removed. No nativecode orframebuffers changed beyondCF0 andplayeroverlayversusr77. Sourceworld_init_r79.asm assemblesbyte-identicalall8wrappers. Exploratory native-state/overlayreset/globalinterrupt/forcedsync prototypes failedorleftgeometryresiduals andwere discarded; one nativebuild failed anassert whilePowerShell continued, thosemixedartifacts were rejected andfinaltests ranonlyaftercheckedbuildsuccess. Preserve originalgraphics-restorationCALL94F9 andnativeIRQtiming; disablingthem wasnotcorrect.\nNewverify_world_jump_r79 assertsBE62=0 andeach640nativeattrs=47 immediatelybefore8721. Negativecontrolr78 fails Stars active during world construction; r79 passes'+str(audit['attributeAudits'])+'initializations acrossroute2/3/4/5/6/7/8/2/3/5/2, cold/cachedloadcounts andnativeinit/object/ship checks pass. MatchedL2front map correlation improves1639old/333r78 residual to107r79 (ship/stars included; notpixelperfect claim); actual comparison_1.png andL2_jump_before_after.png rendered. No large column holes in inspectedscene. All8bossroutes pass (L7+700,others+160), pause64joysticks/exactrestore, actualL6death/respawn, queuedstartupL2visible406/allresident, L5LoadAll/title/cachedphysicalfire restart pass. Retainedcollisionfix naturalrealjoystickhit0.75684s, no forcedprotectionbypass. Palette/nativeart/playerphaseandloader/rt.tap/RTCORE/RTPRELD unchangedr77; allTAPchecksum/reconstruction/ZIPCRCpass. Hardwarepending; otherunrelatedissuesremainopen; stock64KB unchanged. Archive '+report['sha256']+' '+str(report['bytes'])+'bytes. r78publishedarchivepreserved; no referenceproject/sourceZIP modifications.')]:
 with(R/name).open('ab')as f:f.write(('\n\n'+text+'\n').encode('ascii'))
