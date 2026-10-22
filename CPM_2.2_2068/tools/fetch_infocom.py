"""Fetch optional Infocom inputs for a private local build; never publish them."""
from pathlib import Path
import argparse, hashlib, io, urllib.request, zipfile

ROOT=Path(__file__).resolve().parents[1]
SOURCES={
    'planetfall':'planetfall-r37-s851003.z3',
    'zork1':'zork1-r88-s840726.z3',
    'zork2':'zork2-r48-s840904.z3',
}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--games',nargs='+',choices=SOURCES,default=['planetfall','zork1','zork2'])
    a=p.parse_args();folder=ROOT/'build/planetfall';folder.mkdir(parents=True,exist_ok=True)
    urls=[('cpm80.zip','https://eblong.com/infocom/interpreters/cpm80.zip')]
    urls += [(SOURCES[n],'https://eblong.com/infocom/gamefiles/'+SOURCES[n]) for n in a.games]
    for name,url in urls:
        target=folder/name
        if target.exists():
            print('Retaining existing',target)
            continue
        data=urllib.request.urlopen(url,timeout=60).read()
        if name.endswith('.z3') and (len(data)<64 or data[0]!=3):raise ValueError('not a version-3 story: '+name)
        if name.endswith('.zip'):zipfile.ZipFile(io.BytesIO(data)).testzip()
        with target.open('xb') as stream:stream.write(data)
        print(target,hashlib.sha256(data).hexdigest())
    archive=zipfile.ZipFile(folder/'cpm80.zip')
    matches=[n for n in archive.namelist() if n.lower().endswith('/zorkcpm.asm') or n.lower()=='zorkcpm.asm']
    if len(matches)!=1:raise ValueError('unexpected interpreter archive: find zorkcpm.asm manually')
    source=folder/'interpreter/cpm80/zorkcpm.asm';source.parent.mkdir(parents=True,exist_ok=True)
    if not source.exists():
        with source.open('xb') as stream:stream.write(archive.read(matches[0]))
    print('Local inputs ready. Follow docs/software-install.md; these downloads are not part of the public release.')

if __name__=='__main__':main()
