# Experimental native level-one memory contract

This 64KB cartridge runs original-graphics level one on Fuse TS2068. It does not
contain the complete game or the ECM renderer. Final colourful ECM and 512KB
TSPico editions remain targets. Source archives/reference projects are unchanged.

| DOCK chunk | Physical contents | Copy destination / runtime use |
|---|---|---|
|0 $0000|Native input at $1A00, otherwise FF|Persistent ROM during gameplay|
|1 $2000|Original/patch snapshot $6000-$7FFF|HOME3|
|2 $4000|Snapshot $8000-$9FFF|HOME4 via temporary HOME5 helper|
|3 $6000|Snapshot $A000-$BFFF|HOME5, including helper removal|
|4 $8000|AROS bootstrap/header|Resident only during transfer|
|5 $A000|Snapshot $C000-$DFFF|HOME6|
|6 $C000|Snapshot $E000-$FFFF|HOME7|
|7 $E000|Snapshot $4000-$5FFF|HOME2|

All external chunks are ROM. HOME chunks2-7 remain writable during gameplay.
AROS starts with EF specification, preserving lower HOME chunks. Bootstrap owns
DECR=0, DI. Copies use HSR10 plus source bit, with a different HOME destination.
There are no stack operations in those intervals, even when DOCK7 hides stack.
HSR10 is restored after each copy. HOME5 helper maps HSR04 while writing HOME4,
then maps HSR10 and jumps back into DOCK4. Cleanup HSR18 restores HOME5 fully.
Temporary screen stack bytes $58FD-$5900 are repaired before launch.

Final ROM instruction OUT($F4),A at $8632 clears DOCK4, leaving HSR01 (input ROM).
Next fetch is original HOME $8634. DECR0 means original 8x8 colour mode. SPFFFE,
I84, IM2, full original 257-byte vector table ->$8383 ->$BE23. EI precedes OUT;
interrupts are safe after the transition. A=1 is deliberate: $8696 loads A from
$C4B1 before any read of its incoming value. Other general registers/flags and
all49152 HOME RAM bytes match patched checkpoint. R/frame phase are not matched.
No persistent bootstrap helper or unverified RAM code cave remains.

## Input

$8B06 routes through ROM $1A00. That routine calls the selected original keyboard
decoder indirectly, then ORs both native active-low UDLRF stick states into the
original active-high L/R/D/U/fire bits. The keyboard's sixth action remains.
Native directions map bits0,1,2,3,4 to game bits3,2,0,1,4. Neutral adds zero.
Default original redefinable keys: Q left, W right, O up, K down, P fire, Space
secondary action. Original key redefinition remains; no joystick selection needed.
$C011 menu fire check also uses the merged routine, so native fire starts play.

AY register7 bit6 is cleared for port A input while preserving other mixer bits;
register14 is selected, then ports $01F6/$02F6 read both sticks. DI guards AY
selection/read; caller interrupt state is preserved. This routine leaves AY14
selected. Future audio code must select its own register for each atomic write,
respect port direction, and preserve video mode. Audio coexistence is untested.

## Reproducible checks

Run build_native.py --native-input, probe_native.py (byte-exact handoff),
verify_native_input.py (4096 isolated real-CPU cases), and probe_native.py
--frame 8000 --joystick-start. For live movement, capture frame1820 with
--joystick-start, then additionally --move 8 (port1 right) or --move 4 --port 2
(port2 left). Current injection window1800-1809 gives X8 neutral, X12 right,
X4 left; Y10. These are electrical input injections, not forced game state.

## Remaining work

Spectrum tape CALL $0562 at $8F2A must become a native level-content service.
The 64KB baseline fits one snapshot, not all eight original level payloads.
Original code/data in $7000-$77FF and transient $6000 memory conflict with ECM
attributes $6000-$77FF. Relocate/reorganize those owners before enabling ECM;
a native tile/sprite compositor must also resolve shared-cell palette conflicts.
Static audit is partial. No physical hardware, level-completion, ECM gameplay,
enhanced audio or TSPico game banking validation has been performed.


## r2 key-definition completion

$BFD0 calls ROM $1B00 instead of directly calling $C2C5. The wrapper calls the
original routine then waits for all keyboard keys released, preserving its
AF/BC/DE/HL result. This prevents a held final Enter immediately reopening key
selection and erasing the new definitions. It uses only existing writable stack;
no new game workspace. Both native sticks and keyboard remain concurrently active.
