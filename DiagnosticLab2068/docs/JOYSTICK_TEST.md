# Live joystick direction test

Choose **J Joysticks / EAR inputs** directly from the main menu. Help/P remains an alternate entry. Connect compatible TS2068 joysticks and move/press each control in turn.

Each port has a spatial pad: **Up above, Down below, Left/Right on their sides, Fire below**. A **green** label is active now; **cyan** means previously activated and currently released; **white** means unseen. Repeated presses keep switching green/cyan so intermittent contacts remain visible. All five indicators are independent: diagonals, direction+Fire and opposing directions can be displayed simultaneously. Test both ports together to check isolation. Raw hexadecimal bytes remain visible; FF means no active contact but does not establish joystick presence. EAR raw00/40 is shown separately.

Technical Manual §4.3 / Figure4.3-1 (printed105/PDF115) specifies active-low AY R14 bits0=Up,1=Down,2=Left,3=Right,7=Fire. Bits4-6 are unused. R7 bit6 is kept zero (input), and portF6 reads use A8=1 for player1, A9=1 for player2. The diagnostic selects each port independently, without strobing both together.

The display is a live observer, not an automatic joystick/contact certification. Several signals changing together can suggest shared wiring, connector or joystick faults; check expected diagonals before interpreting a combination as a fault. An electrically absent joystick can look identical to a released one. Release held keyboard keys, then press any key to return. A finite scan budget also bounds the observer.

Before transferring to3F00, the low-ROM bridge qualifies the expected first opcode and additive checksum of all96 helper bytes. A mismatch stays in ROM0 and emits family3 without executing the helper. This catches ordinary missing/wrong mapping and changed bytes; additive collisions, late opcode corruption or instruction-fetch-only electrical faults remain exposure. Guarded execution from ROM1 is an explicit dependency of this optional graphical observer, unlike the always-ROM0 minimal RAM reporter.

Tested history uses only the first attribute cell of each label: green or cyan becomes cyan on release. It is optional display data, never an address, counter or control-flow target. A live active input always selects green independently of history. Bad display RAM can spoil the history/colors but cannot redirect the scan or prevent bounded keyboard exit. Reopening the screen resets history. Cyan means an activation was observed, not that the direction or its contacts are certified good. Very brief changes between input samples can be missed; this is not a logic analyzer or debounced event logger.

## Implementation

src/modules.asm::input_joy1/input_joy2 saves the input byte in IXL, draws raw bytes with the cartridge font, and enters src/joystick.asm at fixed3F00. In the cartridge, HSR03 keeps ROM0 and ROM1 code visible and HOME5800 attributes writable. The helper paints five fixed6-cell rectangles from a ROM-resident bit/address table and returns to a ROM0 bridge **before** restoring HSR01. It never executes the next instruction from an unmapped bank, nor uses CALL/RET or RAM pointers/counts/history. In the HOME edition, both ROM regions are HOME and HSR remains00. The builder reserves3F00-3FCF for the helper in both images. Raw state and all control are registers/ROM; failed display writes can corrupt appearance but cannot change loop bounds or destinations.

scripts/verify_joystick.mjs covers all32 active-contact combinations independently on each port for both cartridge and HOME editions (64 per edition), exact active/released rectangles, isolation, release and keyboard cancellation, ROM-only opcode fetch, unchanged SP and mapping restoration. Both-port captures show Up+Right+Fire on port1 and Down+Left+Fire on port2. Physical joystick/connector behavior remains user-observed and has not been bench-qualified.

Sources: original Timex Technical Manual §2.1.6.6,§2.1.7,§4.3/Figure4.3-1 and schematic J5/J6/U14; Josef Jelinek’s TSRun machine/joystick model supplies independent emulator input bytes. No third-party joystick graphics are used.
