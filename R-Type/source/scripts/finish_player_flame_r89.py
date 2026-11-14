from pathlib import Path
import json
R=Path.cwd();O=R/'build/fullgame/walker_selection_r89';source=(R/'build/diagnostics/pixel_movement_trial/ship_phases.bin').read_bytes()[768:1536];v=bytearray(source)
for phase in range(8):
 # Retint the existing two-pixel rear flare; preserve bitmap, coverage and ship size.
 for x in[phase+1,phase+2]:v[phase*96+32+3*4+x//8]=2
for n in range(1,9):
 p=O/f'level{n:02d}_region.bin';b=bytearray(p.read_bytes());assert b[0xed80:0xf080]==source;b[0xed80:0xf080]=v;p.write_bytes(b)
(O/'player_flame_phases.bin').write_bytes(v)
# Regenerate level tapes after this isolated colour change.
import sys;sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
for n in range(1,9):
 b=(O/f'level{n:02d}_region.bin').read_bytes();(O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)));(O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+t*1024:p*8192+(t+1)*1024],k)for k,(p,t)in enumerate((p,t)for p in[0,1,4,5,6,7]for t in range(8))))
p=R/'scripts/verify_boss_game_r89.mjs';s=p.read_text().replace("const out=base;const manifests", "const out=base;const walkerGroups=JSON.parse(fs.readFileSync(path.join(out,'walker_runtime.json')));const manifests");s=s.replace("rec&&level!==1&&ptr===rec.plan_start", "rec&&level!==1&&ptr===rec.plan_start&&!walkerGroups.find(r=>r.level===level)?.groups.some(g=>g.original.includes(selectedID))");s=s.replace("fs.readFileSync(path.join(root,'build/diagnostics/pixel_movement_trial/ship_phases.bin')).subarray(768,1536)","fs.readFileSync(path.join(out,'player_flame_phases.bin'))");p.write_text(s)
