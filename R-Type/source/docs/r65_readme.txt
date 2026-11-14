R-Type TS2068 r65 - expanded RAM disk game

Copy the complete lowercase rtype folder into /TAP (subdirectories supported).
Start rt.tap (lowercase). Replace the whole previous game folder and reset.
Data file names remain uppercase; keep all files together.

Keyboard keys are defined by the game. Both native joystick sockets operate
alongside the keyboard. Hardware fire uses active-low bit 7, including start.

Pause: P. If P is one of your defined gameplay keys (for example QAOP), use
Shift-P to pause so P still moves the ship. Press and release P to resume.
PAUSED appears onscreen. Gameplay/music updates stop, AY volume is muted,
and the original bitmap and ECM cells are restored exactly on resume.

Load All: L at the title, Shift-L during play. Completion returns to the title
with the eight levels resident. Start again normally. L then a number retains
the existing in-game level override. Level assets are loaded only when needed.

Key setup: Enter opens the native key-definition screen. The stale table-clear
call into the reused Force helper has been redirected to native zero-fill.

This release fixes hardware joystick fire and adds pause/title return. The
remaining small stationary L3 terrain fragment is NOT confirmed fixed.
Scripted L3 checks have not reproduced the photographed hardware fragment.
The 64KB cartridge target is unchanged by this expanded disk release.

Emulator validation is recorded in TEST_HISTORY.md; real-hardware recheck is
still needed. Do not mix files from older releases with this folder.
