"""Pair a version-3 story with this project's configured ZIP80 interpreter."""
import argparse
import hashlib
from pathlib import Path
from cpm_disk import decode,read_files,publish

# Known project build: dynamic 64/80 columns and ADM-3A terminal setup.
TEMPLATE_LENGTH=8443
TEMPLATE_HASH='248cb078c734bc31c989e027a624a28d905f0090f539e2c3e9ddb26e00f66cb6'


def prepare(story,template,name):
    name=name.upper()
    if not 1<=len(name)<=8 or any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_' for c in name):
        raise ValueError('choose a 1-8 character CP/M basename using letters, digits or underscore')
    if len(story)<64 or story[0]!=3 or len(story)>131072:
        raise ValueError('this interpreter requires a version-3 (.z3) story, at most 128KB')
    if len(template)<TEMPLATE_LENGTH or len(template)>TEMPLATE_LENGTH+127 or any(template[TEMPLATE_LENGTH:]):
        raise ValueError('not the supported project ZIP80 interpreter')
    program=bytearray(template[:TEMPLATE_LENGTH]);program[5:13]=b'PLANET  '
    if hashlib.sha256(program).hexdigest()!=TEMPLATE_HASH:
        raise ValueError('unsupported interpreter build; use PLANET.COM/ZORK1.COM from this project')
    # In this fingerprinted binary CPMFN is at Z80 address 0105h (file offset 5).
    program[5:13]=name.ljust(8).encode('ascii')
    return bytes(program),story


def load_template(path):
    if path.suffix.lower() in ('.dsk','.tap','.img','.raw'):
        files,_=read_files(decode(path))
        for name in ('PLANET.COM','ZORK1.COM'):
            if name in files:return files[name]
        raise ValueError('template disk must contain project PLANET.COM or ZORK1.COM')
    return path.read_bytes()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--story',required=True,type=Path,help='downloaded version-3 story file')
    parser.add_argument('--name',required=True,help='CP/M basename, for example ZORK2')
    parser.add_argument('--template',type=Path,default=Path('build/infocom-cpm.dsk'),help='project COM interpreter or disk containing PLANET.COM/ZORK1.COM')
    parser.add_argument('--output',type=Path,default=Path('build/newsoftware'),help='new COM/DAT files go here')
    args=parser.parse_args()
    try:
        name=args.name.upper();program,story=prepare(args.story.read_bytes(),load_template(args.template),name)
        targets=[args.output/(name+'.COM'),args.output/(name+'.DAT')]
        if any(path.exists() for path in targets):raise ValueError('output pair exists; preserve it and choose another output folder')
        for path,data in zip(targets,(program,story)):publish(path,data)
        print(f'{targets[0]} and {targets[1]}; run {name} at A>')
        print('Story SHA256 '+hashlib.sha256(story).hexdigest())
    except (OSError,ValueError) as error:parser.exit(1,str(error)+'\n')


if __name__=='__main__':main()
