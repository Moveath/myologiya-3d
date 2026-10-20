"""Fourteen source phalanges: educational display, no coordinate or joint acceptance."""
from left_carpals1_stage6 import SOURCES as PROXIMAL, NOTICE
from left_carpals2_stage6 import SOURCES as DISTAL
from left_metacarpals_stage6 import SOURCES as METACARPALS, BLOCKED

REPORT = 'research/stage6-left-phalanges-report-2026-10-20.md'
SOURCES = {'phalanx_prox_1_left': 'FMA65470', 'phalanx_prox_2_left': 'FMA71915', 'phalanx_prox_3_left': 'FMA71908', 'phalanx_prox_4_left': 'FMA71916', 'phalanx_prox_5_left': 'FMA66791', 'phalanx_mid_2_left': 'FMA23938', 'phalanx_mid_3_left': 'FMA23940', 'phalanx_mid_4_left': 'FMA23942', 'phalanx_mid_5_left': 'FMA23944', 'phalanx_dist_1_left': 'FMA23951', 'phalanx_dist_2_left': 'FMA23953', 'phalanx_dist_3_left': 'FMA23955', 'phalanx_dist_4_left': 'FMA23957', 'phalanx_dist_5_left': 'FMA23959'}
BASE = 'models/bodyparts3d-3.0/left-phalanges'
NOTE = (NOTICE + ' BodyParts3D 3.0/95%, DBCLS; проверены исходная сторона, нумерация, масштаб и крупная форма. '
        'Есть локальные пересечения соседних сеток фаланг и пясти; они не считаются физиологическим контактом. '
        'Точная форма суставных фасеток и дистальных бугристостей не принята. I и III пястные остаются '
        'тестовыми: соответствующие пястно-фаланговые сборки неполны. Модели не отражались; '
        'независимое сканирование левого образца не подтверждено.')


def admit(cards):
    for bone, source in SOURCES.items():
        cards[bone].update(noModel=False, sourceId=source, modelStatus='educational_limited',
            modelNotice=NOTICE, modelRegionLabel='Фаланги левой кисти',
            modelFile=f'{BASE}/{bone}.glb', modelLicense=f'{BASE}/LICENSE-MODELS.txt',
            modelReview=dict(educationalAcceptance=True, fullAnatomicalAcceptance=False, report=REPORT),
            note=NOTE)
        cards[bone]['refs'].append(dict(title='BodyParts3D 3.0 — DBCLS, CC BY-SA 2.1 Japan',
            url=f'{BASE}/LICENSE-MODELS.txt', locator=source+'; производная GLB, учебный допуск',
            scope='geometry_provenance', checked='2026-10-20'))


def review_geometry(record):
    related = {record['b'], *record.get('sh', []), *record.get('catalogueBones', [])}
    related.update(r['bone'] for r in record.get('relations', []))
    available = set(PROXIMAL) | set(DISTAL) | set(METACARPALS) | set(SOURCES) | {'radius_left', 'ulna_left'}
    if not related.intersection(available | set(BLOCKED)):
        return record
    text = (NOTICE + ' Доступны 25 обычных костей левой кисти и предплечье; I/III пястные '
            'остаются тестовыми, два сесамоида MCP I и мягкие ткани без моделей. Пересечения исходных '
            'сеток сохраняются. Координаты и протяжённость этого образования не приняты.')
    record.update(modelNote=text,
        geometryReview=dict(coordinateAcceptance=False, extentAcceptance=False, report=REPORT),
        geometryRequirements=dict(status='unverified_extent' if related <= available else 'missing_model',
                                  neededEvidence=text))
    return record
