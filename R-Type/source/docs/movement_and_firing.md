# Movement and firing investigation

The native 94F1 movement routine loads 7AA1/7AA2 and increments or decrements
one coordinate unit. Bounds are 1..28 horizontally and 0..19 vertically;
rendering and C0E4 collision lookup use those units as 8-pixel cells.
Thus one-pixel motion requires fractional coordinates, shifted bitmap/mask phases,
screen coverage/restoration, collision boundary handling and matching projectile
origins. Changing INC/DEC alone cannot provide this. A visual-only interpolation
would leave the visible ship and collision/weapon positions inconsistent.

The game polls native input at 865F once per complete main update. Its 868C loop
waits for 7A8A >=3 interrupt ticks, but expensive drawing can already consume more
than this. Reducing CP3 alone cannot fix CPU-bound scenes.

Normal fire is also a release action. 95A6 tests bit4 of 74FA and calls 9A2C
while fire is held or charge 7ABF remains nonzero. 9A31 branches to charging
while fire is held; 9A33..9A42 emits a small shot after release for short charges.
9AA2 handles larger charged shots. Quick release/press edges between main polls
can therefore be missed. 9D96 scans sixteen normal projectile slots and exits
when none is free; special projectiles have separate slot and timer limits.
These are source-derived explanations, not yet a captured reproduction of the
user's intermittent firing symptom.

Next implementation targets are more frequent edge sampling with a bounded queue
that preserves charged fire, and a fractional-coordinate ship renderer with
precomputed phases. IRQ sampling must preserve keyboard mapping, both joysticks,
AY register selection, bank state, registers and interrupt contracts. A held-fire
autofire substitution would remove normal charge semantics and is not equivalent.

The selected level5 96x96 core draws in 309200 T-states in an unclipped direct
normal-orientation primitive test, versus 159358 for the old64x64 core, about1.94x.
This is not a whole-game frame-rate measurement. Compiled bitmap/palette drawing
for this large component is a substantial optimization candidate. No movement,
fire or frame-limiter modification is shipped in the r43 artwork trial.
