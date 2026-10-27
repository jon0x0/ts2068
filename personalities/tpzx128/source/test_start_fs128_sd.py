import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from start_fs128_sd import queue_basic_session


class StartupTests(unittest.TestCase):
    def test_complete_sequence_and_no_duplicate_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            with patch('pico_debug.time.time_ns',return_value=1234567890000000000):
                jobs=queue_basic_session(root)
            self.assertEqual(len(jobs),6)
            self.assertEqual([job['requires_reset'] for job in jobs],[False]*5+[True])
            self.assertIn('FS128_BASIC_IMAGE=',jobs[4]['code'])
            self.assertIn('fs128_run_basic()',jobs[5]['code'])
            self.assertEqual(len(list((root/'pending').glob('*.json'))),6)
            ordered=[json.loads(path.read_text()) for path in sorted((root/'pending').glob('*.json'))]
            self.assertEqual([job['id'] for job in ordered],[job['id'] for job in jobs])
            with self.assertRaises(RuntimeError):queue_basic_session(root)


if __name__=='__main__':unittest.main()
