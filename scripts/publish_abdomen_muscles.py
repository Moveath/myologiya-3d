"""Publish the twelve abdominal muscles (ABD-MUSCLES) into the trunk section and generate their cards.

Geometry: native BodyParts3D 3.0 STL of each side -> exact weld -> Blender collapse decimation to the
default muscle budget of build_glb.py -> abdomen_muscles.published_mesh -> meshopt (lossless, no
quantisation). Admission: every muscle must pass verify/verify_abdomen_muscles.py (v3) in the same run.
The thorax GLB is not touched: the muscles load as supplemental models of the trunk section.
Usage: python scripts/publish_abdomen_muscles.py RUN
"""
import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
import numpy as np
import trimesh
from geometry_export_guard import stable_vertex_normals
from abdomen_muscles import EVIDENCE, GROUPS, GROUP_NOTE, MUSCLE_TEMPLATES, MUSCLES, published_mesh

ROOT = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]).resolve()
BASE = 'models/bodyparts3d-3.0/abdomen-muscles'
RAW = ROOT / 'build_abdomen/raw'
OUT = ROOT / 'site' / BASE
REPORT = 'research/abdomen-muscles-2026-10-26.md'
MIRROR_VIEW = {'lat': 'med', 'antlat': 'antmed', 'postlat': 'medpost'}
NOTICE = ('Учебная 3D-модель BodyParts3D. Граница мышечной и апоневротической частей, площади прикреплений, '
          'направление волокон и влагалище прямой мышцы не подтверждены.')
read = lambda name: json.loads((run / name).read_text(encoding='utf8'))
sources = {r['fma']: r for r in read('sources.json')['rows']}
decimated = {r['fma']: r for r in read('blender-decimation.json')['rows']}
review = read('abdomen-topography-v3.json')
reviewed = {r['id']: r for r in review['muscles']}
assert review['passed'] == review['total'] == len(MUSCLES), 'Every muscle must pass the topography review'
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)


def write(path, data):
    if path.exists():
        assert path.read_bytes() == data, f'Refusing to overwrite {path}'
    else:
        with path.open('xb') as f:
            f.write(data)


files, cards = [], {}
for key, parts in MUSCLES.items():
    (fma, _), = parts
    base, side = key.rsplit('_', 1)
    source = sources[fma]
    cached = ROOT / 'research/cache/abdomen-muscles' / (fma + '.stl')
    assert hashlib.sha256(cached.read_bytes()).hexdigest() == source['sha256'], fma
    data = np.load(ROOT / decimated[fma]['output'])
    mesh, flaps = published_mesh(data['vertices'], data['faces'])
    assert len(mesh.faces) == reviewed[key]['triangles'] and flaps == reviewed[key]['removedDecimationFlapTriangles'], key
    mesh.vertex_normals = stable_vertex_normals(mesh.vertices, mesh.faces)
    name = f'm|{key}|'
    scene = trimesh.Scene()
    scene.add_geometry(mesh, node_name=name, geom_name=name)
    raw = RAW / (key + '.glb')
    write(raw, scene.export(file_type='glb', include_normals=True))
    packed = OUT / (key + '.glb')
    if not packed.exists():
        subprocess.run(['node', str(ROOT / 'tools/package-geometry-safe.mjs'), str(raw), str(packed)], cwd=ROOT, check=True,
                       stdout=subprocess.DEVNULL)
    report = json.loads(Path(str(packed) + '.validation.json').read_text(encoding='utf8'))
    assert not report['errors'] and sum(m['faces'] for m in report['output']['meshes']) == len(mesh.faces), key
    entries = reviewed[key]['boneDepth']
    files.append(dict(id=key, fma=fma, sourceName=source['name'], sourceSHA256=source['sha256'], sourceTriangles=source['triangles'],
                      triangles=len(mesh.faces), removedDecimationFlapTriangles=flaps, file=f'{BASE}/{key}.glb',
                      sha256=hashlib.sha256(packed.read_bytes()).hexdigest(), bytes=packed.stat().st_size,
                      rawSHA256=hashlib.sha256(raw.read_bytes()).hexdigest(),
                      inheritedBoneEntries={b: dict(maxDepthMM=v['maxDepthMM'], sourceMaxDepthMM=v['sourceMaxDepthMM'],
                                                    verticesDeeperThan2mm=v['verticesDeeperThan2mm']) for b, v in entries.items()}))
    card = deepcopy(MUSCLE_TEMPLATES[base])
    card['ru'] += ' · ' + ('справа' if side == 'right' else 'слева')
    if side == 'left':
        card['v'] = MIRROR_VIEW.get(card['v'], card['v'])
    card.update(side=side, modelStatus='educational_limited', modelNotice=NOTICE, modelRegionLabel='Мышцы живота',
                modelFile=f'{BASE}/{key}.glb', modelLicense=f'{BASE}/LICENSE-MODELS.txt', modelSource=fma,
                modelReview=dict(educationalAcceptance=True, fullAnatomicalAcceptance=False, report=REPORT,
                                 topography=(run / 'abdomen-topography-v3.json').relative_to(ROOT).as_posix()),
                relatedMuscles=[base + '_' + ('left' if side == 'right' else 'right')])
    cards[key] = card

