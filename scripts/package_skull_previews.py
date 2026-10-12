"""Convert screenshots of our source meshes to lossless web previews.

Render first: node tools/verify-skull-study.mjs --previews-only
The images inherit the source mesh attribution in site/LICENSE-MODELS.txt.
"""
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
for name in ('whole', 'base', 'face', 'sinuses', 'jaws', 'ear', 'muscles', 'variants'):
    source = root / 'shots/head-study' / f'preview-{name}.png'
    with Image.open(source) as im:
        im.save(root / 'site' / f'skull-study-{name}.webp', lossless=True)
print('Packaged 8 previews of existing source geometry')
