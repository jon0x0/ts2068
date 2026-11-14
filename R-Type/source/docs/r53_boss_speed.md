# r53: boss rendering and responsive movement

The standard build keeps the compact L5 artwork (24-pixel spheres, 80-pixel core). This release changes scheduling and drawing code; it does not enlarge bosses or replace graphics.

## Cause and scheduling

The old L5 shader disabled interrupts while composing cells through alternate memory banks. On the sustained movement/fire route it allowed only 59 player ticks in 480 display refreshes. Increasing the distance per tick did not fix the missing input opportunities.

The interrupt entry now keeps the interrupted PC/register pushes on their original bank's stack, switches to a separate HOME interrupt stack, and restores the original stack and bank before returning. The shader uses a temporary valid IM2 table while bank4 is visible. Its stack/bank transitions remain DI; visible cell processing can accept interrupts. The last vector-table byte temporarily uses an asserted-zero title-source byte; the normal vector and that byte are restored before returning.

HOME 5B60..5BBF is reserved for interrupt stack depth; 5B5B is the vector trampoline. The low gateway clone is not used as executable gateway code in gameplay. All live gateway calls remain at FBxx. Background capture has its own stack, and busy input-edge capture uses the interrupt stack, avoiding re-entry into the scene compositor or overwriting the main copy's stack.

An unrestricted player-redraw candidate was tested and retained locally under build/fullgame/boss_input_priority_r53. It improved input cadence but consumed too much scene CPU while moving. The standard build therefore samples inputs/fire edges on every accepted interrupt, including busy capture periods, while publishing movement on alternate available interrupts. Short fire edges queue without another player draw. Fine initial one-pixel steps and sustained five-pixel steps remain; native chosen keys and both joysticks remain combined. No fixed QAOP binding or input-mode menu was introduced.

## Less work on hidden geometry

L5's existing fully opaque cell rejection now happens before interrupt setup/source decoding. Within partly visible cells, an already opaque foreground row advances the source pointer without loading its source row, choosing its colours, or blending it. The forward/backward pointer step is selected once per cell. Unowned copies also select direction/flash once, rather than rechecking them for all eight rows. No new composition pass or full-screen overlap scan was added. Other bosses retain their native clipping and occupied-cell rejection; the shared palette optimization runs on cells that reach the draw path.

The same captured 25-part native L5 arrangement costs 1,242,620 cycles versus 1,274,247 in r52 (2.48% less, including interrupt setup). Source overlap-row decoding falls from 1,064 rows to 554. The synthetic 384-case corpus has 0.41% aggregate extra cycles because it includes cases where interrupt setup costs more than the available culling savings. These are draw-component measurements, not a universal frame-rate claim.

All eight levels also use a smaller native source classifier and colour lookup: high/low-byte bounds checks preserve BC/DE/HL, and redundant pushes/restores are removed. The public retained-token entry stays at the original per-level address, including the normal-black policy. Across 5,088 native draw cases drawn from every descriptor observed on the eight boss routes, measured CPU savings range from about 6% to 7%; direct and retained pixels/attributes/ownership match r52 exactly.

## Verification and limits

- 524,288 native source-classification checks: every 16-bit pointer on all eight levels.
- 384 independent compact composition/coverage cases, plus 384 byte-exact r52 comparisons across ownership, flips, flash and clipping.
- 7,565 injected interrupts, one at each eligible instruction boundary across sphere/core cells, all four orientations and unowned/overlapped drawing. Audio and input-scan stubs isolate stack/bank/register preservation here; real audio and input run in the separate game routes.
- 894 player component ticks plus retained-plane, frozen-copy, empty-backing and collision tests.
- Actual selected keyboard, both joystick ports, normal/charged fire, death/respawn, 116 title states, L1 snake, selected-level restarts, loader failures and full eight-level resident-cache/revisit circuit.
- All eight actual boss-preview routes run for 700 main updates. Death bypass is used for sustained performance routes; the separate death test uses real death/respawn.

Final movement/fire measurements and main-update counts are in build/fullgame/boss_speed_r53/validation_summary.json. Input responsiveness and scene animation are different measurements. Restoring interrupts also restores periodic audio/game timers that previously stalled; more input/audio work takes CPU time. Boss/world animation remains scene dependent and can still be slow. Neither a constant FPS nor a successful real-hardware test is claimed.

The standard package contains the complete matching RTYPE folder. Reset before loading RTFULL.TAP to clear resident older levels. Do not mix the older optional large-art LEVEL05.TAP with this release. Stock 64KB read-only cartridge and all reference projects remain unchanged. No additional diagnostic images were generated: the render-equivalence tests intentionally require unchanged graphics.


## Final standard-build measurements

Same 480-refresh held-movement/8-short-press/one-charged-hold route per level. Death bypass isolates sustained input. Main-update counts are included to distinguish input cadence from scene animation; restored periodic interrupts change timer/attack work, so they are not an identical-scene FPS benchmark.

| Level | Player ticks r52 / r53 | Short shots r52 / r53 | Main updates r52 / r53 |
|---|---:|---:|---:|
| 1 | 160 / 169 | 8 / 8 | 31 / 32 |
| 2 | 127 / 129 | 8 / 8 | 45 / 46 |
| 3 | 164 / 163 | 7 / 8 | 36 / 36 |
| 4 | 192 / 185 | 7 / 8 | 16 / 17 |
| 5 | 59 / 162 | 3 / 8 | 13 / 10 |
| 6 | 167 / 167 | 8 / 8 | 33 / 33 |
| 7 | 147 / 148 | 6 / 8 | 38 / 38 |
| 8 | 171 / 167 | 7 / 8 | 32 / 32 |

Full resident-cache/ending/revisit route: 53389 refreshes. L5 player ticks improve 2.75x; all eight short presses and the charged hold register on every level. Standard separate-stack low-water mark in the input/fire profiles is 5BA4, above the 5B60 reserved lower bound. L5 main scene animation remains a bottleneck; the update counts explicitly do not show an across-the-board animation-rate increase.

Package: `build/fullgame/boss_speed_r53/RType_TS2068_r53.zip`, SHA256 `13e5f302e757ea5a9ae9559d56fde44bad4afd4a06340cafd9baa984e8e93563`. Physical validation pending.
