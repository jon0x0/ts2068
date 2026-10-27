import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
import unittest

spec=importlib.util.spec_from_file_location('fslegacy',Path('firmware/fs128_legacy.py'))
legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)


class MQ:
    def __init__(self,data=b''):self.rx=list(data);self.sent=[]
    def rx_fifo(self):return len(self.rx)
    def tx_fifo(self):return 0
    def get(self):return self.rx.pop(0)
    def put(self,value):self.sent.append(value)


def request(text,direction=1):
    data=text.encode('ascii');length=len(data)
    pre=bytes([66,direction,255,0,0,0,0,length,0])
    pre+=bytes([legacy.xor_bytes(pre)])
    body=bytes([68,length,0])+data
    return pre+body+bytes([legacy.xor_bytes(body)])


def firmware(data=b''):
    fw=SimpleNamespace(MQ=MQ(data),TSP=SimpleNamespace(f_name='',cur_path='/sd/TAP'),
                       files=['FS128.TAP','TPZX128.ROM'],log_entries='')
    for name in ('MOUNT_FILE','ACTIVATE_MQ','SEND_MSG','LOAD_TS','SAVE_TS','CDIR',
                 'UNMOUNT','REW','DIR','PATH','DIR_FILES'):
        setattr(fw,name,Mock())
    return fw


class LegacyTests(unittest.TestCase):
    def test_directory_pages_have_bounded_replies_and_no_total_listing_limit(self):
        header='H'*128
        entries=''.join(('%03d'%i).ljust(32) for i in range(100))
        output=''
        for page in range(8):
            fw=firmware(request('tpi:dirpage %04X'%page));fw.lista=header+entries
            legacy.Legacy100Backend(fw).step()
            sent=fw.MQ.sent
            self.assertEqual(sent[:6],[1,0x40,1,0x40,0x81,1])
            expected_more=(page+1)*448<len(entries)
            self.assertEqual(sent[6],ord('+' if expected_more else '.'))
            data=''.join(chr(v) for v in sent[7:-1])
            self.assertTrue(data.startswith(header))
            self.assertLessEqual(len(data),576)
            output+=data[128:]
            fw.DIR.assert_not_called()
        self.assertEqual(output,entries)
    def test_directory_page_rejects_invalid_page_number(self):
        for number in ('-1','10000','garbage'):
            fw=firmware(request('tpi:dirpage '+number));fw.lista=''
            legacy.Legacy100Backend(fw).step()
            self.assertEqual(fw.SEND_MSG.call_args.args[2],5)
    def test_save_reply_is_held_until_write_cleanup_and_io_restoration(self):
        pre=bytes([0,0,255,0,0,0,0,17,0]);pre+=bytes([legacy.xor_bytes(pre)])
        fw=firmware(pre);events=[]
        native=SimpleNamespace(END_MSG=lambda *args:events.append('reply'))
        original=native.END_MSG
        def save(mq,tsp):
            native.END_MSG(mq,False,'saved','',1)
            events.append('write')
            return mq,tsp,''
        fw.SAVE_TS=save
        fw.DIR_FILES.side_effect=lambda:events.append('directory')
        fw.ACTIVATE_MQ.side_effect=lambda:events.append('io')
        with patch.dict('sys.modules',{'tspico_io':native}),patch('os.umount',create=True,side_effect=lambda p:events.append('unmount')):
            legacy.Legacy100Backend(fw).step()
        self.assertEqual(events,['write','directory','unmount','io','reply'])
        self.assertIs(native.END_MSG,original)
    def test_ack_mid_detection_rejects_floating_bus(self):
        self.assertEqual(legacy.classify_probe(1,0x40),1)
        self.assertEqual(legacy.classify_probe(1,0xf7),2)
        for ack,ready in ((255,255),(1,255),(0,0x40),(1,0)):
            with self.assertRaises(ValueError):legacy.classify_probe(ack,ready)
    def test_mount_reuses_native_handler_and_canonical_case(self):
        fw=firmware(request('tpi:fs128.tap'))
        result=legacy.Legacy100Backend(fw).step()
        self.assertEqual(fw.MQ.sent,[1,0x40,1])
        fw.MOUNT_FILE.assert_called_once_with()
        fw.ACTIVATE_MQ.assert_called_once_with()
        self.assertEqual(fw.TSP.f_name,'/sd/TAP/FS128.TAP')
        self.assertFalse(result['closed'])
    def test_no_memory_or_configuration_commands_forwarded(self):
        for command in ('tpi:memboot','tpi:memdock','tpi:boot','tpi:rm x','tpi:format'):
            fw=firmware(request(command,0));legacy.Legacy100Backend(fw).step()
            self.assertEqual(fw.SEND_MSG.call_args.args[2],5)
            fw.MOUNT_FILE.assert_not_called()
    def test_rom_mount_is_not_allowed_as_data_file(self):
        fw=firmware(request('tpi:TPZX128.ROM'))
        legacy.Legacy100Backend(fw).step()
        fw.MOUNT_FILE.assert_not_called()
        self.assertEqual(fw.SEND_MSG.call_args.args[2],5)
    def test_bad_checksum_does_not_call_handler(self):
        for offset in (9,-1):
            data=bytearray(request('tpi:FS128.TAP'));data[offset]^=1
            fw=firmware(data)
            with self.assertRaises(ValueError):legacy.Legacy100Backend(fw).step()
            fw.MOUNT_FILE.assert_not_called()
    def test_exit_and_directory(self):
        fw=firmware(request('tpi:dir'));legacy.Legacy100Backend(fw).step()
        fw.DIR.assert_called_once_with()
        fw=firmware(request('tpi:fsend',0));backend=legacy.Legacy100Backend(fw)
        self.assertTrue(backend.step()['closed'])
        with self.assertRaises(RuntimeError):backend.step()
    def test_cd_arguments_keep_native_body_offsets(self):
        fw=firmware(request('tpi:cd /',0));legacy.Legacy100Backend(fw).step()
        self.assertEqual(fw.CDIR.call_args.args[1][10:],'/')
    def test_data_transfer_calls_native_loader(self):
        pre=bytes([255,1,255,0,0,0,128,4,0]);pre+=bytes([legacy.xor_bytes(pre)])
        fw=firmware(pre);fw.LOAD_TS.return_value=(fw.MQ,fw.TSP,'loaded')
        legacy.Legacy100Backend(fw).step()
        self.assertEqual(fw.MQ.sent,[1])
        self.assertEqual(fw.log_entries,'loaded')
        self.assertEqual(fw.LOAD_TS.call_args.args[0],pre)
    def test_modern_requires_explicit_verified_factory(self):
        fw=firmware();fw.MQ_READY=Mock()
        with self.assertRaises(ValueError):legacy.select_backend(1,fw)
        with self.assertRaises(ValueError):legacy.select_backend(2,fw)
        factory=Mock(return_value='modern')
        self.assertEqual(legacy.select_backend(2,fw,factory),'modern')


if __name__=='__main__':unittest.main()
