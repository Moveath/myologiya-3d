"""Source-reviewed skull relationships; no coordinates or specimen geometry.

Evidence: research/stage5-skull-2026-10-16/shared-source-review.json.
These definitions are deliberately separate from the active catalogue until its
integration review. Local bone parts retain their existing IDs and coordinates.
"""
from copy import deepcopy
from typing import NamedTuple

from skull_whole_terms import TERMS, GRAY_URL


CHECKED = '2026-10-16'
CBS_URL = 'https://cbspd.s3.ap-south-1.amazonaws.com/assets/documents/9789354661792S.pdf'


def _ref(id, title, url, locator, group, access='full_text', **metadata):
    return dict(id=id, title=title, url=url, locator=locator, authorGroup=group,
                kind='anatomical', scope='bone_relationships', checked=CHECKED,
                access=access, **metadata)


def _gray(id, page, locator):
    return _ref('stage5_gray_' + id, 'Gray / Lewis, Anatomy of the Human Body (1918)',
                GRAY_URL + '#page=' + str(page), f'PDF p. {page}: ' + locator,
                'gray_lewis_1918', year=1918)


def _cbs(id, page, locator):
    return _ref('stage5_cbs_' + id,
                'Yogesh Sontakke. Textbook of Human Anatomy: Head, Neck and Face',
                CBS_URL + '#page=' + str(page), f'Printed / PDF p. {page}: ' + locator,
                'sontakke_cbs', 'publisher_preview', isbn='9789354661792')


