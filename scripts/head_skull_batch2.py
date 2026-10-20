"""Address-specific skull decisions; no coordinates or inferred bone ownership.

geometryKind is a display/extent requirement, not an automatic FMA conversion.
The frozen per-code decisions use the reviewed descriptions and source locators.
"""
from copy import deepcopy
from skull_shared_stage5 import _record, _ref as _base_ref

def _ref(*args, scope='bone_relationships', **metadata):
    result=_base_ref(*args, **metadata)
    result['scope']=scope
    return result

GRAY_URL = 'https://resources.saylor.org/wwwresources/archived/site/wp-content/uploads/2011/07/BIO302-ch2with6c6d.pdf'
OXFORD_URL = 'https://api.pageplace.de/preview/DT0400.9780192664341_A42890947/preview-9780192664341_A42890947.pdf'
OXFORD = _ref('batch2_oxford_occipital', 'van Gijn DR, Dunne J. Oxford Handbook of Head and Neck Anatomy (2022)',
              OXFORD_URL, 'Chapter 1, printed pp.18–21 (PDF pp.37–39), Occipital bone: lateral, basilar and squamous parts; Figs.1.9–1.10.',
              'van_gijn_dunne', scope='representation_and_laterality')
GRAY_OCC = _ref('batch2_gray_occipital', 'Gray / Lewis. Anatomy of the Human Body (1918)',
               GRAY_URL+'#page=76', 'The Occipital Bone, PDF pp.76–80: parts, condyles, jugular structures, fossae and nuchal lines.',
               'gray_lewis_1918', scope='representation_and_laterality')
SAGITTAL = (
    _ref('batch2_gray_sagittal', 'Gray / Lewis. Anatomy of the Human Body (1918)', GRAY_URL,
         'PDF pp.78,83,87,162: occipital, paired parietal and frontal sagittal sulci; inner skull-cap.', 'gray_lewis_1918'),
    _ref('batch2_elsevier_sagittal', 'Elsevier / Complete Anatomy — Groove for Superior Sagittal Sinus (Frontal Part)',
         'https://www.elsevier.com/resources/anatomy/skeletal-system/axial-skeleton/groove-for-superior-sagittal-sinus-frontal-part/20941',
         'Description: anterior frontal, middle paired parietal and posterior occipital portions. No invariant right sinus dominance adopted.',
         'elsevier_complete_anatomy'),
)
NASOLACRIMAL = (
    _ref('batch2_gray_nasolacrimal', 'Gray / Lewis. Anatomy of the Human Body (1918)', GRAY_URL,
         'PDF pp.121,127,136: maxillary lacrimal groove, descending lacrimal part and lacrimal process of inferior nasal concha.', 'gray_lewis_1918'),
    _ref('batch2_janez_nasolacrimal', 'Jañez-Garcia et al. Three-Dimensional Reconstruction of the Bony Nasolacrimal Canal by Automated Segmentation of Computed Tomography Images',
         'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0155436',
         'Introduction, first two paragraphs: three bones and their contributions; only bony canal, not soft-tissue duct. No specimen measurements transferred.',
         'janez_2016', pmid='27187800', doi='10.1371/journal.pone.0155436', year=2016),
)
INFERIOR_PETROSAL = (
    _ref('batch2_gray_petrosal', 'Gray / Lewis. Anatomy of the Human Body (1918)', GRAY_URL,
         'PDF pp.79,98: lateral basilar grooves and corresponding medial posterior petrous border; groove formed by both bones.', 'gray_lewis_1918'),
    _ref('batch2_oxford_petrosal', 'van Gijn DR, Dunne J. Oxford Handbook of Head and Neck Anatomy (2022)',
         OXFORD_URL, 'Printed p.18, Basilar part / Internal surface features: groove at petrous temporal–basioccipital articulation.', 'van_gijn_dunne'),
)