licence = """BodyParts3D, Copyright© The Database Center for Life Science licensed by CC Attribution-Share Alike 2.1 Japan.
Title/release: BodyParts3D 3.0 (DBCLS), STL files from https://github.com/Kevin-Mattheus-Moerman/BodyParts3D at commit f0eeb6e843380cfe6b83797cf8c3e1af74de5e61.
Licence: https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en
Changes: exact vertex weld; Blender 5.2 collapse decimation to the default muscle face budget of the atlas (min(max(0.13 n, min(n, 1500)), 14000));
removal of isolated zero-volume two-triangle flaps created by decimation and of unused vertices; [bp.x,bp.z,-bp.y]/1000 (mm to metres, Z-up to Y-up);
smooth normals; gltfpack meshopt compression without quantisation. No reflection, fitting or deformation: each side is its own source file.
These derivative geometry files remain CC BY-SA 2.1 Japan; commercial use is permitted under its terms.
Preserve attribution, licence and change notices; distribute adaptations under the same licence. No endorsement by DBCLS is implied.
Educational visualisation only; attachment areas, aponeurotic boundaries, fibre directions and clinical accuracy are unaccepted.
Учебные 3D-модели мышц живота. Точные площади прикреплений и граница мышечной и апоневротической частей не подтверждены.
"""
licence += '\nFiles: ' + '; '.join(f'{f["id"]}.glb ({f["fma"]})' for f in files) + '\n'
write(OUT / 'LICENSE-MODELS.txt', licence.encode('utf8'))
passport = dict(release='BodyParts3D 3.0 / STL mirror f0eeb6e8', author='The Database Center for Life Science (DBCLS)',
                license='CC BY-SA 2.1 Japan', derivativeLicense='CC BY-SA 2.1 Japan', evidence=run.relative_to(ROOT).as_posix(),
                review=dict(file='abdomen-topography-v3.json', passed=review['passed'], total=review['total'], rule=review['rule'],
                            limitation=review['limitation'], layers=review['layers']),
                files=files, productionInstalled=True, educationalAcceptance=True, fullAnatomicalAcceptance=False, report=REPORT)
write(OUT / 'provenance.json', (json.dumps(passport, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
fixture = json.loads((ROOT / 'verify/ifaa-abdomen-muscles.json').read_text(encoding='utf8'))
evidence = dict(version=1, checked='2026-10-26', templates=len(MUSCLE_TEMPLATES), instances=len(cards), evidence=EVIDENCE,
                groupNote=GROUP_NOTE, nomenclature=dict(fixture='verify/ifaa-abdomen-muscles.json', page=fixture['pages'][0]),
                independentAnatomistAcceptance=False, completeGeometryClaim=False,
                scope='Мышцы живота по TA98 A04.5.01: шесть парных мышц; мышца, поднимающая яичко, — образование в карточке без модели. '
                      'Сосудистые поля перечисляют проверенные основные источники, а не полный сосудистый атлас.')
(ROOT / 'research/abdomen-muscle-evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
text = ('/* Generated by scripts/publish_abdomen_muscles.py; edit scripts/abdomen_muscles.py. */\n(function(A){\n'
        'const cards=' + json.dumps(cards, ensure_ascii=False, indent=1) + ';\n'
        'for(const id of Object.keys(cards)){if(A.muscles[id])throw new Error("Duplicate muscle ID: "+id);}\n'
        'A.groups.push(...' + json.dumps(GROUPS, ensure_ascii=False) + ');\n'
        'Object.assign(A.muscles,cards);\nA.supplementalMuscles=A.supplementalMuscles||{};\n'
        'A.supplementalMuscles.trunk=[...(A.supplementalMuscles.trunk||[]),...' + json.dumps(list(cards)) + '];\n'
        '})(window.ATLAS);\n')
(ROOT / 'site/data-abdomen.js').write_text(text, encoding='utf8')
print(json.dumps(dict(published=len(files), triangles=sum(f['triangles'] for f in files),
                      megabytes=round(sum(f['bytes'] for f in files) / 1e6, 2))))