TEMPORAL = (
    _gray('temporal', 155, 'The Temporal Fossa: anterior wall, lateral boundary and floor'),
    _cbs('temporal', 11, 'Temporal fossa: Boundaries and Floor'),
)
PPF = (
    _gray('ppf', 157, 'The Pterygopalatine Fossa: bony boundaries'),
    _ref('stage5_cappello_ppf', 'Cappello ZJ, Arbor TC, Potts KL. Anatomy, Pterygopalatine Fossa',
         'https://www.ncbi.nlm.nih.gov/sites/books/NBK513269/',
         'Structure and Function, first paragraph: bone membership only',
         'cappello_arbor_potts', nbk='NBK513269', updated='2024-04-20'),
)
PTERYGO_MAXILLARY = (
    _gray('pmf', 157, 'Pterygomaxillary fissure: first sentence'),
    _ref('stage5_sneha_pmf',
         'Sneha JM, Goshi RC, Vidya CS, Doddawad VG. Morphometric Analysis of Pterygomaxillary Fissure in Dry Skulls and its Clinical Significance During Head and Neck Injury',
         'https://pubmed.ncbi.nlm.nih.gov/40065930/',
         'Abstract, first sentence: maxilla and sphenoid pterygoid process',
         'sneha_2025', 'abstract', pmid='40065930', doi='10.1007/s12070-024-05240-3',
         printYear=2025, electronicDate='2024-11-27'),
)
ANTERIOR_FOSSA = (
    _gray('acf', 163, 'Anterior Fossa: first paragraph'),
    _ref('stage5_kasai_acf', 'Kasai E, Kondo S, Kasai K. Morphological variation in the anterior cranial fossa',
         'https://pubmed.ncbi.nlm.nih.gov/31049216/',
         'Abstract, first sentence and results: three bones, variable interfaces',
         'kasai_2019', 'abstract', pmid='31049216', doi='10.1002/cre2.163',
         printYear=2019, electronicDate='2019-01-31'),
)
PALATOVAGINAL = (
    _cbs('pvc', 15, 'Palatovaginal canal: only bony boundaries'),
    _ref('stage5_herzallah_pvc',
         'Herzallah IR, Amin S, El-Hariri MA, Casiano RR. Endoscopic identification of the pharyngeal (palatovaginal) canal: an overlooked area',
         'https://pubmed.ncbi.nlm.nih.gov/24083128/',
         'Abstract, Objective: palatine sphenoidal process and sphenoid vaginal process; Results: variable bony wall',
         'herzallah_2012', 'abstract', pmid='24083128', doi='10.1055/s-0032-1322798', year=2012),
)
VOMEROVAGINAL = (
    _cbs('vvc', 15, 'Vomerovaginal canal: only bony boundaries, not contents'),
    _ref('stage5_academie_vvc', 'Dictionnaire médical de l’Académie de Médecine, édition 2015',
         'https://www.academie-medecine.fr/le-dictionnaire/index.php?q=canal+vom%C3%A9ro+rostral',
         'Entry canal voméro-vaginal, first definition: ala of vomer and vaginal process',
         'academie_medecine', year=2015),
)
ORBITAL_RIM = (
    _gray('rim', 162, 'The Orbits: paragraph beginning The base of the orbit'),
    _cbs('rim', 7, 'Orbital openings: four margins'),
)
# Export for the existing maxillary contribution's partOf metadata. Consumers
# may append these references without altering the independent catalogue tuple.
RIM_REFS = deepcopy(list(ORBITAL_RIM))
LACRIMAL_FOSSA = (
    _gray('lacrimal', 122, 'The Frontal Process: last part; PDF p. 126: lacrimal orbital surface'),
    _ref('stage5_ullrich_fossa', 'Ullrich K, Malhotra R, Patel BC. Dacryocystorhinostomy',
         'https://www.ncbi.nlm.nih.gov/sites/books/NBK557851/',
         'Anatomy and Physiology: Lacrimal Sac and Duct; Endoscopic Nasal Anatomy, first paragraph',
         'ullrich_malhotra_patel', nbk='NBK557851', updated='2023-08-07'),
)
PIRIFORM = (
    _gray('piriform', 170, 'The Anterior Nasal Aperture: bony boundaries'),
    _cbs('piriform', 7, 'Bony nasal aperture: Boundaries'),
)
CHOANA = (
    _gray('choana', 170, 'Paragraph following The Anterior Nasal Aperture: choanae'),
    _ref('stage5_sobiesk_choana', 'Sobiesk JL, Munakomi S. Anatomy, Head and Neck, Nasal Cavity',
         'https://www.ncbi.nlm.nih.gov/sites/books/NBK544232/?report=printable',
         'Structure and Function > Choanae: four boundary bullets',
         'sobiesk_munakomi', nbk='NBK544232', updated='2023-07-24'),
)
TEMPOROZYGOMATIC = (
    _ref('stage5_ozen_suture',
         'Özen KE, Yeşil HK, Malas MA. Morphometric and morphological evaluation of temporozygomatic suture anatomy in dry adult human skulls',
         'https://pubmed.ncbi.nlm.nih.gov/36374372/',
         'Abstract: temporozygomatic suture in adult skulls; no specimen dimensions transferred',
         'ozen_yesil_malas', 'abstract', pmid='36374372', doi='10.1007/s12565-022-00694-3',
         printYear=2023, electronicDate='2022-11-14', evidenceChecked='2026-10-15',
         evidenceRecord='research/stage4-2026-10-15/pubmed-zygomaticotemporal.json'),
    _ref('stage5_yu_suture', 'Yu M, Wang SM. Anatomy, Head and Neck, Zygomatic',
         'https://www.ncbi.nlm.nih.gov/books/NBK544257/',
         'Structure and Function: temporal process of zygomatic and zygomatic process of temporal at the arch',
         'yu_wang', nbk='NBK544257', updated='2023-06-05', evidenceChecked='2026-10-15'),
)
SUTURE_NOMENCLATURE = dict(
    id='stage5_ifaa_temporozygomatic', title='IFAA TA98, section A03.1.02',
    url='https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/TA98%20EN/03.1.02%20TA98%20EN.htm',
    locator='A03.1.02.024: Sutura temporozygomatica / Temporozygomatic suture',
    kind='nomenclature', checked=CHECKED,
)


