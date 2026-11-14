R-Type TS2068 r64 - native machinery fit, title preload and bolt cleanup

Replace the whole RTYPE folder, reset, and load RTFULL.TAP. Keep the files together.
The folder may be inside another TAP subdirectory. Requires the expanded512KB disk
setup. This is not a new64KB cartridge image; the stock cartridge target is unchanged.

At the R-Type title screen, L loads all missing levels, then returns to the title.
During play, Shift-L loads all missing levels. L then1-8 still jumps to a level.
1-8 selects the starting level. Loaded levels remain resident. M toggles music.
The game asks you to define keys; keyboard and both native joystick ports cooperate.

Level6 machinery now draws only its moving component in the original16x32 footprint.
The fixed mount is no longer duplicated in each sprite. Red/white/magenta flashing
and the accepted darker32x32 head sprites are retained.
Level7 has ECM material highlights for25 native frames, including the walkers.
Their native dimensions and animation are preserved. Walking-head family18-22 uses
accepted arcade-derived artwork at native24x24. The other shading upgrades retain
native drawings; they are not claimed to be newly matched arcade replacements.

A reproducible projectile cleanup bug is fixed: repeated redraws could discard the
ownership masks and leave screen-fixed bolt fragments. The fix also preserves stars
added to bolt bytes. The user-reported L3 hardware photograph has not been reproduced
frame-for-frame, so please recheck that scene. L3 terrain and enemy art are unchanged.

Validation details are in validation_summary.json. Emulator verification is distinct
from physical hardware confirmation. Replace the entire folder rather than mixing
r63 andr64 files.
