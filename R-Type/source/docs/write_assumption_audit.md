# Memory-write compatibility audit after r41

The r41 failure was not a missing graphics conversion. Original Spectrum code
could attempt writes into0000..3FFF because ROM silently ignored them. Writable
DOCK RAM made those side effects destructive. Treat memory permissions, calling
contracts, and bank views as porting requirements, alongside ROM services/ports.

Completed initial scan:
- scripts/audit_write_assumptions.py triages528write-like instructions in the
  existing5483-instruction partial native disassembly. These are candidates,
  not528bugs. Two LD(BC),A sites:9C3E (fixed), BF3C (star attribute destination
  derived from row metadata, merits continued runtime bounds checking).
- Apparent direct LD(0000),HL atF8DD belongs to the obsolete beeper player and
  its operand is self-modified atF8C4. It is not evidence of another live bug.
- audit_writes_progression.mjs checks all8192DOCK0bytes against each correct
  bank image at every active input update. All8stages, ending/restart and second
  cached circuit pass3406checks. Initial comparison used warmLEVEL01 marker
  against coldBOOT and correctly failed; fixed expected baseline toBOOT.
- The tested assertion is now also in rocket_fix_fixture.mjs, so future normal
  validation uses it. No r41 binary/package bytes changed in this follow-up.
- Existing watch_rocket_l3.mjs traps the first actual low-bank write during the
  long rocket route, including transient writes that a frame-boundary hash could
  miss. Both complementary checks should remain.

Next bounded passes, not yet claimed complete:
1. Record every indirect store/block-copy destination on cold boots and extended
   native play across all8levels; protect executable banks, IRQ vectors, stack
   margins and immutable tables, with explicit loader/selfmodification allowances.
2. Test all weapon states and transitions: powerups, attached/detached Force,
   missile/rocket variants, sustainedfire, death/continue, cachehit/cachemiss.
   Fast forced-victory stage traversal does not cover all native behaviors.
3. Expand disassembly/runtime coverage through level-specific indirect dispatch
   and script handlers; audit read/write ports, ROM entrypoints, overlapping copy
   loops, clipping and register/flag contracts. Partial static reachability is
   triage, never proof of absence.
4. Run both read-only DCK/PicoROM and writable expansion-RAM models. Marking a
   bank ROM in an emulator can hide precisely this class of hardware defect.
5. Preserve failing long routes and stop on the first corruption, not the last
   visible crash. r40's divergence should not have been discounted as a death-
   bypass artifact without tracing it; it was the reproducer that exposed r41.
6. Keep integration tests boot-realistic: isolated renderer tests that manufacture
   a valid reversal table or clean buffers can hide initialization failures.

Reproduce initial passes: python scripts/audit_write_assumptions.py and Node
scripts/audit_writes_progression.mjs. Results build/diagnostics/write_assumption_audit/
static.json and build/fullgame/rocket_fix_r41/write_audit_progression.json.
No new confirmed defect found by this bounded follow-up; hardware confirmation
of r41 remains pending.
