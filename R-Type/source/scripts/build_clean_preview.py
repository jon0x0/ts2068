"""Opt-in complete video handover for full-game per-level Fuse previews."""
from pathlib import Path
import subprocess,json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--level',type=int,default=2,choices=range(1,9));args=ap.parse_args();folder=ROOT/f'build/fullgame/level{args.level:02d}';out=ROOT/'build/fullgame/previews_r26';out.mkdir(exist_ok=True)
 assert not(folder/'boss_colours.bin').read_bytes(),'Full palette dictionaries must live in DOCK1'
 sym=(folder/'renderer.sym').read_text();assert 'ecm_game_init: EQU 0x00001485'in sym
 asm=ROOT.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe';p=subprocess.run([str(asm),f'--raw={out/"handover.bin"}',str(ROOT/'src/clean_game_handover.asm')],cwd=ROOT,capture_output=True,text=True);assert not p.returncode,p.stdout+p.stderr
 b=bytearray((folder/'game.bin').read_bytes());original=bytes(b);assert b[0x4640:0x4643]==bytes.fromhex('cd 85 14');b[0x4640:0x4643]=bytes.fromhex('cd f0 0c');b[0xcf0:0xd00]=(out/'handover.bin').read_bytes();assert b[0xa4ae:0xd87c]==original[0xa4ae:0xd87c],'Scenery/collision unchanged'
 name=f'Level_{args.level}_clean_redraw_r26';raw=bytes(b);(out/(name+'.bin')).write_bytes(raw);(out/(name+'.dck')).write_bytes(bytes([0,2,3,3,3,2,2,2,2])+raw)
 report=dict(status='Display-handover diagnostic candidate; reported UI artifact not reproduced in screen RAM or FMF',source_sha256=hashlib.sha256(original).hexdigest(),sha256=hashlib.sha256(raw).hexdigest(),changed_offsets=[i for i,(a,z)in enumerate(zip(original,raw))if a!=z],scenery_collision_unchanged=True,level=args.level,refresh='Two IRQ waits in black standard-video mode, then ECM; one full refresh guaranteed between waits')
 (out/(name+'.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
