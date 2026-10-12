"""Prepare a local, generic-axis OpenEar mesh inspection surface."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build_head/complete_temporal'
source = (ROOT / 'build_head/pintool.html').read_text(encoding='utf-8')
source = source.replace("import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';", "import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';\nimport { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';")
source = source.replace('new GLTFLoader().load(', 'new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).load(')
source = source.replace("'head_hi.glb'", "'skull-openear.glb'")
source = source.replace("/^[mboc]\\|/", "/^openear\\|/")
source = source.replace("kind === 'b' || kind === 'o'", "kind === 'openear'")
source = source.replace('window.__meshes = meshes;', 'window.__meshes = meshes; window.__scene = scene; window.__renderer = r; window.__camera = cam;')
for old, new in [('СПЕРЕДИ · вправо=медиально', '+Z препарата'),
                 ('СЗАДИ · вправо=латерально', '−Z препарата'),
                 ('СНАРУЖИ · вправо=вперёд', '−X препарата'),
                 ('ИЗНУТРИ · вправо=назад', '+X препарата'),
                 ('СВЕРХУ · вверх=назад, вправо=медиально', '+Y препарата'),
                 ('СНИЗУ · вверх=вперёд, вправо=медиально', '−Y препарата')]:
    source = source.replace(old, new)
(OUT / 'review.html').write_text(source, encoding='utf-8')
runner = (ROOT / 'tools/head-review.mjs').read_text(encoding='utf-8')
runner = runner.replace("from 'playwright'", "from '../../tools/node_modules/playwright/index.mjs'")
runner = runner.replace("path.dirname(fileURLToPath(import.meta.url)), '..'", "path.dirname(fileURLToPath(import.meta.url)), '../..'")
runner = runner.replace("'qhead'", "'build_head/complete_temporal/jobs'")
runner = runner.replace("|| 8774", "|| 8778")
runner = runner.replace("'/build_head/pintool.html'", "'/build_head/complete_temporal/review.html'")
(OUT / 'review.mjs').write_text(runner, encoding='utf-8')
(OUT / 'jobs').mkdir(exist_ok=True)
print('Prepared local review surface')
