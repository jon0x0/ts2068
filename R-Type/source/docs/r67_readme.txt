R-Type TS2068 r67 - L2 arcade boss upgrade, expanded RAM disk game

Reset and replace the COMPLETE rtype folder. Start lowercase rt.tap.
Do not mix LEVEL02.TAP / START02.TAP with an older package.
Select level2, start, and press B twice with a release between presses for
boss preview; ordinary level2 progression also uses the new artwork.

Selected192x104 RPC body: brightness44, contrast54, saturation71, gamma0.98,
Sierra Lite, normal black and bright nonblack pairs.18 compressed scenery
pieces reuse the old boss area. Four arcade-source weak-point poses replace
the old yellow mouth; native spawn and hitbox move together. Correct isolated
32px arcade worm heads replace neck-contaminated crops, centered within the
original40x40 gameplay box. Four two-pixel phases retained for each pose.

The scenery uses native scrolling and terrain ownership. All11 measured lower
boss bands move1pixel on each of31 consecutive updates during entry. Native
stop retained. This is completed-frame emulation evidence; physical video
presentation still needs a hardware check. Native collision logic is retained,
with the weak-point descriptor/spawn aligned; no claim of a full boss defeat
or full-level hardware playthrough.

Seven regression groups plus700boss updates pass: ordinary approach, cached
jumps, pause, keyboard setup, actual death/respawn, Load All. Other seven levels,
loader, boot, shared core and controls are unchanged fromr66. Existing stock
64KB target is unchanged. Remaining L3 hardware issue is still open.

Controlled160-update boss comparison:108338030 CPU T-states versus104523296
forr66, about3.65percent additional world-loop CPU time with the richer art.
This is not hardware FPS or a player-response benchmark.

Keys are defined by the game. Both native joystick sockets remain active.
P pauses (Shift-P if P is a defined game key); P resumes. L at title or Shift-L
in game loads all and returns to title. During play L then1-8 changes level.
Initial Shift-L queues Load All. Existing loading/verification feedback retained.

Review: build/graphics/l2_integrated_r67/index.html.
This integrates the selected L2 boss upgrade; some other enemy/scenery artwork
retains earlier conversions. An all-level RPC source inventory is prepared,
including identity-review flags. No unverified source matches auto-installed.
