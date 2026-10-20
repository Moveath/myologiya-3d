"""Addressed skull catalogue additions; no coordinates, TA98 codes or mesh edits."""
from copy import deepcopy
from head_skull_batch2 import _ref, GRAY_URL

REPORT = 'research/stage5-skull-final-2026-10-17/candidate-decisions.json'

def ref(key, title, url, locator, group, **metadata):
    item = _ref('skull_final_'+key, title, url, locator, group,
                scope='anatomical_entity_only', **metadata)
    item['checked'] = '2026-10-17'
    return item

GRAY_MAND = ref('gray_mandible', 'Gray / Lewis. Anatomy of the Human Body (1918)',
    GRAY_URL+'#page=140', 'PDF pp.140–142: body surfaces, ramus surfaces/borders, incisive fossa and condylar articular surface. Not a specimen map.', 'gray_lewis_1918')
GRAY_MAX = ref('gray_maxilla', 'Gray / Lewis. Anatomy of the Human Body (1918)',
    GRAY_URL+'#page=118', 'PDF p.118, anterior surface: facial incisive fossa and canine eminence distinguished from canine fossa.', 'gray_lewis_1918')
GRAY_LAC = ref('gray_lacrimal', 'Gray / Lewis. Anatomy of the Human Body (1918)',
    GRAY_URL+'#page=126', 'PDF pp.126–127, lateral/orbital and medial surfaces; whole surface is not its crest or sulcus.', 'gray_lewis_1918')
NCBI_MAND = ref('ncbi_mandible', 'Breeland G, Aktar A, Patel BC. Anatomy, Head and Neck, Mandible (2023)',
    'https://www.ncbi.nlm.nih.gov/books/NBK532292/',
    'Structure and Function: Body and Ramus; Muscles: incisive fossa. Indexed text read. Used only for surfaces, borders, fossa and articulation, not its erroneous intrinsic-muscle statement or fixed spine count.',
    'breeland_aktar_patel', access='indexed_full_text', pmid='30335325')
NCBI_MAX = ref('ncbi_maxilla', 'Soriano RM, Brizuela M. Anatomy, Head and Neck, Maxilla',
    'https://www.ncbi.nlm.nih.gov/books/NBK538527/table/article-32546.table1/?report=objectonly',
    'Table 1, anterior surface; addressed evidence read in batch 6 completeness-gaps.md. Current direct retrieval CAPTCHA; reuse explicitly, not a new full-text read. EFetch confirms current chapter authors, PMID30860762.',
    'soriano_brizuela', access='prior_indexed_text_batch6', pmid='30860762')
OXFORD_MAX = ref('oxford_maxilla', 'van Gijn DR, Dunne J. Oxford Handbook of Head and Neck Anatomy (2022)',
    'https://api.pageplace.de/preview/DT0400.9780192664341_A42890947/preview-9780192664341_A42890947.pdf',
    'Maxilla, anterior surface: canine eminence; only the bony bulge over the canine socket is used.', 'van_gijn_dunne')
LAC_ATLAS = ref('lacrimal_atlas', 'Anatomy Standard — Os lacrimale (2020)',
    'https://www.anatomystandard.com/ossa-et-juncturae/cranium/os-lacrimale.html',
    'Independently illustrated lateral and medial aspects, captions. Supports the two surfaces, not complete borders or project coordinates.', 'anatomystandard')
TROST = ref('trost', 'Trost M et al. The lingual foramina, a potential risk in oral surgery. A retrospective analysis of location and anatomic variability (2020)',
    'https://pubmed.ncbi.nlm.nih.gov/32229242/',
    'Official EFetch abstract read: median and lateral groups, variable presence, number and position in adult CT cohort. Measurements are not transferred.',
    'trost_mundt_2020', access='efetch_abstract', pmid='32229242', doi='10.1016/j.aanat.2020.151515')
ZHANG = ref('zhang', 'Zhang C et al. Evaluation of Mandibular Lingual Foramina With Cone-Beam Computed Tomography (2018)',
    'https://pubmed.ncbi.nlm.nih.gov/29481515/',
    'Official EFetch abstract read: independent 299-patient CBCT sample; midline/lateral foramina distinguished from nutrient foramina. No fixed count or dimensions inferred.',
    'zhang_2018_lingual', access='efetch_abstract', pmid='29481515', doi='10.1097/SCS.0000000000004390')

def record(candidate, bone, key, ru, kind, description, refs, related, side=None):
    return dict(id='extra_'+bone+'_'+key, b=bone, t='additional', ru=ru, lat='', x=description,
        m=[], g='Дополнительные образования', side=side, geometryKind=kind,
        candidateId=candidate, refs=deepcopy(refs), relatedLandmarks=related,
        educationAvailable=False, nomenclatureStatus='outside_own_TA98_list',
        geometryReview=dict(status='representation_reviewed', source=REPORT,
                            coordinateAcceptance=False, extentAcceptance=False),
        modelNote='Существование образования подтверждено источниками. Его положение и границы на этой модели не подтверждены; 3D-маркер не создан. Отдельный код TA98 не присвоен.')

