"""Record source hashes and compare the standard/+D R-Type level payloads."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def tap_blocks(data):
    result=[];pos=0
    while pos<len(data):
        size=int.from_bytes(data[pos:pos+2],'little');block=data[pos+2:pos+2+size]
        if len(block)!=size:raise ValueError('Truncated TAP')
        checksum=0
        for value in block:checksum^=value
        if checksum:raise ValueError('TAP checksum mismatch')
        result.append(block);pos+=size+2
    return result


def main():
    records=[];tapes={}
    for path in sorted(list((ROOT/'arcade').glob('*.zip'))+list((ROOT/'spectrum').glob('*.zip'))):
        members=[]
        with zipfile.ZipFile(path) as archive:
            for entry in archive.infolist():
                if entry.is_dir():continue
                data=archive.read(entry)
                members.append(dict(name=entry.filename,bytes=len(data),crc32=f'{entry.CRC:08x}',sha256=hashlib.sha256(data).hexdigest()))
                if entry.filename.endswith('.tap'):tapes['+D' if '+D' in entry.filename else 'standard']=tap_blocks(data)
        records.append(dict(file=str(path.relative_to(ROOT)),bytes=path.stat().st_size,
                            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),members=members))
    standard=[b[1:-1] for b in tapes['standard'][9::2]]
    plusd=[b[1:-1] for b in tapes['+D'][7::2]]
    assert len(standard)==8 and standard==plusd
    arcade=[r for r in records if r['file'].startswith('arcade')]
    assert len(arcade)==2 and arcade[0]['sha256']==arcade[1]['sha256']
    validation=ROOT/'build/graphics/fuse_validation.json'
    report=dict(archives=records,arcade_archives_identical=True,
                level_payload_bytes=[len(b) for b in standard],level_total=sum(map(len,standard)),
                standard_plusd_levels_identical=True,
                torasoft_128='TZX BASIC explicitly identifies 128K REMIX BY TORASOFT 1993; modified/trained edition, not assumed to be an official enhanced original',
                status='Source archives retained unchanged')
    (ROOT/'build/source_inventory.json').write_text(json.dumps(report,indent=2)+'\n')
    comparison=ROOT/'build/arcade_capture_zero'
    checks=[]
    if comparison.exists():
        for original in sorted((ROOT/'build/arcade_capture').glob('frame*')):
            other=comparison/original.name
            assert other.exists() and original.read_bytes()==other.read_bytes(), original.name
            checks.append(original.name)
        (ROOT/'build/arcade_standin_validation.json').write_text(json.dumps(dict(
            comparison='Non-emulated archival region stand-ins FF versus 00; identical captured screens, palette RAM, sprite RAM and tile RAM',
            matched_files=checks,caveat='Stand-ins are NOT authentic ROM dumps; original functional ROMs all verified by CRC'),indent=2)+'\n')
    print('Source archives inventoried; 8 level payloads identical; arcade duplicates confirmed')
    print('Archival-region fill comparison:',len(checks),'identical capture files')


if __name__=='__main__':main()
