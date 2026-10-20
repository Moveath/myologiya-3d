"""Reviewed frontoparietal/ethmoid representation, not specimen geometry.

The per-code decisions below are explicit; unknown records are not classified
by words, by an ontology category, or by the existence of a surface coordinate.
"""
from copy import deepcopy
from head_skull_batch2 import _ref, GRAY_URL, OXFORD_URL
from skull_shared_stage5 import _record


def gray(key, page, locator, scope='representation'):
    return _ref('batch3_gray_'+key, 'Gray / Lewis. Anatomy of the Human Body (1918)',
                GRAY_URL+'#page='+str(page), locator, 'gray_lewis_1918', scope=scope)


FRONTAL = (
    gray('frontal', 85, 'PDF pp.85–88: Squama, Surfaces, Orbital or Horizontal Part; Figs.134–135.'),
    _ref('batch3_oxford_frontal', 'van Gijn DR, Dunne J. Oxford Handbook of Head and Neck Anatomy (2022)',
         OXFORD_URL, 'Printed pp.10–12 / PDF pp.29–31: parts and features, Figs.1.4–1.6.',
         'van_gijn_dunne', scope='representation'),
)
PARIETAL = (
    gray('parietal', 82, 'PDF pp.82–85: Surfaces, Borders, Angles; corners are distinguished from named junction points.'),
    _ref('batch3_oxford_parietal', 'van Gijn DR, Dunne J. Oxford Handbook of Head and Neck Anatomy (2022)',
         OXFORD_URL, 'Printed pp.30–31 / PDF pp.49–50: surfaces, borders and angles, Figs.1.17–1.18. The source calls the mastoid-angle groove transverse; it is not used to rename the TA98 sigmoid groove.',
         'van_gijn_dunne', scope='representation'),
)
ETHMOID = (
    gray('ethmoid', 110, 'PDF pp.110–114: cribriform/perpendicular plates, labyrinth, orbital plate, conchae, bulla, uncinate process and hiatus.'),
    _ref('batch3_lunacek_ethmoid', 'Libor Luňáček, Palacký University — Splanchnocranium',
         'https://www.atlascloveka.upol.cz/cs/cs02/cs0201/cs020115.html',
         'Čichová kost = OS ETHMOIDALE; Skořepy nosní: named plates, labyrinth, processes and conchae. No source dimensions transferred.',
         'lunacek_palacky', scope='representation'),
)
CAECUM = (
    gray('caecum', 87, 'PDF p.87: lower frontal crest notch completed by ethmoid; variability and frequent imperviousness. PDF p.110: alae cristae galli.', 'bone_relationships'),
    _ref('batch3_oxford_caecum', 'van Gijn DR, Dunne J. Oxford Handbook of Head and Neck Anatomy (2022)',
         OXFORD_URL, 'Printed p.10 / PDF p.29: Foramen caecum, frontal crest notch–ethmoid articulation.',
         'van_gijn_dunne'),
)
ORBITAL = (
    gray('superior_orbital', 107, 'PDF p.107 and p.166: lesser/greater wings and body of sphenoid; usual lateral completion by orbital plate of frontal.', 'bone_relationships'),
    _ref('batch3_rootman_orbital', 'Rootman J et al. Orbital Fissures: Superior Orbital Fissure. Atlas of Orbital Imaging',
         'https://cris.technion.ac.il/en/publications/orbital-fissures-superior-orbital-fissure-2/',
         'Institutional chapter abstract: sphenoid body medially, lesser wing above, greater wing below, frontal bone laterally. pp.63–67 identify the chapter, not a claim of full-text access.',
         'rootman_orbital_atlas', access='abstract', doi='10.1007/978-3-030-62426-2_5',
         year=2021, dateNote='Institutional record: publication 2021; publisher copyright 2022; publisher page inaccessible.'),
)

