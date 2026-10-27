"""Abdominal muscles (FUT-003, ABD-MUSCLES): BodyParts3D 3.0 source names and teaching cards.

Each side uses its own source file (no mirroring). Nomenclature: IFAA TA98 04.5.01 and the printed
Russian edition (Kolesnikov 2003, pp. 48-49). Every card field cites two independent sources (Kenhub,
UAMS, Loyola, Gray 1918, IMAIOS, StatPearls); disagreements between them stay in the card note.
Geometry and anatomy are separate assertions; no attachment coordinates are supplied.
"""
from copy import deepcopy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from head_terms import BOOK_URL

_tsv = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bp', 'all_named.tsv')
NAME2ID = dict(line.rstrip('\n').split('\t')[::-1] for line in open(_tsv, encoding='utf-8'))

# key -> BodyParts3D concept name without the side token
SOURCE_NAMES = {
    'abdomen_rectus_abdominis': 'rectus abdominis',
    'abdomen_pyramidalis': 'pyramidalis',
    'abdomen_obliquus_externus_abdominis': 'external oblique',
    'abdomen_obliquus_internus_abdominis': 'internal oblique',
    'abdomen_transversus_abdominis': 'transversus abdominis',
    'abdomen_quadratus_lumborum': 'quadratus lumborum',
}
MUSCLES = {f'{key}_{side}': [(NAME2ID[f'{side} {name}'], None)]
           for key, name in SOURCE_NAMES.items() for side in ('right', 'left')}
# Same face budget rule as the other BodyParts3D muscles of the atlas (scripts/build_glb.py default).
MUSCLE_BUILD = (0.13, 1500, 14000)


def target_faces(n, ratio=MUSCLE_BUILD[0], lo=MUSCLE_BUILD[1], hi=MUSCLE_BUILD[2]):
    return int(min(max(n * ratio, min(n, lo)), hi))


def published_mesh(vertices_mm, faces):
    """The decimated BP3D mesh exactly as it is published: [bp.x,bp.z,-bp.y]/1000, exact vertex merge,
    minus zero-volume two-triangle flaps left by collapse decimation (source specks of <=0.1 mm collapse
    into them) and minus vertices that no face uses. Returns (trimesh, removed flap triangles).
    A flap is a pair of triangles over the same three vertices with opposite winding: it covers no area
    and cancels the normals of its vertices, also when those vertices belong to other faces."""
    import numpy as np
    import trimesh
    R = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], dtype=float)
    mesh = trimesh.Trimesh(vertices=np.asarray(vertices_mm) @ R.T / 1000.0, faces=faces, process=True)
    f = np.asarray(mesh.faces)
    order = np.argsort(f, axis=1)
    key = np.take_along_axis(f, order, axis=1)
    # Winding parity: a cyclic rotation of the sorted order is even, a reflection is odd.
    parity = np.array([tuple(o) in ((0, 1, 2), (1, 2, 0), (2, 0, 1)) for o in order])
    _, inverse, counts = np.unique(key, axis=0, return_inverse=True, return_counts=True)
    inverse = inverse.ravel()
    flap = np.zeros(len(f), dtype=bool)
    for group in np.flatnonzero(counts == 2):
        a, b = np.flatnonzero(inverse == group)
        flap[[a, b]] = parity[a] != parity[b]
    mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=f[~flap], process=False)
    mesh.remove_unreferenced_vertices()
    return mesh, int(flap.sum())


KH = 'https://www.kenhub.com/en/library/anatomy/'
UAMS = ('https://medicine.uams.edu/neuroscience/education/medical-school-courses/human-structure-module/'
        'anatomy-tables/muscle-tables/muscles-of-the-abdominal-region/')
LOYOLA = 'https://www.stritch.luc.edu/lumen/meded/grossanatomy/homepage/muscletables/AbdomenMuscleTable.pdf'
GRAY = 'https://www.wikimd.org/wiki/The_Muscles_and_Fasci%C3%A6_of_the_Abdomen'
STAT = 'https://www.ncbi.nlm.nih.gov/sites/books/NBK525975/'
IMAIOS = 'https://www.imaios.com/en/e-anatomy/anatomical-structures/'
IMAIOS_EO = IMAIOS + 'external-abdominal-oblique-muscle-1541084052'
IMAIOS_IO = IMAIOS + 'internal-abdominal-oblique-muscle-1541084808'
IFAA = 'https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/TA98%20EN/04.5.01%20TA98%20EN.htm'
PAGE = {'abdomen_rectus_abdominis': 'rectus-abdominis-muscle', 'abdomen_pyramidalis': 'pyramidalis-muscle',
        'abdomen_obliquus_externus_abdominis': 'external-abdominal-oblique-muscle',
        'abdomen_obliquus_internus_abdominis': 'internal-abdominal-oblique-muscle',
        'abdomen_transversus_abdominis': 'transversus-abdominis-muscle',
        'abdomen_quadratus_lumborum': 'quadratus-lumborum-muscle'}
