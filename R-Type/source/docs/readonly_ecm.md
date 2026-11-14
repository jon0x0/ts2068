Current first-screen fix and measured scan optimizations: [r14](r14_initial_terrain_speed.md).

r13 terrain motion correction: [coherent palette contract](r13_terrain_motion.md).

Current r12 changes and validation supersede historical details below; see [r12 graphics](r12_graphics.md).

# Read-only ECM cartridge r10

The PicoROM output is raw65536 bytes, in ascending8KB DOCK-bank order. The DCK
wrapper adds nine bytes: bank0 followed by eight descriptor values2 (ROM).
The SRAM r9 image is a different target and must not be programmed as this ROM.

To free the ECM plane at HOME6000-77FF, the old game workspace moves to
HOMEA600-BDFF. Immutable sprite data and descriptors move to ROM1 (6792 bytes).
Code and key/input state formerly inside that workspace move by4600hex;133
address relocations are recorded in the manifest. HOME5B00 sound workspace is
preserved: execution tracing showed it is actively used by sound effects.

Runtime mapping is ROM0+ROM1, all remaining chunks HOME RAM. Bootstrap copies
initial writable state before handoff. The35-entry sound pointer table is relocated too. HOME BE00 holds the video-mode shadow.
Existing7800 attribute buffer stores compact background palette tokens; bit7 of
the existing8100 dirty grid carries vertical orientation, with bit0 retained for
dirty status. Restore paths decode tokens into per-scanline ECM colours. This
avoids requiring a second writable6144-byte plane in cartridge space.

The original title/menu runs in mode0 with its existing colours. Gameplay uses
mode2. Level-one game geometry remains Spectrum-derived; full arcade replacement
art, native subsequent-level loading and512KB runtime integration remain work.

## Rebuild and validation

From the project root, with the existing extracted Spectrum baseline and TSRun
reference present:

1. `python scripts/build_ecm_native.py` rebuilds native compatibility and r10 SRAM.
2. Run `scripts/trace_readonly_layout.mjs` with modern Node (v24 was used), to
   regenerate the executed-address/workspace trace against that r9 DCK.
3. `python scripts/build_rom_ecm.py` builds the read-only candidate. Generated
   manifest records source r10 hash, relocations, format and final binary hash.
4. Modern Node: run `verify_rom_ecm_runtime.mjs`, `verify_rom_sprites.mjs`, and
   `verify_rom_background.mjs` from scripts/. They check8000 refreshes,3480
   foreground sprite cases and1160 background cases with8996 restores/erasures.
5. `python scripts/verify_terrain_edges.py --readonly --frame 1200` verifies all
   eight terrain phases in Fuse. Trail, key-selection and240 terrain-span CPU
   checks are additional diagnostics recorded in TEST_HISTORY.md.
6. `python scripts/publish_rom_ecm.py` publishes only if runtime/sprite/background
   reports and terrain probes match the exact candidate hash. It emits the raw
   `.rom`, identical `.bin`, and ROM-only `.dck`.

The runtime guard checks original game accesses to the old workspace, every
cartridge-code write attempt to mapped ROM, and actual bank-byte immutability.
TS2068 firmware makes8192 RAM-detection write attempts before cartridge entry;
these are ignored by ROM and counted separately. They are not game writes.

Physical hardware has not been tested. These checks validate level-one execution
in emulators and do not establish a complete eight-level cartridge release.

Final raw ROM SHA256:
`7b65726ad7a0649ef88238f7e12b744c01c2ed43e1c6e0c9d3a9c02c2f795d7b`

Final runtime:8000 refreshes,792 updates, zero game ROM writes, unchanged banks.
All eight Fuse terrain phases1200 match; keyboard setup and ship retrace pass.

## r10 colour and scroll additions

The shared `src/terrain_live_colour.inc` publishes after original8974 RL shifts,
using their existing DE/BC span bounds. Border0 stays untouched. A non-terrain
left spill cell inherits the entering terrain palette; its legacy attribute is
sky/actor data and must not be reused. Mixed terrain cells use the fine-phase
coverage mask. Whole-byte steps use unrolled flat copies; equal runs skip work.

ROM0 0200-08FF holds boss header tags;0900 onwards holds13 cached colour rows
(nine boss material rows plus four small-enemy ramps). The original raw level
sprite byte format is unchanged. The lookup covers enemy headers C4CE-D7F8 only,
excluding terrain. Read-only background tokens97-109 decode these added rows.
All55 nonzero entries of the70-slot level descriptor table are tested.
