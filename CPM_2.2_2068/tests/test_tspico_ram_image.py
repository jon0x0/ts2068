import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from tspico_ram_image import SIZE,PAGE,MAGIC,tap_code,blocks,decode_chunk,encode_image,encode_volumes,decode_image,decode_volumes

class RamImage(unittest.TestCase):
    def test_volume_sizes_and_round_trip(self):
        image=bytes(range(256))*(SIZE//256)
        volumes=encode_volumes(image);self.assertEqual(len(volumes),8)
        recovered=[]
        for volume,(name,data) in enumerate(volumes.items()):
            self.assertLess(len(data),45056)
            parts=blocks(data);self.assertEqual(len(parts),12)
            self.assertEqual(parts[1][1:13],MAGIC)
            self.assertEqual(parts[1][13:15],bytes((volume,8)))
            for i in range(5):
                record=volume*5+i
                recovered.append(parts[3+i*2][1:-1])
                self.assertEqual(parts[2+i*2][2:12].rstrip(),f'CPM{record:02}'.encode())
        self.assertEqual(b''.join(recovered),image)
        self.assertEqual(len(blocks(encode_image(image))),82)
        self.assertEqual(decode_image(encode_image(image)),image)
        with tempfile.TemporaryDirectory() as folder:
            for name,data in volumes.items():(Path(folder)/name).write_bytes(data)
            self.assertEqual(decode_volumes(Path(folder)),image)
    def test_export_chunks_and_corruption(self):
        data=bytes(range(256))*32
        encoded=tap_code('CPM09',data)
        self.assertEqual(decode_chunk(encoded,'CPM09'),data)
        for bad in [encoded[:-1],encoded[:-1]+bytes((encoded[-1]^1,)),encoded+b'\0']:
            with self.assertRaises(ValueError):decode_chunk(bad,'CPM09')
        with self.assertRaises(ValueError):decode_chunk(encoded,'CPM10')
        with self.assertRaises(ValueError):encode_image(b'short')
        with self.assertRaises(ValueError):decode_chunk(tap_code('CPM09',data[:-1]),'CPM09')

if __name__=='__main__':unittest.main()