# Code -> (display kind, reviewed extent). These are independent decisions.
FRONTAL_KINDS = {
    2: ('volume', 'Вся чешуя включает толщину и обе поверхности; одна наружная поверхность не равна части кости.'),
    4: ('volume', 'Лобное возвышение имеет костный рельеф; вершина не заменяет его объём.'),
    5: ('volume', 'Надбровная дуга рассматривается как протяжённое костное возвышение, а не только кривая его вершины.'),
    6: ('area', 'В этой карточке glabella — межнадбровная область наружной поверхности; краниометрическая точка требует отдельного определения.'),
    9: ('space', 'Представляется отверстие либо открытый проход вырезки; выбранный тип не определяет морфологический вариант данного образца.'),
    10: ('space', 'Представляется просвет лобного отверстия либо вырезки; это не точка её костного края.'),
    13: ('line', 'Указана протяжённая височная линия; её фактическая кривая и раздвоение на образце не размечены.'),
    14: ('volume', 'Скуловой отросток — часть костного вещества с несколькими поверхностями, не единственная точка сочленения.'),
    16: ('volume', 'Для полного лобного гребня нужен костный рельеф; линейная ось не представляет весь гребень.'),
    18: ('space', 'Слепое отверстие — углубление/отверстие у лобно-решётчатого соединения; сквозная проходимость не подразумевается.'),
    19: ('volume', 'Носовая часть включает костное вещество и поверхности сочленения, а не только носовой край.'),
    20: ('volume', 'Носовая ость — выступ с протяжённостью; её конец не заменяет весь выступ.'),
    22: ('volume', 'Глазничная часть включает пластинки и их толщину; нижняя поверхность рассматривается отдельно.'),
    24: ('volume', 'Блоковая ость при наличии — отдельный костный выступ; классификация не подтверждает её наличие в GLB.'),
    25: ('area', 'Блоковая ямка — локальное углубление глазничной поверхности, не канал и не вся глазница.'),
    26: ('area', 'Ямка слёзной железы — углублённая поверхность, не объём самой железы.'),
    28: ('space', 'Решётчатая вырезка здесь представляется как промежуток между глазничными пластинками, а не вся решётчатая кость.'),
    30: ('space', 'Апертура — вход в полость пазухи; её просвет не заменяет всю пазуху.'),
    31: ('volume', 'Межпазушная перегородка — костная пластинка с толщиной, а не линия на одной проекции.'),
}
PARIETAL_KINDS = {
    3: ('area', 'Рассматривается поверхность местной венозной борозды у сосцевидного угла, а не просвет синуса.'),
    5: ('area', 'Артериальная борозда включает дно и края; ось хода сосуда не задаёт её всю поверхность.'),
    6: ('area', 'Совокупность ветвящихся борозд требует набора поверхностных участков, а не одного якоря.'),
    8: ('line', 'Верхняя височная линия требует протяжённой дуги; форма дуги на данном образце не принята.'),
    9: ('line', 'Нижняя височная линия — самостоятельная протяжённая линия, не копия верхней.'),
    10: ('volume', 'Теменной бугор — выпуклый рельеф, а не только точка максимума.'),
    15: ('area', 'Лобный угол — угловая область кости между краями; он не тождественен краниометрической точке bregma.'),
    16: ('area', 'Затылочный угол — угловая область между краями; точка lambda не заменяет эту область.'),
    17: ('area', 'Клиновидный угол — передненижняя область кости; pterion относится к соединению костей, а не заменяет всю область.'),
    18: ('area', 'Сосцевидный угол — усечённая угловая область с внутренней поверхностью; asterion является отдельной точкой соединения.'),
    19: ('space', 'Представляется отверстие; его наличие и размер у конкретного образца не следуют из каталога.'),
}
ETHMOID_KINDS = {
    2: ('volume', 'Решётчатая пластинка — перфорированная костная пластинка; её верхняя поверхность и отверстия различаются.'),
    3: ('space', 'Термин охватывает множество отдельных отверстий пластинки; один маркер не задаёт их число или все просветы.'),
    4: ('volume', 'Петушиный гребень — костный выступ; его задний край не равен всему образованию.'),
    5: ('volume', 'Крыло петушиного гребня — костное продолжение; тип не подтверждает оба крыла существующей точкой.'),
    6: ('volume', 'Перпендикулярная пластинка включает толщину и две стороны; не равна всей носовой перегородке.'),
    7: ('volume', 'Лабиринт — масса костных стенок и ячеек; одна полость или поверхность его не заменяет.'),
    11: ('volume', 'Глазничная пластинка — тонкая костная стенка; её глазничная поверхность не равна всей пластинке.'),
    13: ('volume', 'Верхняя раковина — изогнутая костная часть; край или точка не заменяют её форму.'),
    14: ('volume', 'Средняя раковина — костная пластинка с собственной формой, а не свободный край.'),
    15: ('volume', 'Решётчатый пузырёк рассматривается как костное выпячивание, а не единственная точка на поверхности.'),
    16: ('volume', 'Крючковидный отросток — изогнутая пластинка; прикрепление и форма данного образца отдельно не приняты.'),
    18: ('space', 'Полулунная расщелина — промежуток между соответствующими образованиями, не линия на кости.'),
}


