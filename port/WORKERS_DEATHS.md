# Workers and destruction, v35

Native 64KB cartridge; existing artwork/audio and v34 title, score, and victory message retained.

Idle worker behavior follows WITT/WORKER.SRC EVADE: the worker intercepts the player when construction is finished or its primary mining target is unavailable, with a light velocity-reflecting bump on contact. Mining and crystal carrying retain precedence. Pursuit updates every other physics tick; contact recovery limits repeated bumps. Attract mode excludes the new harassment behavior. The single worker now replenishes after completion too. This is an adaptation, not the complete arcade population/mission system.

One worker is retained in BOTH normal and fast mode. Additional workers have not been implemented. Independent extra workers require their own world state, crystal ownership, shot collisions, radar markers and dirty rectangles; simply duplicating the sprite would be misleading. This cartridge is at its 64KB ceiling. The old diagnostic-only worker path was excluded from the playable build (source retained behind conditional assembly) to fit this increment; only small isolated ROM gaps remain.

Player death now hides the ship and runs six expanding paired explosion bursts across the screen before decrementing the life and respawning, or displaying game over. Sinistar's final hit triggers six paired bursts around the destruction area before the existing victory message. Both sequences take 96 physics ticks (~1.6 seconds), pause gameplay physics, and keep rendering and AY playback running. They reuse the original worker/bomb explosion images and SFX; active speech keeps priority. Cancelled in-flight bombs are counted as expired. No extra graphics slots are drawn in ordinary gameplay.

These are compact explosion adaptations. The original player-fragment simulation, Sinistar eating/spinning animation, dedicated two-part player-death sound, and arcade Sinistar warp/mutating-face transition remain unported. The two effect slots have independent animation timing, but bursts are paired rather than a larger independent explosion pool.

Memory: HOME 7BFB kind, 7BFC countdown, 7BFD wave; HOME 5E72..75 world center. These avoid the IRQ stack pointer at 5E70..71 and score magic at 5E77. Resident code ends at 9FF4; world code 5979/6000; effects bank 8097/8192.

Validation: native tests observe all six waves (13 player-death pictures, 15 Sinistar-death pictures), correct hidden-player state, life decrement/protection, victory, and worker approach from x100 to x84. Earned-ammo playable test passes mining, win, restart, all three lives, and game over. Frontend and gameplay feature tests pass. Fast render stress: 3596 pictures in 18000 refreshes (~12.0 fps for this deliberately varied test), zero late raster writes and zero ROM writes; prior v33 measured 3627 pictures, a difference under 1%. This is not a general gameplay frame-rate guarantee.

Preview GIFs use uniformly timed native published-frame captures, so timing is approximate:
- [Player death](build/death-sequences/player.gif)
- [Sinistar destruction](build/death-sequences/sinistar.gif)
