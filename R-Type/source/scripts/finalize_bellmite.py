import json,hashlib,zipfile,functools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/fullgame/bellmite_orbs_r44'
def main():
    manifest=json.loads((OUT/'manifest.json').read_text())
    draw=json.loads((OUT/'draw_validation.json').read_text());assert draw['passed']and draw['cases']==888
    boss=json.loads((OUT/'boss_preview_validation.json').read_text());assert boss['passed']and boss['results'][0]['level']==5 and 8 in boss['results'][0]['renderedDescriptors']
    assert json.loads((OUT/'cache_progression_validation.json').read_text())['all8_revisited_without_disk']
    for filename,count in [('cache_restart_validation.json',2),('failure_validation.json',4)]:
        rows=json.loads((OUT/filename).read_text());assert len(rows)==count and all(v['passed']for v in rows)
    for record in manifest['regions']:
        tape=(OUT/'RTYPE'/record['file']).read_bytes();at=0;blocks=[]
        while at<len(tape):
            length=int.from_bytes(tape[at:at+2],'little');b=tape[at+2:at+2+length];assert len(b)==length and functools.reduce(int.__xor__,b)==0;blocks.append(b);at+=length+2
        assert len(blocks)==16;data=b''.join(b[1:-1]for b in blocks[1::2]);assert len(data)==65536 and hashlib.sha256(data).hexdigest()==record['sha256']
    readme=OUT/'RTYPE/README.txt';readme.write_text(readme.read_text()+'\nr44 BELLMITE SPHERES: live sphere frames30-33 now use32x32 arcade-derived green shading and red nodes, replacing untouched monochrome native spheres. Three unique source cels serve the four native animation steps. Selected96x96 core retained. Native compositor unchanged: rectangular overlap artifacts remain under investigation. Full-game movement/firing unchanged. Use title5, start, then B/release/B. Physical validation pending.\n')
    archive=OUT/'RType_TS2068_Bellmite_r44.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
        for p in sorted((OUT/'RTYPE').iterdir()):z.write(p,'RTYPE/'+p.name)
    manifest.update(status='Bellmite sphere trial: renderer/boss/cache/restart/error checks passed; hardware and gameplay balance pending',validated_asset_pages=72,package_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),movement_changed=False,firing_changed=False,physical_validation=False)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));print(archive);print(manifest['package_sha256'])
if __name__=='__main__':main()
