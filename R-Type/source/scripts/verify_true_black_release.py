from pathlib import Path
import json,zipfile,functools,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/fullgame/true_black_r31';report=json.loads((out/'live_validation.json').read_text())
 assert len(report)==8 and all(r['updates']>100 and len(r['samples'])==7 and all(v['bad']==0 for v in r['samples'])for r in report)
 image=(out/'RType_TS2068_true_black_r31.ram512').read_bytes();checked=0
 with zipfile.ZipFile(out/'RType_TS2068_disk_r31.zip')as z:
  for name in z.namelist():
   if '/RTFG' not in name or not name.endswith('.TAP'):continue
   data=z.read(name);at=0;idx=0;volume=int(Path(name).stem[-2:],16)
   while at<len(data):
    size=int.from_bytes(data[at:at+2],'little');b=data[at+2:at+size+2];assert functools.reduce(int.__xor__,b)==0
    if idx%2:
     page=volume*4+idx//2;assert b[1:-1]==image[page*8192:(page+1)*8192];checked+=1
    idx+=1;at+=size+2
 assert checked==64
 scripts=ROOT/'scripts'
 fixture=(scripts/'fullgame_fixture.mjs').read_text().replace('build/fullgame/RType_fullgame_candidate.ram512','build/fullgame/true_black_r31/RType_TS2068_true_black_r31.ram512').replace("game=fs.readFileSync(path.join(root,'build/fullgame/level01/game_progression.dck'))","game=Buffer.concat([Buffer.from([0,2,3,3,3,2,2,2,2]),image.subarray(0,65536)])")
 (scripts/'true_black_fixture.mjs').write_text(fixture)
 test=(scripts/'verify_fullgame_ending.mjs').read_text().replace('./fullgame_fixture.mjs','./true_black_fixture.mjs').replace('build/fullgame/ending_validation.json','build/fullgame/true_black_r31/ending_validation.json')
 (scripts/'verify_true_black_ending.mjs').write_text(test)
 node=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
 p=subprocess.run([str(node),str(scripts/'verify_true_black_ending.mjs')],cwd=ROOT,capture_output=True,text=True);(out/'ending_validation.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stdout+p.stderr
 manifest=json.loads((out/'manifest.json').read_text());manifest.update(status='Candidate: all-level normal-black scene checks and ending/progression pass; physical display confirmation pending',live_samples=56,verified_disk_pages=64,ending_validation=True)
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print('56 live samples zero exposed bright black;64 disk pages; all-level transitions/ending/restart pass')
if __name__=='__main__':main()
