"""Bind mixed-load catalog records to completed emulator evidence, not hardware."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
build = ROOT / 'build'
evidence = json.loads((build / 'load-verification.json').read_text())
sha = hashlib.sha256((build / 'diagnostic-v02.dck').read_bytes()).hexdigest()
assert evidence['result'] == 'PASS' and evidence['image_sha256'] == sha
destination = ROOT / 'docs/validation' / ('load-' + sha[:12])
destination.mkdir(parents=True, exist_ok=True)
for name in ['load-verification.json', 'soak-verification.json', 'keyboard-verification.json',
             'suite-verification.json', 'manifest-v02.json', 'diagnostic-v02.dck',
             'diagnostic-v02.bin', 'load-symbols.txt', 'symbols.txt',
             'load-config-active.screen', 'load-warning-active.screen', 'load-running-active.screen']:
    source = build / name
    if source.suffix == '.json' and name != 'manifest-v02.json':
        data = json.loads(source.read_text())
        assert data.get('image_sha256') == sha, (name, 'stale evidence')
    shutil.copy2(source, destination / name)
for name in ['src/load.asm', 'src/load_low.asm', 'src/diagnostic.asm', 'src/modules.asm',
             'scripts/build_suite.py', 'scripts/verify_load.mjs', 'scripts/capture_load_ui.mjs',
             'build/keyboard-rom.asm', 'build/keyboard-scan.asm', 'docs/SINISTAR_LOAD_TEST.md']:
    target = destination / 'source' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / name, target)
path = ROOT / 'docs/test-registry.json'
registry = json.loads(path.read_text())
algorithms = {
 'SOAK-03': 'Configurable ROM-only mixed-load batches: all48K address-hash/March and data-only PUSH/POP, ECM fetch, fixed DOCK signature/isolation traffic, normal-refresh spacing, bounded IM1 entry and frequent synthetic Speech2AY-style R0-R12 writes/readbacks. Eight independent toggles, baseline/all presets, one-batch/continuous, six-second status/count and guarded new-key stop. IRQ sink BFFD/BFFE receives deferred DI-only00/FF tests. Advanced real-return bursts are separately confirmed, not destructive-March resumption.',
 'LOAD-01': 'Real PUSH DE/POP BC data-only pairs sweep every byte4000-FFFF using address-derived complementary bytes; D1-rich data and5ED0/BFFF vicinity included. DI pairs; enabled loads interleave every256 bytes. Popped data never chooses PC/SP/continuation; fixed SP reset and ROM JP recovery.',
 'LOAD-02': 'Explicit R warning/release/new-R opt-in, IM1 or freshly readback-qualified257-byte IM2 table7A00 and JP7B7B; qualify5E70-5ED0/BFE0-BFFF, then bounded5F00 foreground accesses with real saved-register/audio-stack frame IRQ returns,5E70 saved-SP comparison/fixed restore,78DF mapping shadow, AY R0-R12 traffic and safe D1/51 banking. At batch end only; excluded from concurrent destructive March and default Full/soak. Late saved-PC/table/opcode corruption can defeat recovery.'
}
for test in registry['tests']:
    ident = test['id']
    if ident in algorithms:
        test['firmware_status'] = 'implemented'
        if ident == 'SOAK-03':
            test['prerequisites'] = ['rom_execution', 'home_mapping']
        test['algorithm'] = algorithms[ident]
        if ident == 'SOAK-03':
            test['algorithm'] += ' Menu groups N/C as configurable duration before Begin test with S/R; the selected complete duration phrase is green. Option4 explicitly names60Hz screen interrupts; S uses bounded checkpoints and R confirms actual IRQ returns.'
            test['algorithm'] += ' Option6 now cycles quiet/busy slices, adds checked00/FF/55/AA traffic after hash comparisons, rotates0/2/6 video when option3 is enabled, and strengthens AY to14 writes with maximum/envelope amplitudes plus bounded beeper when option7 is enabled. P selects all power loads; quiet phases inhibit IRQ and use bounded ROM waits. RAM phase ordering and fixed-ROM recovery remain separate from auxiliary loads. Running notice explicitly announces TEST STARTED and six-second preparation.'
        if ident == 'LOAD-01':
            test['algorithm'] += ' Recovery latches the original observed POP/read byte through compare_observed, avoiding a second RAM read that could erase transient faults. Exact XOR masks for D0-D7 and multibit26h are verified in each RAM region.'
        test['specification'] = 'SINISTAR_LOAD_TEST.md#current-implementation-and-operator-controls'
        test['implementation_notes'] = 'SINISTAR_LOAD_TEST.md'
        symbol = {'SOAK-03': 'load_batch_start', 'LOAD-01': 'load_stack_begin', 'LOAD-02': 'load_return_start'}[ident]
        test['firmware_locations'] = [dict(path='src/load_low.asm' if ident == 'LOAD-01' else 'src/load.asm', symbol=symbol)]
        test['host_support'] = ['scripts/verify_load.mjs']
        test['observables'] = 'First RAM address/expected/observed/XOR region mask/phase and chip/bit pulses; auxiliary4/5/7 class/address-or-index/expected/observed/phase. No-fault stopped batch count wraps65536. Fault fields replace batch count; no persistent log. Analog output needs observation.'
        test['control_flow_exposure'] = ('Register-only ROM0/ROM4 scheduler, bounded option-independent loops and mapping; optional data PUSH/POP never RETs. Basic IRQ saved PC is write-only. CPU/ROM opcode, shared bus/clock/power failures remain unavoidable.' if ident != 'LOAD-02' else 'Fresh qualification reduces risk but saved PC/stack or IM2/trampoline corruption can derail execution before checker/recovery. This separately confirmed real-return profile is excluded from startup/Full/default soak. No guarantee of survival of arbitrary return corruption.')
        test['validation_evidence'] = [dict(kind='emulator', path=(destination / 'load-verification.json').relative_to(ROOT).as_posix(),
            image_sha256=sha, result='PASS', configuration='TSRun mapped64K DOCK; all256 safe slice masks, representative batches, D1 POP data loss, missing IRQ/bank/AY faults, UI cancellation and real IM1/IM2 return profiles. Physical timing/supply/thermal replication pending.')]
    if ident == 'SOAK-01':
        test['validation_evidence'] = [e for e in test['validation_evidence'] if e['path'] != (destination / 'soak-verification.json').relative_to(ROOT).as_posix()]
        test['validation_evidence'].append(dict(kind='emulator', path=(destination / 'soak-verification.json').relative_to(ROOT).as_posix(), image_sha256=sha,
            result='PASS', configuration='TSRun cartridge; six-second status dwell, guarded stop, first-fault/count/acknowledgement checks. Physical timing pending.'))
    if ident in ['KEY-01', 'KEY-03']:
        note = ' Cartridge fixed keyboard scanning now executes in ROM7 E000-E599 with ROM0 paint/exit bridges; HSR81 during scan,01 at exit; D/E/IX/AF alternate contracts unchanged. HOME keeps its scanner in HOME ROM.'
        if note not in test['algorithm']:
            test['algorithm'] += note
        location = dict(path='build/keyboard-rom.asm', symbol='keyboard_rom_scan')
        if location not in test['firmware_locations']:
            test['firmware_locations'].append(location)
        keyboard_path = (destination / 'keyboard-verification.json').relative_to(ROOT).as_posix()
        test['validation_evidence'] = [e for e in test['validation_evidence'] if e['path'] != keyboard_path]
        test['validation_evidence'].append(dict(kind='emulator', path=keyboard_path, image_sha256=sha,
            result='PASS', configuration='TSRun; all40 matrix contacts, exact rectangles, shared CAPS/BREAK, lost writes/history and exits with unchanged SP and audited ROM0/ROM7 fetches. Physical validation pending.'))
path.write_text(json.dumps(registry, indent=2)+'\n')
print('Recorded implemented load modules and immutable evidence', destination.name)
