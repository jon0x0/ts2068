# R-Type TS2068 project rules

- Read PROJECT_STATE.md and TEST_HISTORY.md before changes.
- Preserve original ZIPs under arcade/ and spectrum/; generated files belong in build/.
- Keep Elite, Sinistar, TSVideoCodec and speech2ay reference projects unchanged.
- Maintain both a 64KB stock-TS2068 cartridge target and a TSPico target using the
  already-proven full 512KB RAM. Share gameplay and asset tools where practical.
- Graphics quality is a primary requirement: exploit legal 8x1 ECM pairs and
  compare vertical palette variation, Sierra Lite, ordered and coherent policies.
- Reuse the Sinistar masks/phases/composition experience; do not assume masks
  solve shared-cell colour conflicts or that retained images eliminate scrolling cost.
- Keep native compatibility patches separate from bank/copy logic and graphics.
- Native joystick ports and keyboard should work together without a mode choice.
- Verify Spectrum ROM calls, interrupt vectors, bank/stack visibility and I/O.
- Prefer deterministic scripted emulation. Do not require manual Fuse operation.
- Generate DCK/BIN from scripts, with static contracts and actual RAM checks.
- Record every diagnostic image and test outcome in TEST_HISTORY.md.
- Distinguish asset previews, static viewers, playable gameplay, hardware tests,
  and measured animation/streaming performance. Do not conflate these milestones.

- Current release entry point: scripts/release_latest.py; read docs/CURRENT_RELEASE.md.
- Preserve the hardware-confirmed r99 archive and enforce version-only identity for r100.
- Reserve the complete L5 DOCK4 IM2 page8F00..8FFF and its temporary9000 endpoint; never place UI/code/art there.
- Keep relocated L5 key/font at8B30/8B70 outside compositor variables and8BF0 row scratch; use src/l5_ui_release.asm.
- Audit ALL cold/runtime gateway references when relocating code. Test early level selection during loading as well as cached transitions.
- Test all256 vector targets; distinguish actual IRQ return probes, fixed-FF emulation, hardware confirmation and gameplay tests with game-over bypasses.
