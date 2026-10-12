"""Summarize source-confirmed geometry without equating pin coverage with completeness."""
from collections import Counter
from pathlib import Path
import json
from head_localization import positions

ROOT = Path(__file__).resolve().parents[1]
rows = positions()
counts = Counter(p['localization'] for p in rows.values())
z = json.loads((ROOT/'site/skull-z-detail.json').read_text(encoding='utf-8'))
ear = json.loads((ROOT/'site/skull-openear.json').read_text(encoding='utf-8'))
remaining = {}
for (bone, code), row in rows.items():
    if row['localization'] != 'surface':
        remaining.setdefault(bone, []).append({'code': code, 'localization': row['localization'],
                                               'modelNote': row['modelNote']})
report = {
    'date': '2026-10-12',
    'policy': 'Только геометрия, подтверждённая опубликованными сканами или исходными моделями; без вымышленных реконструкций.',
    'complete_skull_geometry_claim': False,
    'main_atlas': {'markers': len(rows), 'localization_counts': dict(counts),
                   'newly_reviewed_surface_anchors': 6,
                   'note': 'Поверхностный маркер отмечает участок рельефа, а не доказывает полную геометрию образования.'},
    'separate_models': {
        'z_anatomy': {'bones': len(z['bones']), 'cavities': len(z['cavities']),
                     'independently_placed_markers': len(z['markers']),
                     'metadata': 'site/skull-z-detail.json'},
        'openear': {'structures': len(ear['structures']), 'metadata': 'site/skull-openear.json',
                    'registered_to_main_atlas': False},
        'halle_microct': {'metadata': 'site/skull-microct.json', 'registered_to_main_atlas': False}},
    'remaining_primary_markers': remaining,
    'other_remaining_limitations': [
        'Девять карточек мышц не имеют отдельной геометрии в проверенных совместимых наборах.',
        'Части некоторых мышц не выделены в исходных сетках; список и ограничения сохранены в карточках.',
        'Внутренние структуры OpenEar относятся к одному препарату и не подтверждают автоматически проекции на BodyParts3D.',
        'Варианты строения не обязаны присутствовать у конкретного человека. Их типичная область не заменяет обнаруженный вариант.',
        'Полная геометрия всех отверстий, стенок каналов и их сообщений не подтверждена выбранными источниками.'],
    'reviews': ['research/face-completion-review.json', 'research/cranial-completion-registration.json',
                'research/temporal-completion-review.json', 'verify/ui-head-report.json',
                'verify/ui-skull-detail-report.json']}
(ROOT/'research/skull-completion-status.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Skull status:', dict(counts), '— complete geometry is not claimed')
