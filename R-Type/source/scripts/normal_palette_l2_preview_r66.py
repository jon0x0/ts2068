from pathlib import Path
p=Path('scripts/refine_l2_head_review_r66.py');s=p.read_text().replace("im.save(O/f'{i}_isolated_{size}.png')", "im=Image.fromarray(np.minimum(np.asarray(im),205).astype('uint8'));im.save(O/f'{i}_isolated_{size}.png')");p.write_text(s)
