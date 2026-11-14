R-Type TS2068 r63 - selected level-six artwork

Replace the whole RTYPE folder with this package, reset, then load RTYPE/RTFULL.TAP.
Keep all files together; do not mix releases. The folder may be inside another TAP subdirectory.
Requires the expanded 512KB disk-loading setup. This is not a stock 64KB cartridge image.

Level 6 now includes the accepted darker 32x32 walking-head artwork and cyan-rim
machinery with fuller red lights, small white glints and lower magenta shading.
The small side lights flash too. Lighting switches on immediately with the native
actor animation cycle; it does not reproduce the slow arcade brightness ramp.
The larger machinery keeps its native rendering origin to avoid blending its
shading over the existing mount. All other levels retain r62 assets and behavior.

Gameplay asks you to define keys. Keyboard and both native joystick ports work together.
1-8 selects the starting level. During play, L then a number changes level.
Shift-L preloads missing levels; loaded levels remain resident. Double-B previews
boss encounters. M toggles music. Existing pixel player movement is retained.

Validation: scripted L6 gameplay, all selected pose/light states, redefined keyboard
and both joysticks, repeated cached/cold jumps, full preload/resume, L6 death/respawn,
and Force attach/detach/recall/pickup checks. These are emulator checks, not a new
physical hardware pass. The previously reported L3 terrain-edge issue remains open.
The stock 64KB cartridge target is unchanged by this disk release.
