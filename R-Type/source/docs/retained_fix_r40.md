# R40 retained-bitmap initialization correction

Replace the entire RTYPE folder, load RTFULL.TAP, and play normally. This is a
gameplay correction candidate, not a request for another diagnostic capture.
The earlier Caps Shift+D / Space diagnostic remains available on levels2-8.

The conversion reset the owner/dirty tables and retained colour plane without
clearing the retained pixel plane. Existing snapshots contain loading-header
bytes at retained6000 and stale content elsewhere. R40 explicitly resets the
160x256 playfield pixels at every ECM game initialization, before world drawing.
It clears6000..6FFF and the lower128bytes of each7000..7700page:5120bytes.
The interleaved native workspace in the other halves of7000..77FF and7800..7FFF
is preserved. It does not clear the whole8KB bank. Code runs once per start/
restart/load initialization, adding no ongoing frame-scanning cost.

New helper at HOMEFCC8 (verified unused FF padding), preserving AF/BC/DE/HL and
mapping; existing init wrapper0DC0 calls it after native86C3. Cold sourceDCC8
installs it once and common HOME7 keeps it across cached level switches. Previous
creature, normal-black, disk/cache and transition fixes remain. R39 completed-
frame capture is not included; no additional capture is required for the already
confirmed persistent hardware lines.

Reproduce python scripts/validate_retained_fix.py. Poisoned retained pixels:
old initialization leaves5102nonzero bytes; corrected initialization leaves0,
on all8levels. Independent helper tests prove exact preservation of every other
byte in the workspace bank and original register/bank/front-plane state.
All8-level progression, ending/cached revisit, selected3/8 restart, error controls
and packaged pages pass. Natural keyboard/collision test30000refreshes completes
2435updates,52ship starts,51death entries with continued progress. A deliberately
death-bypassed late run went invalid around7500refreshes; no claim is made that
the artificial invulnerability path is valid or that this hardware symptom has
been reproduced/fixed in that diagnostic run. Earlier versions remain available.

Hardware verification of the reported line artifacts is still pending. This
fix addresses a concrete initialization omission; do not equate that regression
test alone with proof that every reported hardware artifact has the same cause.

Superseded by r41: the late diagnostic divergence was traced to an actual native rocket write into writable DOCK0. See rocket_fix_r41.md; do not dismiss it as merely a death-bypass artifact.
