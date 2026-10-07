# Bomb visibility and original explosion artwork — v26

The four original IEXPLO images in SAM/IMAGE.SRC now replace the provisional eight-fragment worker effect and the large Sinistar impact halo. FALS/N1ALL.SRC ExpObj/Plode selects this sequence; WITT/COLLISIO.SRC routes worker deaths and Sinibomb impacts through object killing/explosion logic. Descriptor center offsets are retained in a common 20×26 canvas. Colors are converted to TS2068 8×1 attributes; geometry is extracted without scaling. This does not implement the additional independently moving fragments from FragExp or the still-missing removal of Sinistar's body pieces.

Worker explosions retain the existing 32-physics-tick lifetime. Bomb impacts advance over four published pictures so they remain visible despite the lower display rate. The arcade uses Task4 scheduling for Plode; picture-paced bomb effects are an explicit display adaptation. A subsequent hit replaces the previous bomb impact effect. Neither effect waits, halts, or suspends game logic. The impact is anchored at the bomb's collision position in the scrolling world, not at a fixed Sinistar center.

The original bomb bitmap is preserved with brighter white/yellow ECM colors for visibility. A bomb cannot be consumed by collision before one picture has been published since launch. Holding B launches the next bomb on the next eligible physics tick after the previous hit or expiry, even while the old explosion is still animating. **There is still one live bomb at a time.** The arcade permits multiple simultaneous Sinibombs; a bomb pool remains needed to match that firing behavior. This revision primarily fixes visible pauses, missing bomb images, and a sound-related freeze; it does not claim a substantially higher average launch rate.

## Interrupt safety

The direct renderer temporarily borrows HOME D800 for its stack. Speech already prevented that path while active; SFX also maps DOCK6 in the ISR and therefore needs the same exclusion. The new pending/active SFX check prevents stack corruption. In both normal and fast mode, the saved v25 cartridge stalls in the controlled farther-range bomb fixture; v26 completes thirteen hits. The fixture keeps the pilot and Sinistar fixed, suppresses contact damage and removes rocks; it is a regression reproduction, not a natural-play performance average.

## Measurements

Close-range fast-mode fixture, held B, thirteen hits with hit-triggered roars:

| Measurement | v25 | v26 |
|---|---:|---:|
| Bombs appearing in a published picture | 10/13 | 13/13 |
| Mean picture interval | 297.8 ms | 174.1 ms |
| Longest picture interval | 417.1 ms | 215.7 ms |
| Mean launch interval | 271.7 ms | 268.8 ms |
| Longest launch interval | 400.0 ms | 364.3 ms |

Normal-mode close-range mean picture interval improves from 391.9 to 256.7 ms; mean launch interval remains approximately 280–283 ms. These demanding repeated-impact fixtures are still well below the 20 fps goal. The independent burst lets a new projectile and the prior explosion appear together.

## Storage and verification

The four source images share a 136-entry triple dictionary (408 bytes) and 312 one-byte cell indices, plus eight bytes of pointers. Source data occupies 728 bytes; a resident decoder expands and shifts the selected pose. Worker and bomb effects share the same data. The cartridge remains eight 8 KB banks (65,545-byte DCK including header).

Native tests cover all four explosion poses at eight horizontal shifts, worker and bomb decoding, bitmap/attribute comparison at every edge, speaking Sinistar overlaps, restoration, all eight speech clips, audio priority, bounce toggling, and the complete earned-ammunition win/restart/loss lifecycle. The scrolling test compares 1,451 pictures including 1,310 controlled cases; an additional 18,000-refresh stress run publishes 3,747 pictures. Both report zero late raster publications and zero ROM writes. Hardware remains untested.

Current SHA-256: `35c3ae356d07199a4a3e5fa5bcceff06c29090045da8e9e865cfe080be974d2b`.

See build/bomb-response-verification.json, build/gameplay-features-verification.json, build/assembly-scrolling-verification.json, build/stress-fast-verification.json and build/fast-playable-verification.json for hash-matched evidence.
