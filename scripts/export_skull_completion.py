"""Summarize source-confirmed geometry without equating pin coverage with completeness."""
from collections import Counter
from pathlib import Path
import json
import re
from head_localization import positions
from manifest_head import MUSCLES
from new_muscle_source_audit import inventory

ROOT = Path(__file__).resolve().parents[1]
rows = positions()
counts = Counter(p['localization'] for p in rows.values())
z = json.loads((ROOT/'site/skull-z-detail.json').read_text(encoding='utf-8'))
ear = json.loads((ROOT/'site/skull-openear.json').read_text(encoding='utf-8'))
ear_landmarks = json.loads((ROOT/'site/skull-openear-landmarks.json').read_text(encoding='utf-8'))
missing_muscles, missing_parts = inventory()
region_file = ROOT/'site/skull-regions.js'
study_regions = [{'id': key, 'ru': title} for key, title in re.findall(
    r"^  \{id:'([^']+)',ru:'([^']+)'", region_file.read_text(encoding='utf-8'), re.MULTILINE)]
if len(study_regions) != 8 or len({r['id'] for r in study_regions}) != len(study_regions):
    raise ValueError('Expected eight distinct study groups in site/skull-regions.js')
variant_file = ROOT/'site/skull-study-variants.json'
variants = json.loads(variant_file.read_text(encoding='utf-8'))
variant_keys = {(p['b'], p['c']) for p in variants}
expected_variant_keys = {key for key, row in rows.items() if row['localization'] == 'variant'}
if len(variants) != len(variant_keys) or variant_keys != expected_variant_keys:
    raise ValueError('Study variant catalogue differs from the reviewed main-atlas variant locations')
remaining = {}
for (bone, code), row in rows.items():
    if row['localization'] != 'surface':
        remaining.setdefault(bone, []).append({'code': code, 'localization': row['localization'],
                                               'modelNote': row['modelNote']})
report = {
    'date': '2026-10-13',
    'policy': 'Только геометрия, подтверждённая опубликованными сканами или исходными моделями; без вымышленных реконструкций.',
    'complete_skull_geometry_claim': False,
    'main_atlas': {'markers': len(rows), 'localization_counts': dict(counts),
                   'newly_reviewed_surface_anchors': 6,
                   'note': 'Поверхностный маркер отмечает участок рельефа, а не доказывает полную геометрию образования.'},
    'muscle_geometry': {
        'cards': len(MUSCLES) + len(missing_muscles), 'modeled_instances': len(MUSCLES),
        'missing_whole_instances_count': len(missing_muscles),
        'missing_whole_instances': missing_muscles,
        'missing_part_instances_count': len(missing_parts),
        'missing_part_instances': missing_parts,
        'source_audit': 'research/new-muscle-source-audit.json',
        'note': 'Парные экземпляры считаются отдельно. Отсутствующие части не являются дополнительными целыми мышцами.'},
    'study_groups': {
        'page': 'site/skull-study.html', 'definitions': 'site/skull-regions.js',
        'groups': study_regions,
        'coordinate_policy': 'Учебные группы используют независимые исходные системы координат. Обязательное совмещение всех образцов с BodyParts3D не требуется; каждый ориентир подтверждается на той сетке, на которой он показан.',
        'variant_catalogue': {'file': 'site/skull-study-variants.json', 'entries': len(variants),
                             'confirmed_variant_meshes': 0,
                             'note': 'Повторно используются проверенные карточки типичных мест вариантов; отдельная геометрия вариантов не добавлена.'}},
    'separate_models': {
        'z_anatomy': {'bones': len(z['bones']), 'cavities': len(z['cavities']),
                     'independently_placed_markers': len(z['markers']),
                     'metadata': 'site/skull-z-detail.json'},
        'openear': {'structures': len(ear['structures']), 'metadata': 'site/skull-openear.json',
                    'independently_placed_markers': len(ear_landmarks['markers']),
                    'marker_localization_counts': dict(Counter(p['loc'] for p in ear_landmarks['markers'])),
                    'marker_metadata': 'site/skull-openear-landmarks.json',
                    'marker_source': 'pins_head/openear-native.json',
                    'complete_ossicle_landmark_catalogue_claim': False,
                    'registered_to_main_atlas': False},
        'halle_microct': {'metadata': 'site/skull-microct.json', 'registered_to_main_atlas': False}},
    'remaining_primary_markers': remaining,
    'other_remaining_limitations': [
        'Девять карточек мышц не имеют отдельной геометрии в проверенных совместимых наборах.',
        'Десять экземпляров частей мышц не выделены в исходных сетках: глубокая часть и ресничный пучок круговой мышцы глаза с двух сторон, две части носовой мышцы с двух сторон, две части круговой мышцы рта.',
        'Внутренние структуры OpenEar относятся к одному препарату и не подтверждают автоматически проекции на BodyParts3D.',
        'Варианты строения не обязаны присутствовать у конкретного человека. Их типичная область не заменяет обнаруженный вариант.',
        'Новые исходники BoneHub Visible Human, NIH 3D и MUG500+ исследованы отдельно; они пока не подтверждают полный перечень мелких образований или 14 вариантов и не заменили опубликованные модели.',
        'Полная геометрия всех отверстий, стенок каналов и их сообщений не подтверждена выбранными источниками.'],
    'reviews': ['research/face-completion-review.json', 'research/cranial-completion-registration.json',
                'research/temporal-completion-review.json', 'research/openear-landmark-review.json',
                'research/new-muscle-source-audit.json', 'research/new-skull-source-audit.json', 'verify/ui-head-report.json',
                'verify/ui-skull-detail-report.json', 'verify/ui-skull-study-report.json',
                'verify/ui-skull-study-navigation-report.json']}
(ROOT/'research/skull-completion-status.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Skull status:', dict(counts), '— complete geometry is not claimed')