def reviewed_decisions():
    result={}
    for bone, prefix, rows, refs in [
        ('frontal','A02.1.03.',FRONTAL_KINDS,FRONTAL),
        ('parietal_right','A02.1.02.',PARIETAL_KINDS,PARIETAL),
        ('parietal_left','A02.1.02.',PARIETAL_KINDS,PARIETAL),
        ('ethmoid','A02.1.07.',ETHMOID_KINDS,ETHMOID),
    ]:
        for number,(kind,reason) in rows.items():
            result[bone,prefix+f'{number:03}']={'kind':kind,'reason':reason,'refs':refs}
    result['sphenoid','A02.1.05.023']={'kind':'space','reason':'Локальная запись клиновидной кости относится к верхней глазничной щели; сторона старого якоря отдельно не принята.','refs':ORBITAL}
    return result


def apply_record_review(record):
    decision=reviewed_decisions().get((record['b'],record['c']))
    if not decision:return
    record['geometryKindReason']=decision['reason']
    record['refs']=deepcopy(record['refs'])
    # Keep original exact field references; add only scoped supporting evidence.
    refs=decision['refs']
    if record['c'] in ('A02.1.03.010','A02.1.03.024'):
        # Existing address-specific study/illustration supports these exceptions;
        # Oxford's generic list is not claimed to describe the unlisted spine/notch.
        refs=(FRONTAL[0],) if record['c'].endswith('.024') else ()
    if record['c']=='A02.1.02.003':
        # Historical transverse-vs-sigmoid wording is preserved, not normalised.
        refs=()
    if record['c']=='A02.1.03.018':
        refs=CAECUM  # The exact locators already cover this record's definition.
    record['refs'].extend(deepcopy(list(refs)))
    if record['c']=='A02.1.03.006':
        record['refs'].append(_ref('batch3_fipat_glabella','FIPAT TA98 — A02.1.03.006',
            'https://ifaa.unifr.ch/Public/EntryPage/TA98%20Tree/Entity%20TA98%20EN/02.1.03.006%20Entity%20TA98%20EN.htm',
            'Material entity; zone of frontal bone. Supports regional scope, not coordinates.', 'fipat',scope='nomenclature'))
    if record['c']=='A02.1.03.018':
        record['relations']=[dict(bone=b,role='boundaryContribution',refs=[r['id'] for r in CAECUM]) for b in ('frontal','ethmoid')]
        record['concept']='frontal-foramen-caecum'
        record['catalogueBones']=['frontal']
        record['modelNote']+=' Образование связано с лобной и решётчатой костями. Старая проекция сохранена только как ориентировочный участок лобной кости; она не подтверждает проходимость или полный контур отверстия.'
    if record['c']=='A02.1.05.023':
        record['lateralityReview']={'pattern':'bilateral','verifiedModelSides':[], 'scope':'catalogue_term',
            'source':'research/stage5-skull-batch3-2026-10-16/source-review.json',
            'note':'Общие щели справа и слева представлены отдельно без координат. Одна старая точка клиновидной кости не подтверждает обе стороны; её сторона не принята для связи partOf.'}
        record['modelNote']+=' Это прежняя запись клиновидного каталога; полная щель также имеет лобный вклад. Старый якорь не переносился в новые общие экземпляры.'


def additional_instances(terminology):
    for side in ('right','left'):
        yield _record('shared_skull_083_'+side,'A02.1.00.083',terminology['A02.1.00.083'],
            'Верхняя глазничная щель',
            'Границы щели включают тело, малое и большое крылья клиновидной кости; латерально её обычно завершает глазничная часть лобной кости.',
            ['sphenoid','frontal'],side,'boundaryContribution','space',ORBITAL,
            'Справочный состав не подтверждает контур или вариант замыкания на этой модели. Сторона старой точки A02.1.05.023 не принята; её координата не назначена ни одному новому экземпляру.',concept='skull-whole-083')
