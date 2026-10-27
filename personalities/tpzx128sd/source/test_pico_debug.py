import tempfile
import time
import unittest
import types
from unittest.mock import patch
from pathlib import Path
from pico_debug import RawREPL,make_job,parse_result,dump,serve


class SerialDouble:
    def __init__(self,stdout=b"{'value': 7}\r\n",stderr=b'',banner=True):
        self.incoming=bytearray();self.writes=[];self.stdout=stdout;self.stderr=stderr;self.banner=banner
    def write(self,data):
        self.writes.append(data)
        if data==b'\r\x01' and self.banner:
            self.incoming.extend(b'>>> \r\nraw REPL; CTRL-B to exit\r\n>')
        if data==b'\x04':self.incoming.extend(b'OK'+self.stdout+b'\x04'+self.stderr+b'\x04>')
        if data==b'\x02':self.incoming.extend(b'\r\nMicroPython test banner\r\n>>> ')
    def read(self,count):
        result=bytes(self.incoming[:count]);del self.incoming[:count];return result
    def __enter__(self):return self
    def __exit__(self,*args):pass


class SerialTests(unittest.TestCase):
    def test_guided_interrupt_confirms_prompt_without_reboot(self):
        port=SerialDouble()
        port.incoming.extend(b'KeyboardInterrupt\r\n>>> ')
        RawREPL(port).interrupt_to_prompt()
        self.assertEqual(port.writes,[b'\x03',b'\x03',b'\x02'])
        self.assertEqual(port.incoming,b'')
        stdout,stderr=RawREPL(port).execute('print(7)')
        self.assertEqual(stderr,'')
    def test_guided_interrupt_missing_prompt_stops(self):
        port=SerialDouble()
        with self.assertRaises(TimeoutError):
            RawREPL(port,timeout=.002).interrupt_to_prompt()
        self.assertNotIn(b'\x04',port.writes)
    def test_filesystem_release_marker_is_shown_before_completion(self):
        port=SerialDouble(stdout=b"FS128_RELEASE_RESET\r\n{'paging_restored': True}\r\n")
        with patch('builtins.print') as printed:
            stdout,stderr=RawREPL(port).execute('run_filesystem_probe()')
        self.assertIn('RELEASE TS RESET NOW',printed.call_args.args[0])
        self.assertEqual(parse_result(stdout),{'paging_restored':True})
        self.assertEqual(stderr,'')
    def test_raw_exec_preserves_globals_without_reset_or_interrupt(self):
        port=SerialDouble();stdout,stderr=RawREPL(port).execute('print(value)\n')
        self.assertEqual(parse_result(stdout),{'value':7});self.assertEqual(stderr,'')
        self.assertEqual(port.writes[0],b'\r\x01');self.assertEqual(port.writes[-1],b'\x02')
        self.assertNotIn(b'\x03',port.writes)
        self.assertEqual(port.writes.count(b'\x04'),1)
        self.assertIn(b'print(value)\n',port.writes)
    def test_no_eof_execution_without_confirmed_raw_banner(self):
        port=SerialDouble(banner=False)
        with self.assertRaises(TimeoutError):RawREPL(port,timeout=.002).execute('reset(True)')
        self.assertEqual(port.writes,[b'\r\x01'])
    def test_target_traceback_separate_from_stdout(self):
        port=SerialDouble(stdout=b'',stderr=b'Traceback: deliberate test\r\n')
        stdout,stderr=RawREPL(port).execute('bad_name()')
        self.assertEqual(stdout,'');self.assertIn('Traceback',stderr)
        self.assertEqual(port.writes[-1],b'\x02')
    def test_source_chunking_and_output_limit(self):
        port=SerialDouble();RawREPL(port).execute('x=1\n'*80)
        chunks=port.writes[1:-2]
        self.assertTrue(all(len(chunk)<=128 for chunk in chunks))
        self.assertEqual(b''.join(chunks),('x=1\n'*80).encode())
        port.incoming.extend(b'oversize')
        with self.assertRaises(RuntimeError):RawREPL(port).read_until(b'!',time.monotonic()+1,limit=3)
    def test_jobs_require_reset_for_active_operations(self):
        for action in ('restart','inspect','pause-dma','fixed-address','rom-arm'):
            self.assertTrue(make_job(action)['requires_reset'])
        self.assertFalse(make_job('preflight')['requires_reset'])
        self.assertFalse(make_job('rom-read')['requires_reset'])
        job=make_job('load','personality128.py')
        self.assertFalse(job['requires_reset'])
        self.assertIn('def start(',job['code'])
        with self.assertRaises(ValueError):make_job('load','../../main.py')
    def test_live_read_is_bounded_to_initial_fifo_count(self):
        class Probe:
            def __init__(self):self.reads=0
            def rx_fifo(self):return 4
            def get(self):self.reads+=1;return 0xf301
        probe=Probe();printed=[]
        job=make_job('rom-read-live');self.assertFalse(job['requires_reset'])
        ns={'_rom_probe':probe,'mem32':{0xd0000004:0},'print':printed.append}
        exec(job['code'],ns)
        self.assertEqual(probe.reads,4)
        self.assertEqual(printed[0]['rom_read_samples_early_late'],[('0xf3','0x1')]*4)
    def test_live_read_decodes_bus_cycle_bits(self):
        class Probe:
            def rx_fifo(self):return 1
            def get(self):return (0x2f3<<12)|0x301
        printed=[];ns={'_rom_probe':Probe(),'ROM_PROBE_SAMPLE_BITS':12,
                       'mem32':{0xd0000004:0},'print':printed.append}
        exec(make_job('rom-read-live')['code'],ns)
        self.assertEqual(printed[0]['rom_read_samples_early_late'],[('0xf3','0x1')])
        self.assertEqual(printed[0]['cycle_signals_early_late'],[[
            {'a0':0,'direction':1,'u6_disabled':0,'mreq':0},
            {'a0':1,'direction':1,'u6_disabled':0,'mreq':0}]])
    def test_custom_code_and_atomic_result(self):
        with self.assertRaises(ValueError):make_job('exec',Path(tempfile.gettempdir())/'outside.py')
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'results'/'job.json';dump(path,{'status':'ok'})
            self.assertIn('ok',path.read_text());self.assertFalse(path.with_suffix('.tmp').exists())
    def test_server_commits_error_and_stops_before_next_job(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            first=make_job('preflight');second=make_job('restart')
            dump(root/'pending'/'01.json',first);dump(root/'pending'/'02.json',second)
            port=SerialDouble(stderr=b'Traceback: test failure\r\n')
            args=types.SimpleNamespace(directory=root,port='FAKE',timeout=1,once=False)
            with patch.dict('sys.modules',{'serial':types.SimpleNamespace(Serial=lambda *a,**kw:port)}), \
                    patch('builtins.input',return_value=''),patch('builtins.print'):
                self.assertEqual(serve(args),1)
            result=(root/'results'/'01.json').read_text()
            self.assertIn('target_error',result)
            self.assertTrue((root/'pending'/'02.json').exists())
            self.assertFalse(list((root/'running').glob('*.json')))


if __name__=='__main__':unittest.main()
