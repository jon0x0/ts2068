"""Validate the canonical test registry and generate its human-readable catalog.

This checks documentation contracts, not diagnostic firmware or target hardware.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_file(relative):
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT), f'Path outside project: {relative}')
    require(path.is_file(), f'Missing referenced file: {relative}')
    return path


def heading_slug(text):
    return re.sub(r'[^\w\- ]', '', text.lower()).replace(' ', '-')


def validate(registry):
    require(registry['schema_version'] == 1, 'Unsupported registry schema')
    ids = [t['id'] for t in registry['tests']]
    require(len(ids) == len(set(ids)), 'Duplicate test ID')
    require(len(ids) > 0, 'Empty registry')
    for t in registry['tests']:
        tid = t['id']
        require(re.fullmatch(r'[A-Z]+-\d{2}', tid), f'Invalid ID: {tid}')
        for field in ('name', 'area', 'algorithm', 'observables', 'failure_interpretation',
                      'control_flow_exposure', 'execution_policy'):
            require(isinstance(t[field], str) and t[field].strip(), f'{tid}: empty {field}')
        require(t['firmware_status'] in registry['firmware_status_values'], f'{tid}: status')
        require(t['prerequisites'], f'{tid}: missing prerequisites')
        require(set(t['prerequisites']) <= set(registry['capabilities']), f'{tid}: unknown prerequisite')
        require(t['recovery_profile'] in registry['recovery_profiles'], f'{tid}: unknown recovery')
        spec, anchor = t['specification'].split('#', 1)
        source = safe_file('docs/' + spec).read_text(encoding='utf-8')
        anchors = {heading_slug(line.lstrip('#').strip()) for line in source.splitlines()
                   if line.startswith('#')}
        require(anchor in anchors, f'{tid}: missing specification heading {anchor}')
        for location in t['host_support']:
            file, _, symbol = location.partition('::')
            path = safe_file(file)
            if symbol:
                require(re.search(r'^def ' + re.escape(symbol) + r'\(', path.read_text(encoding='utf-8'), re.M),
                        f'{tid}: missing host function {symbol}')
        require(isinstance(t['firmware_locations'], list), f'{tid}: firmware locations must be list')
        if t['firmware_status'] in ('partial', 'implemented'):
            require(t['firmware_locations'], f'{tid}: implemented requires real firmware locations')
        for location in t['firmware_locations']:
            require(isinstance(location, dict), f'{tid}: firmware location needs path and symbol')
            safe_file(location['path'])
            require(location.get('symbol'), f'{tid}: missing entry symbol')
        for evidence in t['validation_evidence']:
            require(evidence['kind'] in ('host', 'emulator', 'hardware'), f'{tid}: evidence kind')
            require(evidence.get('result') and evidence.get('configuration'), f'{tid}: incomplete evidence')
            safe_file(evidence['path'])
            if evidence['kind'] in ('emulator', 'hardware'):
                require(re.fullmatch('[0-9a-fA-F]{64}', evidence.get('image_sha256', '')),
                        f'{tid}: target evidence needs image SHA256')


def inline(text):
    return text.replace('|', '\\|').replace('\n', ' ')


def build(registry):
    tests = registry['tests']
    counts = {status: sum(t['firmware_status'] == status for t in tests)
              for status in registry['firmware_status_values']}
    host_count = sum(bool(t['host_support']) for t in tests)
    lines = [
        '# TS2068 diagnostic test catalog', '',
        'Generated from [test-registry.json](test-registry.json) by '
        '[build_test_catalog.py](../scripts/build_test_catalog.py). Edit the registry, then regenerate this file.', '',
        f'The registry contains {len(tests)} tests and diagnostic UI modules. '
        + 'Firmware status counts: ' + ', '.join(f'{status} {count}' for status, count in counts.items()) + '. '
        + f'{host_count} entries reference existing host support; host support is not a target implementation.', '',
        'The algorithm below describes the intended implementation unless firmware locations are populated. '
        'Empty validation evidence means no per-test emulator or physical acceptance evidence has been recorded. '
        'Implementation and validation are separate: code can exist while target validation remains pending.', '',
        'Every entry must obey [FAULT_CONTAINMENT.md](FAULT_CONTAINMENT.md). '
        'Declared control-flow exposure identifies limits that qualification cannot eliminate; exposed advanced tests remain separately selectable.', '',
        '## Inventory', '', '| ID | Test | Firmware | Existing host support |',
        '|---|---|---|---|']
    for t in tests:
        anchor = heading_slug(t['id'] + ' ' + t['name'])
        lines.append(f"| [{t['id']}](#{anchor}) | {inline(t['name'])} | {t['firmware_status']} | "
                     f"{str(len(t['host_support'])) + ' references' if t['host_support'] else 'None'} |")
    lines += ['', '## Prerequisites', '']
    for key, description in registry['capabilities'].items():
        lines.append(f'- **{key}:** {description}')
    lines += ['', '## Recovery contracts', '']
    for key, description in registry['recovery_profiles'].items():
        lines.append(f'- **{key}:** {description}')
    lines += ['', '## Test definitions', '']
    for t in tests:
        lines += [f"### {t['id']} {t['name']}", '',
                  f"**Firmware status:** {t['firmware_status']}. **Prerequisites:** " + ', '.join(t['prerequisites']) + '.', '',
                  '**Implementation method:** ' + t['algorithm'], '',
                  '**Observables:** ' + t['observables'], '',
                  '**Interpretation limits:** ' + t['failure_interpretation'], '',
                  '**Recovery:** ' + t['recovery_profile'] + '.', '',
                  '**Execution policy:** ' + t['execution_policy'] + '.', '',
                  '**Control-flow exposure:** ' + t['control_flow_exposure'], '',
                  f"**Specification:** [Detailed design]({t['specification']}).", '']
        if t.get('implementation_notes'):
            safe_file('docs/' + t['implementation_notes'])
            lines += [f"**Actual implementation and remaining scope:** [Implementation record]({t['implementation_notes']}).", '']
        if t.get('source_credits'):
            lines += ['**Source credits:**', '']
            for credit in t['source_credits']:
                lines.append(f"- {credit['author']} — [{credit['title']}]({credit['url']}), {credit['archive']}. {credit['usage']}.")
            lines.append('')
        if t['firmware_locations']:
            lines.append('**Firmware locations:**')
            lines.append('')
            for location in t['firmware_locations']:
                lines.append(f"- [{location['path']}](../{location['path']}) — entry `{location['symbol']}`.")
        else:
            lines.append('**Firmware locations:** None yet.')
        lines.append('')
        if t['host_support']:
            lines += ['**Existing host support:**', '']
            for location in t['host_support']:
                file, _, symbol = location.partition('::')
                lines.append(f'- [{file}](../{file})' + (f' — `{symbol}`.' if symbol else '.'))
            lines.append('')
        if t['validation_evidence']:
            lines += ['**Validation evidence:**', '']
            for evidence in t['validation_evidence']:
                lines.append(f"- [{evidence['kind']} {evidence['result']}](../{evidence['path']}) — {evidence['configuration']}.")
        else:
            lines.append('**Validation evidence:** None recorded for the target test.')
        lines += ['', '**Required acceptance work:** ' + '; '.join(t['required_validation']) + '.', '']
    lines += ['## Updating a test', '',
              'Keep IDs stable, record actual source/entry symbols when implemented, and attach evidence for the '
              'exact image and configuration tested. Use [TEST_IMPLEMENTATION_TEMPLATE.md](TEST_IMPLEMENTATION_TEMPLATE.md) '
              'for the register, mapping, algorithm and recovery details of nontrivial firmware. Retire an obsolete ID '
              'instead of assigning it to a new algorithm. Record meaningful behavior changes in [CHANGELOG.md](CHANGELOG.md).', '']
    return '\n'.join(lines)


def main():
    registry = json.loads((DOCS / 'test-registry.json').read_text(encoding='utf-8'))
    validate(registry)
    output = build(registry)
    (DOCS / 'TEST_CATALOG.md').write_text(output, encoding='utf-8')
    print(f"Validated {len(registry['tests'])} unique test IDs, specifications, host references and implementation/evidence contracts.")
    print('Generated docs/TEST_CATALOG.md; this is documentation validation, not firmware validation.')


if __name__ == '__main__':
    main()
