R-Type TS2068 r66 - expanded RAM disk game

Replace the complete rtype folder and reset. Start lowercase rt.tap.
Keep all supplied files together; subdirectories below /TAP are supported.

During initial loading, press Shift-L briefly to queue Load All. LOAD ALL QUEUED
confirms acceptance. Release the keys; the request remains latched even if you
select another starting level with1-8. The required startup assets and shared
core finish and verify, then all missing levels load before the title opens.

Stages: READING FILES; VERIFYING MEMORY (full RAM readback); PREPARING GAME
(memory/graphics setup). PREP RAM is the brief context preparation before
Load All. The big numeric counter remains visible while files transfer.

L at title or Shift-L during play also loads all; completion returns to title.
P pauses (Shift-P if P is a defined gameplay key); P resumes. Keys are defined
by the game. Keyboard and both native joystick sockets operate together.
All r65 joystick-fire and keyboard-setup fixes are retained.

This release changes loading, not gameplay artwork or geometry. L2 terrain
presentation and remaining Spectrum artwork are still under investigation.
Offline L2 geometry/arcade comparison: build/graphics/l2_geometry_review_r66.
The remaining L3 hardware fragment is also unresolved. Stock64KB unchanged.
Scripted emulator checks pass; physical-hardware confirmation is still needed.
