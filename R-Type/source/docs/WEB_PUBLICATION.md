# R-Type Pages publication

The r160 publication is staged in build/publication_r160/hub/R-Type/.
The staging script scripts/stage_web_publication_r160.py copies the verified
cartridges and isolated Berzerk TSRun snapshot from Sinistar play-dpad, preserves
its hash manifest, adapts native joystick bit7 and adds browser L+number level
switching. It does not modify cartridge bytes or reference projects.

The maintained frontend lives in web/. The staging script overlays these
reviewed files after adapting the isolated reference runtime.
The TSRun archive contains play/ and README.md; serve the extracted folder
with python -m http.server 8000 and open /play/. All dependencies are local.
Source and third-party attribution are included; original game input ZIPs and
historical build checkpoints are omitted.

Publish to jon0x0/ts2068 under R-Type/. Update the root generator categories
(Remasters, Arcade ports, Spectrum ports) and eight catalog rows, then run
python scripts/build_site.py in the hub checkout. Preserve unrelated projects.
The browser build uses per-level cartridges, not the disk/512KB loader. L+number
is a browser-level cartridge change and resets the chosen level. Physical
cartridges remain single-level. Shift-P is recommended because P is a suggested
movement binding; keyboard setup follows O/P/Q/A/Space/Enter prompts in-game.

Acceptance: verify all eight browser starts, HTTP resources, JS errors, real
key-definition, touch/native joystick fire, music, Shift-P, double-B, L+number
and desktop/phone layouts. Check all included TSRun hashes and cartridge bytes;
verify ZIP CRC and static relative links. Record screenshots/tests separately
from gameplay/hardware acceptance. Commit/push only the reviewed R-Type tree
and the hub/catalog updates. Check Pages deployment and public resource hashes.
