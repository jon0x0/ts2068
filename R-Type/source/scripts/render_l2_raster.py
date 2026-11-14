from pathlib import Path
import numpy as np
from PIL import Image
from build_graphics import PALETTE
out=Path(__file__).resolve().parents[1]/'build/diagnostics/l2_blue'
for p in out.glob('*.pixels.bin'):
 a=np.frombuffer(p.read_bytes(),dtype='uint8').reshape(-1,640);Image.fromarray(PALETTE[a].astype('uint8')).save(p.with_suffix('.png'))