TITLES = {UAMS: 'UAMS: учебная таблица мышц живота', LOYOLA: 'Loyola University Chicago: таблица мышц живота, 2015',
          GRAY: 'Gray, 1918: The Muscles and Fasciæ of the Abdomen', STAT: 'StatPearls: Anterolateral Abdominal Wall, 2023',
          IMAIOS_EO: 'IMAIOS e-Anatomy: наружная косая мышца живота', IMAIOS_IO: 'IMAIOS e-Anatomy: внутренняя косая мышца живота',
          IFAA: 'TA98: номенклатура', BOOK_URL: 'Колесников, 2003'}
GROUPS = [dict(id='abdomen_anterolateral', title='Мышцы переднебоковой стенки живота', region='abdomen', sec='trunk'),
          dict(id='abdomen_posterior', title='Мышцы задней стенки живота', region='abdomen', sec='trunk')]
FEATURE_NOTE = 'Описание строения; отдельной сетки и координат у этого образования нет.'
MUSCLE_TEMPLATES, EVIDENCE = {}, {}


def ref(url, locator):
    return dict(url=url, title=TITLES.get(url, 'Kenhub: открытая статья' if url.startswith(KH) else url), locator=locator)


def kh(key, locator):
    return ref(KH + PAGE[key], locator)


def feature(code, ru, lat, x, refs):
    return dict(code=code, ru=ru, lat=lat, x=x, refs=refs, noModel=True, modelNote=FEATURE_NOTE,
                evidenceStatus='checked_two_sources', geometryValidated=False)


def add(key, ru, lat, code, fields, *, group, depth, layer, view, note, noteRefs, modelNote='', features=None):
    m = dict(ru=ru, lat=lat, code=code, g=group, d=depth, L=layer, v=view, note=note, noteRefs=noteRefs,
             fieldStatus={f: 'checked_two_sources' for f in fields}, noModel=False)
    for f, (text, refs) in fields.items():
        assert len({r['url'] for r in refs}) >= 2, (key, f)
        m[f] = text
    m['fieldRefs'] = {f: refs for f, (_, refs) in fields.items()}
    if modelNote:
        m['modelNote'] = modelNote
    if features:
        m['features'] = features
    MUSCLE_TEMPLATES[key] = m


INTERCOSTAL = 'Нижние межрёберные нервы (T7–T11) и подрёберный нерв (T12).'
FLAT_NERVES = 'Нижние межрёберные нервы (T7–T11), подрёберный нерв (T12), подвздошно-подчревный и подвздошно-паховый нервы (L1).'
FLAT_ARTERIES = ('Нижние задние межрёберные и подрёберная артерии, верхняя и нижняя надчревные артерии, глубокая артерия, '
                 'огибающая подвздошную кость, и поясничные артерии.')

