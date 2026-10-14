"""Regression checks of saved bytecode on the actual assembled Leap VM."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
NODE=Path(__import__('os').environ.get('CROWN_NODE') or __import__('shutil').which('node') or 'node')


class BytecodeTests(unittest.TestCase):
    def build(self,name,source):
        out=ROOT/'build/tests'/name
        out.mkdir(parents=True,exist_ok=True)
        src=out/'source.bas'
        src.write_text(source,encoding='ascii')
        result=self.node('compile',src,out/'bytecode.json')
        self.assertEqual(result.returncode,0,result.stderr)
        subprocess.run([sys.executable,str(ROOT/'scripts/package_leap_cartridge.py'),
                        str(out/'bytecode.json'),'--output',str(out)],check=True,capture_output=True)
        return out

    def node(self,mode,src,out):
        return subprocess.run([str(NODE),str(ROOT/'scripts/leap_headless.mjs'),mode,
                               str(ROOT/'build/host'),str(src),str(out)],
                              capture_output=True,text=True,timeout=45)

    def execute(self,out,expected):
        result=self.node('bytecode',out/'program.lbc',out/'ram-execution.json')
        self.assertEqual(result.returncode,0,result.stderr)
        report=json.loads((out/'ram-execution.json').read_text())
        self.assertFalse(report['sourceLoaded'])
        self.assertEqual(report['vmError'],0)
        self.assertEqual(report['output'],expected)
        return report

    def test_arrays_strings_procedures_and_floats(self):
        out=self.build('language', (ROOT/'examples/cartridge_smoke.bas').read_text())
        self.execute(out,'LEAP BYTECODE CARTRIDGE\nSUM=45\nDOUBLE=90\nFLOAT=3.7500\nROM BYTECODE\nFREE=12985')

    def test_array_larger_than_original_pool(self):
        out=self.build('large_array','DIM a(5500)\na(5499) = 12345\nPRINT a(5499)\nEND\n')
        self.execute(out,'12345')

    def test_bytecode_larger_than_original_limit(self):
        out=self.build('large_code','x = 1\n'*1040+'PRINT x\nEND\n')
        size=len(bytes.fromhex(json.loads((out/'bytecode.json').read_text())['code']))
        self.assertGreater(size,4011)
        self.execute(out,'1')

    def test_string_array_and_branch(self):
        out=self.build('string_array','DIM s$(2,16)\ns$(1) = "CROWN"\nIF s$(1) = "CROWN" THEN\nPRINT s$(1)\nELSE\nPRINT "FAIL"\nENDIF\nEND\n')
        self.execute(out,'CROWN')

    def test_official_nested_array_kind_fix(self):
        # M-4: reads and assignments must retain the outer array's kind.
        out=self.build('nested_array_kind', 'DIM n(3)\nDIM s$(3,8)\nn(0) = 1\ns$(0) = "AB"\ns$(n(0)) = "CROWN"\nn(1) = LEN(s$(0))\nn(LEN(s$(0))) = 7\nPRINT s$(n(0))\nPRINT n(1)\nPRINT n(2)\nEND\n')
        self.execute(out,'CROWN\n2\n7')

    def test_corrupt_payload_and_metadata_are_rejected(self):
        out=self.build('corruption','PRINT "OK"\nEND\n')
        original=(out/'program.lbc').read_bytes()
        for offset in (8,49):
            data=bytearray(original); data[offset]^=1
            bad=out/f'corrupt-{offset}.lbc'; bad.write_bytes(data)
            result=self.node('bytecode',bad,out/'bad.json')
            self.assertNotEqual(result.returncode,0)
            self.assertIn('LBC checksum mismatch',result.stderr)
        data=bytearray(original); data[13]^=1
        bad=out/'wrong-rom.lbc'; bad.write_bytes(data)
        result=self.node('bytecode',bad,out/'bad.json')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('different Leap ROM build',result.stderr)

    def test_compile_and_runtime_errors_are_reported(self):
        out=ROOT/'build/tests/invalid'; out.mkdir(parents=True,exist_ok=True)
        src=out/'source.bas'; src.write_text('PRINT missing(\n')
        result=self.node('compile',src,out/'bytecode.json')
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Compile error',result.stderr)
        out=self.build('divide_zero','x = 1 / 0\nPRINT x\nEND\n')
        result=self.node('bytecode',out/'program.lbc',out/'ram-execution.json')
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(json.loads((out/'ram-execution.json').read_text())['vmError'],5)


if __name__=='__main__':
    unittest.main(verbosity=2)
