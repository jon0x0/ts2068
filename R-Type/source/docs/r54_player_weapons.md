# r54: projectile travel and player/exhaust spill

The reported stray graphics around the L5 player have a reproducible background-restoration fault. R53 fills a full five-byte-wide damage rectangle from a captured background during a scene copy. If the world has changed since that snapshot, it can republish old boss bits and attributes outside the player. A native component test changes one unrelated byte from A5 to3C and its attribute to2 after capture: r53 overwrites them with A5/7. The r54 test preserves3C/2.

Publication now uses the union of the actual old and new ship masks. Pixels outside it keep the live destination value; ECM cells with no ship coverage are untouched. Retained cleanup separately uses only the current ship mask, preventing the later cleanup from replaying stale surrounding pixels. This includes the cached ship's exhaust footprint. It does not invent new flame animation. Shared8x1 cells still have their normal two-colour constraint.

The existing one-pixel fine / five-pixel held movement and selected-key/native-joystick behavior remain. Masking introduces CPU work; inline accumulation/publication, full-byte fast paths and a short unrolled clear reduce its cost. The final component mean/max are recorded in overlay_component_validation.json; gameplay cadence is separately measured. No unchanged update-rate or universal FPS claim is made.

## Projectiles

The 16-slot normal/spread projectile updater now takes up to three original travel steps, then uses the original final draw and hit-resolution path once. An enemy/terrain owner at any tested step stops further travel. Friendly player/shot IDs and dirty cells do not block the sweep. Bounds are checked before metadata access. Each step retains the original native vector behavior, including its original two-character stride for normal shots. This is not a finer-than-original swept pixel collider.

Normal clear-space travel changes from 2 to 6 cells per world update. The actual native updater test verifies slot coordinates8->10 in r53 and8->14 in r54; the new final bitmap/ECM/metadata equal the original renderer at the matched destination. A single-slot example costs5823->6845 cycles, without three draws.4088 native helper cases cover directions, edges, intermediate enemies/terrain and friendly cells. Charged beams, companion weapons and other separate pools keep their prior timing. Projectiles remain on the world-update clock; this increases travel distance, not their redraw frequency.

## Memory ownership

Bank7 engine E400..ED7F uses its existing 2432-byte allocation. New 125-byte helper F080..F0FC fits below the backing pixels F100..F37F. The fixed centre-pose phase cache ED80..F07F and flipped L5 cache F380..F67F are unchanged.

| Purpose | Range, end exclusive |
|---|---|
| OLD saved underlay | F6C0..F700 |
| NEXT saved underlay | F700..F740 |
| Damage coverage | F740..F781 |
| Damage bitmap/attributes | F781..F803 |
| Row pointers | F820..F83A |
| Clean retained-world window | F83A..F87A |
| Collision map | F880..FB00 |

Maximum movement damage is13rows x5bytes. No source graphics, palettes, boss sizes, sound or native input compatibility code are changed. Projectile code uses statically empty low-bank gaps; banking/IRQ gateway/shader code is otherwise identical to r53.

## Verification

The final report distinguishes component checks from live emulation.128 live-world-change cases cover 8 horizontal phases, eight movement directions and fine/held steps; they check outside-coverage pixels and untouched ECM cells after publication and retained cleanup.894 normal player ticks, frozen backing, empty backing and collision checks remain. Slot capacity, native projectile rendering,7565 interrupt-boundary cases, selected keyboard/both joysticks, release/charged fire, real death/respawn,116 title states, snake, loader failures/restarts, all 8 boss 700-update routes and full resident-cache/revisit progression are regression gates. Region hashes are frozen across the final serial run.72 asset pages and archive integrity are verified before packaging.

The package is the standard compact 512KB disk game. Replace all matching RTYPE files and reset before loading RTFULL.TAP. Older resident levels or alternate-large-art files must not be mixed. Stock 64KB cartridge and reference projects remain unchanged. Physical confirmation is pending.

Future player/delta tests must change the background while a copy is outstanding, then verify both publication and retained cleanup. Static background equality alone missed this replay bug. Live screen pixels, retained pixels and clean saved underlay have separate ownership; a cached rectangle is not permission to overwrite live neighbors.

## Final measured build

Engine 2427 bytes; helper 125 bytes. Final player component mean/max 11346.3/49928 cycles versus r53's11132.0/48887. The added correctness work is small in that component after retaining the non-copy fast path and replacing old-mask compositor work with row copies.

L5matched movement/fire route: 158 player ticks /480refreshes versus r53's162; all8shortpresses and1chargedhold register. World updates10, same as the recorded r53route. This is a workload sample, not a universal unchanged-FPS claim. Full resident-cache/ending/revisit route 53981refreshes. All8boss700-update routes pass.

Package `build/fullgame/player_weapons_r54/RType_TS2068_r54.zip`, SHA256 `315178184438410255074c62c53f2e8ade9641fb641c2e46b87d478e7b73fa6e`. Physical validation pending.

Clarification: the separate flame-shaped sprite98 is intentionally timer-gated by native9577/7A98 during launch/respawn and a pickup effect. Native timer tests confirm it stops drawing at zero. This is distinct from cached-ship rear pixels and the stale-neighbour replay fixed here; preserve that timed behavior. See TEST_HISTORY117.
