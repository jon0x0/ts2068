from pathlib import Path
import sys,shutil,re,subprocess,json
R=Path.cwd();sys.path.insert(0,str(R/'scripts'));from build_rocket_fix import code
B=R/'build/fullgame/startup_r66';O=R/'build/fullgame/l2_rpc_r67';O.mkdir(exist_ok=True);(O/'rtype').mkdir(exist_ok=True)
for p in B.iterdir():
 if p.is_file() and p.suffix in ['.bin','.asm','.sym','.json']:shutil.copy2(p,O/p.name)
for p in (B/'rtype').iterdir():
 if p.is_file():shutil.copy2(p,O/'rtype'/p.name)
def asm(name,text):
 p=O/(name+'.asm');p.write_text(text,encoding='utf-8');q=subprocess.run([str(R.parent/'sinistar/tools/sjasmplus/sjasmplus-1.20.3.win/sjasmplus.exe'),f'--raw={p.with_suffix(".bin")}',f'--sym={p.with_suffix(".sym")}',str(p)],capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr
 return p.with_suffix('.bin').read_bytes(),{k:int(v,16)for k,v in re.findall(r'([\w.]+): EQU 0x([0-9a-f]+)',p.with_suffix('.sym').read_text(),re.I)}
b=bytearray((B/'level02_region.bin').read_bytes());A=R/'build/graphics/l2_integrated_r67';j=json.loads((A/'manifest.json').read_text())
tile_source=(R/'src/l2_tile_expand_r67.asm').read_text();tile_source=re.sub(r'tile_table:\n        DW [^\n]+', 'tile_table:\n        DW '+','.join('$%04X'%r['pointer']for r in j['tiles']),tile_source)
pv,ps=asm('palette_lookup',(R/'src/l2_palette_lookup_r67.asm').read_text());v,sy=asm('tile_expand',f'KEEP_TOKEN EQU ${ps["keep_dictionary_token"]:04X}\n'+tile_source);b[0x3848:0x3848+len(v)]=v
v,_=asm('tile_shims',f"        ORG $01C8\n        LD A,$0B\n        OUT ($F4),A\n        JP ${sy['install']:04X}\n        DS $01D8-$,0\n        PUSH AF\n        LD A,$0B\n        OUT ($F4),A\n        JP ${sy['get_tile']:04X}\n        DS $01E8-$,0\n        POP AF\n        PUSH AF\n        LD A,9\n        OUT ($F4),A\n        POP AF\n        RET\n        DS $01F4-$,0\n        LD A,$49\n        OUT ($F4),A\n        JP $DEDB\n        ASSERT $ <= $0200\n");b[0x1c8:0x1c8+len(v)]=v
# The existing warmup still builds reverse tables, then installs the level hooks.
at=b.find(bytes.fromhex('c3 db de'),0xdc0,0xdde);assert at>=0;b[at:at+3]=bytes.fromhex('c3 c8 01')
x=(A/'body_tiles.lz').read_bytes();assert len(x)<=0x870;b[0xb442:0xbcb2]=x.ljust(0x870,b'\0');b[0xc762+56*5:0xc762+64*5]=(A/'map_patch.bin').read_bytes()
x=(R/'build/graphics/l2_actors_r67/palette.bin').read_bytes();b[0x2000:0x2000+len(x)]=x
# Colour lookup recognizes the scratch tile and returns a retained dictionary token.
s=(R/'src/l2_palette_lookup_r67.asm').read_text();v,_=asm('palette_lookup',s);b[0xf80:0xf80+len(v)]=v
# Existing incoming group styles must never modify dictionary token bit3.
s=(R/'src/terrain_groups_full.asm').read_text();s=s[s.index('apply_group_column:'):];s=s[:s.index('        ASSERT')];s=s.replace('        PUSH AF','        CP $90\n        RET NC\n        PUSH AF',1)
v,_=asm('group_column','select_group_row EQU $08F0\n        ORG $09D0\n'+s+'        ASSERT $ <= $0A08\n');b[0x9d0:0x9d0+len(v)]=v
# Terrain scratch is not an actor source: do not re-encode its retained tokens.
s=(R/'src/boss_palette_fast.inc').read_text().replace('full_enemy_source:\n        LD A,H','full_enemy_source:\n        LD A,H\n        CP $C7\n        JR Z,no');s=s[:s.index('        ASSERT $ <= $1937')]
v,_=asm('boss_palette','SOURCE_ENEMY_END EQU $D372\nENEMY_POOL_END EQU 0\nRETAINED_ENTRY EQU $18F6\n'+s);assert len(v)<=0x1928-0x18a7;b[0x18a7:0x18a7+len(v)]=v
mouth=(R/'build/graphics/l2_actors_r67/mouths.bin').read_bytes();b[0xaeae:0xaeae+len(mouth)]=mouth
for n in range(4):
 at=0xb372+(40+n)*4;b[at:at+4]=bytes([4,3])+(0xceae+n*108).to_bytes(2,'little')
assert b[0xcae9]==13;b[0xcae9]=19
x=(R/'build/graphics/l2_actors_r67/head_phases.bin').read_bytes();assert len(x)<=0xfe6;b[0x2400:0x2400+len(x)]=x
x=(R/'build/graphics/l2_actors_r67/head_table.bin').read_bytes();assert b[0xe350]==3;b[0xe350:0xe350+len(x)]=x
b[0x33f0+0x1e8:0x33f0+0x1ec]=bytes.fromhex('c3 80 a4 00')
(O/'level02_region.bin').write_bytes(b)
(O/'rtype/LEVEL02.TAP').write_bytes(b''.join(code(f'RTPAGE{k:02X}',b[k*8192:(k+1)*8192],k)for k in range(8)))
(O/'rtype/START02.TAP').write_bytes(b''.join(code(f'RTSTART{k:02X}',b[p*8192+s*1024:p*8192+(s+1)*1024],k)for k,(p,s)in enumerate((p,s)for p in[0,1,4,5,6,7]for s in range(8))))
print('Built L2',len(v),j['compressed_bytes'])

