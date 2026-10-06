# 60-Hz Sinistar memory contract

The ROM-only DCK maps all eight cartridge pages. The AROS header enters at $8008. Resident code and star-delta payload share DOCK4; baseline HSR is $10. DECR remains $02 for ECM.

| HOME address | Use |
|---|---|
| $4000–57FF | Display bitmap |
| $6000–77FF | ECM color attributes, identical nonlinear row layout |
| $7800–780F | speech2ay state |
| $7810–782F | Tick counter, sequence pointer, frame counter, mapping and scratch |
| $7830–784F | Current 32-byte script record |
| $7A00–7B00 | IM2 vector table |
| $7B7B | ISR jump |
| $7B80 | Writable jump selecting the unrolled 3/7-byte bitmap loop |
| $7D00–7DFF | Staged star/edge XOR operations |
| Below $8000 | Stack, initial SP=$7FFF |
| $A000–BFFF | 256 × 32-byte script records, copied from DOCK3 at boot |
| $F000–F8B1 | 2,226 bytes of AY speech, copied from DOCK2 at boot |

ROM data allocation is recorded in `build/manifest.json`. DOCK0/1/5/6/7 can supply bitmap rows directly while both display planes remain HOME. Attribute streams may also use DOCK2 because their destination is in HOME3. Star/edge streams are copied to HOME $7D00 before writing bitmap pixels, allowing source DOCK2 as well.

DOCK3 is mapped only at startup, with interrupts disabled and no stack access, to copy the script into HOME $A000. Runtime never maps DOCK3. The ISR temporarily restores HSR=$10 before reading the HOME speech stream, then restores the saved source mapping. This permits DOCK7 graphics data without hiding speech during an AY tick. Code, state and stack remain visible throughout runtime banking. Mapping state is set before OUT, including when restoring $10, so an interrupt between the two instructions is safe.

Script records contain two seven-byte sprite descriptors, speech event/direction, two five-byte color-stream descriptors, and a six-byte star-stream descriptor/padding. Bitmap data contains pre-shifted raw rows. Color and star/edge operations contain a count followed by absolute address + nonzero XOR byte. All writes occur in HOME; no cartridge RAM or self-modifying ROM is required.

The build seeds the last frame's colors, stars and sprites before beginning frame zero, allowing an exact cyclic delta sequence. Each subsequent visible write is the final value for that frame. Raster safety is tested independently against TSRun's actual scanout; there is no hardware page flip.