k = 'abdomen_rectus_abdominis'
add(k, 'Прямая мышца живота', 'm. rectus abdominis', 'A04.5.01.001', {
    'o': ('Лобковый гребень и лобковый симфиз.', [kh(k, 'Key facts: Origin; Origin and insertion'), ref(UAMS, 'rectus abdominis, Origin')]),
    'i': ('Мечевидный отросток и хрящи V–VII рёбер.', [kh(k, 'Key facts: Insertion'), ref(UAMS, 'rectus abdominis, Insertion')]),
    'a': ('Сгибает туловище, сдавливает органы брюшной полости, участвует в выдохе.',
          [kh(k, 'Key facts: Function'), ref(LOYOLA, 'С. 1, Rectus abdominis, Main actions'), ref(STAT, 'Structure and Function: forceful expiration')]),
    'n': (INTERCOSTAL, [kh(k, 'Key facts: Innervation'), ref(UAMS, 'rectus abdominis, Innervation')]),
    's': ('Верхняя и нижняя надчревные артерии (aa. epigastricae superior et inferior); ветви нижних задних межрёберных и подрёберной артерий.',
          [kh(k, 'Key facts: Blood supply'), ref(UAMS, 'rectus abdominis, Artery')])},
    group='abdomen_anterolateral', depth=3, layer='Во влагалище прямой мышцы живота', view='ant',
    note=('Мышцу пересекают сухожильные перемычки — обычно три; ниже пупка иногда бывают дополнительные неполные. '
          'Мышца лежит во влагалище, образованном апоневрозами наружной и внутренней косых и поперечной мышц. '
          'Gray описывает два сухожилия начала: латеральное — к лобковому гребню, медиальное — переплетается с противоположным '
          'и со связками перед симфизом. Самые латеральные волокна прикрепляются к переднему концу V ребра; по Kenhub этот пучок '
          'иногда достигает III–IV рёбер или отсутствует.'),
    noteRefs=[ref(GRAY, 'Rectus abdominis: two tendons; tendinous inscriptions'), kh(k, 'Structure; Origin and insertion'),
              ref(UAMS, 'rectus abdominis, Notes')],
    modelNote=('В исходной сетке BodyParts3D есть отдельный небольшой фрагмент (около 1 % граней) у срединной линии над симфизом; '
               'он сохранён как в источнике, его соответствие определённому образованию не установлено. '
               'Сухожильные перемычки и влагалище отдельными сетками не показаны.'),
    features=[
        feature('A04.5.01.002', 'Сухожильные перемычки', 'intersectiones tendineae',
                'Поперечные фиброзные полосы, сращённые с передней стенкой влагалища: обычно на уровне пупка, у конца мечевидного '
                'отростка и посередине между ними.',
                [ref(GRAY, 'Rectus abdominis: tendinous inscriptions'), kh(k, 'Structure: three tendinous intersections')]),
        feature('A04.5.01.003', 'Влагалище прямой мышцы живота', 'vagina musculi recti abdominis',
                'Футляр из апоневрозов наружной и внутренней косых и поперечной мышц; содержит прямую и пирамидальную мышцы.',
                [ref(UAMS, 'rectus abdominis, Notes'), ref(KH + PAGE['abdomen_pyramidalis'], 'Relations: rectus sheath'),
                 ref(GRAY, 'Sheath of the Rectus')]),
        feature('A04.5.01.006', 'Дугообразная линия', 'linea arcuata',
                'Нижний край задней стенки влагалища, немного ниже пупка; ниже неё апоневрозы плоских мышц проходят только впереди прямой мышцы.',
                [ref(STAT, 'Muscles: semicircular line of Douglas'), ref(GRAY, 'Transversus abdominis: upper three-fourths behind, lower fourth in front of the Rectus')]),
        feature('A04.5.01.022', 'Белая линия', 'linea alba',
                'Сухожильный шов по срединной линии от мечевидного отростка до лобкового симфиза, между медиальными краями прямых мышц; '
                'образован переплетением апоневрозов косых и поперечных мышц.',
                [ref(GRAY, 'The Linea Alba'), kh(k, 'Structure: linea alba')])])

k = 'abdomen_pyramidalis'
add(k, 'Пирамидальная мышца', 'm. pyramidalis', 'A04.5.01.007', {
    'o': ('Лобковая кость у лобкового гребня и лобкового симфиза, впереди начала прямой мышцы.',
          [kh(k, 'Key facts: Origin; Origin and insertion'), ref(UAMS, 'pyramidalis, Origin')]),
    'i': ('Белая линия, примерно посередине между пупком и лобковой костью.',
          [kh(k, 'Origin and insertion: halfway between umbilicus and pubis'), ref(GRAY, 'Pyramidalis')]),
    'a': ('Натягивает белую линию.', [kh(k, 'Key facts: Action'), ref(LOYOLA, 'С. 1, Pyramidalis, Main actions')]),
    'n': ('Подрёберный нерв (T12).', [kh(k, 'Key facts: Innervation'), ref(UAMS, 'pyramidalis, Innervation')]),
    's': ('Нижняя надчревная артерия (a. epigastrica inferior).', [kh(k, 'Key facts: Blood supply'), ref(LOYOLA, 'С. 1, Pyramidalis, Blood supply')])},
    group='abdomen_anterolateral', depth=3, layer='Во влагалище прямой мышцы, впереди её нижней части', view='ant',
    note=('Непостоянная мышца: может отсутствовать с одной или обеих сторон, бывает удвоенной или асимметричной. '
          'Иннервацию Kenhub, UAMS и Gray связывают с подрёберным нервом (T12), Loyola — с подвздошно-подчревным нервом.'),
    noteRefs=[ref(GRAY, 'Pyramidalis: may be wanting on one or both sides'), ref(UAMS, 'pyramidalis, Notes'),
              ref(LOYOLA, 'С. 1, Pyramidalis, Innervation'), ref(STAT, 'Physiologic Variants')],
    modelNote='Исходная модель BodyParts3D содержит мышцу с обеих сторон; это один вариант строения, а не частота встречаемости.')

