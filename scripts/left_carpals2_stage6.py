"""Distal-row educational geometry; never generates anatomical coordinates."""
from left_carpals1_stage6 import SOURCES as PROXIMAL, NOTICE

REPORT = 'research/stage6-left-carpals2-report-2026-10-20.md'
SOURCES = {'trapezium_left': 'FMA24444', 'trapezoid_left': 'FMA24445',
           'capitate_left': 'FMA24447', 'hamate_left': 'FMA24449'}
BASE = 'models/bodyparts3d-3.0/left-carpals2'
NOTE = (NOTICE + ' BodyParts3D 3.0/95%, DBCLS; проверены сторона, исходный масштаб и крупное расположение. '
        'В дистальном ряду есть локальные пересечения трапеции с трапециевидной, трапециевидной с головчатой '
        'и головчатой с крючковидной; сохранены прежние пересечения с проксимальным рядом. '
        'Это дефекты согласования исходных сеток, не физиологический контакт. Точные фасетки, зазоры и разметка не приняты. '
        'Модели не отражались; независимое сканирование левого образца не подтверждено.')


def admit(cards):
    for bone, source in SOURCES.items():
        cards[bone].update(noModel=False, sourceId=source, modelStatus='educational_limited',
            modelNotice=NOTICE, modelRegionLabel='Левое запястье',
            modelFile=f'{BASE}/{bone}.glb', modelLicense=f'{BASE}/LICENSE-MODELS.txt',
            modelReview=dict(educationalAcceptance=True, fullAnatomicalAcceptance=False, report=REPORT),
            note=NOTE)
        cards[bone]['refs'].append(dict(title='BodyParts3D 3.0 — DBCLS, CC BY-SA 2.1 Japan',
            url=f'{BASE}/LICENSE-MODELS.txt', locator=source+'; производная GLB, учебный допуск',
            scope='geometry_provenance', checked='2026-10-20'))


def review_geometry(record):
    related = {record['b'], *record.get('sh', []), *record.get('catalogueBones', [])}
    related.update(r['bone'] for r in record.get('relations', []))
    carpals = set(PROXIMAL) | set(SOURCES)
    if not related.intersection(carpals):
        return record
    available = carpals | {'radius_left', 'ulna_left'}
    text = (NOTICE + ' Доступны восемь учебных костей левого запястья и предплечье. '
            'Пясть, фаланги, сесамоиды большого пальца и мягкие ткани слева пока без моделей. '
            'Есть локальные пересечения исходных сеток. Координаты и протяжённость этого образования не приняты.')
    record.update(modelNote=text,
        geometryReview=dict(coordinateAcceptance=False, extentAcceptance=False, report=REPORT),
        geometryRequirements=dict(status='unverified_extent' if related <= available else 'missing_model',
                                  neededEvidence=text))
    return record
