"""Publish the admitted left limb muscles (CAT-MUSCLE-BILATERAL) and generate their cards.

Geometry: native left BodyParts3D 3.0 STL -> exact weld -> Blender collapse decimation to the face
budget of the accepted right part -> [bp.x,bp.z,-bp.y]/1000 -> meshopt (lossless, no quantisation).
Cards: the reviewed paired right card text with the left side, model limits and no pins.
Usage: python scripts/publish_left_limb_muscles.py RUN
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
import numpy as np
import trimesh
from geometry_export_guard import stable_vertex_normals
from left_limb_muscles import table

ROOT = Path(__file__).resolve().parents[1]
run = Path(sys.argv[1]).resolve()
BASE = 'models/bodyparts3d-3.0/left-limb-muscles'
RAW = ROOT / 'build_stage7/left_limb_muscles_v1/raw'
OUT = ROOT / 'site' / BASE
R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)
MIRROR_VIEW = {'lat': 'med', 'med': 'lat', 'antlat': 'antmed', 'antmed': 'antlat', 'postlat': 'medpost', 'medpost': 'postlat'}
NOTICE = ('Учебная 3D-модель левой мышцы BodyParts3D. Точные границы, площади прикреплений, '
          'направление волокон и контакты с соседними структурами не подтверждены.')
REGION = {'arm': 'Левые мышцы верхней конечности (BodyParts3D)', 'leg': 'Левые мышцы таза и нижней конечности (BodyParts3D)'}
read = lambda name: json.loads((run / name).read_text(encoding='utf8'))
decision, targets = read('admission.json'), read('decimation-targets.json')
decimated = {r['leftFMA']: r for r in read('blender-decimation.json')['rows']}
sources = {r['fma']: r for r in read('left-sources.json')['rows']}
review = {r['left']: r for r in read('left-muscle-review-v2.json')['muscles']}
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)


def drop_isolated_pairs(faces):
    """Remove only zero-volume two-triangle flaps left by collapse decimation.

    A flap is a pair of triangles over the same three vertices (opposite winding) whose vertices
    belong to no other face; it has no surface area outside itself and undefined vertex normals.
    """
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


files, cards = [], {}
right_cards = json.loads(subprocess.check_output(['node', str(ROOT / 'tools/dump-atlas-cards.mjs'), 'site/data.js', 'site/data-leg.js'],
                                                 cwd=ROOT, encoding='utf8'))['muscles']
for muscle in table():
    left = muscle['left']
    if muscle['crossRegion'] or left not in decision['admitted']:
        continue
    rows = [t for t in targets if t['left'] == left]
    scene, parts = trimesh.Scene(), []
    for row in rows:
        source = sources[row['leftFMA']]
        cached = ROOT / 'research/cache/left-limb-muscles' / (row['leftFMA'] + '.stl')
        assert hashlib.sha256(cached.read_bytes()).hexdigest() == source['sha256'], row['leftFMA']
        data = np.load(ROOT / decimated[row['leftFMA']]['output'])
        mesh = trimesh.Trimesh(vertices=data['vertices'] @ R.T / 1000.0, faces=data['faces'], process=True)
        kept, flaps = drop_isolated_pairs(mesh.faces)
        mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=kept, process=False)
        mesh.remove_unreferenced_vertices()
        mesh.vertex_normals = stable_vertex_normals(mesh.vertices, mesh.faces)
        name = f"m|{left}|{row['part'] or ''}"
        scene.add_geometry(mesh, node_name=name, geom_name=name)
        parts.append(dict(part=row['part'], node=name, leftFMA=row['leftFMA'], leftName=source['name'],
                          sourceSHA256=source['sha256'], sourceTriangles=source['triangles'], triangles=len(mesh.faces),
                          removedDecimationFlapTriangles=flaps,
                          rightFMA=row['rightFMA'], rightTriangles=row['rightTriangles']))
    raw = RAW / (left + '.glb')
    write(raw, scene.export(file_type='glb', include_normals=True))
    packed = OUT / (left + '.glb')
    if not packed.exists():
        subprocess.run(['node', str(ROOT / 'tools/package-geometry-safe.mjs'), str(raw), str(packed)], cwd=ROOT, check=True,
                       stdout=subprocess.DEVNULL)
    report = json.loads(Path(str(packed) + '.validation.json').read_text(encoding='utf8'))
    assert not report['errors'] and sum(m['faces'] for m in report['output']['meshes']) == sum(p['triangles'] for p in parts)
    files.append(dict(id=left, right=muscle['right'], region=muscle['region'], file=f'{BASE}/{left}.glb',
                      sha256=hashlib.sha256(packed.read_bytes()).hexdigest(), bytes=packed.stat().st_size,
                      rawSHA256=hashlib.sha256(raw.read_bytes()).hexdigest(), parts=parts,
                      reviewedException=decision['reviewedExceptions'].get(left)))
    right = right_cards[muscle['right']]
    card = {k: v for k, v in right.items() if k != 'noModel'}
    exception = decision['reviewedExceptions'].get(left)
    note = ' '.join(x for x in [right.get('note'),
        'Описание повторяет проверенную карточку парной правой мышцы. Ориентиры начала и прикрепления на левых костях '
        'перенесены с правой разметки той же модели и показаны как ориентировочные; точки, не прошедшие проверку формы, '
        'остаются в списке без маркера (scripts/make_left_limb_landmarks.py).',
        'Модель: исходная левая сетка BodyParts3D 3.0, упрощённая до плотности правой; соседство с костями проверено по сторонам.',
        exception] if x)
    if left == 'levator_ani_left':
        note += ' Здесь показаны левые лобково-копчиковая и подвздошно-копчиковая мышцы; лобково-прямокишечная — отдельная карточка.'
    card.update(ru=right['ru'] + ' · слева', side='left', v=MIRROR_VIEW.get(right['v'], right['v']), note=note,
                noModel=False, modelStatus='educational_limited', modelNotice=NOTICE, modelRegionLabel=REGION[muscle['region']],
                modelFile=f'{BASE}/{left}.glb', modelLicense=f'{BASE}/LICENSE-MODELS.txt',
                modelSource=', '.join(p['leftFMA'] for p in parts),
                modelReview=dict(educationalAcceptance=True, fullAnatomicalAcceptance=False, report=decision['report'],
                                 pairedCard=muscle['right'], textCopiedFromPairedCard=True,
                                 leftPins='approximate_contralateral_transfer'),
                relatedMuscles=[muscle['right']] + (['puborectalis_left'] if left == 'levator_ani_left' else []))
    if right.get('parts'):
        assert sorted(right['parts']) == sorted(p['part'] for p in parts), left
    cards[left] = card

licence = """BodyParts3D, Copyright© The Database Center for Life Science licensed by CC Attribution-Share Alike 2.1 Japan.
Title/release: BodyParts3D 3.0 (DBCLS), STL files from https://github.com/Kevin-Mattheus-Moerman/BodyParts3D at commit f0eeb6e843380cfe6b83797cf8c3e1af74de5e61.
Licence: https://creativecommons.org/licenses/by-sa/2.1/jp/deed.en
Changes: exact vertex weld; Blender 5.2 collapse decimation to the face count of the accepted right muscle part; removal of isolated zero-volume two-triangle flaps created by decimation;
[bp.x,bp.z,-bp.y]/1000 (mm to metres, Z-up to Y-up); smooth normals; gltfpack meshopt compression without quantisation.
No reflection, fitting or deformation. These derivative geometry files remain CC BY-SA 2.1 Japan; commercial use is permitted under its terms.
Preserve attribution, licence and change notices; distribute adaptations under the same licence. No endorsement by DBCLS is implied.
Educational visualisation only; attachment areas, part boundaries, fibre directions and clinical accuracy are unaccepted.
Учебные 3D-модели левых мышц. Точные площади прикреплений и границы частей не подтверждены.
"""
licence += '\nFiles: ' + '; '.join(f["id"] + '.glb (' + ', '.join(p['leftFMA'] for p in f['parts']) + ')' for f in files) + '\n'
write(OUT / 'LICENSE-MODELS.txt', licence.encode('utf8'))
passport = dict(release='BodyParts3D 3.0 / STL mirror f0eeb6e8', author='The Database Center for Life Science (DBCLS)',
                license='CC BY-SA 2.1 Japan', derivativeLicense='CC BY-SA 2.1 Japan', evidence=run.relative_to(ROOT).as_posix(),
                files=files, productionInstalled=True, educationalAcceptance=True, fullAnatomicalAcceptance=False,
                report=decision['report'], admission=decision)
write(OUT / 'provenance.json', (json.dumps(passport, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
ids = {sec: [f['id'] for f in files if f['region'] == sec] for sec in ('arm', 'leg')}
text = ('/* Generated by scripts/publish_left_limb_muscles.py; edit scripts/left_limb_muscles.py. */\n(function(A){\n'
        'const cards=' + json.dumps(cards, ensure_ascii=False, indent=1) + ';\n'
        'for(const id of Object.keys(cards)){if(A.muscles[id])throw new Error("Duplicate muscle ID: "+id);}\n'
        'Object.assign(A.muscles,cards);\nA.supplementalMuscles=A.supplementalMuscles||{};\n'
        'for(const [sec,ids] of Object.entries(' + json.dumps(ids) + '))A.supplementalMuscles[sec]=[...(A.supplementalMuscles[sec]||[]),...ids];\n'
        '})(window.ATLAS);\n')
(ROOT / 'site/data-left-limb-muscles.js').write_text(text, encoding='utf8')
print(json.dumps(dict(published=len(files), arm=len(ids['arm']), leg=len(ids['leg']),
                      triangles=sum(p['triangles'] for f in files for p in f['parts']),
                      megabytes=round(sum(f['bytes'] for f in files) / 1e6, 2))))
