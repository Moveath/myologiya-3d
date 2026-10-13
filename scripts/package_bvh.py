"""Pin and ship the MIT raycast accelerator locally, without a CDN dependency."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'tools/node_modules/three-mesh-bvh'
TARGET = ROOT / 'site/vendor/three-mesh-bvh'
VERSION = '0.8.3'
assert json.loads((SOURCE / 'package.json').read_text())['version'] == VERSION
rows = []
for name in ['build/index.module.js', 'LICENSE']:
    target = TARGET / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE / name, target)
    rows.append(dict(file='vendor/three-mesh-bvh/' + name, bytes=target.stat().st_size,
                     sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
(TARGET / 'manifest.json').write_text(json.dumps(dict(package='three-mesh-bvh', version=VERSION,
    source='https://github.com/gkjohnson/three-mesh-bvh', license='MIT',
    modifications='Unmodified distribution files', files=rows), indent=2) + '\n', encoding='utf8')
print('Local raycast accelerator:', len(rows), 'files')