def additional_records():
    for side, suffix in (('right','справа'), ('left','слева')):
        b='maxilla_'+side
        for key,ru,kind,desc,refs in (
            ('facial_incisive_fossa','Резцовая ямка передней поверхности верхней челюсти','area',
             'Углубление передней поверхности над резцами. Это не нёбная резцовая ямка, не резцовый канал и не клыковая ямка.',[GRAY_MAX,NCBI_MAX]),
            ('canine_eminence','Клыковое возвышение','volume',
             'Костный выступ передней поверхности над областью клыковой альвеолы; отличать от соседней клыковой ямки.',[GRAY_MAX,OXFORD_MAX]),
        ):
            yield record('maxilla-'+side+'-'+key.replace('_','-'), b,key,ru+' '+suffix,kind,desc,refs,
                         ['head_'+b+'_A02_1_12_007','head_'+b+'_A02_1_12_009'],side)
        b='lacrimal_'+side
        for key,ru,desc in (
            ('surface_lateral','Латеральная поверхность слёзной кости','Глазничная сторона слёзной кости. Её гребень и борозда — отдельные участки рельефа, не вся поверхность.'),
            ('surface_medial','Медиальная поверхность слёзной кости','Обращённая медиально сторона тонкой слёзной кости; отличается от её глазничной поверхности.'),
        ):
            yield record('candidate_'+b+'_'+key,b,key,ru+' '+suffix,'area',desc,[GRAY_LAC,LAC_ATLAS],
                         ['head_'+b+'_A02_1_09_002'],side)
    for key,ru,desc in (
        ('body_external_surface','Наружная поверхность тела нижней челюсти','Наружная сторона тела. Подбородочное возвышение и подбородочные отверстия не равны всей поверхности.'),
        ('body_internal_surface','Внутренняя поверхность тела нижней челюсти','Внутренняя сторона тела. Подъязычные и поднижнечелюстные ямки являются отдельными участками её рельефа.'),
    ):
        yield record('mandible_'+key,'mandible',key,ru,'area',desc,[GRAY_MAND,NCBI_MAND],['head_mandible_A02_1_15_002'])
    for side,suffix in (('right','справа'),('left','слева')):
        for key,ru,kind,desc,parent in (
            ('ramus_lateral_surface','Латеральная поверхность ветви','area','Наружная сторона соответствующей ветви; жевательная бугристость занимает лишь часть её рельефа.','024'),
            ('ramus_medial_surface','Медиальная поверхность ветви','area','Внутренняя сторона ветви, содержащая отверстие нижней челюсти; не тождественна этому отверстию.','024'),
            ('ramus_anterior_border','Передний край ветви','line','Передняя граница ветви, продолжающаяся к венечному отростку; не вся поверхность или объём ветви.','024'),
            ('ramus_posterior_border','Задний край ветви','line','Задняя граница ветви, продолжающаяся от мыщелкового отдела к углу; не сама область угла.','024'),
            ('condylar_articular_surface','Суставная поверхность головки нижней челюсти','area','Участок поверхности головки, участвующий в сочленении через суставной диск. Не вся головка, не диск и не поверхность височной кости.','036'),
            ('incisive_fossa','Резцовая ямка нижней челюсти','area','Углубление наружной поверхности в резцовом отделе нижней челюсти. Не резцовый канал и не ямка верхней челюсти.','002'),
        ):
            yield record('mandible_'+side+'_'+key,'mandible',side+'_'+key,ru+' '+suffix,kind,desc,
                         [GRAY_MAND,NCBI_MAND],['head_mandible_A02_1_15_'+parent],side)
        yield record('mandible_'+side+'_lateral_lingual_foramina','mandible',side+'_lateral_lingual_foramina',
            'Латеральные язычные отверстия нижней челюсти '+suffix,'space',
            'Вариабельная группа апертур язычной кортикальной поверхности сбоку от средней линии. Число и положение непостоянны; наличие на этом образце не установлено.',
            [TROST,ZHANG],['head_mandible_A02_1_15_002'],side)
    yield record('mandible_median_lingual_foramina','mandible','median_lingual_foramina',
        'Срединные язычные отверстия нижней челюсти','space',
        'Апертуры язычной поверхности в срединной области нижней челюсти. Их число и положение относительно подбородочных остей вариабельны; апертуры не заменяют весь внутрикостный ход.',
        [TROST,ZHANG],['head_mandible_A02_1_15_004','head_mandible_A02_1_15_010'])