k = 'abdomen_obliquus_externus_abdominis'
add(k, 'Наружная косая мышца живота', 'm. obliquus externus abdominis', 'A04.5.01.008', {
    'o': ('Наружные поверхности V–XII рёбер восемью зубцами.',
          [kh(k, 'Key facts: Origin; Origin and insertion'), ref(GRAY, 'Obliquus externus abdominis: eight fleshy digitations')]),
    'i': ('Апоневрозом — к белой линии и лобковому бугорку; задние пучки — к передней половине подвздошного гребня.',
          [kh(k, 'Key facts: Insertion'), ref(UAMS, 'external abdominal oblique, Insertion')]),
    'a': ('При двустороннем сокращении сгибает туловище и сдавливает органы брюшной полости; при одностороннем — наклоняет '
          'туловище в свою сторону и поворачивает его в противоположную.',
          [kh(k, 'Key facts: Action; Function'), ref(IMAIOS_EO, 'Actions / Functions')]),
    'n': (INTERCOSTAL, [kh(k, 'Key facts: Innervation'), ref(UAMS, 'external abdominal oblique, Innervation')]),
    's': ('Нижние задние межрёберные и подрёберная артерии, глубокая артерия, огибающая подвздошную кость (a. circumflexa ilium profunda).',
          [kh(k, 'Key facts: Blood supply'), ref(UAMS, 'external abdominal oblique, Artery')])},
    group='abdomen_anterolateral', depth=1, layer='Поверхностный слой', view='antlat',
    note=('Зубцы начала чередуются с зубцами передней зубчатой и широчайшей мышц спины. Gray уточняет прикрепление к наружной губе '
          'подвздошного гребня. UAMS добавляет к иннервации подвздошно-подчревный и подвздошно-паховый нервы; Kenhub относит '
          'подвздошно-подчревный нерв к чувствительной иннервации. Перечни артерий различаются: UAMS даёт широкий список, '
          'Loyola — верхнюю и нижнюю надчревные артерии.'),
    noteRefs=[kh(k, 'Origin and insertion: interdigitation with serratus anterior and latissimus dorsi'),
              ref(GRAY, 'Obliquus externus abdominis'), ref(UAMS, 'external abdominal oblique, Innervation; Artery'),
              ref(LOYOLA, 'С. 1, External oblique, Blood supply')],
    modelNote=('Исходная сетка BodyParts3D продолжается медиально до белой линии и местами лежит впереди прямой мышцы '
               '(апоневротическая часть); границу мышечной и сухожильной частей модель не различает.'),
    features=[feature('A04.5.01.009', 'Паховая связка', 'lig. inguinale',
                      'Нижний утолщённый край апоневроза между передней верхней подвздошной остью и лобковым бугорком. '
                      'Отдельная модель связки — в разделе «Поясница, таз и нижняя конечность».',
                      [ref(UAMS, 'external abdominal oblique, Notes'), kh(k, 'Origin and insertion: inguinal ligament')])])

