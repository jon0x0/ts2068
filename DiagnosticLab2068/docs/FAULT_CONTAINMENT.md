# Diagnostic fault containment contract

Crash avoidance is a primary acceptance requirement. An ordinary failed RAM bit, missing interrupt, stuck input, failed AY response or unusable display must become a bounded diagnostic result or a skipped dependent test. It must not become a hang, an uncontrolled jump, or a return through suspect memory. This is a requirement for future firmware, not a claim that the current specifications have been demonstrated on hardware.

## Keep diagnostic control in ROM

The test scheduler, timeout loops, first-fault recovery and minimal reporter must use ROM code and a register-only control path. Treat HOME RAM as test data or optional richer state. Keep critical continuations and first-fault data in reserved CPU registers through destructive phases. Never use a RAM-resident return address, function pointer, code pointer, loop bound or HSR value without a bounded/validated interpretation. Clamp counts and addresses independently of target data; a failed RAM byte must not extend a loop indefinitely or move it outside its assigned range.

Register-only startup alone is insufficient: using a tested HOME stack later can still crash if it develops an intermittent fault before RET. Therefore the default RAM, banking, soak and recovery control paths must remain stackless. Prefer fixed ROM jumps and explicit continuation states. A corrupted optional history/UI buffer is discarded, not used to reconstruct execution. Guard bytes are supporting checks, not proof that future stack operations will be safe.

Any optional stack-based renderer/helper must be documented as having an additional failure exposure. Keep it out of the minimal safety-critical scheduler and reporter. Detect bad state through integrity checks where possible, then enter ROM recovery through a fixed JP without POP/RET. Do not advertise arbitrary mid-instruction RAM corruption as software-recoverable.

## Dependency and state rules

- Independently qualify each resource; do not substitute a single RAM-passed flag for block permissions.
- If a required resource is missing or newly suspect, return NOT RUN or LIMITED, retain the failure, and continue independent tests.
- Write complete known control-port values at ownership boundaries; afterward validate masks against the current PC/vector/workspace contract. Hardware readback is evidence, not the authority for recovery.
- A mapping transition must never deliberately hide its executing opcode stream or any enabled handler. Verify data before transferring execution into another ROM chunk.
- Keep interrupts disabled outside isolated, qualified interrupt tests. No unconditional HALT or wait for a presumed frame counter.
- Place a software instruction budget on all waits, retries, encoded data decoding and keyboard/accessory phases. Absolute clock failure cannot be bounded by CPU software.
- Never reserve screen/workspace RAM permanently from testing. Switch to register-only control before destructive coverage of it.
- Discard invalid UI/log state. Preserve a compact current first fault in registers and repeat border/beeper codes when richer output is unavailable.

## Isolate interrupt testing

Where practical, test interrupt arrival using a ROM vector and a handler that transfers to a fixed ROM checkpoint rather than returning through the interrupted RAM stack. The checkpoint discards/reinitializes the interrupt phase's stack position and restarts a known bounded phase; it does not resume arbitrary interrupted computation. Hardware interrupt entry still writes the PC to the selected stack, but this basic test need not read that saved PC to choose its continuation. Audit unintended writes and register ownership explicitly.

Tests of genuine RETI/RETN, arbitrary interrupted-work resumption, IM2 tables in HOME RAM and Sinistar-like stack switching introduce additional RAM-dependent control paths. Keep them separate from the basic interrupt-arrival test, require fresh block qualification and state their residual mid-run corruption exposure. Do not enable those paths automatically merely to make a full test appear more comprehensive.

## Recovery sequence

Each routine has an explicitly audited error exit appropriate to its current mapping. On a detected recoverable fault, preserve compact fault fields in registers, DI, restore a known ROM execution anchor without hiding the current instruction stream, inhibit further frame interrupts where safe, restore mode 0 for FE border reporting, and lower speaker/tape or mute AY as the remaining output paths allow. Quarantine suspect blocks and discard any active RAM stack. Report before attempting another independent phase.

A HOME EXROM gateway must restore DOCK while still executing entirely from verified HOME. It cannot use the generic DOCK recovery sequence while DOCK is absent. Every distinct mapping family needs its own documented fixed-jump recovery route. If the gateway's opcodes fail during execution, passive ROM-only hardware cannot guarantee recovery.

## Expected fault behavior

| Injected fault | Required behavior if CPU and active ROM remain usable |
|---|---|
| RAM stuck bit, alias, sporadic read/write error | Latch address/expected/observed/error mask; identify suspect path; complete or stop a bounded phase; retain minimal reporting |
| Firmware workspace/log/canary corruption | Abandon rich state/stack through fixed ROM JP; retain current register-held fault; enter LIMITED reporting |
| Display RAM corruption or wrong video mode output | Do not depend on text or redraw success; use normal-mode border/beeper codes if those outputs remain functional |
| No IRQ or bad inhibit behavior | Finite test expires and reports FAIL; scheduler continues with interrupts disabled |
| Stuck keyboard row/key or disconnected keyboard | Automatic tests continue; guided test remains incomplete/cancellable; no endless release wait |
| AY missing, wrong register values, silent output | Bounded register result/user observation; no dependency on AY to run other modules |
| Missing tape edges or accessory | Timeout or NOT RUN; no unbounded header/data wait |
| Corrupt encoded ROM data or RAM-held count | Independent length/address bounds stop decoding; no destination overflow or arbitrary jump |
| Bad HSR readback or selected data | Restore known shadow mapping while anchor remains available; log selection/read-path failure; skip unsafe execution transfers |
| Pause/stop during soak | Poll at bounded safe boundaries, record incomplete phase, restore reporting state; remain in diagnostics |

## Unavoidable limits and exposed tests

Software cannot guarantee recovery when the CPU stops clocking, reset/power fails, cartridge opcode fetch becomes corrupt, an active ROM anchor disappears, or a bus fault prevents instruction execution. Passive LROS also cannot report faults that prevent OS handoff before entry. Border and beeper share SCLD dependencies, so failure of both can prevent notification even when code continues.

RAM-resident EXROM gateways, data-qualified ROM execution-transfer tests, and advanced interrupt return/stack tests have narrower but real exposure: the hardware under test participates in instruction or control-flow fetches. Document this exposure per registry entry and keep these modules separately selectable. Skip them if their prerequisite checks fail. Qualification reduces risk but does not prove a component cannot fail during the next instruction.

Do not call all hangs “unavoidable.” A loop waiting forever for IRQ, a RET through an intentionally overwritten stack, a target-controlled count without bounds, or an unsafe bank transition is an implementation defect. Those are prohibited.

## Acceptance evidence

For every implemented test, inject its recoverable faults and verify a defined error/limited/timeout result rather than a crash. Include late workspace corruption, corruption during reporting, no interrupts, stuck keys, absent AY/tape response, mapping-data mismatch and corrupt stream/count cases. Capture the exact image hash, configuration, recovery PC/mapping, bounded completion/cancellation behavior and fault output. Check safety-critical code for implicit stack operations and RAM-derived indirect branches. Host registry checks cannot substitute for emulator and physical evidence.
