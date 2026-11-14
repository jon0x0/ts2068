from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/l5_preshift_r58'
def main():
 v=json.loads((OUT/'validation_summary.json').read_text());assert len(v['checks'])==14 and all(r['passed']for r in v['checks']);archive=OUT/'RType_TS2068_r58_L5_preshift_trial.zip';digest=hashlib.sha256(archive.read_bytes()).hexdigest();assert digest in(OUT/'package_sha256.txt').read_text()
 doc=f"""# r58 L5 two-pixel phase trial (2026-11-05)

Deliverable: build/fullgame/l5_preshift_r58/{archive.name}
SHA256: {digest}

This is a separate expanded-memory gameplay experiment. Standard r57 and the stock64KB cartridge remain unchanged. Select5 before starting, then press/release B twice in gameplay for the boss preview. Chosen controls and both native joystick sockets remain combined.

## Result and limitation

All25 Bellmite parts use actor-local pixel coordinates. Ordinary native8px target changes are approached in2px increments per axis on each existing boss/world update. Larger scripted relocations still snap; this preserves their native arrangement instead of allowing indefinite interpolation lag. Original animation IDs/attack scripts remain, sphere24px/core80px. Padding cells do not enlarge visible graphics. Native enemy collision/AI retains its coarse conventions; this is not a wholesale pixel-collision rewrite.

Four compiled horizontal phases0/2/4/6 are fitted to legal8x1 pairs with exact nonblack coverage. Vertical movement relocates cached raster rows; both orientations are supported. Cache preparation is done during level initialization, not boss entrance. No new arcade cels, music or SFX are claimed.

The matched double-B/700-world-update route takes26295 emulated display refreshes inr57 and36061 inr58:37.14%longer, including boot/entrance. This is not a faster boss clock. The stationary single-shot probe has8worldupdates/480refreshes; the held-input route has6, versus r57's9. Final held-input route retains141player ticks,138projectile phases,8shortshots+1beam. Exact counts depend on the workload. The rapid15-tap probe catches14shots, zero beams and no late catch-up, versus15inr57. Do not claim universal tap capture or a hardware frame rate. Keep the trial separate pending user comparison.

## RAM ownership

Cold phases:7152bytes packed in DOCK1:2400..3FDF plus16tailbytes in DOCK7:E1E0..E1EF, with small dictionaries atE1B0/E1C0. The existing3FE0scroll stack slot is preserved. Source columns contain continuous raster pairs so vertical phases use pointer offsets.

During level init, native assets have already been installed in HOME. Save the128-byte transition tail DOCK6:DBD0..DC4F atDOCK7:E000. Copy the packed cache toDOCK6:C000..DBEF, expand7040corebytes intoDOCK1:2400..3F7F, then2304spherebytes intoDOCK6:C000..C8FF. The latter replaces only the first2304packed bitmap bytes. Remaining packed bytes are retained for exact restoration. Runtime phase data total9344bytes, with no extra RAM region beyond the existing512KB.

Before a cache bank switch, recover the overwritten packed prefix from every other byte of the raw core, restore the packed palette bank/tail, then restore the borrowed DOCK6 native source shadow from HOME and restore its saved transition tail. Set the phase flag cold. Unit checks compare these ranges byte-for-byte, and real L5boss/game-over/cached-boss restart plus full8level cache revisit pass.

Motion/warmup/restore code is DOCK6:DC50, beyond the native source copy endingD87C and the saved tail endingDC50. Cache helper is DOCK4:8C00..8EFF, replacing the retired unshifted pair cache. Per-actor positions occupyDOCK7:E200..E3FF. HOME5BE0..5BE4holds short main-only gateway state. The renderer uses DOCK2's existing private shader stack, separate from HOME's player IRQ stack. Source restoration returns with interrupts disabled. The warmup initializer regenerates the reversal table and uses scratch registers that its initializer callers do not consume.

## Evidence

256native phase/orientation comparisons match independent raw raster decode, exact silhouette/normal-black checks; another256comparisons include8IM2injections through5F/1Fmappings. Cache expansion is exact; pack/native-shadow/tail restoration is exact. Isolated preparation costs2374061Z80cycles, excluding I/O. It runs during loading.

700actualL5boss updates,25actors/16075motion samples, ordinary-travel2px assertions; otherbosses1/2/3/4/6 run200updates and7/8run700to reach their later appearances. Native keys/dualjoysticks, functional8shortshots+1beam, single-shot ordering, realdeath/respawn, title116states, snake route and fourloadererrors pass. Boss/game-over/boss cached restart15890refreshes with justRTBOOT/LEVEL05 mounts. Full8diskloads/ending/cache-onlyrevisit59431refreshes,128blocks,37221code/reversal audits,15core/workspace checks. These boss/cache probes use invulnerability/forcedvictory, not proof of unassisted completion.

All9frozen region hashes, strict byte-ownership changes,72TAPpageflag/XOR/raw reconstruction, unchanged player/projectile/audio/IRQ bank7 code afterE400 and archive integrity checked. Separate rebuild15binary/cache files byte-identical. Real hardware/PicoVideo pending.

## Diagnostics and development outcomes

Native captures at build/diagnostics/l5_preshift_r58/baseline and candidate contain16HOME framebuffer states each. baseline.gif/candidate.gif preserve emulated update spacing; comparison.png and index.html were rendered from them. Comparison PNG visually inspected. Short loop wrap is excerpt restart. They are emulator captures, not hardware photos or an independently timed native-video codec. Existing user photos/reference projects/source ZIPs unchanged.

Rejected early candidate confused CPU addresses with physical source-bank ownership and overwrote saved native assets; never packaged. Revised packed in-frame decoder was substantially slower and initially blocked input, so decoding moved to loading and raw cached rows are interruptible. Empty-cell early exit initially failed to restoreI84 after usingI8F; fixed before final native tests. Recompiled shared copy helpers after shader-state addresses moved. A neutral-coordinate branch incorrectly returned zero; live state assertions caught and fixed it. Initial motion trace mistook banked8CFD for HOME8CFD; fixed mapping/stack filtering. Source-restore EI caused loader core changes; disabled-return entry fixed it. Test-only IM0IRQ setup was wrong; IM2test now passes. A200-update L7probe ended before boss arrival; extended7/8to700. Early failed assembler ranges and the subsequent stale-image probe were rejected, not release evidence. Initial preview renderer syntax error corrected. Baseline investigation initially overwrote r57diagnostic reports; its full8boss700run was rerun, restoring baseline evidence; r57archive hash remains78163450c7385abac3fc844073254313aa9fbb0e4264e919eb3f8823986b96ce.

Future speed work: compile phase-specific cell plans and avoid repeated per-cell source-coordinate/empty checks. Cached pixels alone do not remove clipping, ECM composition, ownership or publication costs. Do not adopt as a speed improvement; user comparison is the purpose of this build.
"""
 (ROOT/'docs/r58_l5_preshift.md').write_text(doc)
 history=f"""

## 121 - L5 actor-local two-pixel phase trial, r58 (2026-11-05)

User requests implementing preshifted graphics/2px L5movement per existing boss update. Separate playable trial {archive.name}, SHA256 {digest}. Standardr57 andstock64KBcart unchanged. Original24pxspheres/80pxcore;25parts use0/2/4/6horizontal phases plus raster-row vertical offsets, bothflips, legal8x1pairs/nonblackcoverage. Ordinary8pxtravel spreadinto2px/axis eachworldupdate; larger scripted relocations retained. Native target/animation/attack scripts and chosenkeys/dualjoysticks retained. EnemyAI/collision remainscoarse; not independentbossIRQclock.

7152packedbytes expands9344rawphasebytes duringloading (2374061isolatedcycles), no bossentrance preparation. ReusesDOCK1paletteRAM andalreadycopiedDOCK6source shadow insideexisting512KB; exactprefix reconstruction/native-shadow/tail restore beforecachedbankleave. CodeDC50afterD87Ccopylimit andDBD0..DC50savedtail, cachehelper8C00, stateE200..E400. IRQdecoderusesDOCK2privatestack, distinctfromHOMEplayerstack. Fullmemorycontracts in docs/r58_l5_preshift.md.

Measured700worldupdate route26295r57->36061r58displayrefreshes (37.14%moreelapsed, boot/entranceincluded). Thus NOTa speedup; trialonly. Final480refresh held-input:141player ticks/138projectilephases/6worldupdates/8shortshots+1beam; separate stationarysingle-shot8worldupdates. Rapid15taps->14shots/noafter-releasebacklog. No universalFPS/captureclaim. Large opportunities remain incompiledphasecellplans/repeatedcoordinate/emptywork.

Final14frozenserialchecks:256phase/orientationnativepixelcases;256morecaseswith8IM2injections at5F/1F; exactcacheexpand/restore;700L5worldupdates/25actors/16075motionsamplesand2pxordinarytravelassertions;chosenkeys/bothjoysticks,8release+1beam,realdeath/respawn,title116,snake,4loaderfailures,single-shotorder,rapidqueueexpiry. Actualboss->gameover->cachedboss15890refreshes, onlyRTBOOT/LEVEL05mounted. Full8loads/ending/cache-onlyrevisit59431refreshes/128blocks/37221code+reverseaudits/15workspacechecks. Otherbosses1/2/3/4/6tested200updates,7/8tested700(laterarrival). Invulnerable/forcedvictorydiagnostics are notunassistedplayproof.72TAPpages/hash/XOR/rawreconstruction/strictchangedbytecontracts/ZIP/repro15filespass. Player/projectile/audio/IRQbank7afterE400byteidenticalr57. Hardware/PicoVideopending.

Developmentfailedcandidates/tests: physicalbankownershipconfusion rejected; slowin-frameunpack movedtoloading; emptycellI8Fearlyreturnrepaired; sharedcopyhelpersrelinked; stationarybranchzero bugcaughtbylivecoordinates; banked8CFDfalsehookfixed; restoreEIloadercorruptionfixed; testIRQIM0->actualIM2; L7probeextended; branchrangebuildfailure/staleimageprobeexcluded; previewPythonsyntaxfixed. r57diagnosticbaseline rewrittenduringinitialtrace restoredbyfull8boss700probe; releasearchivehashunchanged. No sourceZIP/reference/skillfilesmodified.

Images: build/diagnostics/l5_preshift_r58/comparison.png,baseline.png,candidate.png,baseline.gif,candidate.gif andindex.html. SixteennativeHOME captures perbuild; GIFusesemulatedupdatespacing andloops excerpt. ComparisonPNGvisuallyinspected, nothardwarephotos. All detailedoutcomes/evidencelimits in docs/r58_l5_preshift.md.

Deliverable build/fullgame/l5_preshift_r58/{archive.name}. CopyfullRTYPEfolder,reset,loadRTFULL.TAP;select5,thenB-release-Bingame. Keepseparatefromr57forcomparison.
"""
 state=f"""

## Latest experimental build: r58 L5 phase movement (2026-11-05)

User-requestedL5preshifttrial complete; standardrelease remainsr57. Separate build/fullgame/l5_preshift_r58/{archive.name}, SHA256 {digest}. Ordinarynative8pxL5steps now2px/axisperworldupdate,4horizontalphases+verticalrowrelocation,25parts,original24pxspheres/80pxcore. Larger scripted relocations retained. No newbossclock; matched700route37.14%slowerelapsed thanr57, so doNOTpresentasFPSspeedup/replacestandard automatically.

7152packed/9344expandedphasebytes warmed duringlevelinit, existing512KB, source-shadow/native-tail restoredexactlybeforecachedrevisits. Final256pixelcases+8IM2injections,700L5updates/25actors/16075motionsamples,controls/fire/death/title/snake/errors/order,actualboss-gameover-cachedboss andfull8cache/ending/revisitpass.72pages/strictownedbytes/ZIP/repro15filesverified. Otherbosscoverage200updates(1/2/3/4/6),700(7/8). All16framebefore/aftercapturesandnativeGIFs atbuild/diagnostics/l5_preshift_r58/index.html. Testhistory121/docs/r58_l5_preshift.md. Hardwarepending; r57archive,stock64KB,sourceZIPs/referencesunchanged. Nextperformanceopportunity:phase-specificcompiledcellplans, ratherthan repeatedcellmath/emptychecks.
"""
 for name,text,marker in [('TEST_HISTORY.md',history,b'## 121 - L5 actor-local'),('PROJECT_STATE.md',state,b'## Latest experimental build: r58 L5')]:
  p=ROOT/name;old=p.read_bytes();assert marker not in old,'Already recorded';p.write_bytes(old+text.encode('utf-8'))
 print('Recorded r58 trial',digest)
if __name__=='__main__':main()
