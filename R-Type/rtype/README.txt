R-Type TS2068 r161 - normal-black title, score and preparation displays

Replace the complete rtype directory, reset, and start rtype/rt.tap.
The directory can be inside a subdirectory of the TAP folder. Keep the 20 TAP
files together. Uses 512KB expanded RAM to cache all eight levels, or loads
one level at a time on demand. Individual stock64KB cartridges are separate.

Bright black remains a valid hardware colour. This release fixes game-produced
bright black where normal-black space/paper is intended. The normal animated
score colours remain. TAP score paths and L7 preparation text are corrected;
the title initializer keeps ECM active while copying the native attribute plane.
No emulator palette flattening is required. No asset rescaling, bank relocation,
new buffers or gameplay/collision changes. Valid nonblack bright ECM pairs stay.

ENTER defines gameplay keys; suggested movement O P Q A, fire SPACE and Force
ENTER. Keyboard and native joystick work together. L then1..8 changes level;
Shift-L preloads levels; B, release, B jumps to the current boss with pickups;
M toggles music; Shift-P pauses (plain P also works if not a selected game key).

Validation: all8 cold-loaded title/score/gameplay frame audits;14 cold/cached
transitions, cold L1/L5 firing, displayed-frame projectile collision including
negative controls, L5 boss160updates/all256IM2targets. Actual IRQ return probes
at0/255; remaining targets identical. Scripted emulation, not hardware or full
all-boss playthrough confirmation. Previous archives and stable r99/r100 intact.
