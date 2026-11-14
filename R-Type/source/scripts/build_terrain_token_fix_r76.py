from pathlib import Path
import shutil,sys
R=Path.cwd();B=R/'build/fullgame/loading_text_r74';O=R/'build/fullgame/terrain_token_fix_r76';O.mkdir(exist_ok=True);shutil.copytree(B/'rtype',O/'rtype',dirs_exist_ok=True)
for p in B.iterdir():
 if p.is_file()and p.suffix in['.bin','.sym','.asm','.json']:shutil.copy2(p,O/p.name)
b=bytearray((O/'level02_region.bin').read_bytes());assert b[0xfb8:0xfc2]==bytes.fromhex('fe903002cbbf12c384ff');b[0xfb8:0xfc2]=bytes.fromhex('12c384ff000000000000')
p=bytes.fromhex('3ecb3281ff21bf122282ff');at=b.find(p);assert at==14562;b[at:at+len(p)]=bytes.fromhex('3e003281ff2100122282ff');(O/'level02_region.bin').write_bytes(b)
sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
(O/'rtype/LEVEL02.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
(O/'rtype/START02.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+t*1024:p*8192+(t+1)*1024],k)for k,(p,t)in enumerate((p,t)for p in[0,1,4,5,6,7]for t in range(8))))
s=(R/'src/l2_palette_lookup_r67.asm').read_text();s=s.replace('        CP $90\n        JR NC,store\n        RES 7,A\n','');(R/'src/l2_palette_lookup_r76.asm').write_text(s)
s=(R/'src/l2_tile_expand_r67.asm').read_text().replace('LD A,$CB','LD A,0').replace('LD HL,$12BF','LD HL,$1200');(R/'src/l2_tile_expand_r76.asm').write_text(s)
s=(R/'scripts/boss_motion_fixture_r75.mjs').read_text(encoding='utf-8-sig').replace('l2_palette_restore_r75','terrain_token_fix_r76');(R/'scripts/boss_motion_fixture_r76.mjs').write_text(s,encoding='utf-8')
for stem in ['verify_colour_jumps','verify_preload_title','verify_boss_game']:
 s=(R/f'scripts/{stem}_r75.mjs').read_text(encoding='utf-8-sig').replace('boss_motion_fixture_r75','boss_motion_fixture_r76')
 if stem=='verify_colour_jumps':s=s.replace('const n=route[index];',"const n=route[index];if(phase===2&&n!==2)assert.deepEqual(Array.from(m.ram.slice(0xff81,0xff83)),[0,0],'Terrain marker hook leaked from L2');")
 (R/f'scripts/{stem}_r76.mjs').write_text(s,encoding='utf-8')
s=(R/'scripts/l3_trace_r75.mjs').read_text().replace('l3_trace_fixture_r75','boss_motion_fixture_r76').replace('keyMatrix[3]&=~4','keyMatrix[3]&=~2');(R/'scripts/l2_trace_r76.mjs').write_text(s)
print('Two L2 colour-token paths corrected; r74 artwork restored with upgraded L2 body')

# Every world initialization must restore the common ECM token keeper before
# level-specific warmup can install its own hook. CF0..CFF is retired handover
# padding in these playable images, not palette storage or live UI code.
wrapper=bytes.fromhex('cdc386e52100002281ffe1c9')
for n in range(1,9):
 p=O/f'level{n:02d}_region.bin';b=bytearray(p.read_bytes());assert b[0xcf0:0xd00]==bytes([0x45])*16;assert b[0xdc0:0xdc3]==bytes.fromhex('cdc386');b[0xcf0:0xcf0+len(wrapper)]=wrapper;b[0xdc0:0xdc3]=bytes.fromhex('cdf00c');p.write_bytes(b)
 (O/'rtype'/f'LEVEL{n:02d}.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
 (O/'rtype'/f'START{n:02d}.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+t*1024:p*8192+(t+1)*1024],k)for k,(p,t)in enumerate((p,t)for p in[0,1,4,5,6,7]for t in range(8))))

