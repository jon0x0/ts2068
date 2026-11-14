from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'build/fullgame/l5_effects_fast_r59'
TARGETS={0xfda5:8,0xfde9:0,0xfdef:0x72,0xfdf0:0x73,0xfdf8:0xf7}
def patch_calls(data,ranges):
 changes=[]
 for begin,end in ranges:
  for at in range(begin,end-2):
   if data[at]in [0xcd,0xc3]:
    target=int.from_bytes(data[at+1:at+3],'little')
    if target in TARGETS:data[at+1:at+3]=TARGETS[target].to_bytes(2,'little');changes.append(dict(offset=at,target=target,replacement=TARGETS[target]))
 return changes
def protected_native(data):
 data[:6]=bytes.fromhex('06 00 76 10 fd c9');data[8:0x4c]=(BASE/'boot_region.bin').read_bytes()[0xdda5:0xdde9]
 lookup=(BASE/'global_colour_lookup.bin').read_bytes();data[0x4c:0x4c+len(lookup)]=lookup;data[0x1561:0x1567]=bytes.fromhex('cd 4c 00 c3 67 15')
 data[0x72:0x7b]=bytes.fromhex('af 77 54 5d 1c 0b ed b0 c9');data[0xf7:0x100]=bytes.fromhex('21 00 40 01 00 18 c3 72 00')
 return patch_calls(data,[(0xc00,0x2000),(0x4000,0x6600),(0xa000,0xd87c)])
def publisher(data):
 data[0xfba7:0xfbab]=bytes.fromhex('f5 c3 01 0d')
 data[0x1b14:0x1b1d]=bytes.fromhex('c3 e1 0e')+bytes([255])*6
