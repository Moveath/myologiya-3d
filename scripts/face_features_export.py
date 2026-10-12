"""Export independently reviewed facial landmarks, never synthesize missing ones.

The six main-atlas proposals retain BodyParts3D coordinates. Four independent
Z-Anatomy picks retain Z coordinates; they are not a second anatomical specimen
and are not registrations. Screenshots and exact screen selections are retained.
"""
from pathlib import Path
import json
import hashlib
import shutil
from collections import Counter
import numpy as np
import trimesh
from head_face_evidence import DESCRIPTIONS
from ta98 import T
from manifest_head import BONES

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build_head/face_features'
JOBS = OUT / 'jobs'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


PREMAXILLA_REFS = [
    {'title': 'Trevizan и соавт., 2018 — исследование 1138 черепов',
     'url': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC6340201/',
     'locator': 'Introduction: premaxilla bears maxillary incisors; body continuous with maxilla. Discussion: fusion can remove the facial suture.'},
    {'title': 'Hovorakova и соавт., 2018 — Early development of the human dentition revisited',
     'url': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC6036925/',
     'locator': 'The dual origin of the upper lateral incisor: adult premaxilla carries two central and two lateral incisors.'},
    DESCRIPTIONS['A02.1.12.031']['refs'][1],
]
NOTES = {
    'A02.1.12.031': 'Отмечена видимая передняя часть верхней челюсти у альвеол резцов. У взрослого она может быть сращена с остальной костью; отсутствие отдельной линии шва не означает отсутствия резцовой части. Маркер не задаёт все её границы и не подтверждает сохранённый резцовый шов.',
    'A02.1.12.026': 'Отмечен участок вогнутого медиального края глазничной поверхности непосредственно позади лобного отростка. Он сопоставлен со слёзной вырезкой на подписанном медиальном виде и её описанием в независимом учебнике. Маркер не изображает всю вырезку и не подтверждает просвет носослёзного канала.',
    'A02.1.12.027': 'Отмечен видимый поперечный выступ в верхнем отделе носовой поверхности лобного отростка. Обе стороны осмотрены независимо в медиальном и косых ракурсах. Отмечен участок гребня; его точный контур и место соединения со средней раковиной отдельно не сегментированы.',
}


def refs(code):
    return PREMAXILLA_REFS if code == 'A02.1.12.031' else DESCRIPTIONS[code]['refs']


def pick_data(prefix, spec):
    bone, code, view, u, v = spec
    stem = prefix + bone + '_' + code[-3:]
    row = read(OUT / 'picks.json')[stem]
    assert row['bone'] == bone and row['code'] == code
    assert row['uv'] == [u, v]
    assert len(row['p']) == len(row['n']) == 3
    assert .8 < sum(t*t for t in row['n']) < 1.2
    image = OUT / (stem + '.png')
    if (JOBS / (stem + '.png')).exists():
        shutil.copyfile(JOBS / (stem + '.png'), image)
    assert image.exists(), image
    return row, image


def evidence(row, image, source):
    is_bp = source == 'BodyParts3D'
    return {
        'method': 'manual-anatomical-image-review-then-orthographic-raycast',
        'view': row['view'], 'uv': row['uv'],
        'coordinateFrame': 'BodyParts3D atlas metres' if is_bp else 'Z-Anatomy [x,z,-y], metres; not registered to BodyParts3D',
        'source': 'build_head/face_features/' + ('bp-candidate-specs.json' if is_bp else 'z-pick-specs.json'),
        'screenshot': str(image.relative_to(ROOT)).replace('\\', '/'),
        'screenshot_sha256': hashlib.sha256(image.read_bytes()).hexdigest(),
        'review': 'Каждая сторона и каждый источник осмотрены отдельно. Координаты получены лучом после визуального выбора образования, а не отражением другой стороны или расчётом из ограничивающего параллелепипеда.',
        'boundary_segmentation': False,
        'external_expert_review': False,
    }


bp = []
validation = []
for spec in read(OUT / 'bp-candidate-specs.json'):
    row, image = pick_data('', spec)
    bone, code = row['bone'], row['code']
    mesh = trimesh.load(ROOT / 'stl_head' / (BONES[bone][0] + '.stl'), force='mesh')
    mesh.vertices = mesh.vertices[:, [0, 2, 1]] * [.001, .001, -.001]
    # Work in millimetres: trimesh's small-triangle tolerance can misclassify
    # interior projections when metre coordinates make triangle products tiny.
    check_mesh = mesh.copy()
    check_mesh.vertices *= 1000
    _, distance, _ = trimesh.proximity.closest_point_naive(check_mesh, [np.array(row['p']) * 1000])
    distance /= 1000
    assert distance[0] < .00003, (bone, code, distance)
    bp.append({'bone': bone, 'code': code, 'p': row['p'], 'n': row['n'],
               'localization': 'surface', 'modelNote': NOTES[code],
               'refs': refs(code), 'evidence': evidence(row, image, 'BodyParts3D')})
    validation.append({'source': 'BodyParts3D', 'bone': bone, 'code': code,
                       'distance_mm': float(distance[0] * 1000),
                       'anatomical_review_is_separate_from_distance_test': True})
