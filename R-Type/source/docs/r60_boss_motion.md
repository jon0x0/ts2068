# r60 candidate: boss motion and arcade walkers

Packaged expanded-memory disk trial: build/fullgame/boss_motion_r60/RType_TS2068_r60.zip. All17 consolidated emulator checks,72 tape pages,unchanged-engine/terrain contracts,ZIP CRC and32-file separate rebuild pass. Physical hardware validation remains pending. r57 remains the standard baseline; retain r59 for comparison.

Moving boss components use 0/2/4/6 horizontal phases and raster-level vertical placement. Native scripted targets and discontinuous relocations remain; this does not introduce an independent boss clock. L1's stationary large boss and L3's terrain-based giant ship retain their original placement. L4 needs independent histories for its three components, including components sharing one actor record.

L5 retains twelve alternating sphere spawn events rather than twenty-four. The native movement scripts remain unchanged. The existing core and sphere dimensions remain unchanged. This is intended to expose more machinery and reduce drawing work; actual gameplay and timing checks are required before drawing performance conclusions.

L1 large walkers use four genuine arcade walking poses, aspect-fitted to the existing 40x40 footprint before ECM conversion. Two firing poses were excluded. Small walkers receive arcade-derived ECM shading at their existing sizes. Sierra Lite, HSV saturation 2 and gamma 1.8 guide these conversions. This is a targeted upgrade, not a claim that all remaining enemies have been converted.

Important implementation lessons:

- A bank that appears free in isolated sprite tests may still contain terrain source tables. The rejected bank4 renderer/cache layout caused the native terrain writer at 9CB9 to interpret code as graphics and overwrite high HOME memory. The replacement must preserve the entire terrain bank on generic stages.
- Native I84 interrupts assume normal gameplay mappings. Foreign-bank painting needs its own valid raw interrupt vector and stack. The current generic vector table is D800..D900 in bank6, with raw entry 5B5B -> FD20. Bank6-hidden plan writes run with interrupts disabled.
- Cold boot copies more high memory than cached level restoration. Preserve the original native high tail separately, and restore the original native workspace before replacing its source bank with immutable phase assets.
- FD08 in bank7 is bit-reversal data, not the HOME publisher routine at the same CPU address. Patch only the actual HOME boot source.
- Per-level colour-ID tables must be retained independently. Palette previews do not validate sparks, explosions, or shared native renderer clients.
- Sustained gameplay, actual death/respawn, cached revisits, interruptions, clipping and foreground overlap must accompany pixel-only tests.

The first current sustained run passed levels 1-3. L4 reached 593 updates at the original 50000-refresh limit; a longer run is in progress to distinguish workload cost from a genuine stall. No release or speedup claim is justified by these partial results.

The first full sustained run with the actor-history fix completed all eight stages, but its final actor-count assertion rejected the supposed sphere reduction. E641 was the wrong native table; that modification was reverted. The corrected change filters alternating event35 spawns at column73 in the native L5 event stream. The core event24 and every other event remain. The checkpoint event pointer lies before the filtered records. The complete validation suite is being rerun against this correction.

The isolated native-effect fixture initially omitted the generic renderer installation performed by actual level loading. A trace showed the supposed compositor entry executing original bank5 source code and changing HL unexpectedly. Adding the missing installation makes all20,544 native effect cases match r57. During this investigation the shared return helper1FF7 was restored to its original mapping19; generic composition selects29 explicitly. The original fixture failure alone did not prove a runtime bank-return fault, so it must not be reported as one.

L4 remains a performance concern: its current phase fitting runs during painting. A future storage optimization could borrow more of bank5 only after native source copies, retaining a verified restoration path, to hold compressed offline phases. No such optimization has been validated in this candidate.

Final-candidate performance so far: actual L5 route700 updates25,606 display refreshes versus r59's35,862 (28.6% less elapsed emulated time). Actor histories verify13 parts includingcore. A matched held-input480-refresh sample has player163/projectile158 ticks versus r59's173/172; eight shortshots andonebeam stillpass. Faster totalboss simulation therefore doesnotmean every fixed-window IRQ/input countimproves. L4 remains63,800refreshes/700 updates. PhysicalFPS/unassistedbosscompletion have notbeen established.

Final validation: all8bosses700updates;15,875motion samples;L5core+12spheres;2084pixel/ECM/restoration cases;1164edgecases;100IM2cases/200injections;20,544nativeFXcomparisons;customkeys/bothjoysticks,8shortshots+beam,actualdeath/respawn,title116exactstates,snake,loadererrors,rapidfire/noafterburst andsingle-shotforwardorder pass. All7selectedboss game-over/replay checks pass700updatesbefore/after (L4total119901refreshes,L5total47156). Full8-levelending/secondcircuit60876refreshes,all8residentrevisitedwithoutdisk,36,931code/reversal audits,15workspacechecks. Progression forcesvictory toexercise loading; thisisnotunassistedcompletion proof. Delayedselectorpriming reached101712reads onstressroutes;firstselectedL2route neededonlytheprotocolminimum8afterstartupconsumedthetime delay.

NativegamePNG/GIFcontactsheet build/diagnostics/boss_motion_r60/all_bosses.png andindex.html visuallychecked;theseare16-updateexcerptsbeginning100updatesaftercheckpoint,notnecessarilythefinalboss'sfullappearance. Four-posewalkerGIF isasset-onlytiming. FullordinaryL1routeexercisedall4largeposesandall5smallframeIDs. No claimthatallminor-enemyartisfinished.

Install: replacecompleteRTYPEfolder,reset,loadRTFULL.TAP. Definethenativekeysasnormal;keyboardandbothjoystickscoexist. Numberselectslevelbeforestarting;B-release-Bingame previewsencounter;Mtogglesmusic. Stock64KBtargetunchanged. Nativeenemycollisioncellsanddiscontinuousscriptedrelocationsremain. L4costisexplicitlyexperimental;do notdescribeasageneralFPSupgrade.

Package SHA256:458a82915addb4ad98ebc8fe1558713807037fc1da32ecc239304cae56a2cb60.
