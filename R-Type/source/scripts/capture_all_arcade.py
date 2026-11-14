from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'build/fullgame/arcade_reference';out.mkdir(parents=True,exist_ok=True)
 lua=r'''
local out=OUTDIR
local m=manager.machine
local s=m.devices[":maincpu"].spaces["program"]
local frame=0
local function key(name,value)
 for _,port in pairs(m.ioport.ports) do for _,field in pairs(port.fields) do if field.name==name then field:set_value(value) end end end
end
local function dump(base,name,address,size)
 local f=assert(io.open(base.."_"..name..".bin","wb"))
 for a=address,address+size-1 do f:write(string.char(s:read_u8(a))) end
 f:close()
end
sub=emu.add_machine_frame_notifier(function()
 frame=frame+1
 if frame==720 then key("Coin 1",1) end
 if frame==730 then key("Coin 1",0) end
 if frame==780 then key("1 Player Start",1) end
 if frame==790 then key("1 Player Start",0) end
 if frame>850 then
  s:write_u8(0x42fc6,1) -- documented diagnostic invulnerability
  s:write_u8(0x42f32,10)
  s:write_u8(0x4003a,1);s:write_u8(0x4003d,0x80)
  s:write_u8(0x40033,4);s:write_u8(0x40035,4)
  key("P1 Button 1",frame%18<15 and 1 or 0)
  key("P1 Up",frame%600>=0 and frame%600<100 and 1 or 0)
  key("P1 Down",frame%600>=300 and frame%600<500 and 1 or 0)
 end
 if frame>=1200 and frame%300==0 then
  local base=out..string.format("/frame%06d",frame)
  m.screens[":screen"]:snapshot(base..".png")
  dump(base,"palette_sprite",0xc8000,0xc00);dump(base,"palette_tile",0xcc000,0xc00)
  dump(base,"sprites",0xc0000,0x400);dump(base,"state",0x42f00,0x100)
  print("CAPTURE "..frame)
 end
end)
'''.replace('OUTDIR',json.dumps(out.as_posix()))
 script=out/'capture.lua';script.write_text(lua)
 for name in ['cfg','nvram','snap']:(out/name).mkdir(exist_ok=True)
 cmd=['C:/apps/games/MAME/mame.exe','rtype','-noreadconfig','-rompath',str(ROOT/'arcade')+';'+str(ROOT/'build/mame_archival_standins_ff'),'-video','none','-sound','none','-nothrottle','-skip_gameinfo','-seconds_to_run','1800','-autoboot_delay','0','-autoboot_script',str(script),'-cfg_directory',str(out/'cfg'),'-nvram_directory',str(out/'nvram'),'-snapshot_directory',str(out/'snap')]
 p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=300);(out/'mame.log').write_text(p.stdout+p.stderr);print('MAME exit',p.returncode,'captures',len(list(out.glob('*.png'))),p.stdout[-300:],p.stderr[-300:]);assert p.returncode==0
 (out/'provenance.json').write_text(json.dumps(dict(source='Original verified local arcade ROMs, unmodified graphics; MAME0.289',diagnostic_addresses='https://github.com/finalburnneo/FBNeo-cheats/blob/master/cheats/cheat.dat',diagnostics=['Invincibility','Infinite lives','Max beam','Power pods/missiles','Scripted firing and vertical movement'],frames=1800*60,capture_step=300,not_hardware_evidence=True),indent=2))
if __name__=='__main__':main()
