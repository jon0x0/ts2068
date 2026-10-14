"""Build Leap V2 BASIC into bytecode, DCK and a physical ROM image.

Use --prepare once to recreate and assemble the audited Leap source variants.
Requires the workspace SjASMPlus build, WSL and a modern Node.js.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from convert_ts2068_basic import convert_file

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_NODE=Path(__import__('os').environ.get('CROWN_NODE') or __import__('shutil').which('node') or 'node')


def run(*args, cwd=ROOT):
    subprocess.run([str(a) for a in args], cwd=cwd, check=True)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',type=Path)
    ap.add_argument('--output',type=Path,default=Path('build/program'))
    ap.add_argument('--node',type=Path,default=DEFAULT_NODE)
    ap.add_argument('--prepare',action='store_true')
    ap.add_argument('--ts2068',action='store_true',help='Convert a numbered stock TS2068 BASIC listing first')
    ap.add_argument('--segment',type=int,help='Program index for multi-program listing exports')
    ap.add_argument('--allow-hardware',action='store_true')
    ap.add_argument('--udg-escapes',action='store_true')
    ap.add_argument('--profile',type=Path,help='Explicit program adaptation policy')
    ap.add_argument('--wide',action='store_true',help='Use a 16KB ROM bytecode window with display banking')
    ap.add_argument('--data-backend',choices=('inline','packed'),default='inline')
    ap.add_argument('--stream-source',action='store_true')
    ap.add_argument('--crown-test',action='store_true',help='Run scripted Crown gameplay verification')
    ap.add_argument('--no-run',action='store_true',help='Build without unattended execution; use for interactive programs')
    args=ap.parse_args()
    source=args.source.resolve()
    out=args.output.resolve()
    if not args.node.is_file():
        raise SystemExit('Pass --node with the path to a modern Node.js executable')
    if args.prepare:
        run(sys.executable,'scripts/prepare_leap_build.py')
        run('wsl','bash','scripts/assemble_leap.sh')
    if not (ROOT/'build/host/build/test_basic.sym').exists():
        raise SystemExit('Build the compiler/runtime first with --prepare')
    out.mkdir(parents=True,exist_ok=True)
    if args.ts2068:
        converted=out/'converted.leap.bas'
        report=convert_file(source,converted,args.segment,profile=args.profile,allow_hardware=args.allow_hardware,udg_escapes=args.udg_escapes,data_backend=args.data_backend,stream_source=args.stream_source)
        if not report['buildable']:
            for issue in report['diagnostics']: print(f'Line {issue["line"]}: {issue["code"]}: {issue["message"]}')
            raise SystemExit('Conversion has blocking diagnostics; no cartridge was built. See converted.leap.conversion.json.')
        source=converted
    export=out/'bytecode.json'
    host=ROOT/'build'/('wide-host' if args.wide else 'host')
    cartridge=ROOT/'build'/('wide-cartridge' if args.wide else 'cartridge')
    run(args.node,'scripts/leap_headless.mjs','compile',host,source,export)
    run(sys.executable,'scripts/package_leap_cartridge.py',export,'--output',out)
    # Convert the exact path using wslpath, then pass it as an argv item to bash.
    posix=subprocess.check_output(['wsl','--exec','wslpath','-a',out.as_posix()],text=True).strip()
    assembler=subprocess.check_output(['wsl','--exec','wslpath','-a',(ROOT/'tools/sjasmplus/sjasmplus').as_posix()],text=True).strip()
    run('wsl','--exec','bash','-c','cd "$1" && "$2" launcher.asm','leap-build',posix,assembler)
    run(sys.executable,'scripts/finish_leap_cartridge.py',out)
    if args.crown_test:
        run(args.node,'scripts/leap_headless.mjs','game',cartridge,out/'program.dck',out/'gameplay.json')
        manifest=json.loads((out/'manifest.json').read_text())
        manifest.update(source=str(source),verification='TSRun stock-ROM cartridge boot, repeated player/creature redraw bitmap and colour checks, potion and three level transitions passed; Fuse and hardware untested for this game')
        (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        return
    if args.no_run:
        manifest=json.loads((out/'manifest.json').read_text())
        manifest.update(source=str(source),verification='Compiled and packed; runtime not verified (--no-run)')
        (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print(f'Compiled and packed; artifacts in {out}; runtime not verified')
        return
    if args.wide or args.data_backend=='packed':
        raise SystemExit('Use --no-run for interactive/wide/packed programs, or --crown-test for The Crown; RAM-loader comparison supports the small inline build only.')
    run(args.node,'scripts/leap_headless.mjs','bytecode',host,out/'program.lbc',out/'ram-execution.json')
    run(args.node,'scripts/leap_headless.mjs','cartridge',cartridge,out/'program.dck',out/'execution.json')
    a=json.loads((out/'ram-execution.json').read_text())
    b=json.loads((out/'execution.json').read_text())
    if a['output']!=b['output'] or a['arenaFree']!=b['arenaFree']:
        raise SystemExit('RAM and cartridge runs differ')
    manifest=json.loads((out/'manifest.json').read_text())
    manifest.update(source=str(source),verification='RAM load and stock-ROM AROS cartridge boot agree under headless TSRun; Fuse/hardware untested')
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Verified matching RAM/cartridge runs; artifacts in {out}')


if __name__=='__main__':
    main()