write(ROOT / 'pins_head/face-features-bp.json', bp)

markers = []
for spec in read(OUT / 'z-pick-specs.json'):
    row, image = pick_data('z_', spec)
    bone, code = row['bone'], row['code']
    data = read(ROOT / 'research/cache/z-detail' / (bone + '.json'))
    mesh = trimesh.Trimesh(data['vertices'], data['faces'], process=False)
    # Work in millimetres: trimesh's small-triangle tolerance can misclassify
    # interior projections when metre coordinates make triangle products tiny.
    check_mesh = mesh.copy()
    check_mesh.vertices *= 1000
    _, distance, _ = trimesh.proximity.closest_point_naive(check_mesh, [np.array(row['p']) * 1000])
    distance /= 1000
    assert distance[0] < .00003, (bone, code, distance)
    side = 'right' if bone.endswith('right') else 'left'
    latin, russian, _ = T[code]
    markers.append({'id': 'z_face_' + bone + '_' + code.replace('.', '_'),
                    'b': bone, 'c': code, 'ru': russian, 'lat': latin.split(';')[0],
                    'p': row['p'], 'n': row['n'], 'loc': 'surface', 'scope': 'surface', 'mode': 'z',
                    'view': {'d': [0, 0, 1] if row['view'] == 'ant' else [1 if side == 'right' else -1, 0, 0],
                             'up': [0, 1, 0], 'distance': .08},
                    'x': DESCRIPTIONS[code]['x'], 'refs': refs(code),
                    'modelNote': NOTES[code] + ' Это собственный маркер отдельной модели Z-Anatomy; её координаты не перенесены на BodyParts3D.',
                    'source': 'Z-Anatomy', 'side': side,
                    'geometryRefs': [{'title': 'Z-Anatomy — исходная модель',
                                      'url': 'https://github.com/Z-Anatomy/Models-of-human-anatomy',
                                      'locator': 'Startup.blend: Maxilla.r / Maxilla.l; extraction provenance build_head/detail_z/provenance.json'}],
                    'evidence': evidence(row, image, 'Z-Anatomy')})
    validation.append({'source': 'Z-Anatomy', 'bone': bone, 'code': code,
                       'distance_mm': float(distance[0] * 1000),
                       'anatomical_review_is_separate_from_distance_test': True})
write(ROOT / 'pins_head/face-native-features.json', {
    'source': 'Z-Anatomy', 'date': '2026-10-13',
    'license': {'name': 'CC BY-SA 4.0', 'url': 'https://creativecommons.org/licenses/by-sa/4.0/'},
    'coordinateFrame': 'Z-Anatomy [x,z,-y], metres; not registered to BodyParts3D',
    'note': 'Четыре маркера добавлены по отдельным осмотрам. Модель Z-Anatomy производна от BodyParts3D и не считается независимым анатомическим подтверждением исходной сетки.',
    'markers': markers})
write(OUT / 'geometry-validation.json', validation)

# The prior assessment has one record per bone/code and provides the frozen
# pre-change scope. Preserve genuine unresolved findings rather than infer
# completion from the availability of a named region or a source quotation.
old = read(ROOT / 'research/face-completion-review.json')['records']
baseline = [r for r in old if r['current_localization'] == 'projection'
            and r['review_result'] != 'surface-proposal']
