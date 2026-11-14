R-Type TS2068 r72 - reviewed artwork, current-size disk game

Reset and replace the complete rtype folder. Run lowercase rt.tap.
Keep the supplied files together; subfolders under /TAP remain supported.
This is the expanded512KB disk package. Existing stock64KB target is unchanged.

47reviewed source choices are incorporated at CURRENT r67 dimensions. No D-size
enlargements, new strip pitches or actor movement/hitbox coordinates are added.
L1body/head details; L2organic body; L3selected ship strips; L4bosses; L6heads;
L8boss are updated. Existing L6return-pose alias13 follows selected pose10.

EVALUATION HOLDS: L2_003/004/005/006 andL3_040 retain their r67 appearance.
Earlier review flags (L1snake16..19,L3_041,L7_051) and unreviewed assets also stay.
L5 andL7 complete level files are byte-identicalr67.

Packing limits: shared palette rows approximate some native cells. L3strips
retain their existing transparent CELL layout so new graphics cannot overlap
neighbouring features; isolated proposed pixels outside that layout are masked.
L4uses normal-intensity pairs because its existing fine-shift palette synthesizer
operates on the normal bank. Compiled L6/L8phase0 retains selected colours.
L2mouth colours are preserved exactly while palette IDs are reassigned.

Loader protocol, controls, audio, AI and movement are unchanged; asset bindings are updated. L4uses a retired immutable source
area of its three updated compiled bosses for one preload packet. Cache rows
stay at their previous targets. L6/L8 packed restart backups are relocated
with their asset packets and restore the exact previous native source bytes. Runtime code and visibility/clipping paths stay.
The legacy debug module still prints R38; report this package as r72.

Checks: all8boss checkpoints (L7needs700updates toreachboss), ordinaryL3
2000updates andL6poses, repeated cold/cached4/6/4/2/4/8/4/1 and6/8/6/8/4/6/8/1 jumps, pause,
keyboard definitions, L4/L6death/respawn, activeL2/L6LoadAll/title, Force andrapidfire.
All held-source/cache checks, deterministic30product rebuild, tapechecksum/
reconstruction andZIPintegrity checks pass. Hardware confirmation is pending.
Known L3hardware glitches are not claimed fixed by these artwork changes.

Controlled160update L2boss CPUcost isabout1.7percent above r67. This measures
world-loop CPUtime, not hardwareFPS or all-level performance.

Future conversion default derived from37reviewed families across6levels:
Brightness49 / Contrast65 / Saturation78 / Gamma1.13, actual RPC SierraLite.
Levels are weighted equally so the30L3families do not dominate. Explicit holds
and unreviewed choices are excluded. This default is for future work; individual
settings in this build are retained. src/rpc_default_settings.json records it.

Select1-8 at title or use Lthen number inplay. B-release-B previews theboss.
L at title or Shift-L during play loadsall, then returns to title. Initial
Shift-L queuesLoadAll. Keys remain user-defined; both joystick sockets active.
P pauses (Shift-P whenP is a defined game key); P resumes. Music toggle retained.
