"""Build optimized 64KB original-colour ROM/PicoROM without altering r2."""
from pathlib import Path
import json,hashlib,subprocess,sys
from render_optimizations import kernels,patch_kernels
ROOT=Path(__file__).resolve().parents[1]
def main():
 subprocess.run([sys.executable,str(ROOT/'scripts/build_native.py'),'--native-input'],cwd=ROOT,check=True)
 out=ROOT/'build/optimized';code,sym=kernels(ROOT)
 raw=bytearray((ROOT/'build/native/RType_level1_native_experimental_r2.bin').read_bytes());ram=(ROOT/'build/native/snapshot.bin').read_bytes();patched=patch_kernels(ram,sym)
 raw[0x1200:0x1200+len(code)]=code;raw[0x4000:0x6000]=patched[0x4000:0x6000]
 raw=bytes(raw);dck=bytes([0]+[2]*8)+raw
 for ext,data in (('bin',raw),('dck',dck)):(out/f'RType_level1_native_ROM_optimized_r3.{ext}').write_bytes(data)
 (out/'RType_TS2068_64K_PicoROM_r3.rom').write_bytes(raw)
 (out/'rom_manifest.json').write_text(json.dumps(dict(bin_sha256=hashlib.sha256(raw).hexdigest(),dck_sha256=hashlib.sha256(dck).hexdigest(),rom_bytes=len(raw),kernel_bytes=len(code),limitation='Original-colour level-one ROM cartridge; not ECM or full multilevel conversion.'),indent=2))
 print('Built optimized ROM',len(code),'kernel bytes')
if __name__=='__main__':main()
