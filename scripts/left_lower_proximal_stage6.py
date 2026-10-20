"""Four left lower-limb source bones: educational display, no coordinate or joint acceptance."""
from left_carpals1_stage6 import NOTICE

REPORT = 'research/stage6-left-lower-proximal-report-2026-10-20.md'
SOURCES = {'femur_left': 'FMA24475', 'patella_left': 'FMA24487', 'tibia_left': 'FMA24478', 'fibula_left': 'FMA24481'}
BASE = 'models/bodyparts3d-3.0/left-lower-proximal'
NOTE = (NOTICE + ' BodyParts3D 3.0/95%, DBCLS; исходные сторона, масштаб, ориентация и крупная форма проверены. '
        'Есть пересечения исходных сеток: бедренная/тазовая (выборочно до 0,833 мм), большеберцовая/малоберцовая '
        '(до 0,239 мм) и большеберцовая/таранная (до 0,058 мм; таранная пока не подключена). '
        'Это не физиологический контакт; точные суставные поверхности, хрящи, зазоры и пины не приняты. '
        'Модели не отражались и не подгонялись. Независимый левый скан не подтверждён.')


def admit(cards):
    for bone, source in SOURCES.items():
        cards[bone].update(noModel=False, sourceId=source, modelStatus='educational_limited',
            modelNotice=NOTICE, modelRegionLabel='Левое бедро и голень',
            modelFile=f'{BASE}/{bone}.glb', modelLicense=f'{BASE}/LICENSE-MODELS.txt',
            modelReview=dict(educationalAcceptance=True, fullAnatomicalAcceptance=False, report=REPORT),
            note=NOTE)
        cards[bone]['refs'].append(dict(title='BodyParts3D 3.0 — DBCLS, CC BY-SA 2.1 Japan',
            url=f'{BASE}/LICENSE-MODELS.txt', locator=source+'; производная GLB, учебный допуск',
            scope='geometry_provenance', checked='2026-10-20'))


