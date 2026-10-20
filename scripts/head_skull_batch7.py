"""Reviewed facial-bone entities. No coordinate/shape inference or TA extensions."""
from copy import deepcopy
from head_skull_batch2 import _ref, GRAY_URL
from head_face_evidence import PALACKY

BONES = ('zygomatic_right', 'zygomatic_left', 'nasal_right', 'nasal_left',
         'lacrimal_right', 'lacrimal_left', 'inferior_concha_right', 'inferior_concha_left', 'vomer')
REPORT = 'research/stage5-skull-batch7-2026-10-16/geometry-kind-review.json'


def ref(key, title, url, locator, group, access='full_text', **metadata):
    return _ref('batch7_'+key, title, url, locator, group,
                scope='anatomical_entity_and_representation', access=access, **metadata)


GRAY = {
    b: ref('gray_'+b, 'Gray / Lewis. Anatomy of the Human Body (1918)',
           GRAY_URL+'#page='+str(page), locator, 'gray_lewis_1918')
    for b, page, locator in (
        ('nasal', 115, 'PDF pp.115–117: surfaces, borders and articulations; not a source for new specimen coordinates.'),
        ('lacrimal', 126, 'PDF pp.126–127: orbital/nasal surfaces, crest, hamulus and descending process.'),
        ('zygomatic', 127, 'PDF pp.127–131: surfaces, processes, apertures and channels. Historical process terminology is not silently substituted for TA98.'),
        ('inferior_concha', 135, 'PDF pp.135–137: two surfaces, borders, three processes and extremities.'),
        ('vomer', 137, 'PDF pp.137–138: paired alae and lateral grooves; four borders. Not used to resolve crista choanalis.'),
    )
}
PALACKY_REF = ref('palacky', 'Libor Luňáček, Univerzita Palackého — Splanchnocranium',
    PALACKY, 'OS ZYGOMATICUM, OS LACRIMALE, OS NASALE, VOMER and concha nasalis inferior. The disputed vomer definition is retained as disagreement.', 'lunacek_palacky')
KIM = ref('kim2013', 'Kim HS et al. Three-dimensional courses of zygomaticofacial and zygomaticotemporal canals using micro-computed tomography in Korean (2013)',
    'https://pubmed.ncbi.nlm.nih.gov/24036727/', 'Abstract: two named canal systems, intrabony courses, communications and variation; 14 sides. No specimen mapping.',
    'kim_hs_2013', 'abstract', pmid='24036727', doi='10.1097/SCS.0b013e318299775d')
KAWATA = ref('kawata2024', 'Kawata K, Ide Y, Sunohara M. Anatomical study of the zygomaticofacial foramen and zygomatic canals (2024)',
    'https://acbjournal.org/journal/view.html?doi=10.5115/acb.23.293',
    'Introduction; Methods: Identification of zygomatic canals and foramina; original micro-CT study of 104 sides. Distinguishes canal from its apertures; no measurements transferred.',
    'kawata_2024', pmid='38237948', doi='10.5115/acb.23.293', electronicDate='2024-01-19', printDate='2024-06-30')
VOMER_REVIEW = ref('marusic2006', 'Marušić A, Vinter I, Krmpotić-Nemanić J. Lost and found anatomical terms: Crista choanalis vomeris (2006)',
    'https://pubmed.ncbi.nlm.nih.gov/16711168/', 'Abstract: crest from alar angle towards free posterior margin; cuneiform part behind crest. Conflicting atlas definitions remain explicit.',
    'marusic_2006', 'abstract', pmid='16711168', doi='10.1016/j.aanat.2006.01.010')
LIU = ref('liu2020', 'Liu Z et al. Functional nasolacrimal duct decompression for chronic dacryocystitis (2020)',
    'https://pubmed.ncbi.nlm.nih.gov/32791645/',
    'Indexed English abstract, Result (2): descending lacrimal process in the bony wall. EFetch metadata verified; direct PubMed/PMC CAPTCHA. Not used as a complete universal canal-wall definition.',
    'liu_2020', 'indexed_abstract', pmid='32791645', doi='10.13201/j.issn.2096-7993.2020.07.018')