# Each decision is explicit. Prominences are not flattened to their tip; a groove
# includes its surface/banks. A display line does not claim a measured 3-D curve.
OCCIPITAL_KINDS = {
    2: ('space', 'Анатомическое отверстие, а не точка края и не отдельная кость.'),
    5: ('volume', 'Базилярная часть — участок костного вещества с верхней и нижней поверхностями.'),
    7: ('volume', 'Костный бугорок имеет протяжённость; вершина не равна всему бугорку.'),
    8: ('area', 'Костная борозда включает дно и края; ось синуса не заменяет её поверхность.'),
    9: ('volume', 'Латеральная часть — костная часть, а не одна её суставная поверхность.'),
    10: ('volume', 'Чешуя включает толщину и две поверхности; одна поверхность не равна всей части.'),
    13: ('volume', 'Термин описывает отдельную костную часть при варианте; её наличие у образца не подтверждено.'),
    14: ('volume', 'Мыщелок как костное возвышение отличается от покрывающей его суставной поверхности.'),
    17: ('area', 'Мыщелковая ямка — углублённая область поверхности; канал в её дне рассматривается отдельно.'),
    18: ('volume', 'Яремный бугорок — костное возвышение, не яремная вырезка.'),
    19: ('area', 'Яремная вырезка — вогнутый участок костного края; не всё совместное яремное отверстие.'),
    20: ('volume', 'Яремный отросток — костная часть с несколькими поверхностями.'),
    21: ('volume', 'Внутрияремный отросток — костный выступ, а не весь край отверстия; наличие рельефа не принято.'),
    22: ('volume', 'Наружный затылочный выступ не тождественен точечному краниометрическому inion.'),
    23: ('volume', 'Для полного костного гребня требуется протяжённый рельеф, а не только линия его вершины.'),
    24: ('line', 'Именованная выйная линия рассматривается как линия прикрепления; её кривая не размечена.'),
    25: ('line', 'Двусторонняя выйная линия не заменяется одной опорной точкой.'),
    26: ('line', 'Нижняя выйная линия требует протяжённости обеих сторон, а не одного маркера.'),
    28: ('volume', 'Крестообразное костное возвышение — составной рельеф; не единственная точка пересечения.'),
    29: ('volume', 'Внутренний затылочный выступ — рельеф, его вершина не представляет всю структуру.'),
    30: ('volume', 'Здесь требуется полный костный рельеф гребня; линейная ось в классификации FMA не задаёт его форму.'),
    31: ('area', 'Для борозды нужна поверхность с краями; линейное описание хода синуса не подтверждает её полный рельеф.'),
    32: ('area', 'Речь о затылочном участке поверхности венозной борозды, не о просвете самого синуса.'),
    35: ('volume', 'Вариантный костный отросток требует собственной формы; место возможного варианта не доказывает его наличие.'),
    36: ('area', 'Верхняя парная ямка внутренней поверхности — область, не точечный ориентир.'),
    37: ('area', 'Нижняя парная ямка внутренней поверхности — область, не отдельный объём мозжечка.'),
}
# TA98 entity properties were read for all 36 entries; presence/morphology remains
# specimen-specific. Absence of a Bilaterality property is not proof of unpairedness.
BILATERAL_OCCIPITAL = frozenset((8,9,11,12,14,15,16,17,18,19,20,21,24,25,26,31,32,36,37))
SAGITTAL_PARTS = {'frontal':'A02.1.03.017', 'parietal_right':'A02.1.02.004', 'parietal_left':'A02.1.02.004'}

def geometry_decisions():
    result={('occipital', f'A02.1.04.{n:03}'):kind for n,(kind,reason) in OCCIPITAL_KINDS.items()}
    result.update({(bone,code):'area' for bone,code in SAGITTAL_PARTS.items()})
    result.update({('temporal_'+side,'A02.1.06.038'):'area' for side in ('right','left')})
    return result

