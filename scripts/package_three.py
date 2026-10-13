"""Ship the pinned renderer locally so CDN availability cannot disable the atlas."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'tools/node_modules/three'
TARGET = ROOT/'site/vendor/three'
VERSION = '0.170.0'
FILES = ['build/three.module.js', 'examples/jsm/controls/OrbitControls.js',
         'examples/jsm/loaders/GLTFLoader.js', 'examples/jsm/utils/BufferGeometryUtils.js',
         'examples/jsm/libs/meshopt_decoder.module.js', 'LICENSE']
assert json.loads((SOURCE/'package.json').read_text())['version'] == VERSION
rows=[]
for name in FILES:
    source=SOURCE/name
    target=TARGET/name
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target)
    rows.append(dict(file='vendor/three/'+name,bytes=target.stat().st_size,
                     sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
meshopt_license=(ROOT/'tools/node_modules/gltfpack/LICENSE.md').read_text(encoding='utf8')
# The decoder retains its original 2016–2022 copyright notice in the source.
target=TARGET/'MESHOPT-LICENSE.txt'
target.write_text(meshopt_license,encoding='utf8')
rows.append(dict(file='vendor/three/'+target.name,bytes=target.stat().st_size,
                 sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
(ROOT/'site/vendor/three/manifest.json').write_text(json.dumps(dict(package='three',version=VERSION,
    source='https://github.com/mrdoob/three.js/tree/r170',license='MIT',modifications='Unmodified selected distribution files',files=rows),indent=2)+'\n',encoding='utf8')
print('Local renderer:',len(rows),'files;',sum(r['bytes'] for r in rows),'bytes')