k = 'abdomen_obliquus_internus_abdominis'
add(k, 'Внутренняя косая мышца живота', 'm. obliquus internus abdominis', 'A04.5.01.017', {
    'o': ('Пояснично-грудная фасция, передние две трети подвздошного гребня и латеральная часть паховой связки.',
          [ref(UAMS, 'internal abdominal oblique, Origin'), ref(IMAIOS_IO, 'Origin')]),
    'i': ('Нижние края X–XII рёбер, белая линия; нижние пучки вместе с поперечной мышцей (паховый серп) — лобковый гребень и гребенчатая линия.',
          [kh(k, 'Key facts: Insertion'), ref(IMAIOS_IO, 'Insertion')]),
    'a': ('При двустороннем сокращении сгибает туловище, сдавливает органы брюшной полости, участвует в выдохе; при одностороннем — '
          'наклоняет и поворачивает туловище в свою сторону.',
          [kh(k, 'Key facts: Action; Function'), ref(IMAIOS_IO, 'Actions / Functions')]),
    'n': (FLAT_NERVES, [kh(k, 'Key facts: Innervation'), ref(UAMS, 'internal abdominal oblique, Innervation')]),
    's': (FLAT_ARTERIES, [kh(k, 'Key facts: Blood supply'), ref(UAMS, 'internal abdominal oblique, Artery')])},
    group='abdomen_anterolateral', depth=2, layer='Средний слой', view='antlat',
    note=('Протяжённость начала от паховой связки описывают по-разному: Gray, Loyola и IMAIOS — латеральная половина, UAMS — латеральные '
          'две трети, Kenhub — подвздошно-гребенчатая дуга. Число рёбер прикрепления: Kenhub, Loyola и IMAIOS — X–XII, UAMS — три или '
          'четыре нижних ребра. Апоневроз выше дугообразной линии расщепляется и охватывает прямую мышцу спереди и сзади.'),
    noteRefs=[ref(GRAY, 'Obliquus internus abdominis'), ref(LOYOLA, 'С. 1, Internal oblique, Proximal attachment'),
              ref(UAMS, 'internal abdominal oblique, Origin; Insertion'), kh(k, 'Key facts: Origin'),
              ref(IMAIOS_IO, 'Role in the Rectus Sheath'), ref(STAT, 'Muscles: internal oblique')],
    modelNote='Исходная сетка BodyParts3D включает апоневротическую часть, охватывающую прямую мышцу; границы частей не размечены.',
    features=[
        feature('A04.5.01.018', 'Мышца, поднимающая яичко (у мужчин)', 'm. cremaster',
                'Петли мышечных пучков вокруг семенного канатика и яичка — продолжение нижних пучков внутренней косой мышцы; '
                'поднимает яичко. Иннервация — половая ветвь бедренно-полового нерва.',
                [ref(UAMS, 'cremaster; internal abdominal oblique, Notes'), ref(GRAY, 'The Cremaster; Nerves')]),
        feature('A04.5.01.020', 'Паховый серп; соединительное сухожилие', 'falx inguinalis; tendo conjunctivus',
                'Общее сухожилие нижних пучков внутренней косой и поперечной мышц; прикрепляется к лобковому гребню и гребенчатой линии.',
                [kh(k, 'Origin and insertion: conjoint tendon'), ref(GRAY, 'Obliquus internus abdominis: inguinal aponeurotic falx')])])

k = 'abdomen_transversus_abdominis'
add(k, 'Поперечная мышца живота', 'm. transversus abdominis', 'A04.5.01.019', {
    'o': ('Внутренние поверхности хрящей VII–XII рёбер, пояснично-грудная фасция, передняя часть подвздошного гребня и латеральная треть паховой связки.',
          [ref(LOYOLA, 'С. 1, Transversus abdominis, Proximal attachment'), ref(GRAY, 'Transversus abdominis')]),
    'i': ('Белая линия (апоневроз вместе с апоневрозом внутренней косой мышцы); нижние пучки через паховый серп — лобковый гребень и гребенчатая линия.',
          [kh(k, 'Key facts: Insertion'), ref(UAMS, 'transversus abdominis, Insertion')]),
    'a': ('Сдавливает органы брюшной полости, участвует в выдохе.',
          [kh(k, 'Key facts: Action'), ref(UAMS, 'transversus abdominis, Action'), ref(STAT, 'Structure and Function: forceful expiration')]),
    'n': (FLAT_NERVES, [kh(k, 'Key facts: Innervation'), ref(UAMS, 'transversus abdominis, Innervation')]),
    's': (FLAT_ARTERIES, [kh(k, 'Key facts: Blood supply'), ref(UAMS, 'transversus abdominis, Artery')])},
    group='abdomen_anterolateral', depth=3, layer='Глубокий слой', view='antlat',
    note=('Протяжённость начала от подвздошного гребня: Kenhub — передние две трети, UAMS и Gray — передние три четверти (Gray — '
          'внутренняя губа). Рёберные зубцы чередуются с зубцами диафрагмы. Апоневроз в верхних трёх четвертях проходит позади прямой '
          'мышцы, в нижней четверти — впереди неё.'),
    noteRefs=[kh(k, 'Key facts: Origin'), ref(UAMS, 'transversus abdominis, Origin'), ref(GRAY, 'Transversus abdominis'),
              ref(STAT, 'Muscles: transversus abdominis')],
    modelNote=('В исходной сетке BodyParts3D нижний край заходит в тазовую кость атласа до 6 мм у подвздошного гребня и у лобковой кости '
               '(около 1,6 % вершин); у VII–XII рёбер и рёберных хрящей заходят единичные вершины. Это свойство источника: '
               'сетка не деформировалась.'),
    features=[feature('A04.5.01.020', 'Паховый серп; соединительное сухожилие', 'falx inguinalis; tendo conjunctivus',
                      'Общее сухожилие нижних пучков поперечной и внутренней косой мышц; прикрепляется к лобковому гребню и гребенчатой линии.',
                      [kh(k, 'Origin and insertion: conjoint tendon'), ref(GRAY, 'Transversus abdominis: inguinal aponeurotic falx')])])