assert len(baseline) == 57, len(baseline)
verified = {(p['bone'], p['code']): p for p in bp}
records = []
for r in baseline:
    key = r['bone'], r['code']
    current = verified.get(key)
    counterpart = r['code'] == 'A02.1.15.031'
    records.append({
        'bone': r['bone'], 'code': r['code'], 'ru': r['ru'], 'lat': r['lat'],
        'baseline_localization': 'projection',
        'result': 'verified-primary-surface' if current else 'verified-separate-surface-only' if counterpart else 'model-not-resolved',
        'current_primary_localization_proposal': 'surface' if current else 'projection',
        'anatomical_sources': refs(r['code']) if current else r['refs'],
        'geometry_observation': current['modelNote'] if current else r['model_observation'],
        'evidence': current['evidence'] if current else {
            'prior_review_image': r['review_image'],
            'prior_review': 'research/face-completion-review.json',
            'prior_review_scope': 'Предыдущий раздельный осмотр этой кости в BodyParts3D и Z-Anatomy; вывод сохранён, а не выдан за новую независимую проверку.',
            'current_pass': (
                'Повторный осмотр обеих верхних челюстей в передних, медиальных, нижних и косых видах; конкретные подтверждённые участки вынесены в отдельные записи.'
                if r['bone'].startswith('maxilla') else
                'Повторный осмотр обеих скуловых костей в медиальном, латеральном и заднем ракурсах; отдельный краевой бугорок не отделён уверенно от общей формы края.'
                if r['bone'].startswith('zygomatic') else
                'Повторный осмотр медиальных поверхностей обеих нёбных костей; уверенная отдельная верхняя линия гребня или просветы малых каналов не получены.'
                if r['bone'].startswith('palatine') else
                'Сохранён предыдущий индивидуальный обзор; новых собственных координат в этом проходе не подтверждено.'),
            'additional_scan_review': (
                'Halle не содержит нижней челюсти; этот источник не проверяет данный термин.' if r['bone'] == 'mandible' else
                'Halle: нёбная область осмотрена при исходном шаге 0,125 мм без упрощения; снимки build_head/face_features/roi_{palate,incisive,grooves}.png. Разрывы и пористость не позволяют надёжно отделить мелкие именованные каналы/борозды от ограничений маски.'
                if r['bone'].startswith(('maxilla', 'palatine')) else
                'В новом ROI Halle эта кость не осмотрена полностью по данному образованию; подтверждения или вывода об отсутствии по этому скану нет.'),
        },
        'next_requirement': None if current else 'Для полной формы требуется исходная геометрия с различимыми границами именно этого образования; название или общий анатомический источник не заменяют эту проверку.',
    })
write(ROOT / 'research/face-feature-review.json', {
    'date': '2026-10-13', 'scope': '57 ранее не подтверждённых записей лицевого черепа; 32 разных термина TA98.',
    'counts': dict(Counter(r['result'] for r in records)),
    'primary_surface_proposals': 'pins_head/face-features-bp.json',
    'source_native_markers': 'pins_head/face-native-features.json',
    'records': records,
    'methods': [
        'Повторный осмотр медиальных, передних и нижних поверхностей обеих верхних челюстей; дополнительные косые виды справа и слева.',
        'Сравнение с подписанным медиальным изображением Anatomy Standard, независимым учебником Buchanan и университетским атласом Палацкого.',
        'Отдельная проверка значения pars incisiva по двум независимым исследованиям: сращение у взрослого не отменяет часть, несущую альвеолы резцов.',
        'Повторный осмотр скуловых костей с медиальной и латеральной сторон; общий край не объявлен отдельным краевым бугорком без однозначной границы.',
        'Осмотр опубликованной сетки Halle в переднем, нижнем и двух увеличенных видах. Случайные мелкие разрывы и пористость не приняты за именованные отверстия.',
        'Дополнительно построен лицевой ROI из той же исходной маски Halle при шаге 0,125 мм без разрежения, сглаживания и децимации: 14 147 957 треугольников. Осмотрены нижний, передний, верхний виды, область резцового отверстия и латеральная часть нёба. Новые уверенные лицевые ориентиры не получены.',
    ],
    'additional_model_observations': {
        'Halle': 'В опубликованной поверхности и в новом ROI из исходной бинарной маски при 0,125 мм заметны открытые, пористые участки переднего нёба и альвеол. Увеличение детализации сохраняет эти разрывы: в резцовой области видна неровная ямка, но отдельные просветы и непрерывные стенки канала этим осмотром не подтверждены; на латеральном нёбе общий изгиб поверхности не выдан за сосудистую борозду. Это ограничение данного осмотра, а не доказательство отсутствия образования в исходном скане. Полная повторная сегментация исходных томографических интенсивностей и экспертная идентификация каналов не выполнялись. Нижней челюсти в препарате нет. Новая сетка используется только локально и не публикуется как завершённая модель.',
        'Z-Anatomy': 'Большинство лицевых поверхностей производны от BodyParts3D и упрощены. Четыре новые координаты записаны независимо; они не увеличивают число разных образований, уже подтверждённых этой же проверкой на BP.',
        'variants': 'Torus mandibularis и парный резцовый шов на BodyParts3D/Z не подтверждены этой проверкой. Фотографии иных препаратов не меняют статус этих сеток.',
    },
    'complete_face_geometry_claim': False,
})
print(json.dumps({'primary_proposals': len(bp), 'new_Z_markers': len(markers),
                  'reviewed_records': len(records), 'max_surface_distance_mm': max(v['distance_mm'] for v in validation)}))
