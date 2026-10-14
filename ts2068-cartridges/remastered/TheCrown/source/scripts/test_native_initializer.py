"""Check randomized native startup across seeds on the actual TSRun Z80."""
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
NODE=Path(__import__('os').environ.get('CROWN_NODE') or __import__('shutil').which('node') or 'node')
OUT=ROOT/'build/crown-combined'
seeds=[1,2,3,7,42,255,256,1024,4096,12345,32767,65535]
reports=[]
for seed in seeds:
    output=OUT/f'native-seed-{seed}.json'
    result=subprocess.run([str(NODE),'scripts/leap_headless.mjs','startup','build/combined-runtime',str(OUT/'program.dck'),str(output),f'--seed={seed}'],cwd=ROOT,capture_output=True,text=True,timeout=30)
    if result.returncode: raise RuntimeError(f'Seed {seed}: {result.stderr}')
    report=json.loads(output.read_text())
    reports.append({'ms':report['initializationMs'],**report['nativeChecks']})
assert len({r['dungeonHash'] for r in reports})==len(seeds)
# Repeating a seed must reproduce the same dungeon.
repeat=OUT/'native-seed-repeat.json'
subprocess.run([str(NODE),'scripts/leap_headless.mjs','startup','build/combined-runtime',str(OUT/'program.dck'),str(repeat),'--seed=12345'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,timeout=30)
assert json.loads(repeat.read_text())['nativeChecks']['dungeonHash']==next(r['dungeonHash'] for r in reports if r['seed']==12345)
summary={'seeds':reports,'unique_dungeons':len(seeds),'repeat_seed_reproduces_dungeon':True,'minimum_ms':min(r['ms'] for r in reports),'maximum_ms':max(r['ms'] for r in reports),'average_ms':sum(r['ms'] for r in reports)/len(reports)}
(OUT/'native-randomization.json').write_text(json.dumps(summary,indent=2)+'\n')
print(f"{len(seeds)} unique dungeons; startup {summary['minimum_ms']/1000:.3f}-{summary['maximum_ms']/1000:.3f}s; repeated seed reproduced")
