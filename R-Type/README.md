# R-Type Remastered for the TS2068

A ZX Spectrum conversion remastered for the Timex Sinclair 2068, with selected
arcade-derived artwork, extended 8x1 colour shading, native joystick support,
AY music and effects, smoother player motion and enhanced boss presentation.
It belongs to Remastered games, Spectrum ports and arcade-derived conversions.
Original game: Irem; Spectrum edition: Electric Dreams / Software Studios.

[Play in the browser with TSRun: Virtual DPad (phone touchscreen) or keyboard](https://jon0x0.github.io/ts2068/R-Type/play/)
| [Project page](https://jon0x0.github.io/ts2068/R-Type/)
| [TSRun archive](downloads/RType_TS2068_TSRun_r163.zip)
| [Eight 64KB cartridges](downloads/RType_TS2068_64K_cartridges_r163.zip)

## Full-game disk download

[Download the TSPico archive - r161](downloads/RType_TS2068_TSPico_r161.zip).
Extract into the SD card `/TAP/` directory, preserving the complete `rtype/`
folder. Reset and launch **`rtype/rt.tap`**. All 20 loadable TAP files are
already included in that folder; do not mix files from different releases.
The disk edition loads and caches levels in 512KB RAM. The disk stays at r161. Browser/individual cartridges are r163, including the cleared-cell paper fix.

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

r163 is the current eight-cartridge release. All eight software acceptance suites,
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


r161 fixes unintended bright black in title, score, preparation and restored backgrounds. Bright black remains a valid colour; the emulator palette is unchanged. Software verified; hardware confirmation pending.


r162 fixes stale coloured blocks beside the moving/firing ship. [Cause and verification](CLEARED_CELLS_R162.md). Disk archive unchanged at r161.


r163 fixes the obsolete REWIND SIDE2 prompt after game over on later-level cartridges. Resident replay is automatic through the title screen. [Details and verification](CONTINUOUS_RESTART_R163.md). Disk stays at r161.


r163 fixes the obsolete REWIND SIDE2 prompt after game over on later-level cartridges. Resident replay is automatic through the title screen. [Details and verification](CONTINUOUS_RESTART_R163.md). Disk stays at r161.
