# Firmware test implementation record template

Use this structure when a registry entry gains executable target code. Save substantial records under docs/tests/ with the stable test ID; link that record from the registry specification or an added implementation_notes field. Keep the registry algorithm and actual code behavior consistent.

## Identity and source

Test ID and name; algorithm revision; actual source paths and entry/exit symbols; shared helper IDs; image/build hash; whether the code is a ROM routine, a verified HOME gateway, or a future hardware-assisted module. State whether the implementation is complete, partial or experimental and what is omitted.

## Entry and exit contract

Register inputs, preserved/clobbered registers including alternate sets and flags; SP use; stack depth/guards; writable state addresses and qualification requirements; interrupt mode/state/vector/handler; HSR and DECR shadows and required masks; FE and AY state owned. Give a chunk map for each mapping change, showing active PC, stack, vector, code source and destination. Document fixed-jump fallback paths separately from normal return paths.

## Exact algorithm

Give loop order, patterns, seeds/polynomial, address ranges including endpoints, overflow/wrap handling, comparison formula, delay/counter method and any exclusions. Identify scratch/output storage and when it is retested. Explain which physical signals/functions are exercised and which are not. Include pseudocode or a flow table when it makes branching and dependencies clearer; refer to actual source for timing-critical instruction sequences.

## Results and attribution

Define pass/fail criteria, readback masks, user observations, unknown-ROM classification, first-fault records and error-counter saturation. Map errors to chip/bit/signal paths using verified schematic evidence. State competing explanations and what external observation would distinguish them. Do not claim precise thermal or analog results without measurements.

## Cancellation timeout and recovery

Apply FAULT_CONTAINMENT.md. State whether the default critical control path remains stackless and whether this test is separately selectable because it must execute qualified HOME or external code or exercise interrupt returns. Qualification does not eliminate intermittent failure of the next control-flow read.

Specify input polling points, maximum healthy-machine stop latency, incomplete-phase handling and resume policy. Document every timeout and error branch, the restoration order, notification channels and behavior if display/workspace fails. Identify faults that software cannot recover from, such as stopped clock or corrupted instruction fetch.

## Verification evidence

Record static audit results; emulator/tool version, machine/ROM/image hashes, injected fault and expected/observed outcome; and physical board/cartridge/TSPico configuration, peripherals, cold/warm conditions and measurements. Link saved logs and screenshots. Distinguish host data-format checks, target execution and physical electrical validation. List untested configurations and known limitations.

## Modification notes

Describe why the implementation uses this method, what timing/mapping assumptions a change must preserve, and the smallest relevant regression checks. Record changes to fault-code meanings or saved-result formats and their compatibility impact. Update the registry and CHANGELOG.md with the same revision.
