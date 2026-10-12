"""Package a separately licensed, unregistered Z-Anatomy comparison scene.

Input comes from inspect_z_detail.py. This script changes only coordinate axes
and format. It does not carve holes, infer surfaces, or transfer atlas markers.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import trimesh
from head_cranial_evidence import DESCRIPTIONS, GRAY
from head_terms import T, BONES

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/cache/z-detail'
OUT = ROOT / 'build_head/detail_z'
OUT.mkdir(parents=True, exist_ok=True)
report = json.loads((SOURCE / 'meshes.json').read_text(encoding='utf-8'))
scene = trimesh.Scene()
for row in report['meshes']:
    data = json.loads((SOURCE / row['file']).read_text(encoding='utf-8'))
    mesh = trimesh.Trimesh(np.array(data['vertices']), np.array(data['faces']), process=False)
    _ = mesh.vertex_normals
    mesh.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
        name='Bone' if row['kind'] == 'bone' else 'Air cavity volume',
        baseColorFactor=[226, 212, 179, 255] if row['kind']=='bone' else [50, 159, 197, 255],
        metallicFactor=0, roughnessFactor=0.75, doubleSided=True))
    row['bounds'] = mesh.bounds.tolist()
    row['watertight'] = bool(mesh.is_watertight)
    if mesh.is_watertight and mesh.volume <= 0:
        raise ValueError(f"Closed source mesh has inward winding: {row['id']}")
    row['components'] = int(len(mesh.split(only_watertight=False, repair=False)))
    name = ('b|' if row['kind'] == 'bone' else 'o|') + row['id']
    scene.add_geometry(mesh, node_name=name, geom_name=name)
scene.metadata.update(license='CC BY-SA 4.0', source=report['source'],
    attribution='Z-Anatomy, Gauthier Kervyn et al.; BodyParts3D, The Database Center for Life Science',
    modifications='Skull objects extracted; author modifiers evaluated; reflected world transforms compensated in winding; axis conversion; GLB conversion.',
    frame='Independent Z-Anatomy source frame, not registered to the main atlas.')
destination = OUT / 'skull-z-detail.glb'
destination.write_bytes(scene.export(file_type='glb'))
report['output'] = {'file': destination.name, 'bytes': destination.stat().st_size,
                    'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()}
(OUT / 'provenance.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report['output']))

# Keep the independent comparison asset separate from the main BodyParts3D GLB.
site = ROOT / 'site'
(site / 'skull-z-detail.glb').write_bytes(destination.read_bytes())
cavity_codes = {'frontal_sinus': ('frontal', 'A02.1.03.029'),
                'sphenoidal_sinus': ('sphenoid', 'A02.1.05.016')}
for group, code in [('anterior', 'A02.1.07.008'), ('middle', 'A02.1.07.009'),
                    ('posterior', 'A02.1.07.010')]:
    for side in ('left', 'right'):
        cavity_codes[f'ethmoid_cells_{group}_{side}'] = ('ethmoid', code)
cavities = []
for row in report['meshes']:
    if row['kind'] != 'cavity':
        continue
    key = row['id']
    bone, code = cavity_codes[key]
    lat, ru, _ = T[code]
    side = 'left' if key.endswith('_left') else 'right' if key.endswith('_right') else 'both'
    side_ru = {'left': ' — слева', 'right': ' — справа', 'both': ''}[side]
    fact = DESCRIPTIONS[code]
    refs = fact['refs']
    if key == 'sphenoidal_sinus':
        # Public-domain Gray chapter directly states the cavity is in the body.
        refs = [fact['refs'][0], {**GRAY['sphenoid'],
                 'locator': 'Body: sphenoidal sinuses within the body; printed pp.147–149; PDF pp.102–104.'}]
    cavities.append({'id': key, 'node': 'o|' + key, 'bone': bone, 'c': code,
        'ru': ru + side_ru, 'lat': lat, 'side': side, 'x': fact['x'],
        'refs': refs, 'bounds': row['bounds'],
        'modelNote': 'Цветная форма обозначает объём воздухоносной полости в учебной модели Z-Anatomy. Это не отдельная кость и не ткань, заполняющая пазуху. Мелкие сообщения и все индивидуальные варианты не воспроизведены.'})
metadata = {
    'title': 'Кости и околоносовые пазухи · Z-Anatomy',
    'file': 'skull-z-detail.glb',
    'description': 'Отдельная учебная модель: 22 кости и 8 объектов воздухоносных полостей.',
    'modelNote': 'Эта модель показывает дополнительную геометрию и объёмы пазух. Она не заменяет проверку всех 521 ориентиров и не содержит полного набора мелких каналов.',
    'source': report['source'],
    'license': {'name': 'CC BY-SA 4.0', 'url': 'https://creativecommons.org/licenses/by-sa/4.0/',
        'attributions': [
            {'title': 'Z-Anatomy — Gauthier Kervyn и соавторы', 'url': report['source']},
            {'title': 'BodyParts3D — The Database Center for Life Science; CC BY-SA 2.1 Japan', 'url': 'https://dbarchive.biosciencedbc.jp/en/bodyparts3d/'},
            {'title': 'University of Dundee, CAHID — Sophia Lappe, Cranial Nerves and Foramina; CC BY 4.0 (источник, указанный Z-Anatomy)', 'url': 'https://sketchfab.com/3d-models/cranial-nerves-and-foramina-a9358ee7a6dd4ea18a3622114405a4c7'}],
        'sourceLicense': 'https://github.com/Z-Anatomy/Models-of-human-anatomy/blob/master/License.txt',
        'notice': 'Из исходного проекта извлечены только перечисленные 22 кости и 8 объектов пазух. Модели внутреннего уха и почки с ограничением NC не включены. Производная геометрия этого GLB распространяется по CC BY-SA 4.0.',
        'changes': 'Извлечение объектов черепа; вычисление существующих авторских модификаторов решётчатой кости и ячеек; компенсация отражённых преобразований в порядке вершин треугольников; смена осей; конвертация в GLB. Новые отверстия не создавались.'},
    'coordinateFrame': {'units': 'metres', 'x': 'left', 'y': 'superior', 'z': 'anterior',
        'registeredToMainAtlas': False, 'transform': report['coordinate_transform']},
    'bones': [{'id': r['id'], 'node': 'b|' + r['id'], 'bounds': r['bounds']} for r in report['meshes'] if r['kind'] == 'bone'],
    'cavities': cavities,
    'limitations': [
        'Пазухи представлены авторскими учебными поверхностями и объёмами, а не новой сегментацией КТ.',
        'У решётчатой кости применены шесть исходных операций вычитания ячеек. В сетке остаются мелкие изолированные фрагменты и незамкнутые участки; они не обозначаются как самостоятельные анатомические образования.',
        'Сетки пазух содержат открытые края; показатель watertight в техническом отчёте не равнозначен наличию или отсутствию анатомического отверстия.',
        'Модель имеет собственную систему координат. Маркеры из основной модели BodyParts3D на неё не переносятся.',
        'Полнота мелких отверстий, каналов, слуховых косточек и вариантов строения не заявляется.'],
    'geometry': report['output'],
    'provenance': {'archive_sha256': 'e029688545627bd0214b269e1063143abb580aad72b2c2445d6d8a9a0d9da736',
        'source_blend_sha256': report['source_blend_sha256'], 'exporter': 'scripts/inspect_z_detail.py + scripts/package_z_detail.py'}
}
for bone in metadata['bones']:
    base = bone['id'].removesuffix('_right').removesuffix('_left')
    bone.update(ru=BONES[base]['ru'], lat=BONES[base]['lat'], c=BONES[base]['code'])
    if bone['id'].endswith(('_right', '_left')):
        bone['ru'] += ' · ' + ('правая' if bone['id'].endswith('_right') else 'левая')
metadata['markers'] = json.loads((site.parent / 'research/face-completion-z-markers.json').read_text(encoding='utf-8'))
for marker in metadata['markers']:
    assert marker['b'] in {b['id'] for b in metadata['bones']}
    assert len(marker['refs']) >= 2 and marker['evidence'].get('method')
(site / 'skull-z-detail.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
