# R-Type TS2068 ECM full-game r25 candidate

Eight original native level payloads now run with per-level AY music and arcade-derived boss artwork. The TSPico build actively uses all512KB, with one64KB region per level. M toggles music without stopping sound effects or resetting the song. Native keyboard and TS2068 joystick input remain active together. Death effect65 is retained.

## Run

Extract RType_TS2068_ECM_fullgame_TSPico512_r25.zip. Copy its RTYPE directory to the TSPico SD root. Mount RTYPE/RTFULL.TAP using the normal TSPico controls and load it using the native Timex tape-loading command. Leave all16 RTFGxx.TAP volumes beside it. The BASIC wrapper runs the native loader automatically. Loading and verification take roughly110 emulated seconds in the conservative controller model; hardware timing is unmeasured.

The loader uses stock legacy MEMDOCK SRAM slots0,2,...14, paced port0E traffic, full response draining and eight read-only selector-priming accesses. It loads64 pages and performs a second complete readback sweep before launching. ERROR E2 means a checksum or distinct-region verification failed; reset before retrying.

The .ram512 file is a raw eight-region memory image for tools that explicitly support that layout. It is not a64KB PicoROM, DCK or tape. Per-level game_progression.dck files are diagnostic snapshots, not an alternative full-game SD loader.

## Graphics and music

Arcade source captures and an independent M72 sprite decoder supply the boss art. Both palette-preserving and colour-emphasized conversions remain under build/fullgame/converted/{preserve,chroma}; chroma is active. Gomander's terrain-based body is converted separately. The giant ship is reconstructed across several arcade captures, then fitted to the original strip-based boss renderer. Selected cramped frames use checked free level payload space. Original native movement/AI and gameplay structure remain; these are conversions into the Spectrum-derived engine, not the arcade engine or all arcade animation frames.

The accepted level-one arcade-derived terrain is preserved. Each level has its own palette theme, with separate arrangements for independent terrain groups. Colour transitions remain coherent during scrolling. Gomander's body uses a conservative32-row flesh palette; it remains a candidate for further visual refinement.

Eight2019 Goodboy/Tiboh level arrangements are integrated, one per level. All16 source entries were extracted and converted; the remaining eight are prepared assets, not additional event tracks currently selected by the game. MSX/CPC provenance of the arrangement is still uncertain. AY effects retain channel ownership over music. Music grammars are depth-limited to22 so their pending stack cannot overwrite player state.

## Verification and limits

All eight levels pass8000 refreshes of sustained native gameplay each. Every native enemy descriptor is checked through four flips, three clip positions and normal/damage palettes, comparing actual Z80 bitmap and ECM output byte-for-byte. All eight songs match source register shadows for two loops. M passes four held/released toggles in each level while effects remain audible and the song position continues.

Actual Z80 MEMDOCK transition code passes all eight region changes, preserving score and music preference. The native final-level ending runs and returns to level-one gameplay. Progression tests inject boss-victory countdowns and bypass player death; they do not constitute normal unassisted playthroughs or prove boss difficulty after artwork changes.

The actual native SD loader loads all524288 bytes exactly in the packet/TAP controller model, including plain/verbose replies and delayed SRAM selection. A deliberately aliased memory region is rejected by the second sweep. Physical TSPico and TS2068 execution has not been tested for this candidate.

The standalone64KB read-only output remains the accepted level-one r22 build: build/readonly_ecm/RType_level1_ECM_64K_PicoROM_r22.rom. Its bytes are not writable runtime workspace. All eight levels/art/music do not currently fit that build; r25 is a512KB TSPico release and does not claim a full-game64KB cartridge.

## Reproduce

Set RTYPE_TITLE_DELTA=1 and RTYPE_LEVEL_SELECT=1 and run python scripts/build_fullgame.py using the audited local source ROM/tape captures already documented in TEST_HISTORY.md. RTYPE_NODE can select a modern Node executable. Dependencies: Python NumPy/Pillow, sjasmplus and the read-only TSRun CPU/machine modules. Stage-specific builders and validators are listed by that orchestration script. The publisher checks report hashes before creating a versioned ZIP/image. Original source archives and reference projects remain unchanged.


Title update: narrow retained raster replacements use reusable shifted suffix silhouettes and settle final ECM colours after overlap clears. Four-pixel steps produce116 pictures in approximately3.76 emulated seconds, versus46 pictures in4.39 seconds in r22. Text star protection includes the upper menu lines and the copyright band. This is a specialized TSCodec-style replacement-window implementation, not a full-frame video stream.


Starting level: On the title screen, press1–8 to select a starting level. The line “1-8 LEVEL n” confirms it. Release the number and press joystick Fire or the original keyboard0 Fire key. Numbers select only; they do not start the game. Default is1. The selected starting level persists for the session and is used at each new game; normal level progression continues from that level. Selection is available in the full512KB package only.

The ZIP also includes Fuse-level-previews/Level_1.dck through Level_8.dck. Open the desired file and press Fire to test that stage without the SD loader. These single-level previews do not load the next stage after victory; title number selection is part of the full TSPico512 build.
