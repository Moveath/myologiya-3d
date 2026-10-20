"""Left forearm catalogue, deliberately independent of any geometric reflection."""
from copy import deepcopy
from ta98 import T, BONE
from arm_forearm_stage5_review import (
    RADIUS, ULNA, GRAY_REF, SOB_REF, TA, ref, additional_records as arm_additional,
)

REPORT = 'research/stage5-left-forearm-report-2026-10-19.md'
MODEL_REPORT = 'research/stage6-forearm-educational-admission-2026-10-20.md'
MODEL_NOTICE = 'Учебная 3D-модель. Точная геометрия суставных поверхностей и зазоров не подтверждена.'
MODEL_BASE = 'models/bodyparts3d-3.0/left-forearm'
NOTE = (MODEL_NOTICE + ' BodyParts3D 3.0 / DBCLS: сторона, масштаб и крупное положение проверены. '
        'Исходник уже упрощён автором; клиническая точность и независимое сканирование левой стороны не доказаны. '
        'Координаты, контуры и площади ориентиров не назначены. Геометрия правой стороны не отражалась.')
MODEL_REF = dict(id='bp3d_left_forearm_geometry', title='BodyParts3D © DBCLS — CC BY-SA 2.1 Japan; происхождение и изменения',
    url=MODEL_BASE+'/LICENSE-MODELS.txt', access='model_provenance', checked='2026-10-20',
    locator='BodyParts3D 3.0 / 20110915 / OBJ 95%; FMA23465, FMA23468; only educational geometry acceptance.')
FOREARM_REF = dict(id='left_forearm_ncbi', title='Patel, Varacallo — Forearm Bones (2023)',
    url='https://www.ncbi.nlm.nih.gov/sites/books/NBK545260/', locator='Introduction; Structure and Function: laterality and joint surfaces only.',
    access='full_text', checked='2026-10-19')
BONES = {}
for bone, ru, lat, code, candidate, definition in (
    ('radius_left', 'Левая лучевая кость', 'radius', 'A02.4.05.001', 'FMA23465',
     'Латеральная кость левого предплечья в анатомическом положении. Проксимальная головка участвует в локтевом и проксимальном лучелоктевом сочленениях; дистальный конец имеет локтевую вырезку и запястную суставную поверхность.'),
    ('ulna_left', 'Левая локтевая кость', 'ulna', 'A02.4.06.001', 'FMA23468',
     'Медиальная кость левого предплечья в анатомическом положении. Проксимально расположены локтевой и венечный отростки, блоковидная и лучевая вырезки; головка находится дистально. Суставной диск отделяет головку от костей запястья.'),
):
    BONES[bone] = dict(ru=ru, lat=lat, code=code, g='b_free', sub='forearm', sec='arm', side='left',
        noModel=False, contextTargets=['humerus_left'], candidateSourceId=candidate, sourceId=candidate,
        modelStatus='educational_limited', modelNotice=MODEL_NOTICE,
        modelFile=MODEL_BASE+'/'+bone+'.glb', modelLicense=MODEL_BASE+'/LICENSE-MODELS.txt',
        modelReview=dict(educationalAcceptance=True, fullAnatomicalAcceptance=False, report=MODEL_REPORT),
        x=definition, note=NOTE, refs=deepcopy([GRAY_REF, SOB_REF, FOREARM_REF, MODEL_REF,
            ref('ta98', 'FIPAT / IFAA — TA98 osteology', TA, code, 'official_list')]))


def unmodelled(record):
    p = deepcopy(record)
    assert p.get('p') is None and p.get('n') is None
    p.update(side='left', educationAvailable=False, modelNote=NOTE,
        geometryRequirements=dict(status='unverified_extent', neededEvidence=
            'Учебная модель кости доступна. Нужны подтверждённая локализация и разметка конкретной поверхности/траектории/объёма на её хеше; для суставов также границы сопряжённых поверхностей и сведения о хряще/позе.'),
        geometryReview=dict(coordinateAcceptance=False, extentAcceptance=False, report=MODEL_REPORT),
        leftForearmReview=dict(source=REPORT, scope='catalogue_with_limited_educational_model', geometryAccepted=False))
    p.pop('armForearmReview', None)
    return p


def catalogue_records():
    # Shared anatomical definitions, never coordinates/attachments of a right specimen.
    for bone, table in (('radius_left', RADIUS), ('ulna_left', ULNA)):
        for code in BONE[bone]:
            kind, definition = table[int(code.split('.')[-1])]
            p = dict(id='context_'+bone+'_'+code.replace('.', '_'), b=bone, t='ta', c=code,
                ru=T[code][1], lat=T[code][0], p=None, n=None, m=[],
                x=definition, anatomicalDefinition=definition, geometryKind=kind,
                geometryKindReason=definition, refs=deepcopy([GRAY_REF, SOB_REF,
                    ref('ta98', 'FIPAT / IFAA — TA98 osteology', TA, code, 'official_list')]))
            parents = {'A02.4.05.003':'A02.4.05.002', 'A02.4.05.004':'A02.4.05.002',
                       'A02.4.05.011':'A02.4.05.010', 'A02.4.06.016':'A02.4.06.015'}
            if code in parents: p['partOf'] = 'context_'+bone+'_'+parents[code].replace('.', '_')
            yield unmodelled(p)


def additional_records():
    # Explicitly selected bilateral anatomical entities; templates have no geometry.
    keys = {'extra_radius_nutrient_foramina', 'extra_ulna_nutrient_foramina',
            'extra_ulna_distal_fovea', 'extra_ulna_ecu_groove',
            'extra_humerus_elbow_joint', 'extra_humerus_humeroulnar_joint',
            'extra_humerus_humeroradial_joint', 'extra_radius_proximal_radioulnar_joint',
            'extra_radius_distal_radioulnar_joint'}
    templates = [p for p in arm_additional({'humerus','radius','ulna'}) if p['id'] in keys]
    assert {p['id'] for p in templates} == keys
    def left_id(id):
        for b in ('humerus','radius','ulna'):
            if id.startswith('extra_'+b+'_'): return id.replace('extra_'+b+'_', 'extra_'+b+'_left_', 1)
        raise ValueError(id)
    for original in templates:
        p = unmodelled(original)
        p.update(id=left_id(p['id']), b=p['b']+'_left', ru=p['ru'].replace('справа','слева'))
        if 'relations' in p:
            p['relations'] = [dict(r, bone=r['bone']+'_left') for r in p['relations']]
            p['modelNote'] = (MODEL_NOTICE + ' Доступны учебные модели левых radius/ulna и существующая плечевая кость. '
                'Показанные кости не представляют весь сустав: хрящ, капсула, координаты и контуры не размечены и не приняты. Геометрия правой стороны не отражалась.')
        if 'partOf' in p: p['partOf'] = left_id(p['partOf'])
        yield p
