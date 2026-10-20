"""Limited educational admission of four source carpal models; no pin coordinates."""
REPORT = 'research/stage6-left-carpals1-report-2026-10-20.md'
SOURCES = {'scaphoid_left':'FMA24436', 'lunate_left':'FMA24438',
           'triquetrum_left':'FMA24440', 'pisiform_left':'FMA24442'}
BASE = 'models/bodyparts3d-3.0/left-carpals1'
NOTICE = 'Учебная 3D-модель. Точная геометрия суставных поверхностей, границ и зазоров не подтверждена.'
NOTE = (NOTICE + ' BodyParts3D 3.0/95%, DBCLS; сторона, исходный масштаб и крупное расположение проверены. '
        'Есть локальные пересечения в шести парах соседних сеток запястья, включая контрольный дистальный ряд; полный перечень сохранён в отчёте партии. '
        'Это ограничение исходной учебной сборки, не физиологический контакт. Разметка и клиническая точность не приняты. '
        'Модели не отражались; независимое сканирование левого образца не подтверждено.')

def admit(cards):
    for bone, source in SOURCES.items():
        cards[bone].update(noModel=False,sourceId=source,modelStatus='educational_limited',
            modelNotice=NOTICE,modelRegionLabel='Левое запястье',
            modelFile=f'{BASE}/{bone}.glb',modelLicense=f'{BASE}/LICENSE-MODELS.txt',
            modelReview=dict(educationalAcceptance=True,fullAnatomicalAcceptance=False,report=REPORT),
            note=NOTE)
        cards[bone]['refs'].append(dict(title='BodyParts3D 3.0 — DBCLS, CC BY-SA 2.1 Japan',
            url=f'{BASE}/LICENSE-MODELS.txt',locator=source+'; производная GLB, учебный допуск',
            scope='geometry_provenance',checked='2026-10-20'))

def review_geometry(record):
    related={record['b'],*record.get('sh',[]),*record.get('catalogueBones',[])}
    related.update(r['bone'] for r in record.get('relations',[]))
    if not related.intersection(SOURCES):
        return record
    available=set(SOURCES)|{'radius_left','ulna_left'}
    complete=related<=available
    text=(NOTICE+' В сборке доступны четыре кости проксимального ряда слева и предплечье. '
          'Другие левые кости кисти и мягкие ткани пока без моделей. Координаты и протяжённость этого образования не приняты.')
    record.update(modelNote=text,geometryReview=dict(coordinateAcceptance=False,extentAcceptance=False,report=REPORT),
        geometryRequirements=dict(status='unverified_extent' if complete else 'missing_model',
                                  neededEvidence=text))
    return record
