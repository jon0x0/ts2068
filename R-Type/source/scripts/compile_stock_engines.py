"""Compile current player/projectile engines for stock RAM. Internal linking stage."""
from pathlib import Path
import json,re,subprocess,sys
R=Path.cwd();n=int(sys.argv[1]);O=R/f'build/cartridges/integration_work/level{n:02d}';layout=json.loads((O/'player_ram_layout.json').read_text());ram=layout['allocations'];assembler=R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'

def assemble(name,text):
 p=O/(name+'.asm');p.write_text(text);r=subprocess.run([str(assembler),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert not r.returncode,r.stdout+r.stderr
 return p.with_suffix('.bin').read_bytes()
flags=layout['clock_flags'][0];state=ram['player_state'][0];back=ram['backing_pixels'][0];attrs=ram['backing_attributes'][0];phases=ram['player_phases'][0];owner=ram['published_owner_map'][0];bolts=ram['projectile_state'][0]
def reloc(a):
 if 0xf680<=a<0xf880:return state+a-0xf680
 if 0x5bc0<=a<0x5bd8:return flags+a-0x5bc0
 if 0xf080<=a<0xf100:return 0x1e20+a-0xf080
 return {0xe400:0x2400,0xed80:phases,0xf100:back,0xf880:owner,0x74fa:0xbafa,0x6c00:(attrs-back)&65535,0x6bf6:(attrs-back-10)&65535}.get(a,a)
def transform(s):return re.sub(r'\$([0-9A-Fa-f]{4})',lambda m:f'${reloc(int(m[1],16)):04X}',s)
s=(R/'build/fullgame/visible_hits_r145/overlay.asm').read_text();s=transform(s).replace('ASSERT $ <= $ED80','ASSERT $ <= $2D80');s=re.sub(r'LD A,\$(?:81|89|8D)\b','LD A,3',s)
# Retained-source pixel/colour bridges for the compact stock HOME workspace.
# Working pixels live atA600; source colours remain compact native tokens.
a=s.index('publish_pixels:');b=s.index('keep_pixel:',a)
s=s[:a]+s[a:b].replace('SET 5,H','CALL $0200').replace('RES 5,H','CALL $0203')+s[b:]
a=s.index('publish_attrs_done:');b=s.index('no_backing_attr_write:',a)
s=s[:a]+'publish_attrs_done:\n'+s[b:]
a=s.index('fast_retained_window:');b=s.index('fast_restore_pixels:',a)
s=s[:a]+s[a:b].replace('SET 5,H','CALL $0200')+s[b:]
a=s.index('fast_world_attributes:');b=s.index('fast_attr_done:',a)
s=s[:a]+s[a:b].replace('RES 5,H','; clean colours stay in compact source tokens').replace('        LD (HL),A\n','')+s[b:]
a=s.index('cache_backing:');b=s.index('cache_attr:',a)
s=s[:a]+s[a:b].replace('SET 5,H','CALL $0200').replace('RES 5,H','; future_attribute accepts working raster address')+s[b:]
a=s.index('cache_attr:');b=s.index('cache_next_row:',a)
s=s[:a]+s[a:b].replace('LD A,(HL)','CALL $0206').replace('        LD (HL),A\n','')+s[b:]
a=s.index('cache_zero_row:');b=s.index('cache_map_pointer:',a)
q=s[a:b].replace('RES 5,H','; compact colour tokens are not raster memory')
block='''        DUP 10
        LD (HL),A
        INC HL
        EDUP
'''
assert q.count(block)==2
q=''.join(q.rsplit(block,1))
s=s[:a]+q+s[b:]
if ram['backing_attributes'][1]-attrs==160:
 # Cache tokens once per character row; keep all64 backing pixel rows.
 a=s.index('cache_patch_row:');z=s.index('cache_pixel:',a)
 block=s[a:z];old='        CALL cache_map_pointer\n';assert block.count(old)==1
 block=block.replace(old,old+'        DI\n        CALL $020F\n        EI\n',1);s=s[:a]+block+s[z:]
 a=s.index('cache_pixel:');z=s.index('cache_next_row:',a);block=s[a:z]
 # The linked F69C scratch is PLAYER_STATE+1C.
 marker=f'        LD (${state+0x1c:04X}),DE\n';assert block.count(marker)==1
 block=block[:block.index(marker)+len(marker)];s=s[:a]+block+s[z:]
 a=s.index('cache_zero_row:');z=s.index('cache_map_pointer:',a);block=s[a:z];assert block.count(marker)==1
 block=block[:block.index(marker)+len(marker)]+'        JP cache_next_row\n';s=s[:a]+block+s[z:]
 a=s.index('backing_fill_cell:');z=s.index('        INC HL',a);block=s[a:z]
 first=block.index('        PUSH HL');last=block.index('        POP HL',first)+len('        POP HL\n')
 block=block[:first]+'        CALL $020C\n        LD (IY+65),A\n'+block[last:];s=s[:a]+block+s[z:]
s=s.replace('JP $9501','JP $0D90')
s='; INTERNAL stock retained backend; native player hooks linked by shared builder.\n'+s
player=assemble('stock_player_engine',s)
s=transform((R/'src/player_damage.asm').read_text()).replace('ASSERT $ <= $F100','ASSERT $ <= $1F20').replace('INC L','INC HL')
# The private block moved by a half-page: use full address arithmetic for coverage.
old='''        LD A,IXL
        SUB $80
        LD E,A
        LD D,$F7'''
new=f'''        PUSH HL
        LD E,IXL
        LD D,0
        LD HL,${state+0x80:04X}
        ADD HL,DE
        EX DE,HL
        POP HL'''
assert s.count(old)==2;s=s.replace(old,new)
# The relocated scratch starts at5C01: subtracting65 crosses a page.
# Original low-byte-only subtraction was safe atF7xx, but aliases5CC0 here.
old_mask='''        LD A,E
        SUB 65
        LD E,A'''
assert s.count(old_mask)==1
s=s.replace(old_mask,'''        PUSH HL
        LD HL,-65
        ADD HL,DE
        EX DE,HL
        POP HL''')
pos=s.index('restore_attr:');s=s[:pos]+s[pos:].replace('LD A,(HL)','CALL $0206');damage=assemble('stock_player_damage',s)
s=(R/'build/fullgame/visible_hits_r145/projectile_clock.asm').read_text();s=s.split('\nvisible_owner:',1)[0];s=s.replace('ORG $5880','ORG $1B20').replace('ASSERT $ <= $5B50','ASSERT $ <= $1DA0')
s='visible_owner EQU $1DB0\n'+s;s=s.replace('$B05B','$1DD0')
for oldv,newv in [(0x5f80,bolts),(0x5fb0,bolts+0x30),(0x5fc0,bolts+0x40),(0x5ff0,bolts+0x70),(0x5ff1,bolts+0x71),(0x5ff2,bolts+0x72),(0x5ff3,bolts+0x73),(0x5ff4,bolts+0x74),(0x5ff5,bolts+0x75),(0x5ff6,bolts+0x76),(0x5ff7,bolts+0x77)]:s=s.replace(f'${oldv:04X}',f'${newv:04X}')
for oldv,newv in [(0x0190,0x0d30),(0x1e20,0x0d40),(0x19e3,0x0d50),(0x09b6,0x0d70)]:s=s.replace(f'${oldv:04X}',f'${newv:04X}')
projectile=assemble('stock_projectile_engine',s+'\n ASSERT $ <= $1DA0\n')
visible=assemble('stock_visible_owner',f''' ORG $1DB0
 PUSH HL
 CALL $C0E4
 LD HL,${(owner-0x7e00)&65535:04X}
 ADD HL,DE
 LD A,(HL)
 POP HL
 RET
 ASSERT $ <= $1DD0
''')
shims=assemble('stock_projectile_shims',''' ORG $0D30
 LD B,(HL)
 SET 5,H
 LD C,(HL)
 RES 5,H
 RET
 ASSERT $ <= $0D40
 DS $0D40-$,$FF
 LD (HL),B
 SET 5,H
 LD (HL),C
 RES 5,H
 RET
 ASSERT $ <= $0D50
 DS $0D50-$,$FF
 LD A,B
 ADD A,A
 ADD A,B
 ADD A,$B4
 LD L,A
 LD H,$5E
 LD A,(HL)
 INC L
 LD D,(HL)
 INC L
 LD E,(HL)
 RET
 ASSERT $ <= $0D70
 DS $0D70-$,$FF
 LD C,A
 LD A,B
 ADD A,A
 ADD A,B
 ADD A,$B4
 LD L,A
 LD H,$5E
 LD (HL),C
 INC L
 LD (HL),D
 INC L
 LD (HL),E
 RET
 ASSERT $ <= $0D90
''')
shared=(O.parent/'L1_common_source.bin').read_bytes();(O/'stock_projectile_glyphs.bin').write_bytes(shared[0xb05b-0xa600:0xb05b-0xa600+54])
gateway=assemble('stock_projectile_gateway',''' ORG $0D90
 CP 6
 RET NC
 PUSH BC
 PUSH DE
 PUSH HL
 PUSH IX
 PUSH IY
 LD L,A
 LD H,0
 LD E,A
 LD D,0
 ADD HL,HL
 ADD HL,DE
 LD DE,$1B20
 ADD HL,DE
 LD DE,done
 PUSH DE
 JP (HL)
done:
 POP IY
 POP IX
 POP HL
 POP DE
 POP BC
 RET
 ASSERT $ <= $0DD0
''')
region=(R/f'build/fullgame/visible_hits_r145/level{n:02d}_region.bin').read_bytes();(O/'stock_player_phases.bin').write_bytes(region[0xed80:0xf080])
assert len(player)<=0x980 and len(projectile)<=640
(O/'stock_engine_link.json').write_text(json.dumps(dict(level=n,status='Internal current player/retained-copy backend; native player hooks linked by shared builder; independent projectile clock lifecycle pending',player=dict(address=0x2400,bytes=len(player)),damage=dict(address=0x1e20,bytes=len(damage)),projectile=dict(address=0x1b20,bytes=len(projectile)),visible_owner=dict(address=0x1db0,bytes=len(visible)),shims=dict(address=0xd30,bytes=len(shims)),retained_copy_backend_complete=True),indent=2));print(n,len(player),len(damage),len(projectile))
