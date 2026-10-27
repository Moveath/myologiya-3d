"""Publish the six left connective-tissue structures (CAT-SOFT-TISSUE-BILATERAL) and generate their cards.

Geometry: native left BodyParts3D 3.0 STL -> exact weld -> Blender collapse decimation to the face
count of the accepted right node -> [bp.x,bp.z,-bp.y]/1000 -> meshopt (lossless, no quantisation).
Cards: the paired right card text with the left side and model limits; no landmarks are created.
Usage: python scripts/publish_left_soft_tissues.py RUN
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import numpy as np
import trimesh
from geometry_export_guard import stable_vertex_normals

ROOT = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]).resolve()
BASE = 'models/bodyparts3d-3.0/left-soft-tissues'
RAW = ROOT / 'build_stage7/left_soft_tissues_v1/raw'
OUT = ROOT / 'site' / BASE
R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)
MIRROR_VIEW = {'lat': 'med', 'med': 'lat'}
NOTICE = ('Учебная 3D-модель левой структуры BodyParts3D. Точные границы связки или сухожилия, '
          'места прикрепления и соотношения с соседними структурами не подтверждены.')
REGION = {'arm': 'Левые соединительнотканные структуры руки (BodyParts3D)',
          'leg': 'Левые связки и сухожилия ноги (BodyParts3D)'}
REPORT = 'research/BONES_MUSCLES_FULL_AUDIT.md'
read = lambda name: json.loads((run / name).read_text(encoding='utf8'))
targets, review = read('decimation-targets.json'), {r['left']: r for r in read('left-soft-tissue-review.json')['structures']}
decimated = {r['leftFMA']: r for r in read('blender-decimation.json')['rows']}
sources = {(r['side'], r['fma']): r for r in read('left-sources.json')['rows']}
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)


def drop_isolated_pairs(faces):
    """Remove only zero-volume two-triangle flaps left by collapse decimation (as for the left muscles)."""
    faces = np.asarray(faces)
    key = np.sort(faces, axis=1)
    _, inverse, counts = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    use = np.bincount(faces.ravel(), minlength=faces.max() + 1)
    paired = (counts[inverse.ravel()] == 2) & np.all(use[faces] == 2, axis=1)
    return faces[~paired], int(paired.sum())


def write(path, data):
    if path.exists():
        assert path.read_bytes() == data, f'Refusing to overwrite {path}'
    else:
        with path.open('xb') as f:
            f.write(data)


right_cards = json.loads(subprocess.check_output(['node', '--input-type=module', '-e',
    'import fs from "node:fs";import vm from "node:vm";const c={window:{}};c.window.window=c.window;vm.createContext(c);'
    'for(const f of ["site/data.js","site/data-leg.js"])vm.runInContext(fs.readFileSync(f,"utf8"),c);'
    'process.stdout.write(JSON.stringify(c.window.ATLAS.bones));'], cwd=ROOT, encoding='utf8'))
files, cards = [], {}
for row in targets:
    left = row['left']
    assert review[left]['passed'], left
    source = sources[('left', row['leftFMA'])]
    cached = ROOT / 'research/cache/left-soft-tissues' / (row['leftFMA'] + '.stl')
    assert hashlib.sha256(cached.read_bytes()).hexdigest() == source['sha256'], row['leftFMA']
    data = np.load(ROOT / decimated[row['leftFMA']]['output'])
    mesh = trimesh.Trimesh(vertices=data['vertices'] @ R.T / 1000.0, faces=data['faces'], process=True)
    kept, flaps = drop_isolated_pairs(mesh.faces)
    mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=kept, process=False)
    mesh.remove_unreferenced_vertices()
    mesh.vertex_normals = stable_vertex_normals(mesh.vertices, mesh.faces)
    scene = trimesh.Scene()
    scene.add_geometry(mesh, node_name='o|' + left, geom_name='o|' + left)
    raw = RAW / (left + '.glb')
    write(raw, scene.export(file_type='glb', include_normals=True))
    packed = OUT / (left + '.glb')
    if not packed.exists():
        subprocess.run(['node', str(ROOT / 'tools/package-geometry-safe.mjs'), str(raw), str(packed)], cwd=ROOT, check=True,
                       stdout=subprocess.DEVNULL)
    report = json.loads(Path(str(packed) + '.validation.json').read_text(encoding='utf8'))
    assert not report['errors'] and sum(m['faces'] for m in report['output']['meshes']) == len(mesh.faces)
    files.append(dict(id=left, right=row['right'], region=row['region'], file=f'{BASE}/{left}.glb',
                      sha256=hashlib.sha256(packed.read_bytes()).hexdigest(), bytes=packed.stat().st_size,
                      rawSHA256=hashlib.sha256(raw.read_bytes()).hexdigest(), leftFMA=row['leftFMA'], leftName=source['name'],
                      sourceSHA256=source['sha256'], sourceTriangles=source['triangles'], triangles=len(mesh.faces),
                      removedDecimationFlapTriangles=flaps, rightFMA=row['rightFMA'], rightTriangles=row['rightTriangles'],
                      review={k: review[left][k] for k in ('medianSymmetricDistanceMM', 'extentRatio', 'areaRatio', 'leftBones', 'rightBones')}))
    right = right_cards[row['right']]
    card = dict(right)
    card.update(ru=right['ru'] + ' · слева', side='left', sec=row['region'], sourceId=row['leftFMA'], noModel=False,
                note=' '.join(x for x in [right.get('note'),
                    'Описание повторяет карточку парной правой структуры. Модель: исходная левая сетка BodyParts3D 3.0, '
                    'упрощённая до плотности правой; сторона, размеры, форма относительно отражённой правой и соседство с костями своей стороны проверены. '
                    'Ориентиры на левой структуре не размечались.'] if x),
                modelStatus='educational_limited', modelNotice=NOTICE, modelRegionLabel=REGION[row['region']],
                modelFile=f'{BASE}/{left}.glb', modelLicense=f'{BASE}/LICENSE-MODELS.txt', modelSource=row['leftFMA'],
                modelReview=dict(educationalAcceptance=True, fullAnatomicalAcceptance=False, report=REPORT,
                                 pairedCard=row['right'], textCopiedFromPairedCard=True))
    if right.get('v'):
        card['v'] = MIRROR_VIEW.get(right['v'], right['v'])
    cards[left] = card

licence = """BodyParts3D, Copyright© The Database Center for Life Science licensed by CC Attribution-Share Alike 2.1 Japan.
Title/release: BodyParts3D 3.0 (DBCLS), STL files from https://github.com/Kevin-Mattheus-Moerman/BodyParts3D at commit f0eeb6e843380cfe6b83797cf8c3e1af74de5e61.
Licence: https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en
Changes: exact vertex weld; Blender 5.2 collapse decimation to the face count of the accepted right structure; removal of isolated zero-volume two-triangle flaps created by decimation;
[bp.x,bp.z,-bp.y]/1000 (mm to metres, Z-up to Y-up); smooth normals; gltfpack meshopt compression without quantisation.
No reflection, fitting or deformation. These derivative geometry files remain CC BY-SA 2.1 Japan; commercial use is permitted under its terms.
Preserve attribution, licence and change notices; distribute adaptations under the same licence. No endorsement by DBCLS is implied.
Educational visualisation only; ligament/tendon boundaries, attachment areas and clinical accuracy are unaccepted.
Учебные 3D-модели левых соединительнотканных структур. Точные границы и места прикрепления не подтверждены.
"""
licence += '\nFiles: ' + '; '.join(f'{f["id"]}.glb ({f["leftFMA"]} {f["leftName"]})' for f in files) + '\n'
write(OUT / 'LICENSE-MODELS.txt', licence.encode('utf8'))
passport = dict(release='BodyParts3D 3.0 / STL mirror f0eeb6e8', author='The Database Center for Life Science (DBCLS)',
                license='CC BY-SA 2.1 Japan', derivativeLicense='CC BY-SA 2.1 Japan', evidence=run.relative_to(ROOT).as_posix(),
                files=files, productionInstalled=True, educationalAcceptance=True, fullAnatomicalAcceptance=False, report=REPORT,
                admissionRule=read('left-soft-tissue-review.json')['rule'])
write(OUT / 'provenance.json', (json.dumps(passport, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
ids = {sec: [f['id'] for f in files if f['region'] == sec] for sec in ('arm', 'leg')}
text = ('/* Generated by scripts/publish_left_soft_tissues.py; edit scripts/left_soft_tissues.py. */\n(function(A){\n'
        'const cards=' + json.dumps(cards, ensure_ascii=False, indent=1) + ';\n'
        'for(const id of Object.keys(cards)){if(A.bones[id])throw new Error("Duplicate bone ID: "+id);}\n'
        'Object.assign(A.bones,cards);\nA.supplementalSoftTissues=A.supplementalSoftTissues||{};\n'
        'for(const [sec,ids] of Object.entries(' + json.dumps(ids) + '))A.supplementalSoftTissues[sec]=[...(A.supplementalSoftTissues[sec]||[]),...ids];\n'
        '})(window.ATLAS);\n')
(ROOT / 'site/data-left-soft-tissues.js').write_text(text, encoding='utf8')
print(json.dumps(dict(published=len(files), arm=ids['arm'], leg=ids['leg'], triangles=sum(f['triangles'] for f in files),
                      kilobytes=round(sum(f['bytes'] for f in files) / 1e3, 1))))
