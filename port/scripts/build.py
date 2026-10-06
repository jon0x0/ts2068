"""Build the independent port kernel; never writes the saved demo."""
from pathlib import Path
import hashlib, json, re, subprocess

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / 'reference/original'
PIN = 'dc00bce37e5c5c7947369cf5040c10e4799f4a06'

def number(expr):
    # Only the literal/shift grammar actually used in STBLSINI; no eval.
    match = re.fullmatch(r'(\$[0-9A-Fa-f]+|[0-9]+\.)(?:!>([0-7]))?', expr)
    if not match:
        raise ValueError(expr)
    n = match[1]
    return (int(n[1:], 16) if n.startswith('$') else int(n[:-1], 10)) >> int(match[2] or 0)

def main():
    commit = subprocess.check_output(['git', '-C', str(UPSTREAM), 'rev-parse', 'HEAD'], text=True).strip()
    assert commit == PIN, 'Unexpected original source revision'
    assert not subprocess.check_output(['git', '-C', str(UPSTREAM), 'status', '--porcelain'], text=True).strip(), 'Original source modified'
    build = ROOT/'build'
    build.mkdir(exist_ok=True)
    text = (UPSTREAM/'WITT/STBLSINI.SRC').read_text()
    rows = [[number(d), number(v), int(s)] for d,v,s in re.findall(r'fdb\s+\(([^)]+)\),\(([^)]+)\),asrd([0-7])', text, re.I)]
    assert len(rows) == 9 and rows[-1][0] == 0
    (build/'sinistar-speeds.asm').write_text(''.join(f' DW {d},{v}\n DB {s}\n' for d,v,s in rows))
    (build/'sinistar-speeds.json').write_text(json.dumps(rows, indent=2)+'\n')
    original = (UPSTREAM/'SAM/SAMTABLE.SRC').read_text()
    tables = {}
    for label, end in [('SINETBL','* quadrant table'), ('QUADTBL','* rectangle to angle')]:
        block=original.split(label+'\tFCB',1)[1].split(end,1)[0]
        values=[]
        for line in block.splitlines():
            line=line.strip().removeprefix('FCB').strip()
            if not line: continue
            values += [int(v[1:],2) if v.startswith('%') else int(v,16) for v in line.split(',')]
        tables[label]=values
    assert len(tables['SINETBL'])==64 and len(tables['QUADTBL'])==15
    (build/'player-tables.asm').write_text('sines:\n DB '+','.join(map(str,tables['SINETBL']))+'\nquadrants:\n DB '+','.join(map(str,tables['QUADTBL']))+'\n')
    (build/'player-tables.json').write_text(json.dumps(tables,indent=2)+'\n')
    exe = ROOT.parent/'tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'
    subprocess.run([str(exe), '--dirbol', '--raw=build/bank4.bin', '--sym=build/symbols.txt', 'src/kernel.asm'], cwd=ROOT, check=True)
    bank = (build/'bank4.bin').read_bytes()
    assert len(bank) == 8192
    dck = bytes([0,0,0,0,0,2,0,0,0])+bank
    flat = bytes([255])*32768+bank+bytes([255])*24576
    assert len(flat) == 65536 and len(dck) == 8201
    (build/'sinistar-port-kernel.dck').write_bytes(dck)
    (build/'sinistar-port-kernel.bin').write_bytes(flat)
    source_files = ['WITT/VELOCITY.SRC', 'WITT/STBLSINI.SRC', 'SAM/EXECJNK.SRC', 'SAM/FUNCTION.SRC', 'SAM/MACROS.SRC','SAM/SAMTABLE.SRC','SAM/IRQ.SRC','SAM/SAMEQUAT.SRC','WITT/CHASE.SRC','WITT/SINI.SRC','WITT/DISTANCE.SRC','FALS/N1ALL.SRC','FALS/N1SYM.EQU']
    manifest = dict(stage='movement-kernel diagnostic, not playable', source_repository='https://github.com/historicalsource/sinistar', source_commit=PIN,
                    source_sha256={f:hashlib.sha256((UPSTREAM/f).read_bytes()).hexdigest() for f in source_files},
                    dck_sha256=hashlib.sha256(dck).hexdigest(), bytes=len(dck), table=rows)
    (build/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