k = 'abdomen_quadratus_lumborum'
add(k, 'Квадратная мышца поясницы', 'm. quadratus lumborum', 'A04.5.01.027', {
    'o': ('Подвздошно-поясничная связка и прилежащая задняя часть подвздошного гребня.',
          [kh(k, 'Key facts: Origin'), ref(UAMS, 'quadratus lumborum, Origin')]),
    'i': ('Нижний край XII ребра (примерно медиальная половина) и верхушки поперечных отростков L1–L4.',
          [kh(k, 'Key facts: Insertion'), ref(GRAY, 'Quadratus lumborum'), ref(LOYOLA, 'С. 1, Quadratus lumborum, Proximal attachment')]),
    'a': ('Фиксирует XII ребро; при одностороннем сокращении наклоняет туловище в свою сторону, при двустороннем — разгибает поясничный отдел позвоночника.',
          [kh(k, 'Key facts: Function; Function'), ref(LOYOLA, 'С. 1, Quadratus lumborum, Main actions'), ref(UAMS, 'quadratus lumborum, Action')]),
    'n': ('Подрёберный нерв (T12) и передние ветви спинномозговых нервов L1–L4.',
          [kh(k, 'Key facts: Innervation'), ref(UAMS, 'quadratus lumborum, Innervation')]),
    's': ('Поясничные и подрёберная артерии; подвздошно-поясничная артерия.',
          [kh(k, 'Key facts: Blood supply'), ref(UAMS, 'quadratus lumborum, Artery'), ref(LOYOLA, 'С. 1, Quadratus lumborum, Blood supply')])},
    group='abdomen_posterior', depth=3, layer='Задняя стенка живота', view='post',
    note=('Loyola называет концы в обратном порядке: XII ребро и поперечные отростки — проксимальное прикрепление, подвздошный гребень — '
          'дистальное. Роль в дыхании описывают по-разному: Gray и Loyola — фиксация XII ребра при вдохе (опора для диафрагмы); '
          'Kenhub в ключевых фактах — при вдохе, в разделе о функции — поддержка выдоха. При двустороннем сокращении Gray допускает '
          'сгибание туловища, Kenhub и Loyola — разгибание. Иннервация по Gray — T12, L1–L2. Иногда впереди лежит добавочная часть от '
          'поперечных отростков нижних поясничных позвонков к XII ребру.'),
    noteRefs=[ref(LOYOLA, 'С. 1, Quadratus lumborum'), ref(GRAY, 'Quadratus lumborum; Actions; Nerve Supply'),
              kh(k, 'Key facts; Function')],
    modelNote='Ориентиры прикреплений на рёбрах, позвонках и тазовой кости не размечены: поясничные позвонки и таз показаны в этом разделе только как контекст.')

GROUP_NOTE = ('Gray и Loyola относят к мышцам задней стенки живота также большую и малую поясничные и подвздошную мышцы; '
              'в атласе подвздошно-поясничная мышца стоит в мышцах таза (раздел «Поясница, таз и нижняя конечность»).')


def finalize():
    for key, m in MUSCLE_TEMPLATES.items():
        refs = [r for rr in m['fieldRefs'].values() for r in rr] + m['noteRefs']
        refs += [r for f in m.get('features', []) for r in f['refs']]
        refs += [dict(title=TITLES[IFAA], url=IFAA, locator=m['code']), dict(title=TITLES[BOOK_URL], url=BOOK_URL, locator='С. 48–49; ' + m['code'])]
        m['refs'] = list({(r['url'], r['locator']): r for r in refs}.values())
        EVIDENCE[key] = dict(code=m['code'], fields=m['fieldRefs'], fieldStatus=m['fieldStatus'], note=m['note'],
                             noteRefs=m['noteRefs'], features=deepcopy(m.get('features', [])), geometryValidated=False)


finalize()
assert set(MUSCLE_TEMPLATES) == set(SOURCE_NAMES)


if __name__ == '__main__':
    import json
    print(json.dumps(MUSCLES, indent=1))