class Definition(NamedTuple):
    number: int
    bones: tuple[str, ...]
    paired: bool
    role: str
    geometryKind: str
    refs: tuple[dict, ...]
    note: str = ''


# Explicit sides: a pair can involve the same unpaired bones, e.g. number 65.
DEFINITIONS = (
    Definition(22, ('frontal', 'parietal_{side}', 'temporal_{side}', 'sphenoid', 'zygomatic_{side}'), True, 'boundaryContribution', 'area', TEMPORAL,
               'Связи описывают всю область. Gray включает скуловую в описание дна, CBS относит её к передней стенке; разное разграничение частей сохранено. Этот список нельзя считать перечнем только костей дна.'),
    Definition(25, ('sphenoid', 'maxilla_{side}', 'palatine_{side}'), True, 'boundaryContribution', 'space', PPF),
    Definition(26, ('maxilla_{side}', 'sphenoid'), True, 'boundaryContribution', 'space', PTERYGO_MAXILLARY),
    Definition(48, ('frontal', 'ethmoid', 'sphenoid'), False, 'component', 'area', ANTERIOR_FOSSA,
               'Индивидуальные границы между тремя костями вариабельны.'),
    Definition(64, ('palatine_{side}', 'sphenoid'), True, 'boundaryContribution', 'volume', PALATOVAGINAL,
               'Наличие и ход просвета на этом образце не установлены; не объединять с сошниково-влагалищным каналом.'),
    Definition(65, ('vomer', 'sphenoid'), True, 'boundaryContribution', 'volume', VOMEROVAGINAL,
               'Правая и левая стороны учитываются отдельно при одном наборе непарных костей; не объединять с нёбно-влагалищным каналом.'),
    Definition(69, ('frontal', 'maxilla_{side}', 'zygomatic_{side}'), True, 'boundaryContribution', 'space', ORBITAL_RIM,
               'Вход является отверстием, а не всей глазницей или её краем A02.1.00.070.'),
    Definition(70, ('frontal', 'maxilla_{side}', 'zygomatic_{side}'), True, 'boundaryContribution', 'line', ORBITAL_RIM),
    Definition(72, ('maxilla_{side}', 'zygomatic_{side}'), True, 'boundaryContribution', 'line', ORBITAL_RIM,
               'Общий подглазничный край включает обе кости; существующая запись верхней челюсти A02.1.12.006 обозначает её локальный вклад. Её точка не является полным общим краем.'),
    Definition(73, ('frontal', 'zygomatic_{side}'), True, 'boundaryContribution', 'line', ORBITAL_RIM,
               'Это латеральный край входа, не латеральная стенка глазницы.'),
    Definition(74, ('frontal', 'maxilla_{side}'), True, 'boundaryContribution', 'line', ORBITAL_RIM,
               'Это медиальный край входа, не медиальная стенка глазницы.'),
    Definition(82, ('maxilla_{side}', 'lacrimal_{side}'), True, 'component', 'area', LACRIMAL_FOSSA,
               'Ямка слёзного мешка отличается от локальных слёзных борозд двух костей; доли костных вкладов вариабельны.'),
    Definition(88, ('nasal_right', 'nasal_left', 'maxilla_right', 'maxilla_left'), False, 'boundaryContribution', 'space', PIRIFORM),
    Definition(96, ('sphenoid', 'vomer', 'palatine_{side}'), True, 'boundaryContribution', 'space', CHOANA,
               'Gray дополнительно указывает крыло сошника в верхней границе; краткое описание Bookshelf называет там клиновидную кость. Общий набор костей подтверждён, точное распределение границы по участкам не заявляется.'),
)