def apply_record_review(record):
    bone,code=record['b'],record['c']
    if bone=='occipital':
        number=int(code.rsplit('.',1)[1])
        if number in OCCIPITAL_KINDS:
            record['geometryKindReason']=OCCIPITAL_KINDS[number][1]
        if number in BILATERAL_OCCIPITAL:
            record['lateralityReview']={'pattern':'bilateral', 'verifiedModelSides':[],
                'scope':'catalogue_term', 'source':'research/stage5-skull-batch2-2026-10-16/fipat-occipital.json',
                'note':'Образование рассматривается справа и слева. В каталоге сохранены один ID и одна исходная точка; они не подтверждают обе стороны. Раздельная разметка сторон ещё не принята.'}
        # The original sources remain. These are additional, scoped references.
        if (number in OCCIPITAL_KINDS or number in BILATERAL_OCCIPITAL) and number not in (13,21,35):
            record['refs']=deepcopy(record['refs'])+[deepcopy(OXFORD)]
        if number==18:
            for ref in record['refs']:
                if 'anatomystandard.com' in ref.get('url',''):
                    ref['locator']+=' Ограничение источника: английская подпись Tuberculum jugulare — Jugular notch ошибочна; TA98 A02.1.04.018: jugular tubercle. Не смешивать с incisura jugularis.'
            record['refs'].append(_ref('batch2_ta98_jugular_tubercle','FIPAT TA98 — A02.1.04.018',
                'https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/Entity%20TA98%20EN/02.1.04.018%20Entity%20TA98%20EN.htm',
                'English equivalent: jugular tubercle; Bilaterality. Терминология, не координата.', 'fipat', scope='nomenclature'))
    if SAGITTAL_PARTS.get(bone)==code:
        record['partOf']='shared_skull_038'
        record['geometryKindReason']='Локальная поверхность борозды — часть общего образования, а не его независимый дубликат.'
        record['refs']=deepcopy(record['refs'])+deepcopy(list(SAGITTAL))
        record['modelNote']+=' Это локальный костный участок общей борозды A02.1.00.038. Его маркер не задаёт всю борозду.'
    if bone.startswith('temporal_') and code=='A02.1.06.038':
        record['partOf']='shared_skull_052_'+bone.rsplit('_',1)[1]
        record['geometryKindReason']='Поверхность местной венозной борозды не равна просвету синуса.'
        record['refs']=deepcopy(record['refs'])+deepcopy(list(INFERIOR_PETROSAL))
        record['modelNote']+=' Это височный участок общей борозды A02.1.00.052 своей стороны. Его точка не задаёт весь затылочно-височный рельеф.'
    if bone=='occipital' and code=='A02.1.04.008':
        record['modelNote']+=' Общие борозды A02.1.00.052 существуют справа и слева. Сторона этой старой затылочной разметки не принята; её точка не переносилась в общие экземпляры.'

def additional_instances(terminology):
    yield _record('shared_skull_038','A02.1.00.038',terminology['A02.1.00.038'],
        'Борозда верхнего сагиттального синуса',
        'Общая борозда внутренней поверхности черепа включает лобный, правый и левый теменные и затылочный участки. Локальные костные записи сохранены как части.',
        ['frontal','parietal_right','parietal_left','occipital'],None,'component','area',SAGITTAL,
        'Не является самим венозным синусом. Затылочный участок участвует в общем образовании; отдельная новая точка ему не присвоена.',concept='skull-whole-038')
    for side in ('right','left'):
        yield _record('shared_skull_052_'+side,'A02.1.00.052',terminology['A02.1.00.052'],
            'Борозда нижнего каменистого синуса',
            'Общая костная борозда складывается из участка у бокового края базилярной части затылочной кости и соответствующего участка каменистой части височной кости своей стороны.',
            ['occipital','temporal_'+side],side,'component','area',INFERIOR_PETROSAL,
            'Не является самим венозным синусом. Сторона старой затылочной разметки ещё не принята; её точка не присвоена ни одному общему экземпляру.',concept='skull-whole-052')
    for side in ('right','left'):
        yield _record('shared_skull_085_'+side,'A02.1.00.085',terminology['A02.1.00.085'],
            'Носослёзный канал',
            'Костный канал образован верхней челюстью, слёзной костью и слёзным отростком нижней носовой раковины своей стороны. Он отличается от проходящего в нём мягкотканного носослёзного протока.',
            ['maxilla_'+side,'lacrimal_'+side,'inferior_concha_'+side],side,'boundaryContribution','volume',NASOLACRIMAL,
            'Слёзная ямка, локальные борозды и отверстие канала сохраняются отдельными структурами. Средние измерения из публикаций не переносились на модель.',concept='skull-whole-085')
