"""A bounded CP/M 2.2 sector view of ordinary SD files, for MicroPython.

256KB, 1KB blocks, 128 directory entries, user 0. Only metadata is resident;
unclosed data lives in private block scratch files, never a public disk image.
"""
import os
import json

SECTOR = 128
BLOCK = 1024
BLOCKS = 256
DIRECTORY_BYTES = 4096
SECTORS = BLOCKS * 8
SIGNATURE = b'CPMD\x01\x80\x00\x08'
OWNER = b'TS2068 CP/M directory v1\n'

def exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False

def filename(name):
    """Return canonical 8.3 or None; never accept host path syntax."""
    parts = name.upper().split('.')
    allowed = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&()-@^_{}~'
    if len(parts) == 1:
        parts.append('')
    if len(parts) != 2 or not 1 <= len(parts[0]) <= 8 or not 0 <= len(parts[1]) <= 3:
        return None
    return (parts[0]+('.'+parts[1] if parts[1] else '')) if all(c in allowed for p in parts for c in p) else None

def put(path, data):
    with open(path, 'wb') as f:
        if f.write(data) != len(data):
            raise OSError('short write')
        f.flush()

class DirectoryVolume:
    def __init__(self, root, size=262144, block_size=1024):
        if (size, block_size) not in ((262144,1024),(327680,2048)):
            raise OSError("unsupported directory geometry")
        self.block_size = block_size
        self.block_count = size//block_size
        self.sectors = size//128
        self.per_block = block_size//128
        self.extent_bytes = block_size*16
        self.extent_records = self.extent_bytes//128
        self.extent_mask = block_size//1024-1
        self.signature = b"CPMD"+bytes((1 if block_size==1024 else 2,128,self.sectors&255,self.sectors>>8))
        self.root = root.rstrip('/')
        if not os.stat(self.root)[0] & 0x4000:
            raise OSError('CP/M root is not a directory')
        self.work = self.root + '/.cpm-work'
        self._prepare_work()
        self._recover()
        # Abandoned unclosed sectors do not survive a fresh mount.
        for name in os.listdir(self.work):
            if name != 'OWNER':
                os.remove(self.work + '/' + name)
        self.directory = bytearray(b'\xe5' * DIRECTORY_BYTES)
        self.owners = {}
        self.native = self._scan()
        block = DIRECTORY_BYTES // self.block_size
        slot = 0
        for name in sorted(self.native):
            actual, size, _ = self.native[name]
            records = (size + 127) // 128
            for extent, start in enumerate(range(0, max(1, records), self.extent_records)):
                count = min(self.extent_records, max(0, records-start))
                allocation = (count+self.per_block-1)//self.per_block
                if slot >= 128 or block+allocation > self.block_count:
                    raise OSError('CP/M directory capacity exceeded')
                entry = bytearray(32)
                stem, _, ext = name.partition('.')
                entry[1:12] = ('%-8s%-3s' % (stem, ext)).encode()
                logical_extent = extent*(self.extent_mask+1)+max(0,count-1)//128
                entry[12] = logical_extent & 31
                entry[14] = logical_extent >> 5
                entry[15] = (count-1)%128+1 if count else 0
                entry[16:16+allocation] = bytes(range(block, block+allocation))
                self.directory[slot*32:slot*32+32] = entry
                for i in range(allocation):
                    self.owners[block+i] = (actual, (start*128)+i*self.block_size)
                block += allocation
                slot += 1
        self.entries = self._parse(self.directory)

    def _prepare_work(self):
        if not exists(self.work):
            os.mkdir(self.work)
            put(self.work+'/OWNER', OWNER)
        with open(self.work+'/OWNER', 'rb') as f:
            if f.read() != OWNER:
                raise OSError('reserved work directory has wrong owner')
        for name in os.listdir(self.work):
            if name in ('OWNER', 'TRANSACTION', 'COMMITTED'):
                continue
            if len(name) == 9 and name[0] in 'BTO' and name[1:5].isdigit() and name[5:] in ('.BLK','.NEW','.OLD'):
                continue
            raise OSError('unexpected file in reserved work directory')

    def _scan(self):
        files = {}
        for actual in os.listdir(self.root):
            name = filename(actual)
            if not name:
                continue
            st = os.stat(self.root+'/'+actual)
            if st[0] & 0x4000:
                continue
            if name in files:
                raise OSError('case-colliding CP/M filenames')
            files[name] = (actual, st[6], st[8])
        return files

    def _parse(self, directory):
        files = {}
        allocated = set()
        for pos in range(0, DIRECTORY_BYTES, 32):
            e = directory[pos:pos+32]
            if e[0] == 0xe5:
                continue
            if e[0] != 0 or e[15] > 128 or e[12] > 31 or e[13] != 0 or e[14] > 63:
                raise OSError('unsupported CP/M directory entry/user area')
            stem = bytes(b & 127 for b in e[1:9]).decode().rstrip(' ')
            ext = bytes(b & 127 for b in e[9:12]).decode().rstrip(' ')
            name = filename(stem+'.'+ext)
            if name is None:
                raise OSError('invalid CP/M filename')
            logical_extent = e[12] + 32*e[14]
            extent = logical_extent//(self.extent_mask+1)
            parts = files.setdefault(name, {})
            if extent in parts:
                raise OSError('duplicate extent')
            blocks = list(e[16:32])
            for block in blocks:
                if block:
                    if block < DIRECTORY_BYTES//self.block_size or block >= self.block_count or block in allocated:
                        raise OSError('invalid or shared allocation block')
                    allocated.add(block)
            parts[extent] = ((logical_extent & self.extent_mask)*128+e[15], blocks)
        return files

    def _block_path(self, block):
        return self.work+'/B%04d.BLK' % block

    def _data(self, block, offset, count):
        if not block:
            return bytes(count)
        scratch = self._block_path(block)
        if exists(scratch):
            with open(scratch, 'rb') as f:
                f.seek(offset)
                return f.read(count)
        if block not in self.owners:
            return bytes(count)
        name, base = self.owners[block]
        with open(self.root+'/'+name, 'rb') as f:
            f.seek(base+offset)
            data = f.read(count)
        pad = b'\x1a' if name.upper().endswith(('.TXT','.ASM','.SUB')) else b'\0'
        return data + pad*(count-len(data))

    def read(self, lba):
        if not 0 <= lba < self.sectors:
            raise OSError('sector outside volume')
        if lba < 32:
            return bytes(self.directory[lba*128:lba*128+128])
        return self._data(lba//self.per_block, (lba%self.per_block)*128, 128)

    def _size(self, parts):
        return max(extent*self.extent_bytes+records*128 for extent,(records,_) in parts.items()) if parts else 0

    def _write_file(self, path, parts, size):
        with open(path, 'wb') as f:
            for offset in range(0, size, 128):
                extent = offset//self.extent_bytes
                within = offset%self.extent_bytes
                blocks = parts.get(extent, (0,[0]*16))[1]
                data = self._data(blocks[within//self.block_size], within%self.block_size, min(128,size-offset))
                if f.write(data) != len(data):
                    raise OSError('short native file write')
            f.flush()

    def _recover(self):
        transaction = self.work+'/TRANSACTION'
        if not exists(transaction):
            return
        with open(transaction, 'r') as f:
            plan = json.loads(f.read())
        old = plan['old']
        new = plan['new']
        if any(filename(name) is None for name in old+new):
            raise OSError('invalid recovery journal filename')
        if not exists(self.work+'/COMMITTED'):
            # Remove installed new files only when original is backed up,
            # or when there was no original by that name.
            for name in new:
                original = next((i for i,v in enumerate(old) if v.upper()==name.upper()), None)
                if original is None or exists(self.work+'/O%04d.OLD' % original):
                    if exists(self.root+'/'+name):
                        os.remove(self.root+'/'+name)
            for i,name in enumerate(old):
                backup = self.work+'/O%04d.OLD' % i
                if exists(backup):
                    if exists(self.root+'/'+name):
                        os.remove(self.root+'/'+name)
                    os.rename(backup,self.root+'/'+name)
        for name in os.listdir(self.work):
            if name.startswith(('O','T')) and name != 'OWNER' and name != 'TRANSACTION':
                os.remove(self.work+'/'+name)
        if exists(self.work+'/COMMITTED'):
            os.remove(self.work+'/COMMITTED')
        os.remove(transaction)

    def _commit(self, directory):
        files = self._parse(directory)
        if self._scan() != self.native:
            raise OSError('SD directory changed outside CP/M; remount required')
        changed = []
        for name,parts in files.items():
            dirty = any(exists(self._block_path(b)) for _,blocks in parts.values() for b in blocks if b)
            if parts != self.entries.get(name) or dirty:
                changed.append(name)
        removed = [name for name in self.entries if name not in files or name in changed]
        old_names = [self.native[name][0] for name in removed]
        sizes = {}
        # Stage every replacement before renaming or deleting any native file.
        for i,name in enumerate(changed):
            parts = files[name]
            size = self._size(parts)
            # Rename/attribute-only changes preserve untouched native lengths.
            source = next((n for n,p in self.entries.items() if p==parts), None)
            dirty = any(exists(self._block_path(b)) for _,bs in parts.values() for b in bs if b)
            if source is not None and not dirty:
                size = self.native[source][1]
            sizes[name] = size
            self._write_file(self.work+'/T%04d.NEW' % i,parts,size)
        put(self.work+'/TRANSACTION',json.dumps({'old':old_names,'new':changed}).encode())
        try:
            for i,name in enumerate(old_names):
                os.rename(self.root+'/'+name,self.work+'/O%04d.OLD' % i)
            for i,name in enumerate(changed):
                os.rename(self.work+'/T%04d.NEW' % i,self.root+'/'+name)
            put(self.work+'/COMMITTED',b'1')
        except OSError:
            self._recover()
            raise
        self._recover()
        # All visible changes are committed. Publish the new sector metadata.
        self.directory = directory
        self.entries = files
        self.native = self._scan()
        owners = {}
        for name,parts in files.items():
            for extent,(_,blocks) in parts.items():
                for i,block in enumerate(blocks):
                    if block:
                        owners[block] = (self.native[name][0],extent*self.extent_bytes+i*self.block_size)
        self.owners = owners
        for block in owners:
            scratch = self._block_path(block)
            if exists(scratch):
                os.remove(scratch)

    def write(self, lba, data):
        if not 0 <= lba < self.sectors or len(data) != 128:
            raise OSError('invalid sector write')
        if lba < 32:
            directory = bytearray(self.directory)
            directory[lba*128:lba*128+128] = data
            self._commit(directory)
        else:
            block = lba//self.per_block
            contents = bytearray(self._data(block,0,self.block_size))
            contents[(lba%self.per_block)*128:(lba%self.per_block)*128+128] = data
            put(self._block_path(block),contents)
