"""Validate evidence and packaged TAP bytes before publishing the r42 candidate."""
import json, hashlib, functools, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/boss_preview_r42'

def main():
    manifest=json.loads((OUT/'manifest.json').read_text())
    boss=json.loads((OUT/'boss_preview_validation.json').read_text())
    assert boss['passed'] and [v['level']for v in boss['results']]==list(range(1,9))
    for v,ident in zip(boss['results'],[8,3,41,27,8,18,53,42]):
        assert v['passed']and v['jumps']==1 and v['after']>=700 and ident in v['renderedDescriptors']
    progress=json.loads((OUT/'cache_progression_validation.json').read_text())
    assert progress['passed']and progress['all8_revisited_without_disk']
    restart=json.loads((OUT/'cache_restart_validation.json').read_text())
    assert len(restart)==2 and all(v['passed']for v in restart)
    failures=json.loads((OUT/'failure_validation.json').read_text())
    assert len(failures)==4 and all(v['passed']for v in failures)
    pages=0
    for row in manifest['regions']:
        tape=(OUT/'RTYPE'/row['file']).read_bytes();blocks=[];at=0
        while at<len(tape):
            length=int.from_bytes(tape[at:at+2],'little');b=tape[at+2:at+2+length]
            assert len(b)==length and functools.reduce(int.__xor__,b)==0
            blocks.append(b);at+=length+2
        assert len(blocks)==16
        data=b''.join(b[1:-1]for b in blocks[1::2]);assert len(data)==65536
        assert hashlib.sha256(data).hexdigest()==row['sha256']
        assert data[0x1fa3:0x1fa3+manifest['hook_bytes']]==(OUT/'boss_preview.bin').read_bytes()
        if row['file']=='RTBOOT.TAP':
            assert data[0x465f:0x4662]==bytes.fromhex('cd a3 1f')
            assert data[0x5c3c:0x5c3f]==bytes.fromhex('cd f8 fc'),'Rocket guard preserved'
        pages+=8
    assert pages==72
    readme=OUT/'RTYPE/README.txt';text=readme.read_text().replace('Candidate pending validation.','Deterministic emulator validation passed; physical confirmation pending.')
    text+='Level 6 restarts at the moving-maze entrance to retain its required setup. Artwork remains r41; selected Sierra Lite changes are not included.\n'
    readme.write_text(text)
    archive=OUT/'RType_TS2068_boss_preview_r42.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
        for p in sorted((OUT/'RTYPE').iterdir()):z.write(p,'RTYPE/'+p.name)
    manifest.update(status='All eight native boss previews and cache/restart/error checks passed in deterministic emulation; physical confirmation pending',validated_asset_pages=pages,package_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),physical_validation=False)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print(archive);print(manifest['package_sha256'])

if __name__=='__main__':main()
