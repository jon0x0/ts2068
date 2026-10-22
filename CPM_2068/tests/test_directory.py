import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'firmware'))
from cpm_directory import DirectoryVolume

class Directory(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        (self.root/'HELLO.COM').write_bytes(b'hello')
        self.v=DirectoryVolume(str(self.root))
    def tearDown(self):self.tmp.cleanup()
    def entry(self,name):
        raw=self.v.directory
        stem,ext=name.split('.');key=f'{stem:8}{ext:3}'.encode()
        return next(i for i in range(0,4096,32) if raw[i]==0 and bytes(raw[i+1:i+12])==key)
    def directory_write(self,offset,change):
        sector=offset//128;data=bytearray(self.v.read(sector));change(data,offset%128)
        self.v.write(sector,data)
    def test_mount_lengths_padding_and_native_names(self):
        p=self.entry('HELLO.COM');e=self.v.directory[p:p+32]
        self.assertEqual(e[15],1);self.assertEqual(self.v.read(e[16]*8),b'hello'+bytes(123))
        self.assertEqual((self.root/'HELLO.COM').read_bytes(),b'hello')
        (self.root/'long-file-name.txt').write_text('ignored')
        (self.root/'SUBDIR').mkdir();v=DirectoryVolume(str(self.root))
        self.assertEqual(list(v.entries),['HELLO.COM'])
    def test_320kb_physical_extents_and_high_offsets(self):
        data=bytes(range(256))*700;(self.root/'LARGE.BIN').write_bytes(data)
        v=DirectoryVolume(str(self.root),327680,2048)
        self.assertEqual(v.signature,b'CPMD\x02\x80\0\x0a')
        for extent,(records,blocks) in v.entries['LARGE.BIN'].items():
            for n in range(records):
                pos=extent*32768+n*128
                self.assertEqual(v.read(blocks[n//16]*16+n%16),data[pos:pos+128].ljust(128,b'\0'))
        v.write(0,v.read(0))
        self.assertEqual((self.root/'LARGE.BIN').read_bytes(),data)
        extent=2;records,allocation=v.entries['LARGE.BIN'][extent]
        v.write(allocation[0]*16,b'\x17'*128)
        # Closing the directory entry publishes staged data through 32KB extents.
        for sector in range(32):v.write(sector,v.read(sector))
        actual=(self.root/'LARGE.BIN').read_bytes()
        self.assertEqual(actual[65536:65664],b'\x17'*128)
    def test_rename_preserves_exact_length(self):
        p=self.entry('HELLO.COM')
        self.directory_write(p,lambda s,i:s.__setitem__(slice(i+1,i+9),b'RENAMED '))
        self.assertFalse((self.root/'HELLO.COM').exists())
        self.assertEqual((self.root/'RENAMED.COM').read_bytes(),b'hello')
    def test_delete_native_file(self):
        p=self.entry('HELLO.COM');self.directory_write(p,lambda s,i:s.__setitem__(i,0xe5))
        self.assertFalse((self.root/'HELLO.COM').exists())
    def test_data_staging_and_close(self):
        p=self.entry('HELLO.COM');block=self.v.directory[p+16]
        self.v.write(block*8,bytes(range(128)))
        self.assertEqual((self.root/'HELLO.COM').read_bytes(),b'hello')
        self.v.write(p//128,self.v.read(p//128))
        self.assertEqual((self.root/'HELLO.COM').read_bytes(),bytes(range(128)))
    def test_new_file_and_remount(self):
        block=5;self.v.write(block*8,b'NEW'+bytes(125))
        e=bytearray(32);e[1:12]=b'NEW     BIN';e[15]=1;e[16]=block
        s=bytearray(self.v.read(0));s[32:64]=e;self.v.write(0,s)
        self.assertEqual((self.root/'NEW.BIN').read_bytes(),b'NEW'+bytes(125))
        self.assertIn('NEW.BIN',DirectoryVolume(str(self.root)).entries)
    def test_external_edits_refuse_commit(self):
        (self.root/'NEW.COM').write_bytes(b'external')
        with self.assertRaises(OSError):self.v.write(0,self.v.read(0))
        self.assertEqual((self.root/'NEW.COM').read_bytes(),b'external')
    def test_bad_user_and_shared_blocks_are_rejected(self):
        s=bytearray(self.v.read(0));s[0]=1
        with self.assertRaises(OSError):self.v.write(0,s)
        s=bytearray(self.v.read(0));s[32:64]=s[:32];s[33:41]=b'COPY    '
        with self.assertRaises(OSError):self.v.write(0,s)
        self.assertEqual((self.root/'HELLO.COM').read_bytes(),b'hello')
    def test_large_files_use_multiple_extents_without_loading_contents(self):
        data=bytes(range(256))*200;(self.root/'LARGE.BIN').write_bytes(data)
        v=DirectoryVolume(str(self.root));self.assertEqual(len(v.entries['LARGE.BIN']),4)
        for extent,(records,blocks) in v.entries['LARGE.BIN'].items():
            for n in range(records):
                pos=extent*16384+n*128
                self.assertEqual(v.read(blocks[n//8]*8+n%8),data[pos:pos+128])
    def test_capacity_and_reserved_folder(self):
        (self.root/'HUGE.BIN').write_bytes(bytes(256*1024))
        with self.assertRaises(OSError):DirectoryVolume(str(self.root))
        (self.root/'HUGE.BIN').unlink();(self.root/'.cpm-work/foreign').write_text('keep')
        with self.assertRaises(OSError):DirectoryVolume(str(self.root))
        self.assertTrue((self.root/'.cpm-work/foreign').exists())
    def test_rollback_when_install_rename_fails(self):
        import cpm_directory
        real=cpm_directory.os.rename
        def fail(src,dst):
            if src.endswith('.NEW'):raise OSError('injected failure')
            real(src,dst)
        p=self.entry('HELLO.COM')
        with patch.object(cpm_directory.os,'rename',side_effect=fail):
            with self.assertRaises(OSError):
                self.directory_write(p,lambda s,i:s.__setitem__(slice(i+1,i+9),b'RENAMED '))
        self.assertEqual((self.root/'HELLO.COM').read_bytes(),b'hello')
        self.assertFalse((self.root/'RENAMED.COM').exists())
    def test_recover_interrupted_transaction(self):
        import json,os
        work=self.root/'.cpm-work'
        (work/'TRANSACTION').write_text(json.dumps({'old':['HELLO.COM'],'new':['NEW.COM']}))
        os.rename(self.root/'HELLO.COM',work/'O0000.OLD');(self.root/'NEW.COM').write_bytes(b'incomplete')
        DirectoryVolume(str(self.root))
        self.assertEqual((self.root/'HELLO.COM').read_bytes(),b'hello')
        self.assertFalse((self.root/'NEW.COM').exists())
    def test_extensionless_and_lowercase_files(self):
        (self.root/'notes').write_bytes(b'no extension')
        v=DirectoryVolume(str(self.root));self.assertIn('NOTES',v.entries)
        s=bytearray(v.read(0))
        pos=next(i for i in range(0,128,32) if s[i+1:i+9]==b'NOTES   ')
        s[pos+1:pos+9]=b'RENAMED '
        v.write(0,s)
        self.assertFalse((self.root/'notes').exists())
        self.assertEqual((self.root/'RENAMED').read_bytes(),b'no extension')
    def test_preserve_exact_length_when_other_file_changes(self):
        (self.root/'LONG.BIN').write_bytes(bytes(range(256))*200)
        self.v=DirectoryVolume(str(self.root));p=self.entry('LONG.BIN')
        # Dirty the first block of a multi-extent file and close it.
        block=self.v.directory[p+16]
        self.v.write(block*8,b'X'*128);self.v.write(p//128,self.v.read(p//128))
        self.assertEqual((self.root/'HELLO.COM').read_bytes(),b'hello')
        self.assertEqual((self.root/'LONG.BIN').read_bytes()[:128],b'X'*128)
