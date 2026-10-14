"""Test translation semantics through the assembled Leap compiler and VM."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

from convert_ts2068_basic import Converter, Parser, convert_file, read_segments, split_statements

ROOT=Path(__file__).resolve().parents[1]
NODE=Path(__import__('os').environ.get('CROWN_NODE') or __import__('shutil').which('node') or 'node')


class ConversionTests(unittest.TestCase):
    def test_nested_numeric_index_in_string_array(self):
        self.run_listing('nested_string_array','10 DIM n(2): DIM s$(2,8)\n20 LET n(1)=2: LET s$(2)="GOBLIN"\n30 PRINT s$(n(1)): STOP\n','GOBLIN')

    def run_listing(self,name,text,expected):
        out=ROOT/'build/conversion-tests'/name; out.mkdir(parents=True,exist_ok=True)
        src=out/'source.bas'; dst=out/'source.leap.bas'; src.write_text(text)
        report=convert_file(src,dst)
        self.assertTrue(report['buildable'],report['diagnostics'])
        r=subprocess.run([str(NODE),str(ROOT/'scripts/leap_headless.mjs'),'compile',str(ROOT/'build/host'),str(dst),str(out/'bytecode.json')],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr+'\n'+dst.read_text())
        subprocess.run([sys.executable,str(ROOT/'scripts/package_leap_cartridge.py'),str(out/'bytecode.json'),'--output',str(out)],check=True,capture_output=True)
        r=subprocess.run([str(NODE),str(ROOT/'scripts/leap_headless.mjs'),'bytecode',str(ROOT/'build/host'),str(out/'program.lbc'),str(out/'result.json')],capture_output=True,text=True,timeout=20)
        self.assertEqual(r.returncode,0,r.stderr)
        result=json.loads((out/'result.json').read_text())['output']
        self.assertEqual(result,expected)

    def test_numbered_game_style_program(self):
        self.run_listing('smoke',(ROOT/'examples/regular_basic_smoke.bas').read_text(),
                         'SUM=204\n12 CROWN\nFLOOR=-2\nEXPVAR=3\n\n\n\n\nDONE')

    def test_if_controls_entire_remainder_of_line(self):
        self.run_listing('conditional','10 LET x=0\n20 IF x THEN PRINT "BAD": LET x=9\n30 IF x=0 THEN PRINT "OK": PRINT "STILL OK"\n40 STOP\n', 'OK\nSTILL OK')

    def test_nested_gosub_and_nonexistent_target(self):
        self.run_listing('subroutines','10 GO SUB 95: PRINT "BACK": STOP\n100 PRINT "OUTER": GO SUB 200: RETURN\n200 PRINT "INNER": RETURN\n','OUTER\nINNER\nBACK')

    def test_mixed_data_and_computed_restore(self):
        self.run_listing('data','10 LET t=200: RESTORE t: READ a,s$: PRINT a;s$\n20 RESTORE: READ a: PRINT a\n30 STOP\n100 DATA 1\n200 DATA -2.5,"X"\n','-2.5000X\n1')

    def test_strings_fixed_width_and_logical_values(self):
        self.run_listing('strings','10 DIM s$(2,5): LET s$(1)="HI"\n20 PRINT LEN(s$(1));LEN(s$(2))\n30 LET t$="ABC": PRINT t$(2 TO 3)\n40 PRINT 3 AND 5;",";0 OR 7\n50 STOP\n','55\nBC\n3,7')

    def test_graphics_coordinate_origin(self):
        self.run_listing('graphics','10 PLOT 4,170: DRAW 3,0\n20 LET a=POINT(4,170): LET b=POINT(7,170): LET c=POINT(7,169)\n30 PRINT a;b;c: STOP\n','110')

    def test_long_print_literal(self):
        self.run_listing('long_print','10 PRINT "'+('A'*40)+'"\n20 STOP\n',('A'*32)+'\n'+('A'*8))

    def test_read_into_fixed_width_string_array(self):
        self.run_listing('read_string_array','10 DIM s$(1,5): READ s$(1): PRINT LEN(s$(1));s$(1)\n20 STOP\n30 DATA "HI"\n','5HI')

    def test_unsupported_conversion_writes_partial_only(self):
        out=ROOT/'build/conversion-tests/blocked'; out.mkdir(parents=True,exist_ok=True)
        src=out/'source.bas'; dst=out/'source.leap.bas'
        src.write_text('10 ON ERR GO TO 100\n100 STOP\n')
        report=convert_file(src,dst)
        self.assertFalse(report['buildable'])
        self.assertIn('.partial.bas',report['output'])
        self.assertTrue(dst.with_suffix('.conversion.json').is_file())

    def test_computed_branch(self):
        self.run_listing('computed','10 LET n=95: GO TO n\n20 PRINT "BAD": STOP\n100 PRINT "OK": STOP\n','OK')

    def test_step_zero_loop(self):
        self.run_listing('zero_loop','10 FOR i=1 TO 2 STEP 0: LET i=i+1\n20 IF i<3 THEN NEXT i\n30 PRINT i: STOP\n','3')

    def test_blocking_operations_are_not_silently_dropped(self):
        for text in ('LOAD "LEVEL2" CODE','POKE 23562,10','ON ERR GO TO 100','RANDOMIZE USR 40000'):
            c=Converter([(10,text),(100,'STOP')]); report=c.convert()
            self.assertFalse(report['buildable'],text)
            self.assertTrue(report['diagnostics'])

    def test_listing_segments_and_strings_with_colons(self):
        self.assertEqual(split_statements('PRINT "A:B": REM C:D'),['PRINT "A:B"','REM C:D'])
        src=ROOT/'build/conversion-tests/segments.bas'; src.parent.mkdir(parents=True,exist_ok=True)
        src.write_text('10 STOP\n1 PRINT "GAME"\n2 STOP\n')
        self.assertEqual(len(read_segments(src)),2)
        with self.assertRaisesRegex(ValueError,'contains 2 programs'): convert_file(src,src.with_suffix('.leap.bas'))


if __name__=='__main__': unittest.main(verbosity=2)