# Frozen entity-specific decisions, not a name-to-type classifier.
DECISIONS = {
 'zygomatic': ('A02.1.14.', {
  5: ('volume', 'Отросток — костный объём, участвующий в дуге; его соединительный шов — отдельная линия.'),
  6: ('volume', 'Восходящий отросток имеет толщину и поверхности; не равен лобно-скуловому шву.'),
  7: ('volume', 'Глазничный бугорок — костное возвышение за краем глазницы; маркер вершины не описывает его форму.'),
  8: ('volume', 'Краевой бугорок — выступ заднего края отростка, а не вся линия края; скобки TA98 сохранены без вывода о частоте.'),
  9: ('space', 'Апертура глазничной поверхности отличается от внутрикостных каналов; число входов вариабельно.'),
 10: ('space', 'Выход на лицевой поверхности — отверстие, не весь скулолицевой канал и не единственная обязательная апертура.'),
 11: ('space', 'Выход на височной поверхности не подменяет весь ветвящийся скуловисочный ход.'),
 }),
 'nasal': ('A02.1.10.', {
  2: ('area', 'Борозда — открытое ложе внутренней поверхности; её ширина не представлена одной осевой линией.'),
  3: ('space', 'Носовые отверстия — апертуры наружной поверхности; одна координата не подтверждает число всех отверстий.'),
 }),
 'lacrimal': ('A02.1.09.', {
  2: ('volume', 'Задний слёзный гребень — костный рельеф глазничной поверхности, а не вся ямка слёзного мешка.'),
  3: ('area', 'Собственное открытое костное ложе перед гребнем не равно всему общему носослёзному каналу.'),
  4: ('volume', 'Крючок — костный выступ конца гребня, отличающийся от нисходящего отростка перед гребнем.'),
 }),
 'inferior_concha': ('A02.1.08.', {
  2: ('volume', 'Восходящий слёзный отросток — костная часть раковины; не нисходящий отросток слёзной кости.'),
  3: ('volume', 'Отогнутая пластинка имеет толщину и две стороны; не вся медиальная стенка верхнечелюстной пазухи.'),
  4: ('volume', 'Решётчатый отросток — собственная восходящая костная пластинка; соседний крючковидный отросток не её дубликат.'),
 }),
 'vomer': ('A02.1.11.', {
  2: ('volume', 'Крылья — парные костные расширения верхнего края; не один верхний край и не клиновидный клюв.'),
  3: ('area', 'Носонёбные борозды занимают ложа на обеих боковых поверхностях; одиночная координата не доказывает обе стороны.'),
  4: ('volume', 'По Marušić это костный гребень, отличный от свободного края. Объёмный тип не разрешает спор о границах и определении.'),
  5: ('volume', 'Клиновидная часть обозначает костную часть позади гребня, не пустой клиновидный промежуток; её граница остаётся спорной.'),
 }),
}


def reviewed_decisions():
    result = {}
    for bone in BONES:
        base = bone.removesuffix('_right').removesuffix('_left')
        prefix, entries = DECISIONS[base]
        for num, (kind, reason) in entries.items():
            result[bone, prefix+f'{num:03}'] = dict(kind=kind, reason=reason, group=base, number=num)
    return result


def decision_sources(decision):
    refs = [GRAY[decision['group']], PALACKY_REF]
    if decision['group']=='zygomatic' and decision['number'] in (9,10,11): refs += [KIM, KAWATA]
    if decision['group']=='vomer' and decision['number'] in (4,5): refs = [PALACKY_REF, VOMER_REVIEW]
    return refs


def apply_record_review(record):
    decision = reviewed_decisions().get((record['b'], record['c']))
    if not decision: return
    assert record['geometryKind']==decision['kind']
    record['geometryReview'] = dict(status='representation_reviewed', rationale=decision['reason'], source=REPORT,
                                    coordinateAcceptance=False, extentAcceptance=False)
    record['refs'] = record['refs'] + deepcopy(decision_sources(decision))
    record['modelNote'] += ' Проверен тип образования; точная локализация, полный контур и объём на этом образце не приняты.'
    if record['b']=='vomer' and record['c'] in ('A02.1.11.002', 'A02.1.11.003'):
        record['lateralityReview'] = dict(pattern='bilateral_on_unpaired_bone', status='coverage_unconfirmed',
            note='Крылья и боковые борозды представлены справа и слева на непарном сошнике. У этой каталожной записи сохранён один прежний маркер; он не подтверждает обе стороны. Координаты не зеркалировались.')


def additional_records():
    """Eight evidenced extras, kept outside the own-bone TA98 catalogue."""
    for side in ('right','left'):
        zyg = 'zygomatic_'+side
        for key, label, opening in (
            ('zygomaticofacial_canals', 'Скулолицевые каналы', 'A02.1.14.010'),
            ('zygomaticotemporal_canals', 'Скуловисочные каналы', 'A02.1.14.011'),
        ):
            yield _extra(zyg, key, label, 'volume',
                'Внутрикостные ходы скуловой кости, связанные с соответствующими отверстиями. Их число, ветвление и сообщения различаются; возможны общие участки. Апертуры и каналы — разные структуры.',
                [KIM, KAWATA], ['head_'+zyg+'_A02_1_14_009', 'head_'+zyg+'_'+opening.replace('.','_')])
        yield _extra(zyg, 'maxillary_process', 'Верхнечелюстной отросток скуловой кости', 'volume',
            'Костная часть скуловой кости, направленная к верхней челюсти. Это не скуловой отросток верхней челюсти и не весь соединяющий их шов.',
            [GRAY['zygomatic'], PALACKY_REF], ['head_maxilla_'+side+'_A02_1_12_012'])
        lac = 'lacrimal_'+side
        yield _extra(lac, 'descending_process', 'Нисходящий отросток слёзной кости', 'volume',
            'Нижнее продолжение слёзной кости перед задним слёзным гребнем, участвующее в костной стенке носослёзного канала. Отличается от слёзного крючка и от слёзного отростка нижней носовой раковины.',
            [GRAY['lacrimal'], LIU], ['shared_skull_085_'+side, 'head_'+lac+'_A02_1_09_004'])


def _extra(bone, key, ru, kind, description, refs, related):
    return dict(id='extra_'+bone+'_'+key, b=bone, t='additional', ru=ru, lat='', x=description,
        m=[], g='Дополнительные образования', side=bone.rsplit('_',1)[1], geometryKind=kind,
        refs=deepcopy(refs), relatedLandmarks=related, educationAvailable=False,
        nomenclatureStatus='outside_own_TA98_list',
        geometryReview=dict(status='representation_reviewed', source=REPORT, coordinateAcceptance=False, extentAcceptance=False),
        modelNote='Существование образования подтверждено источниками. Его положение, границы и геометрия на этой модели не подтверждены; 3D-маркер не создан. Отдельный код TA98 не присвоен.')
