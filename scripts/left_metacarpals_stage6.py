"""Three educational admissions; I and III remain trial-only, without pin edits."""
from left_carpals1_stage6 import SOURCES as PROXIMAL, NOTICE
from left_carpals2_stage6 import SOURCES as DISTAL

REPORT = 'research/stage6-left-metacarpals-report-2026-10-20.md'
SOURCES = {'metacarpal_2_left': 'FMA24467', 'metacarpal_4_left': 'FMA24471',
           'metacarpal_5_left': 'FMA24473'}
BASE = 'models/bodyparts3d-3.0/left-metacarpals'
NOTE = (NOTICE + ' BodyParts3D 3.0/95%, DBCLS; проверены сторона, нумерация, масштаб и крупная форма. '
        'Есть локальные пересечения II пястной с трапецией и IV с V пястной; это дефекты согласования '
        'исходных сеток, не физиологический контакт. Девять прежних пар пересечений запястья сохраняются. '
        'Точные фасетки, хрящи, зазоры и разметка не приняты. Модели не отражались; '
        'независимое сканирование левого образца не подтверждено.')
BLOCKED = {
    'metacarpal_1_left': 'Пробная геометрия найдена, но не подключена: проникновение основания в трапецию '
                         'до 1,153449 мм среди проверенных вершин/центров граней. Нужна независимая приёмка CMC I и исходников.',
    'metacarpal_3_left': 'Пробная геометрия найдена, но не подключена: пересечение с трапециевидной костью '
                         'до 0,545677 мм в проверенной выборке. Этот контакт не принят как нормальное сочленение; нужна проверка основания и соседних фасеток.',
}


def admit(cards):
    for bone, source in SOURCES.items():
        cards[bone].update(noModel=False, sourceId=source, modelStatus='educational_limited',
            modelNotice=NOTICE, modelRegionLabel='Левая пясть (II, IV, V)',
            modelFile=f'{BASE}/{bone}.glb', modelLicense=f'{BASE}/LICENSE-MODELS.txt',
            modelReview=dict(educationalAcceptance=True, fullAnatomicalAcceptance=False, report=REPORT),
            note=NOTE)
        cards[bone]['refs'].append(dict(title='BodyParts3D 3.0 — DBCLS, CC BY-SA 2.1 Japan',
            url=f'{BASE}/LICENSE-MODELS.txt', locator=source+'; производная GLB, учебный допуск',
            scope='geometry_provenance', checked='2026-10-20'))
    for bone, reason in BLOCKED.items():
        mirror = (
            " Проверено отражение правой кости: конфликт с проксимальной фалангой I до 1,258745 мм; зеркальный кандидат также не подключён."
            if bone == "metacarpal_1_left" else
            " Проверено отражение правой кости: конфликты с trapezoid до 1,317846 мм, II пястной до 1,105602 мм и проксимальной фалангой III до 0,820490 мм; зеркальный кандидат также не подключён.")
        assert cards[bone].get('noModel') is True
        cards[bone].update(note=reason + mirror + ' Глубины выборочные, не физиологический допуск. Без произвольного смещения или деформации.',
            modelReview=dict(educationalAcceptance=False, fullAnatomicalAcceptance=False,
                             report=REPORT, blockedReason=reason,
                             mirrorReport='research/stage6-mirrored-recovery-2026-10-20.md'))


def review_geometry(record):
    related = {record['b'], *record.get('sh', []), *record.get('catalogueBones', [])}
    related.update(r['bone'] for r in record.get('relations', []))
    hand = set(PROXIMAL) | set(DISTAL) | set(SOURCES) | set(BLOCKED)
    if not related.intersection(hand):
        return record
    available = set(PROXIMAL) | set(DISTAL) | set(SOURCES) | {'radius_left', 'ulna_left'}
    text = (NOTICE + ' Доступны восемь костей левого запястья, II/IV/V пястные и предплечье. '
            'I и III пястные остались тестовыми из-за дефектов совмещения. Фаланги, сесамоиды большого '
            'пальца и мягкие ткани слева пока без моделей. Координаты и протяжённость этого образования не приняты.')
    record.update(modelNote=text,
        geometryReview=dict(coordinateAcceptance=False, extentAcceptance=False, report=REPORT),
        geometryRequirements=dict(status='unverified_extent' if related <= available else 'missing_model',
                                  neededEvidence=text))
    return record
