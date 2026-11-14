from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/clean_player_r56'
def read(p):return json.loads(p.read_text())
def main():
 assert read(OUT/'final_run.json')['passed'] and read(OUT/'validation_summary.json')['passed']
 archive=OUT/'RType_TS2068_r56.zip';sha=hashlib.sha256(archive.read_bytes()).hexdigest()
 profiles=[read(ROOT/f'build/diagnostics/clean_player_r56/masked_L{i}.json')for i in range(1,9)]
 cache=read(OUT/'cache_progression_validation.json');component=read(OUT/'overlay_component_validation.json')
 history=f'''

## 119 - Stale organic-boss fragments around the ship, r56 (2026-11-04)

User reports sporadic L5organic-ball pieces around the player, cleaned only after delay. Reproduced by capturing a real L5native copy entry after100boss updates and comparing the native slow copy with an IRQ-moving player against a clean reference. Empty metadata0/3 cells still contain stale boss bitmap/attribute bytes; they are not valid background. R54exact-mask publication preserved pixels outside ship coverage in those retained cells. Marking them player-owned3 then caused the native8x8cell copier to publish the entire cell, revealing old boss pixels outside the ship. Previous tests bypassed the actual slow native copy and did not cover this empty-to-owned transition.

Newcache preparation zeros only unowned0/3 bytes in its existing10column x64raster patch, in both retained planes and backing. Top aligned to8rasterlines so newly marked character cells cannot copy unsanitized lines above/below the player. Occupied scene cells are preserved. Cleanup reuses exactclean OLD64byte underlay captured by lastpublication into WORLD instead of per-byte banked resampling; normal/moving/frozen cases pass. Newengine2423bytes vsr552427; onlyE400..ED7F changes acrossall9regions. Artwork, boss shaders/sizes, palette assets, playerphases/settings/keys/joysticks, timedplume/audio, independentprojectiles and cache/loader/gate code byte-identical to r55. Stock64KBROMunchanged.

Focused45cases neutral/eightdirections xfiveinterruptintervals: baseline695unexpectedpixel-bytechanges, fixed0. Audio/input/star callbacks stubbed to isolate copy composition, artificialIRQs never nest. Two cases lose one existing star byte each inside sweptshipcoverage, separately recorded, not claimed fixed; snapshotmetadata atthatstar is0. Initialfourright-moving timings compare exactly afterfix.112edge/finephase empty/mixedowner backingcases preserve23936ownedbytes and616448outsidepatchbytes, clean47744unownedbytes. Frozen full894player ticks,128real-varied live-world mutationcases, unchanged componentmean/max{component['mean_tick_cycles']}/{component['max_tick_cycles']}cycles. Full16slotprojectiles/nativeglyph/ECM/hitonce/staleactor/cleanup tests and7565IRQ-boundary injections retained.

Development diagnostics: initial manual-IRQ fixture hung because it could inject a second artificialIRQ before the first returned; fixed harness and stubbed audio/input. Native moving stars initially differed from no-IRQreference; isolated starcallback to measure copy defect. Broader matrix found two missing starbytes inside sweptcoverage; report distinguishes these from addedbossartifacts, rather than hiding differences or claiming full-frame identity. First mixed-cache generator used Buffer.from(arraylike,callback), which ignores callback and generated zeros; corrected to Array.from thenBuffer.from, assert nonzeroownedcoverage, and corrected inherited128case varied-data generator too. The prior r55test's actual data did not match its intendedrandom description; it still tested outside-mask bit changes, but not this ownership defect. Finalreports rerun on corrected fixtures.

Images: build/diagnostics/player_ghost_r56/ghost_before.png, ghost_after.png, ghost_comparison.png. Rendered directly from captured emulatorHOME bitmap/ECM after the same copy/rightmovement; comparison sheet crop/nearest-neighbourzoom visually inspected, not hardwarephotos or newlyauthoredgameart. Capturestate/home/dock0..7, reference.home.bin, baseline.home.bin, clean.home.bin, copy_comparison.json, copy_clean_comparison.json and logs retained. No userphotos/referenceprojects/sourcearchives changed.

Finalfrozen serialrun: cache/copy,projectile/IRQ/capacity,894playercomponent,128worldchanges,movement,chosencontrols/bothjoysticks,8shortshots+1beam,realdeath/respawn,title116,snake,restarts3/8,loaderfailures,all8boss700worldupdates, full8diskload/ending/cache-onlyrevisit{cache['frames']}refreshes. Seven of8inputprofiles8shortshots+1beam; L5unshifted7shortshots+1beam, one-frame-shift L5restores8+1. Dedicatedfunctional8presstestpasses; shorttapsremainworkloadsensitive. r55shift1/2/4/8all8shots, so do not claim this exact miss was reproduced in r55. No control/projectile bytechanges inr56; redraw cost shifts relativeIRQ timing. (level,playerticks,projectilephases,worldupdates) {[(p['level'],p['ticks'],p['projectilePhases'],p['world_updates'])for p in profiles]}. Scripted boss/cache routes use invulnerability/forcedvictory for coverage, not successfulunassistedplay.72assetpages/XOR/rawreconstruction, strictoutside-enginebyteidentity andZIP integrity pass. Separate rebuildall9regions/playerengine byte-identical. Hardwarevalidationpending.

Deliverable build/fullgame/clean_player_r56/RType_TS2068_r56.zip SHA256 {sha}. ReplacefullmatchingRTYPEfolder, RESET beforeRTFULL.TAP; residentoldbankcode mustbe cleared. docs/r56_clean_player.md. Lesson: ownershipmetadata, not retainedpixelcontents, defines validscene; ECM8x1colour masks do not change native8x8dirty-copy granularity. Test the whole ownership/copy transition, and assert generated testdata actually spans occupied and empty states.
'''
 marker=b'## 119 - Stale organic-boss'
 assert marker not in (ROOT/'TEST_HISTORY.md').read_bytes()
 with (ROOT/'TEST_HISTORY.md').open('ab')as f:f.write(history.encode())
 state=f'''

## Latest packaged build: r56 (2026-11-04)

StaleL5boss fragments around player reproduced/fixed. Unownedretained0/3cells cancarryoldbossgarbage; markingplayerdirty3publishedwhole8x8cells outsideexactshipmask. Sanitizeonlyunownedbytes in10x64backingpatch beforeoverlay, aligntop8rows, retainownedscene. ReuseOLD64cleanunderlay forcleanup; engine2423vs2427bytes, ordinarytickcostunchanged. OnlyE400..ED7F differsr55all9regions; playerfine/heldmotion, independentprojectiles, art/boss/audio/gates/cache unchanged.45nativecopycases695unwantedbytechanges->0;112mixed/edgecachecases preserveowned/outsidebytes. Two sweptstarbytesmissing recorded separately. Correctedzero-filledtestdatagenerator;128realvariedworldcasespass.

Final894playercomponent/7565IRQ/projectilecapacity/control/fire/death/title116/snake/restart/error/all8boss700/full8cacheendingrevisit{cache['frames']}refreshes pass. L5unshifted7/8shorttaps, one-frame-shift8/8; dedicatedfiretest8/8, shorttap heavy-draw timinglimitation recorded.72pages/strictownedranges/TAP/ZIP and separateall9rebuildverified. Physicalhardwarepending; stock64KBROMunchanged. docs/r56_clean_player.md, TEST_HISTORY119, diagnosticbefore/afterimages under build/diagnostics/player_ghost_r56.

Deliverable build/fullgame/clean_player_r56/RType_TS2068_r56.zip SHA256 {sha}. Reset and reloadentirematchingRTYPEfolder beforeRTFULL.TAP.
'''
 with (ROOT/'PROJECT_STATE.md').open('ab')as f:f.write(state.encode())
 p=ROOT/'docs/r56_clean_player.md';s=p.read_text();s+=f'\nFinal full resident circuit: {cache["frames"]} refreshes. All eight bosses passed 700 updates; seven input profiles detected eight short shots and one charged beam; unshifted L5 detected seven plus one beam, and one-frame-shift L5 detected eight plus one. ZIP SHA256 `{sha}`.\n';p.write_text(s)
 print('Recorded r56:',sha)
if __name__=='__main__':main()
