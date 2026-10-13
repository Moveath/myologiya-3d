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
native = json.loads((ROOT/'site/skull-native-features.json').read_text(encoding='utf-8'))
catalogue = json.loads((ROOT/'site/skull-feature-catalogue.json').read_text(encoding='utf-8'))
extent = json.loads((ROOT/'site/skull-geometry-review.json').read_text(encoding='utf-8'))
examples = json.loads((ROOT/'site/skull-variant-examples.json').read_text(encoding='utf-8'))['examples']
channel_models = []
for mode, stem in [('channels', 'skull-temporal-channels'), ('cranial_channels', 'skull-cranial-channels')]:
    path=ROOT/'site'/f'{stem}.json'
    if not path.exists():
        continue
    model=json.loads(path.read_text(encoding='utf8'))
    slices=json.loads((ROOT/'site'/model['slicesFile']).read_text(encoding='utf8'))
    channel_models.append({'mode':mode, 'metadata':str(path.relative_to(ROOT)),
        'source':model['source'], 'license':model['license'],
        'source_ct_reslices':sum(len(s['frames']) for s in slices['series']),
        'structures':[{'id':d['id'], 'ta98':d['ta98'], 'scope':d['scope'],
                       'completeFeatureGeometry':d['completeFeatureGeometry'],
                       'continuousLumenConfirmed':d.get('continuousLumenConfirmed'), 'modelNote':d['modelNote']}
                      for d in model['structures']],
        'main_bodyparts3d_status_changed':False})
native_by_code = {}
for mode, markers in native['markers'].items():
    for marker in markers:
        native_by_code.setdefault(marker['c'], []).append({
            'mode': mode, 'id': marker['id'], 'scope': marker.get('scope', 'surface'),
            'modelNote': marker['modelNote'], 'specimen': marker['specimen']})
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
    'policy': 'Исходная геометрия сохраняется отдельно. По разрешению пользователя от 13 октября 2026 добавлены обозначенные учебные схемы по источникам; если форма не обоснована, дано явное объяснение ограничений. Схемы не меняют статусы исходных моделей.',
    'complete_skull_geometry_claim': False,
    'main_atlas': {'markers': len(rows), 'localization_counts': dict(counts),
                   'newly_reviewed_surface_anchors': 12,
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
                             'published_image_examples': len(examples),
                             'unique_TA98_terms_with_examples': len({e['c'] for e in examples}),
                             'note': 'Каждому из 12 разных терминов соответствует опубликованная фотография или КТ другого препарата. 14 карточек включают парные места. Изображения не считаются интерактивной геометрией.'}},
    'separate_models': {
        'z_anatomy': {'bones': len(z['bones']), 'cavities': len(z['cavities']),
                     'independently_placed_markers': len(native['markers']['z']),
                     'metadata': 'site/skull-z-detail.json'},
        'openear': {'structures': len(ear['structures']), 'metadata': 'site/skull-openear.json',
                    'independently_placed_markers': len(native['markers']['openear']),
                    'marker_localization_counts': dict(Counter(p['loc'] for p in native['markers']['openear'])),
                    'marker_metadata': 'site/skull-native-features.json',
                    'marker_source': 'pins_head/openear-native.json',
                    'complete_ossicle_landmark_catalogue_claim': bool(ear_landmarks.get('ossicle_ta98_subterms_complete')),
                    'complete_ossicle_detailed_geometry_claim': bool(ear_landmarks.get('ossicle_detailed_geometry_complete')),
                    'ossicle_subterm_count': len([p for p in native['markers']['openear'] if p['c'].startswith('A15.3.02.')]),
                    'registered_to_main_atlas': False},
        'halle_microct': {'metadata': 'site/skull-microct.json', 'registered_to_main_atlas': False}},
    'skull_whole_catalogue': {'file':'site/skull-whole.json','terms':97,'current_module':89,'future_modules':8,'geometry_policy':'Ракурс и состав группы не означают полную геометрию каждого образования.'},
    'muscle_attachment_catalogue': {'file':'site/skull-muscle-attachments.json','muscles':52,'parts':26,'complete_attachment_areas':0},
    'bone_feature_extent_review': {'file':'site/skull-geometry-review.json','records':extent['total'],
        'counts':extent['counts'],'scope':extent['scope'],'independent_expert_validation':False,
        'note':'Полнота относится только к явно указанной макроскопической форме. Исходные статусы маркеров не меняются; это не процент анатомической готовности всего черепа.'},
    'remaining_primary_markers': remaining,
    'source_channel_geometry': channel_models,
    'cross_source_evidence': {
        'catalogue': 'site/skull-feature-catalogue.json',
        'terms_with_supplemental_material': len(catalogue['features']),
        'native_marker_counts': native['counts'],
        'native_unique_terms': len(native_by_code),
        'main_projection_unique_terms': len({c for (b,c),r in rows.items() if r['localization']=='projection'}),
        'terms': native_by_code,
        'policy': 'Счётчики основного образца и дополнительных материалов независимы. Поверхностный участок, апертура, объём воздуха, полный канал и изображение другого препарата не складываются в процент полной геометрии.'},
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
                'verify/ui-skull-study-navigation-report.json',
                'research/face-feature-review.json', 'research/cranial-feature-review.json',
                'research/temporal-feature-review.json', 'research/variant-example-review.json',
                'verify/ui-skull-features-report.json', 'research/head-muscle-field-review.json',
                'research/skull-whole-model-review.json', 'verify/head-source-geometry.json',
                'verify/ui-atlas-runtime-report.json', 'verify/ui-skull-catalogues-report.json',
                'verify/ui-skull-channels-report.json', 'verify/ui-skull-geometry-report.json',
                'research/face-feature-extent-review.json', 'research/cranial-feature-extent-review.json',
                'research/temporal-feature-extent-review.json', 'research/face-feature-extent-cross-review.json',
                'research/temporal-variant-geometry-review.json', 'research/cranial-variant-geometry-search.json',
                'research/cranial-orbital-variant-review.json',
                'verify/ui-atlas-touch-report.json']}
education=ROOT/'research/skull-educational-release.json'
if education.exists():
    release=json.loads(education.read_text(encoding='utf8'))
    report['educational_release']={k:release[k] for k in ('counts','educationalDispositionComplete','completeSkullGeometry','independentAnatomistReview','physicalDeviceTests','meaning')}
    report['educational_release']['page']='site/skull-education.html'
(ROOT/'research/skull-completion-status.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Skull status:', dict(counts), '— complete geometry is not claimed')