# Only the reviewed membership is asserted here; the richer catalogue remains
# accessible by concept. Evidence for a relation does not inherit every fact in it.
DESCRIPTIONS = {
    22: 'Височная ямка связана с лобной, теменной, височной, клиновидной и скуловой костями; источники по-разному разграничивают дно и переднюю стенку.',
    25: 'Костные границы крыловидно-нёбной ямки образованы верхней челюстью, нёбной и клиновидной костями.',
    26: 'Крыловидно-верхнечелюстная щель находится между верхней челюстью и крыловидным отростком клиновидной кости.',
    48: 'Передняя черепная ямка образована участками лобной, решётчатой и клиновидной костей.',
    64: 'Нёбно-влагалищный канал расположен между клиновидным отростком нёбной кости и влагалищным отростком клиновидной кости.',
    65: 'Сошниково-влагалищный канал расположен между крылом сошника и влагалищным отростком клиновидной кости.',
    69: 'Вход в глазницу ограничен лобной и скуловой костями и верхней челюстью; он отличается от всей полости глазницы.',
    70: 'Общий глазничный край образован лобной и скуловой костями и верхней челюстью.',
    72: 'Общий подглазничный край образован верхней челюстью и скуловой костью.',
    73: 'Латеральный край входа в глазницу образован лобной и скуловой костями.',
    74: 'Медиальный край входа в глазницу образован лобной костью и верхней челюстью.',
    82: 'В образовании ямки слёзного мешка участвуют верхняя челюсть и слёзная кость.',
    88: 'Грушевидную апертуру ограничивают обе носовые кости и обе верхние челюсти.',
    96: 'Костные границы хоаны связаны с клиновидной костью, сошником и нёбной костью своей стороны.',
}

MODEL_LIMIT = ('Связи отражают справочную анатомию. Координаты, полный контур, границы и размеры '
               'этой структуры на данной 3D-модели не подтверждены; новая точка или геометрия не создавались.')


def _record(id, code, lat, ru, description, bones, side, role, kind, refs, note, **extra):
    sources = deepcopy(list(refs))
    if side:
        ru += ' · ' + ('справа' if side == 'right' else 'слева')
    return dict(id=id, c=code, b=bones[0], t='ta', lat=lat, ru=ru, x=description,
                side=side, m=[], g='Общие образования черепа', catalogueBones=[], anchors=[],
                relationScope='reference_anatomy', geometryKind=kind, modelNote=MODEL_LIMIT + (' ' + note if note else ''),
                refs=sources, relations=[dict(bone=b, role=role, refs=[r['id'] for r in sources]) for b in bones],
                **extra)


def additional_instances(terminology):
    """Yield independent records with source relationships and no p/n fields."""
    for definition in DEFINITIONS:
        number = definition.number
        code = f'A02.1.00.{number:03}'
        for side in ('right', 'left') if definition.paired else (None,):
            bones = [bone.format(side=side) for bone in definition.bones]
            ru = TERMS[number]['ru'] + (' глазницы' if number in (73, 74) else '')
            yield _record(f'shared_skull_{number:03}' + ('_' + side if side else ''),
                          code, terminology[code], ru, DESCRIPTIONS[number],
                          bones, side, definition.role, definition.geometryKind, definition.refs,
                          definition.note, concept=f'skull-whole-{number:03}')
    for side in ('right', 'left'):
        yield _record('shared_temporozygomatic_suture_' + side,
                      'A03.1.02.024', 'sutura temporozygomatica', 'Скуловисочный шов',
                      'Шов между височным отростком скуловой кости и скуловым отростком височной кости своей стороны.',
                      ['temporal_' + side, 'zygomatic_' + side], side,
                      'boundaryContribution', 'line', TEMPOROZYGOMATIC,
                      'Шов не тождественен всей скуловой дуге или скуловисочному отверстию A02.1.14.011.',
                      concept='temporozygomatic-suture', educationAvailable=False,
                      nomenclatureRefs=[deepcopy(SUTURE_NOMENCLATURE)])
