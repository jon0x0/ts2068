"""Exercise the actual supplied firmware handlers against a temporary image."""
import importlib.util,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'firmware'))
class Service(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'drive.img'
        self.initial=bytes(range(256))*192;self.path.write_bytes(self.initial)
        self.answer=[]
        def call(fn):
            try:return fn(),1
            except OSError:return 'error',3
        self.tp=types.ModuleType('dev_tspico')
        self.tp.PARAMS=lambda pre:pre
        self.tp.getArgs=lambda cmd:cmd.split(' ',1)[1] if ' ' in cmd else ''
        self.tp.CMD_PUT=self.answer.append;self.tp.MQ_READY=lambda:None
        self.tp.CH_READY=lambda:None;self.tp.CH_CALL=call
        self.tp.tspico_io=types.SimpleNamespace(CAN_STREAM=lambda:False)
        catalog=types.SimpleNamespace(resolve=lambda cur,name:str(self.path))
        ts=types.ModuleType('TS');ts.catalog=catalog
        self.modules=patch.dict(sys.modules,{'dev_tspico':self.tp,'TS':ts});self.modules.start()
        spec=importlib.util.spec_from_file_location('cpm_service',ROOT/'firmware/cpm_service.py')
        self.s=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.s)
        self.s.STORAGE='image'
        self.tsp=types.SimpleNamespace(cur_path='/')
    def tearDown(self):self.modules.stop();self.tmp.cleanup()
    def invoke(self,handler,lba=0,cmd=''):
        self.answer.clear();getattr(self.s,handler)(None,self.tsp,(lba,0),cmd)
        return bytes(self.answer)
    def test_capability_and_all_byte_values(self):
        out=self.invoke('CAP');self.assertEqual(out[2:-1],self.s.SIGNATURE)
        for lba in (0,1,63,64,383):
            out=self.invoke('READ',lba);self.assertEqual(out[2:-1],self.initial[lba*128:(lba+1)*128])
            crc=0
            for b in out[2:-1]:crc^=b
            self.assertEqual(out[-1],crc)
    def test_binary_write_commits_only_second_half(self):
        data=bytes(reversed(range(128)))
        self.assertEqual(self.invoke('WRITE0',10,'cmd '+data[:64].hex()),b'\x01')
        self.assertEqual(self.path.read_bytes(),self.initial)
        self.assertEqual(self.invoke('WRITE1',10,'cmd '+data[64:].hex()),b'\x01')
        self.assertEqual(self.path.read_bytes()[1280:1408],data)
    def test_wrong_second_half_does_not_write(self):
        self.invoke('WRITE0',1,'cmd '+'17'*64)
        self.assertEqual(self.invoke('WRITE1',2,'cmd '+'00'*64),b'\x05')
        self.assertEqual(self.path.read_bytes(),self.initial)
    def test_bad_hex_range_and_short_image(self):
        self.assertEqual(self.invoke('WRITE0',0,'cmd '+'xz'*64),b'\x05')
        self.assertEqual(self.invoke('READ',384),b'\x06')
        self.path.write_bytes(b'short')
        self.assertEqual(self.invoke('CAP'),b'\x03')
    def test_intervening_read_cancels_pending(self):
        self.invoke('WRITE0',1,'cmd '+'17'*64);self.invoke('READ',0)
        self.assertEqual(self.invoke('WRITE1',1,'cmd '+'00'*64),b'\x05')
        self.assertEqual(self.path.read_bytes(),self.initial)
    def test_320kb_config_and_high_sector(self):
        config=types.ModuleType('cpm_config')
        config.CPM_DIRECTORY='/CPM/FILES';config.CPM_STORAGE='image'
        config.CPM_IMAGE_PATH='/CPM/DRIVEA.IMG';config.CPM_IMAGE_SIZE=327680
        with patch.dict(sys.modules,{'cpm_config':config}):
            spec=importlib.util.spec_from_file_location('service320',ROOT/'firmware/cpm_service.py')
            service=importlib.util.module_from_spec(spec);spec.loader.exec_module(service)
        self.s=service;self.initial=bytes(range(256))*1280;self.path.write_bytes(self.initial)
        self.assertEqual(self.invoke('CAP')[2:-1],b'CPM1\x01\x80\x00\x0a')
        for lba in (511,512,2048,2559):
            self.assertEqual(self.invoke('READ',lba)[2:-1],self.initial[lba*128:(lba+1)*128])
        self.assertEqual(self.invoke('READ',2560),b'\x06')
        self.assertEqual(self.invoke('WRITE0',2559,'cmd '+'17'*64),b'\x01')
        self.assertEqual(self.invoke('WRITE1',2559,'cmd '+'ff'*64),b'\x01')
        self.assertEqual(self.path.read_bytes()[-128:],b'\x17'*64+b'\xff'*64)
    def test_directory_tap_mount_save_and_refresh(self):
        root=Path(self.tmp.name);folder=root/'CPM/FILES';folder.mkdir(parents=True)
        (folder/'HELLO.COM').write_bytes(b'hello')
        self.s.catalog.resolve=lambda cur,name:str(root/name.lstrip('/'))
        self.s.STORAGE='directory';self.s.CPM_DIRECTORY_KB=320
        self.assertEqual(self.invoke('CAP')[2:-1],b'CPMD\x02\x80\0\x0a')
        self.assertEqual(self.invoke('SAVE',cmd='cmd FIRST.TAP'),b'\x01')
        self.assertEqual(self.invoke('MOUNT',cmd='cmd FIRST.TAP'),b'\x01')
        self.assertEqual(self.invoke('WRITE0',32,'cmd '+'17'*64),b'\x01')
        self.assertEqual(self.invoke('WRITE1',32,'cmd '+'ff'*64),b'\x01')
        self.assertEqual(self.invoke('READ',32)[2:-1],b'\x17'*64+b'\xff'*64)
        self.assertEqual((folder/'HELLO.COM').read_bytes(),b'hello')
        self.assertEqual(self.invoke('SAVE',cmd='cmd SECOND.TAP'),b'\x01')
        self.assertEqual(self.invoke('SAVE',cmd='cmd FIRST.TAP'),b'\x03')
        (folder/'NEW.COM').write_bytes(b'new')
        self.assertEqual(self.invoke('MOUNT',cmd='cmd DIR'),b'\x01')
        self.assertIn('NEW.COM',self.s._directory.entries)
        self.assertEqual(self.invoke('MOUNT',cmd='cmd ../FIRST.TAP'),b'\x03')
