# r61 responsive loading and level-jump repair

Expanded-memory disk build, retaining r60 gameplay/rendering and the approved blue-armour small walkers. Stock 64KB cartridge and reference projects are unchanged.

Startup shows the logo and number selection before asset transfers. Each START file carries 48 1KB fragments for immutable pages 0/1/4/5/6/7. RTCORE carries 22 common pieces. Number selection is polled during transfers and settling, but switching waits until the current header/data pair drains. Runtime LEVEL files retain eight 8KB pages. Completion flags are set only after the final readback/alias verification; missing flags require a load.

L, release, number starts the requested level. The original implementation returned to 8659, halfway through the old world update. It skipped 8640's ECM initialization, 8721's object/terrain reset and 8BAE's ship setup. The corrected stack continuation enters 8640 after native selection/checkpoint setup, including same-level restarts. This avoids retaining old actor and screen state.

Shift-L snapshots the current HOME context into banks 2/3 of three other slots, excluding current/resident loader slots; the loader fills only immutable pages and restores the original game, registers, stack, bitmap and ECM. AY volumes are saved/muted/restored. All-resident requests do not read disk.

The combined preload/jump regression exposed a native lifetime bug: C496 calls FDAA, an interior entry five bytes into the popup at FDA5. Earlier relocation redirected FDA5 only; loader context in FDAA then ran as instructions. A write to bank0:161B (INC D replaced by zero) was trapped. Redirect C496 to low 000D, the corresponding entry in the relocated popup. The r61 builder applies this compatibility fix separately to boot and all eight levels, including the shared cold C000 prefix. Static scanning covers unconditional and conditional CALL/JP operands into FDA5..FDE8 across the executable source ranges. Two byte-pattern matches are explicitly excluded after checking instruction boundaries: L2 D55B is the FC operand of AND FC; L6 C732 is the DC operand of JP E6DC. Neither is a call into popup code. This is why a byte-exact snapshot alone does not prove borrowed memory is safe: every live entry point must also be redirected.

Regression scripts use actual mainline key input and actual post-transition world updates, not just successful transport or selected-level flags. Repeated routes cover fresh loads, cached returns, L5's different dispatcher, same-level restart, and an explicitly invalidated level that must reload. Post-jump HOME captures are rendered separately from asset previews. Hardware confirmation remains pending.

Build: scripts/build_responsive_startup_r61.py. Checks: scripts/run_startup_r61_checks.py. Packaging: scripts/finalize_startup_r61.py. See the generated validation summary for the completed checks; do not infer a full new all-boss performance sweep from loader checks.
